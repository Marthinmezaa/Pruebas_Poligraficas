from database import conectar, crear_tablas
from datetime import date
import pandas as pd
from pathlib import Path

PRECIO_POR_PRUEBA = 100000 # guaranies (ejemplo)

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
    print('\n--- MENU DE PRUEBAS ---')
    print('[A] Agregar prueba')
    print('[B] Pruebas no hechas')
    print('[C] Ver pruebas del dia')
    print('[D] Mostrar pruebas')
    print('[E] Editar prueba')
    print('[F] Eliminar prueba')
    print('[G] Ver total a cobrar')
    print('[H] Exportar a excel')
    print('[I] Cargar empresa')
    print('[S] Salir')

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
    nueva_cantidad = pedir_entero(
        'Nueva cantidad de pruebas (1 a 6): ', 1, 6
    )

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT e.precio_por_prueba '
        'FROM pruebas p JOIN empresa e ON p.empresa_id = e.id '
        'WHERE p.id = ?',
        (prueba_id,)
    )
    precio = cursor.fetchone()[0]

    nuevo_total = nueva_cantidad * precio

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
            agg_prueba()

        elif option == 'b':
            print('\nFuncion no implementada.')

        elif option == 'c':
            total_del_dia()

        elif option == 'd':
            mostrar_pruebas()

        elif option == 'e':
            editar_prueba()

        elif option == 'f':
            eliminar_prueba()

        elif option == 'g':
            total_del_mes()

        elif option == 'h':
            print('\n[1] Exportar todo')
            print('[2] Exportar mes')
            sub = pedir_texto('Seleccione opcion: ')

            if sub == '1':
                exportar_excel()
            elif sub == '2':
                exportar_excel_mes()
            else:
                print('Opcion invalida')

        elif option == 'i':
            cargar_empresa()

        else:
            print('\nOpcion no valida, intente de nuevo...')

if __name__ == '__main__':
    main()