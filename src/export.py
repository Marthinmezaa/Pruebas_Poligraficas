import pandas as pd
from pathlib import Path
from .database import db_obtener_datos_exportacion_todo, db_obtener_datos_exportacion_rango

def exportar_excel(navegador):
    """Exporta todos los datos a Excel."""
    print('\n--- EXPORTAR TODO ---')
    empresa_id = None  # Todas las empresas
    
    print('Generando reporte completo...')
    columnas, filas = db_obtener_datos_exportacion_todo()
    
    if not filas:
        print('\nNo hay datos para exportar.')
        return
    
    df = pd.DataFrame(filas, columns=columnas)
    
    # Path logic: como export.py está en src/, subimos UN nivel (..) para llegar a la raíz
    base_dir = Path(__file__).resolve().parent
    export_dir = base_dir / 'exports'
    export_dir.mkdir(exist_ok=True)
    from datetime import datetime
    nombre_archivo = f'pruebas_poligraficas_completo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    archivo = export_dir / nombre_archivo
    df.to_excel(archivo, index=False)
    print(f'\nArchivo Excel generado correctamente.\n{archivo}')

def exportar_excel_mes(anio, mes):
    """Exporta datos de un mes específico a Excel."""
    # Calcular rango del mes
    import calendar
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fecha_desde = f'{anio}-{mes:02d}-01'
    fecha_hasta = f'{anio}-{mes:02d}-{ultimo_dia}'

    empresa_id = None  # Se mantiene compatible con la interfaz

    print(f'\nGenerando reporte del mes {mes}/{anio}...')
    columnas, filas = db_obtener_datos_exportacion_rango(fecha_desde, fecha_hasta, empresa_id)

    if not filas:
        print(f'\nNo hay datos para exportar en el mes {mes}/{anio}.')
        return

    df = pd.DataFrame(filas, columns=columnas)

    # Path logic: como export.py está en src/, subimos UN nivel (..) para llegar a la raíz
    base_dir = Path(__file__).resolve().parent
    export_dir = base_dir / 'exports'
    export_dir.mkdir(exist_ok=True)
    nombre_archivo = f'pruebas_poligraficas_{anio}_{mes:02d}.xlsx'
    archivo = export_dir / nombre_archivo
    df.to_excel(archivo, index=False)
    print(f'\nArchivo Excel generado correctamente.\n{archivo}')