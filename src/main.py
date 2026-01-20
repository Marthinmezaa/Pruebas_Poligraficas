from database_pg import conectar, crear_tablas
from datetime import date
from pathlib import Path

# -----------------------------
# Constantes
# -----------------------------
ANCHO_EMPRESA = 25
LINEA = '-' * 95

# -----------------------------
# Entradas seguras
# -----------------------------

# --- Pedir texto ---
def pedir_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print('No puede estar vacio.')

# --- Pedir entero ---
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

# --- Pedir fecha ---
def pedir_fecha():
    print('Fecha de la prueba:')
    print('[Enter] para usar la fecha de hoy')

    opcion = input('Presione Enter o escriba cualquier tecla para fecha manual: ').strip()

    if not opcion:
        return date.today().isoformat()

    while True:
        try:
            anio = pedir_entero('Año (YYYY): ', 1900, 2100)
            mes = pedir_entero('Mes (MM): ', 1, 12)
            dia = pedir_entero('Día (DD): ', 1, 31)

            fecha = date(anio, mes, dia)
            return fecha.isoformat()

        except ValueError:
            print('Fecha inválida. Intente nuevamente.')

# --- Pedir tipo de prueba ---
def pedir_tipo_prueba():
    while True:
        tipo = pedir_texto('Tipo de prueba (PRE, RUT, POST): ').upper()
        if tipo in ('PRE', 'RUT', 'POST'):
            return tipo
        print('Tipo invalido. Use PRE, RUT o POST.')
        
# --- Elegir empresa ---
def elegir_empresa_o_todas():
    print('\n[0] TODAS las empresas')

    opcion = pedir_entero(
        'Seleccione ID de empresa (0 = todas): ', 0
    )

    if opcion == 0:
        return None
    return opcion

# -----------------------------
# Mostrar pruebas no hechas
# -----------------------------
def mostrar_pruebas_no_hechas_simple():
    mostrar_pruebas(no_hechas=True)           

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

# -----------------------------
# [A] Agregar prueba
# -----------------------------

# Submenu de pruebas
def menu_pruebas():
    while True:
        print('\n--- PRUEBAS ---')
        print('[1] Registrar prueba')
        print('[2] Listado de pruebas')
        print('[3] Editar prueba')
        print('[4] Buscar pruebas')
        print('[5] Cambiar estado / pago')
        print('[6] Eliminar prueba')
        print('[0] Volver')

        op = pedir_texto('Opcion: ')

        if op == '1':
            agg_prueba()
        elif op == '2':
            menu_ver_pruebas()
        elif op == '3':
            editar_prueba()
        elif op == '4':
            buscar_pruebas()
        elif op == '5':
            menu_estados_pruebas()
        elif op == '6':
            eliminar_prueba()
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

# === [1] Agregar pruebas ===
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
            localidad, cantidad, total, estado, estado_pago
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        fecha_test,
        legajo_numero,
        tipo_prueba,
        empresa_id,
        'pendiente',
        1,
        precio,
        'HECHA',
        'NO PAGADO'
    ))

    conn.commit()
    conn.close()

    print('\nPrueba cargada como HECHA.')
    print(f'Total a cobrar: {precio} Gs.')

# === [2] Sub menu VER PRUEBAS ===
def menu_ver_pruebas():
    while True:
        print('\n--- VER PRUEBAS ---')
        print('[1] Todas las pruebas')
        print('[2] Solo NO HECHAS')
        print('[0] Volver')

        op = pedir_texto('Opcion: ')

        if op == '1':
            mostrar_pruebas()
        elif op == '2':
            mostrar_pruebas(no_hechas=True)
        elif op == '0':
            break
        else:
            print('Opcion invalida.')


# --- [1] Mostrar pruebas ---
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
            p.estado,
            p.estado_pago
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
    
    print('\nID | Fecha      | Legajo | Tipo | Empresa                   | Total   | Estado   | Pago')
    print(LINEA)
    for f in filas:
        fecha_str = (
            f[1].strftime('%Y-%m-%d')
            if hasattr(f[1], 'strftime')
            else str(f[1])
        )
        print(
            f'{f[0]:<3}| {fecha_str:<10} | {f[2]:<6} | '
            f'{f[3]:<4} | {f[4]:<{ANCHO_EMPRESA}} | '
            f'{f[5]:<7} | {f[6]:<8} | {f[7]}'
        )

# === [3] Editar prueba ===
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

# === [4] Buscar pruebas ===
def buscar_pruebas():
    while True:
        print('\n--- BUSCAR PRUEBAS ---')
        print('[1] Buscar por ID')
        print('[2] Buscar por fecha')
        print('[3] Buscar por legajo')
        print('[4] Buscar por empresa')
        print('[5] Última prueba HECHA (por legajo)')
        print('[0] Volver')

        op = pedir_texto('Opcion: ')

        conn = conectar()
        cursor = conn.cursor()

        if op == '1':
            prueba_id = pedir_entero('Ingrese ID: ', 1)
            cursor.execute('''
                SELECT
                    p.id,
                    p.fecha,
                    p.legajo,
                    p.tipo_prueba,
                    e.nombre,
                    p.total,
                    p.estado,
                    p.estado_pago
                FROM pruebas p
                JOIN empresa e ON p.empresa_id = e.id
                WHERE p.id = %s
            ''', (prueba_id,))

        elif op == '2':
            fecha = pedir_fecha()
            cursor.execute('''
                SELECT
                    p.id,
                    p.fecha,
                    p.legajo,
                    p.tipo_prueba,
                    e.nombre,
                    p.total,
                    p.estado,
                    p.estado_pago
                FROM pruebas p
                JOIN empresa e ON p.empresa_id = e.id
                WHERE p.fecha = %s
            ''', (fecha,))

        elif op == '3':
            legajo = pedir_texto('Ingrese legajo: ')
            cursor.execute('''
                SELECT
                    p.id,
                    p.fecha,
                    p.legajo,
                    p.tipo_prueba,
                    e.nombre,
                    p.total,
                    p.estado,
                    p.estado_pago
                FROM pruebas p
                JOIN empresa e ON p.empresa_id = e.id
                WHERE p.legajo = %s
            ''', (legajo,))

        elif op == '4':
            empresas = listar_empresas()
            if not empresas:
                conn.close()
                return

            empresa_id = pedir_entero('Ingrese ID de empresa: ', 1)
            cursor.execute('''
                SELECT
                    p.id,
                    p.fecha,
                    p.legajo,
                    p.tipo_prueba,
                    e.nombre,
                    p.total,
                    p.estado,
                    p.estado_pago
                FROM pruebas p
                JOIN empresa e ON p.empresa_id = e.id
                WHERE p.empresa_id = %s
            ''', (empresa_id,))

        elif op == '5':
            cursor.execute('''
                SELECT
                    p.id,
                    p.fecha,
                    p.legajo,
                    p.tipo_prueba,
                    e.nombre,
                    p.total,
                    p.estado,
                    p.estado_pago
                FROM pruebas p
                JOIN empresa e ON p.empresa_id = e.id
                WHERE p.estado = 'HECHA'
                ORDER BY p.legajo DESC, p.fecha DESC
                LIMIT 1
            ''')

        elif op == '0':
            conn.close()
            break

        else:
            print('Opcion invalida.')
            conn.close()
            continue

        filas = cursor.fetchall()
        conn.close()

        if not filas:
            print('\nNo se encontraron resultados.')
            continue

        print('\nID | Fecha      | Legajo | Tipo | Empresa          | Total  | Estado   | Pago')
        print('-' * 95)

        for f in filas:
            fecha_str = f[1].strftime('%Y-%m-%d')
            print(
            f'{f[0]:<3}| {fecha_str:<10} | {f[2]:<6} | '
            f'{f[3]:<4} | {f[4]:<14} | {f[5]:<6} | '
            f'{f[6]:<8} | {f[7]}'
            )    

# === [5] Sub menu ESTADOS DE PRUEBA ===
def menu_estados_pruebas():
    while True:
        print('\n--- ESTADOS / PAGOS ---')
        print('[1] Marcar prueba como NO HECHA')
        print('[2] Marcar prueba como PAGADA (por legajo)')
        print('[3] Marcar PAGADAS por rango de fechas')
        print('[0] Volver')

        op = pedir_texto('Opcion: ')

        if op == '1':
            marcar_no_hecha()
        elif op == '2':
            marcar_pagada()
        elif op == '3':
            marcar_pagadas_por_rango()
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

# --- [1] Marcar prueba como NO hecha ---
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

# --- [2] Marcar pruebas como PAGADA ---
def marcar_pagada():
    legajo = pedir_texto(
        '\nIngrese el LEGAJO a marcar como PAGADO: '
    )

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, fecha, total
        FROM pruebas
        WHERE legajo = %s
          AND estado = 'HECHA'
          AND estado_pago = 'NO PAGADO'
        ORDER BY fecha DESC
        LIMIT 1
    ''', (legajo,))

    fila = cursor.fetchone()

    if not fila:
        print('\n❌ No hay pruebas HECHAS y NO PAGADAS para ese legajo.')
        conn.close()
        return

    prueba_id, fecha, total = fila

    print(f'''
Se marcará como PAGADA la siguiente prueba:
Legajo: {legajo}
Fecha: {fecha}
Total: {total} Gs
''')

    confirmar = pedir_texto('Confirmar? (SI/NO): ').upper()
    if confirmar != 'SI':
        print('Operación cancelada.')
        conn.close()
        return

    cursor.execute('''
        UPDATE pruebas
        SET estado_pago = 'PAGADO'
        WHERE id = %s
    ''', (prueba_id,))

    conn.commit()
    conn.close()

    print('\n✅ Prueba marcada como PAGADA correctamente.')  

# --- [3] Marcar pruebas como PAGADA POR RANGO ---             
def marcar_pagadas_por_rango():
    print('\n--- MARCAR PAGADAS POR RANGO DE FECHAS ---')

    # Elegir empresa
    empresas = listar_empresas()
    print('\n[0] Todas las empresas')
    empresa_id = pedir_entero('Seleccione ID de empresa: ', 0)

    print('\nFecha DESDE:')
    fecha_desde = pedir_fecha()

    print('\nFecha HASTA:')
    fecha_hasta = pedir_fecha()

    conn = conectar()
    cursor = conn.cursor()

    query = '''
        UPDATE pruebas
        SET estado_pago = 'PAGADO'
        WHERE estado = 'HECHA'
          AND estado_pago = 'NO PAGADO'
          AND fecha BETWEEN %s AND %s
    '''

    params = [fecha_desde, fecha_hasta]

    if empresa_id != 0:
        query += ' AND empresa_id = %s'
        params.append(empresa_id)

    cursor.execute(query, params)
    cantidad = cursor.rowcount

    conn.commit()
    conn.close()

    if cantidad == 0:
        print('\nNo se encontraron pruebas para marcar como PAGADAS.')
    else:
        print(f'\n✅ {cantidad} pruebas marcadas como PAGADAS.')

# === [6] Eliminar pruebas ===
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
# [B] Empresas
# -----------------------------

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

# --- [1] Cargar empresa ---
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

# --- [2] Listar empresas ---
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
# [C] Totales Reportes
# -----------------------------

# Submenu TOTALES/REPORTES
def menu_totales():
    while True:
        print('\n--- TOTALES / REPORTES ---')
        print('[1] Total del día')
        print('[2] Total por rango de fechas')
        print('[3] Pruebas NO HECHAS (dinero perdido)')
        print('[0] Volver')

        op = pedir_texto('Opcion: ')

        if op == '1':
            total_del_dia()
        elif op == '2':
            total_por_rango()
        elif op == '3':
            pruebas_no_hechas_reporte()
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

# --- [1] Total del dia ---
def total_del_dia():
    fecha = pedir_fecha()
    empresa_id = elegir_empresa_o_todas()

    conn = conectar()
    cursor = conn.cursor()

    if empresa_id:
        cursor.execute('''
            SELECT SUM(total)
            FROM pruebas
            WHERE fecha = %s
              AND empresa_id = %s
              AND estado = 'HECHA'
              AND estado_pago = 'PAGADO'
        ''', (fecha, empresa_id))
    else:
        cursor.execute('''
            SELECT SUM(total)
            FROM pruebas
            WHERE fecha = %s
              AND estado = 'HECHA'
        ''', (fecha,))

    total = cursor.fetchone()[0] or 0
    conn.close()

    print(f'\nTotal del día {fecha}: {total} Gs')

# --- [2] Total por rango ---
def total_por_rango():
    empresa_id = elegir_empresa_o_todas()

    print('\nFecha DESDE:')
    fecha_desde = pedir_fecha()

    print('\nFecha HASTA:')
    fecha_hasta = pedir_fecha()

    conn = conectar()
    cursor = conn.cursor()

    if empresa_id:
        cursor.execute('''
            SELECT SUM(total)
            FROM pruebas
            WHERE empresa_id = %s
              AND estado = 'HECHA'
              AND estado_pago = 'PAGADO'
              AND fecha BETWEEN %s AND %s
        ''', (empresa_id, fecha_desde, fecha_hasta))
    else:
        cursor.execute('''
            SELECT SUM(total)
            FROM pruebas
            WHERE estado = 'HECHA'
              AND fecha BETWEEN %s AND %s
        ''', (fecha_desde, fecha_hasta))

    total = cursor.fetchone()[0] or 0
    conn.close()

    print(
        f'\nTotal desde {fecha_desde} hasta {fecha_hasta}: {total} Gs'
    )

# --- [3] Pruebas no hechas ---
def pruebas_no_hechas_reporte():
    print('\n--- PRUEBAS NO HECHAS (DINERO PERDIDO) ---')

    empresas = listar_empresas()
    print('\n[0] Todas las empresas')
    empresa_id = pedir_entero('Seleccione ID de empresa: ', 0)

    print('\nFecha DESDE:')
    fecha_desde = pedir_fecha()

    print('\nFecha HASTA:')
    fecha_hasta = pedir_fecha()

    conn = conectar()
    cursor = conn.cursor()

    query = '''
        SELECT
            p.id,
            p.fecha,
            e.nombre,
            p.total
        FROM pruebas p
        JOIN empresa e ON p.empresa_id = e.id
        WHERE p.estado = 'NO HECHA'
          AND p.fecha BETWEEN %s AND %s
    '''

    params = [fecha_desde, fecha_hasta]

    if empresa_id != 0:
        query += ' AND e.id = %s'
        params.append(empresa_id)

    query += ' ORDER BY p.fecha'

    cursor.execute(query, params)
    filas = cursor.fetchall()
    conn.close()

    if not filas:
        print('\nNo hay pruebas NO HECHAS para ese criterio.')
        return

    print('\nID | Fecha      | Empresa               | Perdido')
    print('-' * 55)

    total_perdido = 0
    for f in filas:
        print(f'{f[0]:<3}| {f[1]:<10} | {f[2]:<20} | {f[3]} Gs')
        total_perdido += f[3]

    print('-' * 55)
    print(f'TOTAL PERDIDO: {total_perdido} Gs')

# -----------------------------
# [D] Exportar
# -----------------------------

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

# --- [1] Exportar a Excel ---
def exportar_excel():
    import pandas as pd
    conn = conectar()

    query = '''
        SELECT
            p.id,
            p.fecha,
            p.legajo,
            p.tipo_prueba,
            e.nombre AS empresa,
            p.total,
            p.estado
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

# --- [2] Exportar a Excel por mes ---    
def exportar_excel_mes():
    import pandas as pd
    print('\n--- EXPORTAR EXCEL POR RANGO DE FECHAS ---')

    print('\nFecha DESDE:')
    fecha_desde = pedir_fecha()

    print('\nFecha HASTA:')
    fecha_hasta = pedir_fecha()

    empresas = listar_empresas()
    print('\n[0] Todas las empresas')

    empresa_id = pedir_entero('Seleccione ID de empresa: ', 0)

    conn = conectar()

    query = '''
        SELECT
            p.id,
            p.fecha,
            p.legajo,
            p.tipo_prueba,
            e.nombre AS empresa,
            p.total,
            p.estado
        FROM pruebas p
        JOIN empresa e ON p.empresa_id = e.id
        WHERE p.estado = 'HECHA'
          AND p.fecha BETWEEN %s AND %s
    '''

    params = [fecha_desde, fecha_hasta]

    if empresa_id != 0:
        query += ' AND e.id = %s'
        params.append(empresa_id)

    query += ' ORDER BY p.fecha'

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        print('\nNo hay datos para exportar en ese período.')
        return

    base_dir = Path(__file__).resolve().parent.parent
    export_dir = base_dir / 'exports'
    export_dir.mkdir(exist_ok=True)

    nombre_empresa = 'todas' if empresa_id == 0 else f'empresa_{empresa_id}'
    archivo = export_dir / f'pruebas_{nombre_empresa}_{fecha_desde}_a_{fecha_hasta}.xlsx'

    df.to_excel(archivo, index=False)

    print('\n✅ Excel generado correctamente:')
    print(archivo)
    
# -----------------------------
# Main
# -----------------------------
def main():
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