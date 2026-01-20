import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'sslmode': os.getenv('DB_SSLMODE', 'require')
}
 
def conectar():
    return psycopg2.connect(**DB_CONFIG)

def crear_tablas():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS empresa (
        id SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL,
        precio_por_prueba INTEGER NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pruebas (
        id SERIAL PRIMARY KEY,
        fecha DATE NOT NULL,
        legajo TEXT NOT NULL,
        tipo_prueba TEXT NOT NULL,
        localidad TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        total INTEGER NOT NULL,
        estado TEXT NOT NULL,
        estado_pago TEXT NOT NULL DEFAULT 'NO PAGADO',
        empresa_id INTEGER NOT NULL,
        CONSTRAINT fk_empresa
            FOREIGN KEY (empresa_id)
            REFERENCES empresa(id)
            ON DELETE RESTRICT
    );
    """)

    conn.commit()
    conn.close()