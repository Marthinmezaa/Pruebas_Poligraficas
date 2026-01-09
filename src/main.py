from database import conectar, crear_tablas

PRECIO_POR_PRUEBA = 100000 # guaranies (ejemplo)

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
    while True:
        fecha_test = input('\nFecha de test (DD/MM/YYY): ').strip()
        if not fecha_test:
            print('\nDebe agregar una fecha.')
            continue
        break

    while True:
        cantidad_dia = int(input('\nIngrese la cantidad de pruebas del dia: ').strip())
        if not cantidad_dia:
            print('Debe agregar una cantidad de pruebas diaria (1 al 6).')
            continue
        break

    while True:
        legajo_numero = input('\nIngrese numero de legajo: ').strip()
        if not legajo_numero:
            print('\nPorfavor agrege un numero de legajo.')
            continue
        break

    while True:    
        tipo_prueba = input('\nTipo de test (Pre, Rut, Post)?: ').strip().lower()
        if not tipo_prueba:
            print('\nPor favor inserte el tipo de test')
            continue
        break

    print('Prueba cargada (por ahora solo en memoria).')
    print(fecha_test, cantidad_dia, legajo_numero, tipo_prueba)

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
        option = input('\nSeleccione una opcion: ').lower().strip()

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