import sqlite3
from pathlib import Path

# -----------------------------
# Ruta absoluta a la base de datos
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'pruebas.db'


def conectar():
    '''
    Crea y retorna una conexion a la base SQLite.
    Si el archivo no existe, SQLite lo crea.
    '''
    return sqlite3.connect(DB_PATH)

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS empresa (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        precio_por_prueba INTEGER NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pruebas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        legajo TEXT NOT NULL,
        tipo_prueba TEXT NOT NULL,
        localidad TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        total INTEGER NOT NULL
    )
    ''')

    conn.commit()
    conn.close()