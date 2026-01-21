import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'sslmode': os.getenv('DB_SSLMODE', 'require')
}

# -----------------------------
# 1. Conexión base (Privada)
# -----------------------------
def _conectar():
    return psycopg2.connect(**DB_CONFIG)

# -----------------------------
# 2. El Gestor de Contexto
# -----------------------------
@contextmanager
def obtener_cursor():
    conn = _conectar()
    cursor = conn.cursor()
    try:
        yield cursor

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# -----------------------------
# 3. Funciones de Base de Datos (Interface Pública)
# -----------------------------
def crear_tablas():
    sql_empresa = '''
    CREATE TABLE IF NOT EXISTS empresa (
        id SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL,
        precio_por_prueba INTEGER NOT NULL
    );
    '''
    sql_pruebas = '''
    CREATE TABLE IF NOT EXISTS pruebas (
        id SERIAL PRIMARY KEY,
        fecha DATE NOT NULL,
        legajo TEXT NOT NULL,
        tipo_prueba TEXT NOT NULL,
        localidad TEXT NOT NULL DEFAULT 'pendiente',
        cantidad INTEGER NOT NULL DEFAULT 1,
        total INTEGER NOT NULL,
        estado TEXT NOT NULL,
        estado_pago TEXT NOT NULL DEFAULT 'NO PAGADO',
        empresa_id INTEGER NOT NULL,
        CONSTRAINT fk_empresa
            FOREIGN KEY (empresa_id)
            REFERENCES empresa(id)
            ON DELETE RESTRICT
    );
    '''

    with obtener_cursor() as cursor:
        cursor.execute(sql_empresa)
        cursor.execute(sql_pruebas)

# --- AGREGAR PRUEBAS ---
def agregar_pruebas(fecha, legajo, tipo, empresa_id, monto_total):
    sql = '''
        INSERT INTO pruebas (
            fecha, legajo, tipo_prueba, empresa_id,
            localidad, cantidad, total, estado, estado_pago
        )
        VALUES (%s, %s, %s, %s, 'pendiente', 1, %s, 'HECHA', 'NO PAGADO')
        RETURNING id;
    '''

    datos = (fecha, legajo, tipo, empresa_id, monto_total)

    with obtener_cursor() as cursor:
        cursor.execute(sql, datos)
        id_nueva_prueba = cursor.fetchone()[0]
        return id_nueva_prueba

# --- PRECIO POR EMPRESA EMPRESA ---    
def obtener_precio_empresa(empresa_id):
    sql = 'SELECT precio_por_prueba FROM empresa WHERE id = %s'

    with obtener_cursor() as cursor:
        cursor.execute(sql, (empresa_id,))

        resultado = cursor.fetchone()

    if resultado:
        return resultado[0]
    else:
        return None

# --- MOSTRAR TODAS LAS EMPRESAS ---    
def obtener_todas_empresas():
    sql = 'SELECT id, nombre, precio_por_prueba FROM empresa ORDER BY id ASC'

    with obtener_cursor() as cursor:
        cursor.execute(sql)
        resultado = cursor.fetchall()

    return resultado

# --- ELIMINAR PRUEBA ---
def eliminar_prueba(pruebas_id):
    sql = 'DELETE FROM pruebas WHERE id = %s'

    with obtener_cursor() as cursor:
        cursor.execute(sql, (pruebas_id,))

        filas_borradas = cursor.rowcount

    return filas_borradas > 0

# --- BUSCAR PRUEBAS ---
def buscar_pruebas_dinamico(filtro_sql, datos_tupla):
    sql_base = """
        SELECT 
            p.id, p.fecha, p.legajo, p.tipo_prueba, 
            e.nombre, p.total, p.estado, p.estado_pago
        FROM pruebas p
        JOIN empresa e ON p.empresa_id = e.id
    """

    if filtro_sql:
        sql_final = f'{sql_base} WHERE {filtro_sql} ORDER BY p.id DESC'
    else:
        sql_final = sql_base + ' ORDER BY p.id DESC'

    with obtener_cursor() as cursor:
        cursor.execute(sql_final, datos_tupla)
        resultados = cursor.fetchall()
    
    return resultados

# --- AZTUALIZAR PRUEBAS ---
def actualizar_prueba(id_prueba, fecha, legajo, tipo, empresa_id, total, estado):
    sql = """
        SELECT 
            p.id, p.fecha, p.legajo, p.tipo_prueba, 
            e.nombre, p.total, p.estado, p.estado_pago,
            p.empresa_id
        FROM pruebas p
        JOIN empresa e ON p.empresa_id = e.id
    """

    params = (fecha, legajo, tipo, empresa_id, total, estado, id_prueba)

    with obtener_cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.rowcount > 0

# --- CALCULO DE TOTAL A COBRAR ---    
def db_calcular_total_cobrado(fecha_desde, fecha_hasta=None, empresa_id=0):
    sql = """
        SELECT SUM(total) 
        FROM pruebas 
        WHERE estado = 'HECHA' 
          AND estado_pago = 'PAGADO' 
          AND fecha >= %s
    """
    params = [fecha_desde]

    if fecha_hasta:
        sql += " AND fecha <= %s"
        params.append(fecha_hasta)
    else:
        sql += " AND fecha <= %s" 
        params.append(fecha_desde)

    if empresa_id and empresa_id != 0:
        sql += " AND empresa_id = %s"
        params.append(empresa_id)

    with obtener_cursor() as cursor:
        cursor.execute(sql, tuple(params))
        resultado = cursor.fetchone()

    total = resultado[0] if resultado and resultado[0] else 0
    return total

# --- PRUEBAS PERDIDAS ---
def db_obtener_pruebas_perdidas(fecha_desde, fecha_hasta, empresa_id=0):
    sql = """
        SELECT 
            p.id, 
            p.fecha, 
            e.nombre, 
            p.total
        FROM pruebas p
        JOIN empresa e ON p.empresa_id = e.id
        WHERE p.estado = 'NO HECHA'
          AND p.fecha BETWEEN %s AND %s
    """

    params = [fecha_desde, fecha_hasta]

    if empresa_id and empresa_id != 0:
        sql += " AND p.empresa_id = %s"
        params.append(empresa_id)

    sql += " ORDER BY p.fecha ASC"

    with obtener_cursor() as cursor:
        cursor.execute(sql, tuple(params))
        resultados = cursor.fetchall()
        
    return resultados