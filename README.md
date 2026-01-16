# Sistema de Gestión de Pruebas Poligráficas

Aplicación de consola desarrollada en Python para la gestión de pruebas poligráficas,
empresas, estados de realización y pagos, con generación de reportes y exportación a Excel.

---

## Funcionalidades principales

### Pruebas
- Registrar pruebas poligráficas
- Editar y eliminar pruebas
- Marcar pruebas como HECHAS / NO HECHAS
- Marcar pruebas como PAGADAS (una o por rango de fechas)
- Buscar pruebas por:
  - ID
  - Fecha
  - Legajo
  - Empresa
  - Última prueba HECHA por legajo

---

### Empresas
- Cargar empresas
- Listar empresas
- Precio por prueba asociado a cada empresa

---

### Totales y reportes
- Total del día (solo pruebas HECHAS y PAGADAS)
- Total por rango de fechas
- Reporte de pruebas NO HECHAS (dinero perdido)
- Filtros por empresa o todas

---

### Exportación
- Exportar todas las pruebas a Excel
- Exportar pruebas por rango de fechas y empresa

---

## Base de datos

- PostgreSQL (Neon)
- Tablas principales:
  - `empresa`
  - `pruebas`

Estados utilizados:
- `estado`: HECHA / NO HECHA
- `estado_pago`: PAGADO / NO PAGADO

---

## Requisitos

- Python 3.10+
- Librerías:
  - psycopg2
  - pandas
  - openpyxl

Instalación de dependencias:
```bash
pip install psycopg2 pandas openpyxl