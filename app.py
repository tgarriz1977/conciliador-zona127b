from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from db import get_db_connection
from importer import import_clientes, import_pagos_mp
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/importar', methods=['GET', 'POST'])
def importar():
    msg = None
    msg_type = 'info'
    
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        file = request.files.get('archivo')
        
        if not file or file.filename == '':
            msg = "Debes seleccionar un archivo."
            msg_type = 'danger'
        else:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            if tipo == 'clientes':
                campana = request.form.get('campana')
                if not campana:
                    msg = "Debes indicar la Campaña."
                    msg_type = 'danger'
                else:
                    res = import_clientes(filepath, campana)
                    msg = res
                    msg_type = 'success' if 'Error' not in res else 'danger'
                    
            elif tipo == 'pagos':
                res = import_pagos_mp(filepath)
                msg = res
                msg_type = 'success' if 'Error' not in res else 'danger'
            
            # Limpiar archivo
            try:
                os.remove(filepath)
            except:
                pass
                
    return render_template('importar.html', msg=msg, msg_type=msg_type)

@app.route('/')
def index():
    conn = get_db_connection()
    status = "Desconectado"
    stats = {}
    if conn:
        status = "Conectado a la Base de Datos"
        cursor = conn.cursor(dictionary=True)
        
        # Stats simples
        cursor.execute("SELECT COUNT(*) as c FROM pagos_mp WHERE estado_conciliacion='PENDIENTE'")
        stats['pagos_pendientes'] = cursor.fetchone()['c']
        
        cursor.execute("SELECT COUNT(*) as c FROM clientes_pedidos WHERE estado_liquidacion='PENDIENTE'")
        stats['pedidos_pendientes'] = cursor.fetchone()['c']
        
        cursor.close()
        conn.close()
    return render_template('index.html', status=status, stats=stats)

@app.route('/conciliacion')
def conciliacion():
    # Filtros
    fecha_min = request.args.get('fecha_min')
    fecha_max = request.args.get('fecha_max')
    pagador = request.args.get('pagador', '').strip()
    orden = request.args.get('orden', 'DESC') # ASC o DESC
    
    conn = get_db_connection()
    if not conn:
        return "Error de DB", 500
    
    cursor = conn.cursor(dictionary=True)
    
    # Construir Query Dinámica (SOLO INGRESOS para Conciliación)
    query = """
        SELECT * FROM pagos_mp 
        WHERE estado_conciliacion='PENDIENTE'
          AND monto_neto > 0 
          AND nombre_pagador NOT LIKE 'Rendimientos%'
    """
    params = []
    
    if fecha_min:
        query += " AND fecha_cobro >= %s"
        params.append(fecha_min)
        
    if fecha_max:
        query += " AND fecha_cobro <= %s"
        params.append(fecha_max + ' 23:59:59')
        
    if pagador:
        query += " AND nombre_pagador LIKE %s"
        params.append(f"%{pagador}%")
        
    # Validar orden
    order_sql = "ASC" if orden.upper() == "ASC" else "DESC"
    query += f" ORDER BY fecha_cobro {order_sql}"
    
    cursor.execute(query, params)
    pagos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('conciliacion.html', pagos=pagos, args=request.args)

@app.route('/transferencias')
def transferencias():
    conn = get_db_connection()
    if not conn: return "Error DB", 500
    cursor = conn.cursor(dictionary=True)
    
    # Solo Egresos
    cursor.execute("SELECT * FROM pagos_mp WHERE monto_neto < 0 ORDER BY fecha_cobro DESC")
    pagos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('transferencias.html', pagos=pagos)

@app.route('/rendimientos')
def rendimientos():
    conn = get_db_connection()
    if not conn: return "Error DB", 500
    cursor = conn.cursor(dictionary=True)
    
    # Solo Rendimientos
    cursor.execute("SELECT * FROM pagos_mp WHERE nombre_pagador LIKE 'Rendimientos%' ORDER BY fecha_cobro DESC")
    pagos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('rendimientos.html', pagos=pagos)

@app.route('/api/buscar_cliente')
def buscar_cliente():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Busqueda por nombre o cuenta (si es numerico)
    sql = """
        SELECT * FROM clientes_pedidos 
        WHERE (nombre_clienta LIKE %s OR cuenta LIKE %s)
          AND estado_liquidacion = 'PENDIENTE'
          AND fk_pago_mp_id IS NULL
        LIMIT 20
    """
    like_q = f"%{q}%"
    cursor.execute(sql, (like_q, like_q))
    resultados = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(resultados)

@app.route('/api/conciliar', methods=['POST'])
def conciliar():
    data = request.json
    pago_id = data.get('pago_id')
    cliente_id = data.get('cliente_id')
    
    if not pago_id or not cliente_id:
        return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Iniciar transaccion
        
        # 1. Verificar estado actual
        # ... (Podriamos agregar checks extra aqui)
        
        # 2. Actualizar Pago
        sql_pago = "UPDATE pagos_mp SET estado_conciliacion='CONCILIADO', fk_cliente_id=%s WHERE id_pago_mp=%s"
        cursor.execute(sql_pago, (cliente_id, pago_id))
        
        # 3. Actualizar Pedido
        sql_pedido = "UPDATE clientes_pedidos SET fk_pago_mp_id=%s WHERE cliente_id=%s"
        cursor.execute(sql_pedido, (pago_id, cliente_id))
        
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
