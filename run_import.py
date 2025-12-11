from importer import import_clientes, import_pagos_mp
import os

def run():
    print("--- Iniciando Importación ---")
    
    # Importar Clientes
    if os.path.exists('clientes.csv'):
        print("Importando clientes.csv...")
        res = import_clientes('clientes.csv')
        print(res)
    else:
        print("No se encontró clientes.csv")

    # Importar Pagos MP
    # Buscar archivo que coincida con pattern account_statement*.csv
    files = [f for f in os.listdir('.') if f.startswith('account_statement') and f.endswith('.csv')]
    if files:
        target = files[0]
        print(f"Importando pagos desde {target}...")
        res = import_pagos_mp(target)
        print(res)
    else:
        print("No se encontró archivo de estado de cuenta de MP")

    print("--- Fin de Importación ---")

if __name__ == '__main__':
    run()
