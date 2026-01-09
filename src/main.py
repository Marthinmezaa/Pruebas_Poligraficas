from database import conectar, crear_tablas
from datetime import date

PRECIO_POR_PRUEBA = 100000 # guaranies (ejemplo)

# -----------------------------
# Entradas seguras
# -----------------------------
def pedir_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print('No puede estar vacio.')

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

# -----------------------------
# Mostrar menu
# -----------------------------
def mostrar_menu():
    print('\n--- MENU DE PRUEBAS ---')
    print('[A] Agregar prueba')
    print('[B] Pruebas no hechas')
    print('[C] Ver pruebas del dia')
    print('[D] Ver total a cobrar')
    print('[E] Exportar a excel')
    print('[S] Salir')

# -----------------------------
# [A] Agregar prueba
# -----------------------------
def agg_prueba():
    fecha_test = date.today().isoformat()
    cantidad_dia = pedir_entero('\nCantidad de pruebas del dia (1 a 6): ', 1, 6)
    legajo_numero = pedir_texto('Numero de legajo: ')
    tipo_prueba = pedir_texto('Tipo de prueba (PRE, RUT, POST): ').lower()

    total = cantidad_dia * PRECIO_POR_PRUEBA

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO pruebas (fecha, legajo, tipo_prueba, localidad, cantidad, total)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        fecha_test,
        legajo_numero,
        tipo_prueba,
        'pendiente',
        cantidad_dia,
        total
    ))

    conn.commit()
    conn.close()

    print('\nPrueba guardada en la base de datos.')
    print(f'\nTotal a cobrar: {total} Gs.')

# -----------------------------
# [C] Total del día
# -----------------------------
def total_del_dia():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT SUM(total)
        FROM pruebas
        WHERE fecha = date('now')
    ''')

    total = cursor.fetchone()[0] or 0
    conn.close()

    print(f'\nTotal del dia: {total} Gs.')

# -----------------------------
# [D] Total del mes
# -----------------------------
def total_del_mes():
    mes = input('\nIngrese mes (MM): ').strip()
    anio = input('\nIngrese el año (YYYY): ').strip()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT SUM(total)
        FROM pruebas
        WHERE strftime('%m', fecha) = ?
          AND strftime('%Y', fecha) = ?
    ''', (mes, anio))

    total = cursor.fetchone()[0] or 0
    conn.close()

    print(f'\nTotal del mes {mes}/{anio}: {total} Gs')


# -----------------------------
# Main
# -----------------------------
def main():
    crear_tablas()

    while True:
        mostrar_menu()
        option = pedir_texto('\nSeleccione opcion: ').lower()

        if option == 's':
            print('\nSaliendo del programa...')
            break

        elif option == 'a':
            agg_prueba()

        elif option == 'c':
            total_del_dia()

        elif option == 'd':
            total_del_mes()

        else:
            print('\nOpcion no valida, intente de nuevo...')

if __name__ == '__main__':
    main()