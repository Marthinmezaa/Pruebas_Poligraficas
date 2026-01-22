from datetime import date

# --- Constantes Visuales ---
ANCHO_EMPRESA = 25
LINEA = '-' * 95

# --- Funciones de Entrada ---

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

def pedir_fecha():
    print('Fecha de la prueba:')
    print('[Enter] para usar la fecha de hoy')
    opcion = input('Presione Enter o escriba cualquier tecla para fecha manual: ').strip()

    if not opcion:
        return date.today().isoformat()

    while True:
        try:
            anio = pedir_entero('Año (YYYY): ', 1900, 2100)
            mes = pedir_entero('Mes (MM): ', 1, 12)
            dia = pedir_entero('Día (DD): ', 1, 31)
            fecha = date(anio, mes, dia)
            return fecha.isoformat()
        except ValueError:
            print('Fecha inválida. Intente nuevamente.')

def pedir_tipo_prueba():
    while True:
        tipo = pedir_texto('Tipo de prueba (PRE, RUT, POST): ').upper()
        if tipo in ('PRE', 'RUT', 'POST'):
            return tipo
        print('Tipo invalido. Use PRE, RUT o POST.')