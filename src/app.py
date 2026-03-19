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
# Clase Navegador (Stack-based Navigation)
# -----------------------------
class Navegador:
    """Gestiona la navegación entre menús usando una pila (stack)."""
    
    def __init__(self):
        self.stack = []
    
    def push(self, menu_func):
        """Apila un menú actual antes de entrar a uno nuevo."""
        self.stack.append(menu_func)
    
    def pop(self):
        """Desapila y retorna el menú anterior."""
        if self.stack:
            return self.stack.pop()
        return None
    
    def puede_volver(self):
        """Retorna True si hay menús anteriores en el stack."""
        return len(self.stack) > 0
    
    def volver(self):
        """Simula la acción de presionar 'B' para volver atrás."""
        return 'volver'
    
    def esta_en_menu_principal(self):
        """Retorna True si estamos en el menú principal (stack vacío)."""
        return len(self.stack) == 0


# -----------------------------
# Funciones Auxiliares del Menú
# -----------------------------
def elegir_empresa_o_todas():
    print('\n[0] TODAS las empresas')
    opcion = pedir_entero('Seleccione ID de empresa (0 = todas): ', 0)
    if opcion == 0:
        return None
    return opcion

def mostrar_menu(navegador):
    """Muestra el menú principal con opción de volver contextual."""
    print('\n=== MENU PRINCIPAL ===')
    print('[A] Pruebas')
    print('[B] Empresas')
    print('[C] Totales / Reportes')
    print('[D] Exportar')
    print('[S] Salir')
    if navegador.puede_volver():
        print('[B] Volver atrás')
    
    op = pedir_texto('\nSeleccione opcion: ').lower()
    
    # Manejar opción de volver
    if op == 'b' and navegador.puede_volver():
        return 'volver'
    
    return op

def submenu_editar_prueba(navegador):
    """Submenú de edición de pruebas con navegación."""
    while True:
        print('\n--- OPCIONES DE EDICION ---')
        print('[1] Editar prueba (detalles)')
        print('[2] Marcar prueba como NO HECHA')
        print('[3] Marcar prueba como PAGADA (individual)')
        print('[4] Marcar pruebas como PAGADAS por rango')
        print('[0] Volver')
        if navegador.puede_volver():
            print('[B] Volver atrás')
        
        op = pedir_texto('Opcion: ').lower()
        
        # Manejar opción de volver
        if op == 'b' and navegador.puede_volver():
            return 'volver'
        
        if op == '1':
            editar_prueba(navegador)
        elif op == '2':
            marcar_no_hecha(navegador)
        elif op == '3':
            marcar_pagada(navegador)
        elif op == '4':
            marcar_pagadas_por_rango(navegador)
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

# -----------------------------
# [A] Pruebas
# -----------------------------
def menu_pruebas(navegador):
    """Menú principal de pruebas con navegación."""
    while True:
        print('\n--- PRUEBAS ---')
        print('[1] Registrar prueba')
        print('[2] Listado de pruebas')
        print('[3] Editar prueba')
        print('[4] Buscar pruebas')
        print('[5] Eliminar prueba')
        print('[0] Volver')
        if navegador.puede_volver():
            print('[B] Volver atrás')
        
        op = pedir_texto('Opcion: ').lower()
        
        # Manejar opción de volver
        if op == 'b' and navegador.puede_volver():
            return 'volver'
        
        if op == '1':
            agg_prueba(navegador)
        elif op == '2':
            menu_ver_pruebas(navegador)
        elif op == '3':
            submenu_editar_prueba(navegador)
        elif op == '4':
            buscar_pruebas(navegador)
        elif op == '5':
            opcion_eliminar_prueba(navegador)
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

def agg_prueba(navegador):
    """Registra una nueva prueba."""
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

def menu_ver_pruebas(navegador):
    """Submenú para ver pruebas."""
    while True:
        print('\n--- VER PRUEBAS ---')
        print('[1] Todas las pruebas')
        print('[2] Solo NO HECHAS')
        print('[0] Volver')
        if navegador.puede_volver():
            print('[B] Volver atrás')
        
        op = pedir_texto('Opcion: ').lower()
        
        # Manejar opción de volver
        if op == 'b' and navegador.puede_volver():
            return 'volver'
        
        if op == '1':
            mostrar_pruebas()
        elif op == '2':
            mostrar_pruebas(no_hechas=True)
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

def mostrar_pruebas(no_hechas=False):
    """Muestra lista de pruebas."""
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

def editar_prueba(navegador):
    """Edita una prueba específica."""
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

def buscar_pruebas(navegador):
    """Busca pruebas según criterios."""
    print('\n--- BUSCAR PRUEBAS ---')
    print('[1] Buscar por ID')
    print('[2] Buscar por fecha')
    print('[3] Buscar por legajo')
    print('[0] Volver')
    if navegador.puede_volver():
        print('[B] Volver atrás')
    
    op = pedir_texto('Opcion: ').lower()
    filtro = ''
    dato = ()

    # Manejar opción de volver
    if op == 'b' and navegador.puede_volver():
        return 'volver'
    
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

def opcion_eliminar_prueba(navegador):
    """Elimina una prueba con confirmación."""
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
def menu_estados_pruebas(navegador):
    """Menú de estados y pagos."""
    while True:
        print('\n--- ESTADOS / PAGOS ---')
        print('[1] Marcar prueba como NO HECHA')
        print('[2] Marcar prueba como PAGADA (por legajo)')
        print('[3] Marcar PAGADAS por rango de fechas')
        print('[0] Volver')
        if navegador.puede_volver():
            print('[B] Volver atrás')
        
        op = pedir_texto('Opcion: ').lower()
        
        # Manejar opción de volver
        if op == 'b' and navegador.puede_volver():
            return 'volver'
        
        if op == '1':
            marcar_no_hecha(navegador)
        elif op == '2':
            marcar_pagada(navegador)
        elif op == '3':
            marcar_pagadas_por_rango(navegador)
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

def marcar_no_hecha(navegador):
    """Marca una prueba como NO HECHA."""
    mostrar_pruebas()
    prueba_id = pedir_entero('\nIngrese el ID a marcar como NO HECHA: ', 1)

    from .database import obtener_cursor
    with obtener_cursor() as cursor:
        cursor.execute('UPDATE pruebas SET estado = %s WHERE id = %s', ('NO HECHA', prueba_id))
    print('\nPrueba marcada como NO HECHA.')

def marcar_pagada(navegador):
    """Marca una prueba como PAGADA por legajo."""
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

def marcar_pagadas_por_rango(navegador):
    """Marca múltiples pruebas como PAGADAS por rango de fechas."""
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
def menu_empresas(navegador):
    """Menú principal de empresas con navegación."""
    while True:
        print('\n--- EMPRESAS ---')
        print('[1] Cargar empresa')
        print('[2] Listar empresas')
        print('[3] Editar empresa')  
        print('[4] Eliminar empresa') 
        print('[0] Volver')
        if navegador.puede_volver():
            print('[B] Volver atrás')
        
        op = pedir_texto('Opcion: ').lower()
        
        # Manejar opción de volver
        if op == 'b' and navegador.puede_volver():
            return 'volver'
        
        if op == '1':
            cargar_empresa(navegador)
        elif op == '2':
            listar_empresas()
        elif op == '3':
            editar_empresa_ui(navegador)       
        elif op == '4':
            eliminar_empresa_ui(navegador)    
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

def cargar_empresa(navegador):
    """Carga una nueva empresa."""
    nombre = pedir_texto('Nombre de la empresa: ')
    precio = pedir_entero('Precio por prueba (Gs): ', 1)
    
    from .database import obtener_cursor
    with obtener_cursor() as cursor:
        cursor.execute('INSERT INTO empresa (nombre, precio_por_prueba) VALUES (%s, %s)', (nombre, precio))
    print('\nEmpresa cargada correctamente.')

def listar_empresas():
    """Lista todas las empresas."""
    empresas = obtener_todas_empresas()
    if not empresas:
        print('\nError: No hay empresas cargadas.')
        return []
    
    print('\nID | Empresa               | Precio')
    print('-' * 35)
    for e in empresas:
        print(f'{e[0]:<3}| {e[1]:<20} | {e[2]} Gs')
    return empresas

def editar_empresa_ui(navegador):
    """Interfaz para editar una empresa."""
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

def eliminar_empresa_ui(navegador):
    """Interfaz para eliminar una empresa."""
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
def menu_totales(navegador):
    """Menú de totales y reportes con navegación."""
    while True:
        print('\n--- TOTALES / REPORTES ---')
        print('[1] Total del día')
        print('[2] Total por rango de fechas')
        print('[3] Pruebas NO HECHAS (dinero perdido)')
        print('[0] Volver')
        if navegador.puede_volver():
            print('[B] Volver atrás')
        
        op = pedir_texto('Opcion: ').lower()
        
        # Manejar opción de volver
        if op == 'b' and navegador.puede_volver():
            return 'volver'
        
        if op == '1':
            total_del_dia(navegador)
        elif op == '2':
            total_por_rango(navegador)
        elif op == '3':
            pruebas_no_hechas_reporte(navegador)
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

def total_del_dia(navegador):
    """Muestra total cobrado en un día específico."""
    print('\n--- REPORTE DEL DÍA ---')
    fecha = pedir_fecha()
    empresa_id = elegir_empresa_o_todas()
    total = db_calcular_total_cobrado(fecha, empresa_id=empresa_id)
    nombre_empresa = "TODAS" if not empresa_id else f"Empresa {empresa_id}"
    print(f'\nTotal cobrado el {fecha} ({nombre_empresa}): {total} Gs')

def total_por_rango(navegador):
    """Muestra total cobrado en un rango de fechas."""
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

def pruebas_no_hechas_reporte(navegador):
    """Muestra reporte de pruebas no hechas (dinero perdido)."""
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
def menu_exportar(navegador):
    """Menú de exportación con navegación."""
    while True:
        print('\n--- EXPORTAR ---')
        print('[1] Exportar todo a Excel')
        print('[2] Exportar mes a Excel')
        print('[0] Volver')
        if navegador.puede_volver():
            print('[B] Volver atrás')
        
        op = pedir_texto('Opcion: ').lower()
        
        # Manejar opción de volver
        if op == 'b' and navegador.puede_volver():
            return 'volver'
        
        if op == '1':
            exportar_excel(navegador)
        elif op == '2':
            exportar_excel_mes(navegador)
        elif op == '0':
            break
        else:
            print('Opcion invalida.')

def exportar_excel(navegador):
    """Exporta todos los datos a Excel."""
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

def exportar_excel_mes(navegador):
    """Exporta datos de un mes específico a Excel."""
    import pandas as pd
    print('\n--- EXPORTAR MES ---')
    print('Seleccione el mes a exportar:')
    mes = pedir_entero('Número de mes (1-12): ', 1, 12)
    anio = pedir_entero('Año (ej. 2025): ', 1900, 2100)
    
    print(f"Generando reporte del mes {mes}/{anio}...")
    columnas, filas = db_obtener_datos_exportacion_rango(mes, anio)

    if not filas:
        print('\nNo hay datos para exportar en ese período.')
        return
    
    df = pd.DataFrame(filas, columns=columnas)
    
    base_dir = Path(__file__).resolve().parent.parent
    export_dir = base_dir / 'exports'
    export_dir.mkdir(exist_ok=True)
    archivo = export_dir / f'pruebas_poligraficas_{anio}-{mes:02d}.xlsx'
    df.to_excel(archivo, index=False)
    print(f'\nArchivo Excel generado correctamente.\n{archivo}')

def run():
    """Función principal que inicia la aplicación."""
    navegador = Navegador()
    
    while True:
        opcion = mostrar_menu(navegador)
        
        if opcion == 'volver':
            if navegador.puede_volver():
                navegador.pop()
            continue
            
        if opcion == 's':
            print('\n¡Hasta luego!')
            break
            
        if opcion == 'a':
            navegador.push(menu_pruebas)
            menu_pruebas(navegador)
        elif opcion == 'b':
            navegador.push(menu_empresas)
            menu_empresas(navegador)
        elif opcion == 'c':
            navegador.push(menu_totales)
            menu_totales(navegador)
        elif opcion == 'd':
            navegador.push(menu_exportar)
            menu_exportar(navegador)
        else:
            print('Opción inválida.')

if __name__ == '__main__':
    run()