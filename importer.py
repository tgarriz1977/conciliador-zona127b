import pandas as pd
import mysql.connector
from db import get_db_connection
from datetime import datetime

def parse_amount(amount_str):
    """
    Convierte string de moneda formato '1.781.939,69' a float 1781939.69
    """
    if pd.isna(amount_str):
        return 0.0
    # Eliminar puntos de miles y reemplazar coma decimal por punto
    clean_str = str(amount_str).replace('.', '').replace(',', '.')
    try:
        return float(clean_str)
    except ValueError:
        return 0.0

def import_pagos_mp(file_path):
    """
    Importa pagos desde CSV de Mercado Pago.
    Columnas esperadas: RELEASE_DATE, TRANSACTION_TYPE, REFERENCE_ID, TRANSACTION_NET_AMOUNT
    """
    conn = get_db_connection()
    if not conn:
        return "Error de conexión a DB"
    
    cursor = conn.cursor()
    try:
        # Detectar cabecera dinámicamente
        header_row = 0
        with open(file_path, 'r', encoding='latin1') as f:
            for i, line in enumerate(f):
                if 'RELEASE_DATE' in line and 'REFERENCE_ID' in line:
                    header_row = i
                    break
        
        print(f"DEBUG - Header detected at line: {header_row}")
        df = pd.read_csv(file_path, sep=';', skiprows=header_row, encoding='latin1') 
        print(f"DEBUG - Pagos Loaded: {len(df)} rows")
        print(f"DEBUG - Columns: {df.columns.tolist()}")
        if not df.empty:
            print(f"DEBUG - First Query Row: {df.iloc[0].to_dict()}")
        
        count_inserted = 0
        count_duplicates = 0
        
        for _, row in df.iterrows():
            # Validar que sea una fila válida
            ref_id = row.get('REFERENCE_ID')
            if pd.isna(ref_id):
                continue
                
            transaction_id = ref_id
            date_str = row['RELEASE_DATE']
            amount_str = row['TRANSACTION_NET_AMOUNT']
            desc = row['TRANSACTION_TYPE']
            
            # Limpieza
            try:
                fecha_cobro = datetime.strptime(date_str, '%d-%m-%Y')
            except:
                continue # Fecha inválida
                
            monto = parse_amount(amount_str)
            
            # Extraer nombre pagador
            nombre_pagador = str(desc).replace('Transferencia recibida ', '').strip()
            
            # Insertar (Ignorar duplicados por ID)
            sql = """
                INSERT IGNORE INTO pagos_mp (id_pago_mp, fecha_cobro, monto_neto, nombre_pagador, estado_conciliacion)
                VALUES (%s, %s, %s, %s, 'PENDIENTE')
            """
            val = (transaction_id, fecha_cobro, monto, nombre_pagador)
            
            cursor.execute(sql, val)
            if cursor.rowcount > 0:
                count_inserted += 1
            else:
                count_duplicates += 1
                
        conn.commit()
        cursor.close()
        conn.close()
        return f"Procesado: {count_inserted} nuevos, {count_duplicates} duplicados."
        
    except Exception as e:
        return f"Error importando pagos: {str(e)}"

def import_clientes(file_path, campana):
    """
    Importa clientes desde CSV.
    Columnas: orden, reparto, cuenta, nombre, deuda
    """
    conn = get_db_connection()
    if not conn:
        return "Error de conexión a DB"
        
    cursor = conn.cursor()
    try:
        # Forzar latin1 y separador ;
        df = pd.read_csv(file_path, sep=';', encoding='latin1')
        
        count_inserted = 0
        count_skipped = 0
        
        check_sql = "SELECT 1 FROM clientes_pedidos WHERE orden=%s AND cuenta=%s AND campana=%s"
        insert_sql = """
            INSERT INTO clientes_pedidos (orden, reparto, cuenta, nombre_clienta, monto_pedido, campana, estado_liquidacion)
            VALUES (%s, %s, %s, %s, %s, %s, 'PENDIENTE')
        """
        
        for _, row in df.iterrows():
            cuenta = row.get('cuenta')
            nombre = row.get('nombre')
            deuda = parse_amount(row.get('deuda'))
            orden = row.get('orden')
            reparto = row.get('reparto')
            
            if pd.isna(nombre):
                continue
            
            # Chequear duplicado (Orden + Cuenta + Campaña)
            cursor.execute(check_sql, (orden, cuenta, campana))
            if cursor.fetchone():
                count_skipped += 1
                continue
                
            val = (orden, reparto, cuenta, nombre, deuda, campana)
            cursor.execute(insert_sql, val)
            count_inserted += 1
            
        conn.commit()
        cursor.close()
        conn.close()
        return f"Campaña '{campana}': {count_inserted} pedidos importados ({count_skipped} duplicados ignorados)."
        
    except Exception as e:
        return f"Error importando clientes: {str(e)}"
