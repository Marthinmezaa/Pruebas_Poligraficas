from database_pg import conectar, crear_tablas
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
# Marcar prueba NO hecha
# -----------------------------
def marcar_no_hecha():
    mostrar_pruebas()

    prueba_id = pedir_entero('\nIngrese el ID a marcar como NO HECHA: ', 1)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        'UPDATE pruebas SET estado = %s WHERE id = %s',
        ('NO HECHA', prueba_id)
    )

    conn.commit()
    conn.close()

    print('\nPrueba marcada como NO HECHA.')

# -----------------------------
# Mostrar pruebas no hechas
# -----------------------------
def mostrar_pruebas_no_hechas():
    mostrar_pruebas(no_hechas=True)           

# -----------------------------
# Cargar empresas
# -----------------------------
def cargar_empresa():
    nombre = pedir_texto('Nombre de la empresa: ')
    precio = pedir_entero('Precio por prueba (Gs): ', 1)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO empresa (nombre, precio_por_prueba) VALUES (%s, %s)',
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
    
    print('\nID | Empresa              | Precio')
    print('-' * 35)
    for e in empresas:
        print(f'{e[0]:<3}| {e[1]:<20} | {e[2]} Gs')

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
        print('[5] Marcar prueba como NO hecha')
        print('[6] Ver pruebas NO hechas')
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
        elif op == '5':
            marcar_no_hecha()
        elif op == '6':
            mostrar_pruebas_no_hechas()
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
        print('[5] Pruebas NO HECHAS (dinero perdido)')
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
        elif op == '5':
            ver_pruebas_no_hechas()
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
        'SELECT precio_por_prueba FROM empresa WHERE id = %s',
        (empresa_id,)
    )
    fila = cursor.fetchone()

    if not fila:
        print('Empresa no valida.')
        conn.close()
        return

    precio = fila[0]

    cursor.execute('''
        INSERT INTO pruebas (
            fecha, legajo, tipo_prueba, empresa_id,
            localidad, cantidad, total, estado
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        fecha_test,
        legajo_numero,
        tipo_prueba,
        empresa_id,
        'pendiente',
        1,          
        precio,
        'HECHA'
    ))

    conn.commit()
    conn.close()

    print('\nPrueba cargada como HECHA.')
    print(f'Total a cobrar: {precio} Gs.')

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
        WHERE fecha = %s
    ''', (fecha,))

    total = cursor.fetchone()[0] or 0
    conn.close()

    print(f'\nTotal del dia: {total} Gs.')

# -----------------------------
# [D] Mostrar pruebas
# -----------------------------
def mostrar_pruebas(no_hechas=False):
    conn = conectar()
    cursor = conn.cursor()

    query = '''
        SELECT
            p.id,
            p.fecha,
            p.legajo,
            p.tipo_prueba,
            e.nombre,
            p.total,
            p.estado
        FROM pruebas p
        JOIN empresa e ON p.empresa_id = e.id
    '''

    if no_hechas:
        query += " WHERE p.estado = 'NO HECHA'"

    query += ' ORDER BY p.id DESC'

    cursor.execute(query)
    filas = cursor.fetchall()
    conn.close()

    if not filas:
        print('\nNo hay pruebas para mostrar.')
        return
    
    print('\nID | Fecha      | Legajo | Tipo | Empresa          | Total  | Estado')
    print('-' * 75)
    for f in filas:
        fecha_str = f[1].strftime('%Y-%m-%d')
        print(
            f'{f[0]:<3}| {fecha_str:<10} | {f[2]:<6} | '
            f'{f[3]:<4} | {f[4]:<14} | {f[5]:<6} | {f[6]}'
        )

# -----------------------------
# [E] Editar prueba
# -----------------------------
def editar_prueba():
    mostrar_pruebas()

    prueba_id = pedir_entero('\nIngrese el ID de la prueba a editar: ', 1)

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT fecha, legajo, tipo_prueba, empresa_id, estado
        FROM pruebas
        WHERE id = %s
    ''', (prueba_id,))

    fila = cursor.fetchone()
    if not fila:
        print('Prueba no encontrada.')
        conn.close()
        return

    fecha_actual, legajo_actual, tipo_actual, empresa_actual, estado_actual = fila

    print('\n--- Deje ENTER para mantener el valor actual ---')

    # Fecha
    nueva_fecha = input(
        f'Fecha [{fecha_actual}]: '
    ).strip()
    if not nueva_fecha:
        nueva_fecha = fecha_actual
    else:
        try:
            date.fromisoformat(nueva_fecha)
        except ValueError:
            print('Fecha invalida.')
            conn.close()
            return

    # Legajo
    nuevo_legajo = input(
        f'Legajo [{legajo_actual}]: '
    ).strip()
    if not nuevo_legajo:
        nuevo_legajo = legajo_actual

    # Tipo de prueba
    nuevo_tipo = input(
        f'Tipo [{tipo_actual}]: '
    ).strip().upper()
    if not nuevo_tipo:
        nuevo_tipo = tipo_actual
    elif nuevo_tipo not in ('PRE', 'RUT', 'POST'):
        print('Tipo invalido.')
        conn.close()
        return

    # Estado
    nuevo_estado = input(
        f'Estado [{estado_actual}]: '
    ).strip().upper()
    if not nuevo_estado:
        nuevo_estado = estado_actual
    elif nuevo_estado not in ('HECHA', 'NO HECHA'):
        print('Estado invalido.')
        conn.close()
        return

    # Empresa
    print('\nEmpresas disponibles:')
    listar_empresas()

    nueva_empresa = input(
        f'Empresa ID [{empresa_actual}]: '
    ).strip()
    if not nueva_empresa:
        nueva_empresa = empresa_actual
    else:
        nueva_empresa = int(nueva_empresa)

    # Precio nuevo
    cursor.execute(
        'SELECT precio_por_prueba FROM empresa WHERE id = %s',
        (nueva_empresa,)
    )
    fila_precio = cursor.fetchone()
    if not fila_precio:
        print('Empresa invalida.')
        conn.close()
        return

    nuevo_total = fila_precio[0]

    # UPDATE final
    cursor.execute('''
        UPDATE pruebas
        SET fecha = %s,
            legajo = %s,
            tipo_prueba = %s,
            empresa_id = %s,
            total = %s,
            estado = %s
        WHERE id = %s
    ''', (
        nueva_fecha,
        nuevo_legajo,
        nuevo_tipo,
        nueva_empresa,
        nuevo_total,
        nuevo_estado,
        prueba_id
    ))

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
        'DELETE FROM pruebas WHERE id = %s',
        (prueba_id,)
    )

    conn.commit()
    conn.close()

    print('\nPrueba eliminada correctamente.')

# -----------------------------
# [G] Total del mes
# -----------------------------
def total_del_mes():
    mes = int(pedir_texto('Ingrese mes (MM): '))
    anio = int(pedir_texto('Ingrese año (YYYY): '))

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT SUM(total)
        FROM pruebas
        WHERE EXTRACT(MONTH FROM fecha) = %s
          AND EXTRACT(YEAR FROM fecha) = %s
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
    mes = int(pedir_texto('Ingrese mes (MM): '))
    anio = int(pedir_texto('Ingrese año (YYYY): '))

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            e.nombre,
            SUM(p.total)
        FROM pruebas p
        JOIN empresa e ON p.empresa_id = e.id
        WHERE EXTRACT(MONTH FROM fecha) = %s
          AND EXTRACT(YEAR FROM fecha) = %s
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
    mes = int(pedir_texto('Ingrese mes (MM): '))
    anio = int(pedir_texto('Ingrese año (YYYY): '))
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
        WHERE EXTRACT(MONTH FROM fecha) = %s
          AND EXTRACT(YEAR FROM fecha) = %s
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
# Total perdido
# -----------------------------
def total_perdido():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT SUM(total)
        FROM pruebas
        WHERE estado = 'NO_HECHA'
    ''')

    total = cursor.fetchone()[0] or 0
    conn.close()

    print(f'\n💸 Dinero perdido por pruebas no hechas: {total} Gs.')

# -----------------------------
# Ver pruebas no hechas
# -----------------------------
def ver_pruebas_no_hechas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            p.id,
            p.fecha,
            e.nombre,
            p.total
        FROM pruebas p
        JOIN empresa e ON p.empresa_id = e.id
        WHERE p.estado = %s
        ORDER BY p.fecha
    ''', ('NO HECHA',))

    filas = cursor.fetchall()
    conn.close()

    if not filas:
        print('\nNo hay pruebas NO HECHAS.')
        return

    print('\nPRUEBAS NO HECHAS')
    print('-' * 50)

    total_perdido = 0
    for f in filas:
        print(f'ID {f[0]} | {f[1]} | {f[2]} | {f[3]} Gs')
        total_perdido += f[3]

    print('-' * 50)
    print(f'TOTAL PERDIDO: {total_perdido} Gs')

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