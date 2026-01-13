from database import conectar, crear_tablas
from datetime import date
import pandas as pd
from pathlib import Path

# -----------------------------
# Entradas seguras
# -----------------------------
def pedir_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print('No puede estar vacio.')

def pedir_entero(mensaje, minimo=None, maximo=None):
    while True:
        try:
            valor = int(input(mensaje).strip())
            if minimo is not None and valor < minimo:
                print(f'Debe ser >= {minimo}')
                continue
            if maximo is not None and valor > maximo:
                print(f'Debe ser <= {maximo}')
                continue
            return valor
        except ValueError:
            print('Ingrese numero valido.')

def pedir_tipo_prueba():
    while True:
        tipo = pedir_texto('Tipo de prueba (PRE, RUT, POST): ').upper()
        if tipo in ('PRE', 'RUT', 'POST'):
            return tipo
        print('Tipo invalido. Use PRE, RUT o POST.')
        
# -----------------------------
# Pedir fecha
# -----------------------------
def pedir_fecha():
    while True:
        fecha = input('Fecha (YYYY-MM-DD) [Enter = hoy]: ').strip()
        if not fecha:
            return date.today().isoformat()
        try:
            date.fromisoformat(fecha)
            return fecha
        except ValueError:
            print('Formato invalido. Use AÑO-MES-DIA')

# -----------------------------
# Cargar empresas
# -----------------------------
def cargar_empresa():
    nombre = pedir_texto('Nombre de la empresa: ')
    precio = pedir_entero('Precio por prueba (Gs): ', 1)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO empresa (nombre, precio_por_prueba) VALUES (?, ?)',
        (nombre, precio)
    )

    conn.commit()
    conn.close()

    print('\nEmpresa cargada correctamente.')

# -----------------------------
# Listar empresas
# -----------------------------
def listar_empresas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('SELECT id, nombre, precio_por_prueba FROM empresa')
    empresas = cursor.fetchall()
    conn.close()

    if not empresas:
        print('\nNo hay empresas cargadas.')
        return []
    
    print('\nEmpresas disponibles.')
    for e in empresas:
        print(f'{e[0]} - {e[1]} ({e[2]} Gs por prueba)')

    return empresas

# -----------------------------
# Mostrar menu
# -----------------------------
def mostrar_menu():
    print('\n=== MENU PRINCIPAL ===')
    print('[A] Pruebas')
    print('[B] Empresas')
    print('[C] Totales / Reportes')
    print('[D] Exportar')
    print('[S] Salir')

# Submenu de pruebas
def menu_pruebas():
    while True:
        print('\n--- PRUEBAS ---')
        print('[1] Agregar prueba')
        print('[2] Mostrar pruebas')
        print('[3] Editar prueba')
        print('[4] Eliminar prueba')
        print('[0] Volver')

        op = pedir_texto('Opcion: ')

        if op == '1':
            agg_prueba()
        elif op == '2':
            mostrar_pruebas()
        elif op == '3':
            editar_prueba()
        elif op == '4':
            eliminar_prueba()
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

# Submenu de empresas
def menu_empresas():
    while True:
        print('\n--- EMPRESAS ---')
        print('[1] Cargar empresa')
        print('[2] Listar empresas')
        print('[0] Volver')

        op = pedir_texto('Opcion: ')

        if op == '1':
            cargar_empresa()
        elif op == '2':
            listar_empresas()
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

# Submenu TOTALES/REPORTES
def menu_totales():
    while True:
        print('\n--- TOTALES / REPORTES ---')
        print('[1] Total del día')
        print('[2] Total del mes')
        print('[3] Total por empresa')
        print('[4] Total por empresa (mes)')
        print('[0] Volver')

        op = pedir_texto('Opcion: ')

        if op == '1':
            total_del_dia()
        elif op == '2':
            total_del_mes()
        elif op == '3':
            total_por_empresa()
        elif op == '4':
            total_por_empresa_mes()
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

# Submenu exportar
def menu_exportar():
    while True:
        print('\n--- EXPORTAR ---')
        print('[1] Exportar todo a Excel')
        print('[2] Exportar mes a Excel')
        print('[0] Volver')

        op = pedir_texto('Opcion: ')

        if op == '1':
            exportar_excel()
        elif op == '2':
            exportar_excel_mes()
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

# -----------------------------
# [A] Agregar prueba
# -----------------------------
def agg_prueba():
    fecha_test = pedir_fecha()
    cantidad_dia = pedir_entero('\nCantidad de pruebas del dia (1 a 6): ', 1, 6)
    legajo_numero = pedir_texto('Numero de legajo: ')
    tipo_prueba = pedir_tipo_prueba()

    empresas = listar_empresas()
    if not empresas:
        print('Debe cargar una empresa primero')
        return
    
    empresa_id = pedir_entero('Seleccione ID de empresa: ', 1)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT precio_por_prueba FROM empresa WHERE id = ?',
        (empresa_id,)
    )
    precio = cursor.fetchone()
    conn.close()

    if not precio:
        print('Empresa no valida.')
        return
    
    total = cantidad_dia * precio[0]

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO pruebas (
            fecha, legajo, tipo_prueba, empresa_id, localidad, cantidad, total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        fecha_test,
        legajo_numero,
        tipo_prueba,
        empresa_id,
        'pendiente',
        cantidad_dia,
        total
    ))

    conn.commit()
    conn.close()

    print('\nPrueba guardada en la base de datos.')
    print(f'Total a cobrar: {total} Gs.')

# -----------------------------
# [C] Total del día
# -----------------------------
def total_del_dia():
    fecha = pedir_fecha()
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT SUM(total)
        FROM pruebas
        WHERE fecha = date('now')
    ''')

    total = cursor.fetchone()[0] or 0
    conn.close()

    print(f'\nTotal del dia: {total} Gs.')

# -----------------------------
# [D] Mostrar pruebas
# -----------------------------
def mostrar_pruebas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            p.id,
            p.fecha,
            p.legajo,
            p.tipo_prueba,
            e.nombre,
            p.cantidad,
            p.total
        FROM pruebas p
        JOIN empresa e ON p.empresa_id = e.id
        ORDER BY p.id DESC
    ''')

    filas = cursor.fetchall()
    conn.close()

    if not filas:
        print('\nNo hay pruebas cargadas.')
        return
    
    print('\nID |  Fecha     | Legajo | Tipo | Empresa        | Cant | Total')
    print('-' * 75)
    for f in filas:
        print(f'{f[0]:<3}| {f[1]:<10} | {f[2]:<6} | {f[3]:<4} | {f[4]:<14} | {f[5]:<4} | {f[6]}')

# -----------------------------
# [E] Editar prueba
# -----------------------------
def editar_prueba():
    mostrar_pruebas()

    prueba_id = pedir_entero('\nIngrese el ID a editar: ', 1)
    nueva_cantidad = pedir_entero('Nueva cantidad de pruebas (1 a 6): ', 1, 6)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT e.precio_por_prueba '
        'FROM pruebas p JOIN empresa e ON p.empresa_id = e.id '
        'WHERE p.id = ?',
        (prueba_id,)
    )
    fila = cursor.fetchone()
    if not fila:
        print('Prueba no encontrada.')
        conn.close()
        return

    precio = fila[0]

    nuevo_total = nueva_cantidad * precio

    cursor.execute(
        'UPDATE pruebas SET cantidad = ?, total = ? WHERE id = ?',
        (nueva_cantidad, nuevo_total, prueba_id)
    )

    conn.commit()
    conn.close()

    print('\nPrueba actualizada correctamente.')

# -----------------------------
# [F] Eliminar prueba
# -----------------------------
def eliminar_prueba():
    mostrar_pruebas()

    prueba_id = pedir_entero('\nIngrese el ID a eliminar: ', 1)

    confirmacion = pedir_texto(
        'Escriba "SI" para confirmar eliminacion: '
    ).upper()

    if confirmacion != 'SI':
        print('Eliminacion cancelada.')
        return
    
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM pruebas WHERE id = ?',
        (prueba_id,)
    )

    conn.commit()
    conn.close()

    print('\nPrueba eliminada correctamente.')

# -----------------------------
# [G] Total del mes
# -----------------------------
def total_del_mes():
    mes = pedir_texto('\nIngrese mes (MM): ')
    anio = pedir_texto('\nIngrese el año (YYYY): ')

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT SUM(total)
        FROM pruebas
        WHERE strftime('%m', fecha) = ?
          AND strftime('%Y', fecha) = ?
    ''', (mes, anio))

    total = cursor.fetchone()[0] or 0
    conn.close()

    print(f'\nTotal del mes {mes}/{anio}: {total} Gs')

# -----------------------------
# [H] Exportar a Excel (todo)
# -----------------------------
def exportar_excel():
    conn = conectar()

    query = '''
        SELECT
            p.id,
            p.fecha,
            p.legajo,
            p.tipo_prueba,
            p.localidad,
            p.cantidad,
            p.total,
            e.nombre AS empresa
        FROM pruebas p
        JOIN empresa e ON p.empresa_id = e.id
        ORDER BY fecha
    '''

    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print('\nNo hay datos  para exportar')
        return
    
    base_dir = Path(__file__).resolve().parent.parent
    export_dir = base_dir / 'exports'
    export_dir.mkdir(exist_ok=True)

    archivo = export_dir / 'pruebas_poligraficas.xlsx'
    df.to_excel(archivo, index=False)

    print(f'\nArchivo Excel generado correctamente.')
    print(archivo)

# -----------------------------
# [I] Total por empresa
# -----------------------------
def total_por_empresa():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            e.nombre,
            SUM(p.total)
        FROM pruebas p
        JOIN empresa e ON p.empresa_id = e.id
        GROUP BY e.id
        ORDER BY e.nombre
    ''')
    
    filas = cursor.fetchall()
    conn.close()

    if not filas:
        print('\nNo hay datos para mostrar')
        return
    
    print('\nTOTAL POR EMPRESA')
    print('-' * 40)
    for nombre,total in filas:
        print(f'{nombre:<20} {total or 0} Gs')

# -----------------------------
# [J] Total de empresa por mes
# -----------------------------
def total_por_empresa_mes():
    mes = pedir_texto('Ingrese mes (MM): ')
    anio = pedir_texto('Ingrese año (YYYY): ')

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            e.nombre,
            SUM(p.total)
        FROM pruebas p
        JOIN empresa e ON p.empresa_id = e.id
        WHERE strftime('%m', p.fecha) = ?
          AND strftime('%Y', p.fecha) = ?
        GROUP BY e.id
        ORDER BY e.nombre
    ''', (mes, anio))

    filas = cursor.fetchall()
    conn.close()

    if not filas:
        print('\nNo hay datos para ese periodo.')
        return
    
    print(f'\nTOTAL POR EMPRESA - {mes}/{anio}')
    print('-' * 40)
    for nombre, total in filas:
        print(f'{nombre:<20} {total or 0} Gs')

# -----------------------------
# Exportar a Excel por mes
# -----------------------------
def exportar_excel_mes():
    mes = pedir_texto('Ingrese mes (MM): ')
    anio = pedir_texto('Ingrese año (YYYY): ')

    conn = conectar()

    query = '''
        SELECT
            id,
            fecha,
            legajo,
            tipo_prueba,
            localidad,
            cantidad,
            total
        FROM pruebas
        WHERE strftime('%m', fecha) = ?
          AND strftime('%Y', fecha) = ?
        ORDER BY fecha
    '''

    df = pd.read_sql_query(query, conn, params=(mes, anio))
    conn.close()

    if df.empty:
        print('\nNo hay datos para ese periodo')
        return
    
    base_dir = Path(__file__).resolve().parent.parent
    export_dir = base_dir / 'exports'
    export_dir.mkdir(exist_ok=True)

    archivo = export_dir / f'pruebas_{anio}_{mes}.xlsx'
    df.to_excel(archivo, index=False)

    print(f'\nExcel mensual generado:')
    print(archivo)

# -----------------------------
# Main
# -----------------------------
def main():
    crear_tablas()

    while True:
        mostrar_menu()
        option = pedir_texto('\nSeleccione opcion: ').lower()

        if option == 's':
            print('\nSaliendo del programa...')
            break
        elif option == 'a':
            menu_pruebas()
        elif option == 'b':
            menu_empresas()
        elif option == 'c':
            menu_totales()
        elif option == 'd':
            menu_exportar()
        else:
            print('Opcion invalida.')

if __name__ == '__main__':
    main()