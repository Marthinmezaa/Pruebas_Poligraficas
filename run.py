from src.app import crear_tablas, mostrar_menu, menu_pruebas, menu_empresas, menu_totales, menu_exportar
from src.app import Navegador

if __name__ == '__main__':
    print("Verificando base de datos...")
    crear_tablas()

    print("Iniciando sistema...")
    navegador = Navegador()
    
    # Bucle principal del sistema
    while True:
        opcion = mostrar_menu(navegador)
        
        if opcion == 's':
            print('\n¡Hasta luego!')
            break
        elif opcion == 'a':
            resultado = menu_pruebas(navegador)
            if resultado == 'volver':
                continue
        elif opcion == 'b' and not navegador.puede_volver():
            resultado = menu_empresas(navegador)
            if resultado == 'volver':
                continue
        elif opcion == 'c':
            resultado = menu_totales(navegador)
            if resultado == 'volver':
                continue
        elif opcion == 'd':
            resultado = menu_exportar(navegador)
            if resultado == 'volver':
                continue
        else:
            print('Opción inválida.')
