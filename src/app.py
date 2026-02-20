# src/app.py
from pathlib import Path

from .database import (
    crear_tablas, agregar_pruebas, obtener_precio_empresa, obtener_todas_empresas, 
    eliminar_prueba, buscar_pruebas_dinamico, actualizar_prueba, 
    db_calcular_total_cobrado, db_obtener_pruebas_perdidas, 
    db_buscar_deuda_legajo, db_marcar_pagado_individual, db_marcar_pagado_masivo,
    db_obtener_datos_exportacion_todo, db_obtener_datos_exportacion_rango, 
    obtener_empresa_por_id, actualizar_empresa, eliminar_empresa
)
from .utils import (
    pedir_texto, pedir_entero, pedir_fecha, pedir_tipo_prueba,
    ANCHO_EMPRESA, LINEA
)

# -----------------------------
# Funciones Auxiliares del Menú
# -----------------------------
def elegir_empresa_o_todas():
    print('\n[0] TODAS las empresas')
    opcion = pedir_entero('Seleccione ID de empresa (0 = todas): ', 0)
    if opcion == 0:
        return None
    return opcion

def mostrar_menu():
    print('\n=== MENU PRINCIPAL ===')
    print('[A] Pruebas')
    print('[B] Empresas')
    print('[C] Totales / Reportes')
    print('[D] Exportar')
    print('[S] Salir')

# -----------------------------
# [A] Pruebas
# -----------------------------
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
            opcion_eliminar_prueba()
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

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
        id_nuevo = agregar_pruebas(fecha_test, legajo_numero, tipo_prueba, empresa_id, precio)
        print(f'\nPrueba #{id_nuevo} cargada exitosamente.')
        print(f'Total a cobrar: {precio} Gs.')
    except Exception as e:
        print(f"\nOcurrió un error al guardar: {e}")        

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

def mostrar_pruebas(no_hechas=False):
    filtro = "p.estado = 'NO HECHA'" if no_hechas else ""
    filas = buscar_pruebas_dinamico(filtro, ())

    if not filas:
        print('\nNo hay pruebas para mostrar.')
        return
    
    print('\nID | Fecha      | Legajo | Tipo | Empresa                   | Total   | Estado   | Pago')
    print(LINEA)
    for f in filas:
        fecha_str = str(f[1])
        print(
            f'{f[0]:<3}| {fecha_str:<10} | {f[2]:<6} | '
            f'{f[3]:<4} | {f[4]:<{ANCHO_EMPRESA}} | '
            f'{f[5]:<7} | {f[6]:<8} | {f[7]}'
        )

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
    empresa_old_id = actual[8] 

    print(f'\nEditando prueba #{prueba_id}')
    print('--- Deje ENTER para mantener el valor actual ---')

    nueva_fecha = input(f'Fecha [{fecha_old}]: ').strip()
    fecha_final = nueva_fecha if nueva_fecha else fecha_old

    nuevo_legajo = input(f'Legajo [{legajo_old}]: ').strip()
    legajo_final = nuevo_legajo if nuevo_legajo else legajo_old

    nuevo_tipo = input(f'Tipo [{tipo_old}]: ').strip().upper()
    tipo_final = nuevo_tipo if nuevo_tipo else tipo_old

    nuevo_estado = input(f'Estado [{estado_old}]: ').strip().upper()
    estado_final = nuevo_estado if nuevo_estado else estado_old

    print('\nSi cambia la empresa, se recalculará el precio.')
    nueva_empresa_str = input(f'ID Nueva Empresa (Actual: {empresa_old_id}): ').strip()

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
        empresa_final_id = empresa_old_id

    try:
        exito = actualizar_prueba(
            prueba_id, fecha_final, legajo_final, tipo_final, 
            empresa_final_id, total_final, estado_final
        )
        if exito:
            print('\nPrueba actualizada correctamente.')
        else:
            print('\nNo se pudo actualizar.')
    except Exception as e:
        print(f"Error crítico: {e}")

def buscar_pruebas():
    print('\n--- BUSCAR PRUEBAS ---')
    print('[1] Buscar por ID')
    print('[2] Buscar por fecha')
    print('[3] Buscar por legajo')
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
        print('\nID | Fecha      | Legajo | Tipo | Empresa                   | Total   | Estado   | Pago')
        print(LINEA)
        for r in resultados:
            fecha_str = str(r[1])
            print(f'{r[0]:<3}| {fecha_str:<10} | {r[2]:<6} | {r[3]:<4} | {r[4]:<{ANCHO_EMPRESA}} | {r[5]:<7} | {r[6]:<8} | {r[7]}')

def opcion_eliminar_prueba():
    mostrar_pruebas()
    prueba_id = pedir_entero('\nIngrese el ID a eliminar: ', 1)
    confirmacion = pedir_texto('Escriba "SI" para confirmar: ').upper()

    if confirmacion != 'SI':
        print('Eliminacion cancelada.')
        return
    
    se_borro = eliminar_prueba(prueba_id)
    if se_borro:
        print(f'\nPrueba {prueba_id} eliminada correctamente.')
    else:
        print(f'\nNo se encontró ninguna prueba con el ID {prueba_id}.')

# -----------------------------
# [A-5] Estados y Pagos
# -----------------------------
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

def marcar_no_hecha():
    mostrar_pruebas()
    prueba_id = pedir_entero('\nIngrese el ID a marcar como NO HECHA: ', 1)

    from .database import obtener_cursor
    with obtener_cursor() as cursor:
        cursor.execute('UPDATE pruebas SET estado = %s WHERE id = %s', ('NO HECHA', prueba_id))
    print('\nPrueba marcada como NO HECHA.')

def marcar_pagada():
    print('\n--- COBRAR INDIVIDUAL ---')
    legajo = pedir_texto('Ingrese el LEGAJO a marcar como PAGADO: ')
    deuda = db_buscar_deuda_legajo(legajo)

    if not deuda:
        print('\nNo hay pruebas pendientes de pago para ese legajo.')
        return
    
    prueba_id, fecha, total = deuda
    print(f'''
    --------------------------------
    Se marcará como PAGADA:
    Legajo: {legajo}
    Fecha:  {fecha}
    Total:  {total} Gs
    --------------------------------
    ''')

    confirmar = pedir_texto('¿Confirmar pago? (SI/NO): ').upper()
    if confirmar == 'SI':
        if db_marcar_pagado_individual(prueba_id):
           print('\n¡Pago registrado correctamente!')
        else:
            print('\nError extraño: No se pudo actualizar.')
    else:
        print('Operación cancelada.') 

def marcar_pagadas_por_rango():
    print('\n--- COBRAR LOTE (MASIVO) ---')
    empresa_id = elegir_empresa_o_todas()
    print('\nFecha DESDE:')
    fecha_desde = pedir_fecha()
    print('\nFecha HASTA:')
    fecha_hasta = pedir_fecha()

    if fecha_desde > fecha_hasta:
        print("Error: Fechas incoherentes.")
        return

    print("\nProcesando pagos...")
    cantidad = db_marcar_pagado_masivo(fecha_desde, fecha_hasta, empresa_id)

    if cantidad == 0:
        print('\nNo se encontraron pruebas pendientes en ese rango.')
    else:
        print(f'\n¡ÉXITO! Se marcaron {cantidad} pruebas como PAGADAS.')

# -----------------------------
# [B] Empresas
# -----------------------------
def menu_empresas():
    while True:
        print('\n--- EMPRESAS ---')
        print('[1] Cargar empresa')
        print('[2] Listar empresas')
        print('[3] Editar empresa')   
        print('[4] Eliminar empresa') 
        print('[0] Volver')
        op = pedir_texto('Opcion: ')

        if op == '1':
            cargar_empresa()
        elif op == '2':
            listar_empresas()
        elif op == '3':
            editar_empresa_ui()      
        elif op == '4':
            eliminar_empresa_ui()     
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

def cargar_empresa():
    nombre = pedir_texto('Nombre de la empresa: ')
    precio = pedir_entero('Precio por prueba (Gs): ', 1)
    
    from .database import obtener_cursor
    with obtener_cursor() as cursor:
        cursor.execute('INSERT INTO empresa (nombre, precio_por_prueba) VALUES (%s, %s)', (nombre, precio))
    print('\nEmpresa cargada correctamente.')

def listar_empresas():
    empresas = obtener_todas_empresas()
    if not empresas:
        print('\nError: No hay empresas cargadas.')
        return []
    
    print('\nID | Empresa               | Precio')
    print('-' * 35)
    for e in empresas:
        print(f'{e[0]:<3}| {e[1]:<20} | {e[2]} Gs')
    return empresas

# -----------------------------
# [B] Empresas
# -----------------------------
def menu_empresas():
    while True:
        print('\n--- EMPRESAS ---')
        print('[1] Cargar empresa')
        print('[2] Listar empresas')
        print('[3] Editar empresa')  
        print('[4] Eliminar empresa') 
        print('[0] Volver')
        op = pedir_texto('Opcion: ')

        if op == '1':
            cargar_empresa()
        elif op == '2':
            listar_empresas()
        elif op == '3':
            editar_empresa_ui()       
        elif op == '4':
            eliminar_empresa_ui()    
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

def cargar_empresa():
    nombre = pedir_texto('Nombre de la empresa: ')
    precio = pedir_entero('Precio por prueba (Gs): ', 1)
    
    from .database import obtener_cursor
    with obtener_cursor() as cursor:
        cursor.execute('INSERT INTO empresa (nombre, precio_por_prueba) VALUES (%s, %s)', (nombre, precio))
    print('\nEmpresa cargada correctamente.')

def listar_empresas():
    empresas = obtener_todas_empresas()
    if not empresas:
        print('\nError: No hay empresas cargadas.')
        return []
    
    print('\nID | Empresa               | Precio')
    print('-' * 35)
    for e in empresas:
        print(f'{e[0]:<3}| {e[1]:<20} | {e[2]} Gs')
    return empresas

def editar_empresa_ui():
    print('\n--- EDITAR EMPRESA ---')
    listar_empresas()
    
    empresa_id = pedir_entero('\nIngrese el ID de la empresa a editar: ', 1)
    
    datos = obtener_empresa_por_id(empresa_id)
    if not datos:
        print("Empresa no encontrada.")
        return

    _, nombre_old, precio_old = datos
    
    print(f'\nEditando: {nombre_old}')
    print('--- Deje ENTER para mantener el valor actual ---')
    
    nuevo_nombre = input(f'Nombre [{nombre_old}]: ').strip()
    nombre_final = nuevo_nombre if nuevo_nombre else nombre_old
    
    precio_input = input(f'Precio [{precio_old}]: ').strip()
    if precio_input:
        try:
            precio_final = int(precio_input)
        except ValueError:
            print("Precio inválido. Se mantiene el anterior.")
            precio_final = precio_old
    else:
        precio_final = precio_old
        
    try:
        if actualizar_empresa(empresa_id, nombre_final, precio_final):
            print('\nEmpresa actualizada correctamente.')
        else:
            print('\nNo se pudo actualizar.')
    except Exception as e:
        print(f"Error al actualizar: {e}")

def eliminar_empresa_ui():
    print('\n--- ELIMINAR EMPRESA ---')
    listar_empresas()
    
    empresa_id = pedir_entero('\nIngrese el ID de la empresa a eliminar: ', 1)
    
    # Advertencia de seguridad
    print("ADVERTENCIA: Si elimina la empresa, debe asegurarse de que NO tenga pruebas registradas.")
    print("Si tiene pruebas, el sistema protegerá los datos y no permitirá borrarla.")
    
    confirmar = pedir_texto('Escriba "SI" para confirmar eliminación: ').upper()
    if confirmar != 'SI':
        print("Operación cancelada.")
        return

    try:
        if eliminar_empresa(empresa_id):
            print(f'\nEmpresa {empresa_id} eliminada correctamente.')
        else:
            print(f'\nNo se encontró la empresa ID {empresa_id}.')
    except Exception as e:
        if "violates foreign key constraint" in str(e):
            print("\nERROR: No se puede eliminar esta empresa.")
            print("MOTIVO: Tiene pruebas registradas en el sistema.")
            print("SOLUCIÓN: Primero elimine o reasigne todas las pruebas de esta empresa.")
        else:
            print(f"\nError de base de datos: {e}")

# -----------------------------
# [C] Totales / Reportes
# -----------------------------
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

def total_del_dia():
    print('\n--- REPORTE DEL DÍA ---')
    fecha = pedir_fecha()
    empresa_id = elegir_empresa_o_todas()
    total = db_calcular_total_cobrado(fecha, empresa_id=empresa_id)
    nombre_empresa = "TODAS" if not empresa_id else f"Empresa {empresa_id}"
    print(f'\nTotal cobrado el {fecha} ({nombre_empresa}): {total} Gs')

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
    print(f'\nTotal cobrado desde {fecha_desde} hasta {fecha_hasta} ({nombre_empresa}):\n💰 {total} Gs')

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

def exportar_excel():
    import pandas as pd
    print("Generando reporte completo...")
    columnas, filas = db_obtener_datos_exportacion_todo()

    if not filas:
        print('\nNo hay datos para exportar.')
        return
    
    df = pd.DataFrame(filas, columns=columnas)
    
    # Path logic: como app.py está en src/, subimos DOS niveles (..) para llegar a la raíz
    base_dir = Path(__file__).resolve().parent.parent
    export_dir = base_dir / 'exports'
    export_dir.mkdir(exist_ok=True)
    archivo = export_dir / 'pruebas_poligraficas_completo.xlsx'
    df.to_excel(archivo, index=False)
    print(f'\nArchivo Excel generado correctamente.\n{archivo}')

def exportar_excel_mes():
    import pandas as pd
    print('\n--- EXPORTAR EXCEL POR RANGO ---')
    print('\nFecha DESDE:')
    fecha_desde = pedir_fecha()
    print('\nFecha HASTA:')
    fecha_hasta = pedir_fecha()
    empresa_id = elegir_empresa_o_todas()
    print("Consultando base de datos...")

    columnas, filas = db_obtener_datos_exportacion_rango(fecha_desde, fecha_hasta, empresa_id)

    if not filas:
        print('\nNo hay datos para exportar en ese período.')
        return

    df = pd.DataFrame(filas, columns=columnas)

    base_dir = Path(__file__).resolve().parent.parent
    export_dir = base_dir / 'exports'
    export_dir.mkdir(exist_ok=True)
    nombre_empresa = 'todas' if not empresa_id else f'empresa_{empresa_id}'
    archivo = export_dir / f'pruebas_{nombre_empresa}_{fecha_desde}_a_{fecha_hasta}.xlsx'
    df.to_excel(archivo, index=False)
    print(f'\nExcel generado correctamente:\n{archivo}')

# --- Start ---
def run():
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