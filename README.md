# Sistema de Gestión de Pruebas Poligráficas

Aplicación de línea de comandos (CLI) desarrollada en Python para la administración eficiente de pruebas poligráficas, gestión de cobranzas a empresas y generación de reportes financieros.

## Características Principales

* **Gestión de Pruebas:** Registro, edición, búsqueda y eliminación de pruebas.
* **Gestión de Empresas:** Administración de clientes corporativos y precios personalizados.
* **Control de Pagos:**
    * Cobro individual por legajo.
    * **Cobro Masivo:** Actualización de estados de pago por rango de fechas en lote.
* **Reportes Financieros:** Cálculo de totales diarios, mensuales y dinero perdido (pruebas no realizadas).
* **Exportación de Datos:** Generación de reportes en Excel (`.xlsx`) utilizando Pandas.
* **Base de Datos:** Persistencia robusta con PostgreSQL.

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.x
* **Base de Datos:** PostgreSQL
* **Librerías Clave:**
    * `psycopg2`: Conexión y transacciones seguras a BD.
    * `pandas`: Procesamiento de datos y exportación.
    * `python-dotenv`: Gestión de variables de entorno.

## Estructura del Proyecto

El proyecto sigue una arquitectura modular para facilitar la escalabilidad:

```text
PROYECTO/
├── .env                # Variables de entorno (No incluido en repo)
├── run.py              # Punto de entrada de la aplicación
├── requirements.txt    # Dependencias del proyecto
├── exports/            # Carpeta de salida para reportes Excel
└── src/
    ├── app.py          # Lógica de menús y flujo de la aplicación
    ├── database.py     # Capa de acceso a datos (DAO Pattern)
    └── utils.py        # Funciones auxiliares y validaciones