from database_pg import _conectar, crear_tablas, agregar_pruebas, obtener_precio_empresa, obtener_todas_empresas, eliminar_prueba
from database_pg import buscar_pruebas_dinamico, actualizar_prueba, db_calcular_total_cobrado, db_obtener_pruebas_perdidas
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

    precio = obtener_precio_empresa(empresa_id)

    if precio is None:
        print('Error: La empresa no existe!.')
        return
    
    try:
        agg_prueba(fecha_test, legajo_numero, tipo_prueba, empresa_id, precio)
        print('\nPrueba cargada como HECHA')
        print(f'Total a cobrar: {precio} Gs.')
    except Exception as e:
        print(f'Error al guardar: {e}.')

    try:
        id_nuevo = agregar_pruebas(fecha_test, legajo_numero, tipo_prueba, empresa_id, precio)

        print(f'\nPrueba #{id_nuevo} cargada exitosamente.')
        print(f'Total a cobrar: {precio} Gs.')

    except Exception as e:
        print(f"\nOcurrió un error al guardar: {e}")        

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
    conn = _conectar()
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
    print('\n--- EDITAR PRUEBA ---')
    prueba_id = pedir_entero('Ingrese el ID de la prueba a editar: ', 1)

    resultados = buscar_pruebas_dinamico("p.id = %s", (prueba_id,))

    if not resultados:
        print('Prueba no encontrada.')
        return

    actual = resultados[0]

    fecha_old, legajo_old, tipo_old = actual[1], actual[2], actual[3]
    total_old, estado_old = actual[5], actual[6]

    print(f'\nEditando prueba #{prueba_id}')
    print('--- Deje ENTER para mantener el valor actual ---')

    # --- FECHA ---
    nueva_fecha = input(f'Fecha [{fecha_old}]: ').strip()
    if not nueva_fecha:
        fecha_final = fecha_old
    else:
        fecha_final = nueva_fecha

    # --- LEGAJO ---
    nuevo_legajo = input(f'Legajo [{legajo_old}]: ').strip()
    legajo_final = nuevo_legajo if nuevo_legajo else legajo_old

    # --- TIPO ---
    nuevo_tipo = input(f'Tipo [{tipo_old}]: ').strip().upper()
    tipo_final = nuevo_tipo if nuevo_tipo else tipo_old

    # --- ESTADO ---
    nuevo_estado = input(f'Estado [{estado_old}]: ').strip().upper()
    estado_final = nuevo_estado if nuevo_estado else estado_old

    print('\nSi cambia la empresa, se recalculará el precio.')

    nueva_empresa_str = input('ID Nueva Empresa (Enter para no cambiar): ').strip()

    empresa_final_id = 0
    total_final = total_old

    if nueva_empresa_str:
        empresa_final_id = int(nueva_empresa_str)
        nuevo_precio = obtener_precio_empresa(empresa_final_id)

        if nuevo_precio is None:
            print("Empresa no válida. Cancelando edición.")
            return
        
        total_final = nuevo_precio
        print(f"Empresa cambiada. Nuevo precio actualizado a: {total_final}")
    else:
        pass

    empresa_old_id = actual[8]

    nueva_empresa_str = input(f'ID Empresa (Actual ID: {empresa_old_id}): ').strip()

    if nueva_empresa_str:
        empresa_final_id = int(nueva_empresa_str)
        nuevo_precio = obtener_precio_empresa(empresa_final_id)
        if nuevo_precio is None:
            print("Empresa inválida.")
            return
        total_final = nuevo_precio
    else:
        empresa_final_id = empresa_old_id
        total_final = total_old

    # --- GUARDAR CAMBIOS ---
    try:
        exito = actualizar_prueba(
            prueba_id, 
            fecha_final, 
            legajo_final, 
            tipo_final, 
            empresa_final_id, 
            total_final, 
            estado_final
        )
        
        if exito:
            print('\nPrueba actualizada correctamente.')
        else:
            print('\nNo se pudo actualizar (quizás el ID no existe).')
            
    except Exception as e:
        print(f"Error crítico: {e}")

# === [4] Buscar pruebas ===
def buscar_pruebas():
    print('\n--- BUSCAR PRUEBAS ---')
    print('[1] Buscar por ID')
    print('[2] Buscar por fecha')
    print('[3] Buscar por legajo')
    # ... otras opciones ...
    print('[0] Volver')

    op = pedir_texto('Opcion: ')

    filtro = ''
    dato = ()

    if op == '1':
        id_buscado = pedir_entero('Ingrese ID: ', 1)
        filtro = 'p.id = %s'
        dato = (id_buscado,)

    elif op == '2':
        fecha = pedir_fecha()
        filtro = "p.fecha = %s"
        dato = (fecha,)

    elif op == '3':
        legajo = pedir_texto('Ingrese legajo: ')
        filtro = "p.legajo = %s"
        dato = (legajo,)

    elif op == '0':
        return
    else:
        print('Opcion no valida')
        return
    
    resultados = buscar_pruebas_dinamico(filtro, dato)

    if not resultados:
        print('\nNo se encontraron resultados.')
    else:
        print(f"\nSe encontraron {len(resultados)} pruebas:")
        for r in resultados:
            print(r)

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

    conn = _conectar()
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

    conn = _conectar()
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
        print('\nNo hay pruebas HECHAS y NO PAGADAS para ese legajo.')
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

    conn = _conectar()
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
        print(f'\n{cantidad} pruebas marcadas como PAGADAS.')

# === [6] Eliminar pruebas ===
def opcion_eliminar_prueba():
    mostrar_pruebas()

    prueba_id = pedir_entero('\nIngrese el ID a eliminar: ', 1)

    confirmacion = pedir_texto(
        'Escriba "SI" para confirmar eliminacion: '
    ).upper()

    if confirmacion != 'SI':
        print('Eliminacion cancelada.')
        return
    
    se_borro = eliminar_prueba(prueba_id)

    if se_borro:
        print(f'\nPrueba {prueba_id} eliminada correctamente.')
    else:
        print(f'\nNo se encontró ninguna prueba con el ID {prueba_id}.')

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

    conn = _conectar()
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
    empresas = obtener_todas_empresas()

    if not empresas:
        print('\nError: No hay empresas cargadas.')
        return
    
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
    print('\n--- REPORTE DEL DÍA ---')
    fecha = pedir_fecha()

    empresa_id = elegir_empresa_o_todas()

    total = db_calcular_total_cobrado(fecha, empresa_id=empresa_id)

    nombre_empresa = "TODAS" if not empresa_id else f"Empresa {empresa_id}"
    print(f'\nTotal cobrado el {fecha} ({nombre_empresa}): {total} Gs')

# --- [2] Total por rango ---
def total_por_rango():
    print('\n--- REPORTE POR RANGO ---')
    empresa_id = elegir_empresa_o_todas()

    print('\nFecha DESDE:')
    fecha_desde = pedir_fecha()

    print('\nFecha HASTA:')
    fecha_hasta = pedir_fecha()

    if fecha_desde > fecha_hasta:
        print("Error: La fecha 'Desde' es mayor que 'Hasta'.")
        return
    
    total = db_calcular_total_cobrado(fecha_desde, fecha_hasta, empresa_id)

    nombre_empresa = "TODAS" if not empresa_id else f"Empresa {empresa_id}"
    print(
        f'\nTotal cobrado desde {fecha_desde} hasta {fecha_hasta} '
        f'({nombre_empresa}):\n💰 {total} Gs'
    )

# --- [3] Pruebas no hechas ---
def pruebas_no_hechas_reporte():
    print('\n--- PRUEBAS NO HECHAS (DINERO PERDIDO) ---')

    empresa_id = elegir_empresa_o_todas()

    print('\nFecha DESDE:')
    fecha_desde = pedir_fecha()

    print('\nFecha HASTA:')
    fecha_hasta = pedir_fecha()

    if fecha_desde > fecha_hasta:
        print("La fecha de inicio no puede ser mayor a la fecha fin.")
        return
    
    filas = db_obtener_pruebas_perdidas(fecha_desde, fecha_hasta, empresa_id)

    if not filas:
        print('\n¡Buenas noticias! No hay dinero perdido en este período.')
        return

    print('\nID | Fecha      | Empresa              | Perdido')
    print('-' * 55)

    total_perdido = 0

    for f in filas:
        fecha_str = str(f[1])
        print(f'{f[0]:<3}| {fecha_str:<10} | {f[2]:<20} | {f[3]} Gs')

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
    conn = _conectar()

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

    conn = _conectar()

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