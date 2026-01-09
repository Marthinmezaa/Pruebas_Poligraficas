import sqlite3
from pathlib import Path

# Ruta absoluta a la base de datos
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'pruebas.db'


def conectar():
    '''
    Crea y retorna una conexion a la base SQLite.
    Si el archivo no existe, SQLite lo crea.
    '''
    return sqlite3.connect(DB_PATH)