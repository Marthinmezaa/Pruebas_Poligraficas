# -----------------------------
# Show menu
# -----------------------------
def show_menu():
    print('\n--- MENU DE PRUEBAS ---')
    print('[A] Agregar prueba')
    print('[B] Pruebas no hechas')
    print('[C] Ver pruebas del dia')
    print('[D] Ver total a cobrar')
    print('[E] Exportar a excel')
    print('[S] Salir')

# -----------------------------
# Add test
# -----------------------------
def add_test():
    while True:
        date_test = input('\nFecha de test (DD/MM/YYY): ').strip()
        if not date_test:
            print('\nDebe agregar una fecha.')
            continue
        break

    while True:
        legajo_number = input('\nIngrese numero de legajo: ').strip()
        if not legajo_number:
            print('\nPorfavor agrege un numero de legajo.')
            continue
        break

    while True:    
        type_test = input('\nTipo de test (Pre, Rut, Post)?: ').strip().lower()
        if not type_test:
            print('\nPor favor inserte el tipo de test')
            continue
        break

    while True:
        company = input('\nCual es la empresa?: ').strip().lower()
        if not company:
            print('\nPorfavor agregue una empresa.')
            continue
        break

    print('Prueba cargada (por ahora solo en memoria).')
    print(date_test, legajo_number, type_test, company)

# -----------------------------
# Main
# -----------------------------
def main():
    while True:
        show_menu()
        option = input('\nSeleccione una opcion: ').lower().strip()

        if option == 's':
            print('\nSaliendo del programa...')
            break

        elif option == 'a':
            add_test()

        else:
            print('\nOpcion no valida, intente de nuevo...')

if __name__ == '__main__':
    main()