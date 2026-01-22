from src.app import run, crear_tablas

if __name__ == '__main__':
    print("Verificando base de datos...")
    crear_tablas()

    print("Iniciando sistema...")
    run()