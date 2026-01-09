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

def pedir_tipo_prueba():
    while True:
        tipo = pedir_texto('Tipo de prueba (PRE, RUT, POST): ').upper()
        if tipo in ('PRE', 'RUT', 'POST'):
            return tipo
        print('Tipo invalido. Use PRE, RUT o POST.')

# -----------------------------
# Mostrar menu
# -----------------------------
def mostrar_menu():
    print('\n--- MENU DE PRUEBAS ---')
    print('[A] Agregar prueba')
    print('[B] Pruebas no hechas')
    print('[C] Ver pruebas del dia')
    print('[D] Mostrar pruebas')
    print('[E] Editar prueba')
    print('[F] Eliminar prueba')
    print('[G] Ver total a cobrar')
    print('[H] Exportar a excel')
    print('[S] Salir')

# -----------------------------
# [A] Agregar prueba
# -----------------------------
def agg_prueba():
    fecha_test = date.today().isoformat()
    cantidad_dia = pedir_entero('\nCantidad de pruebas del dia (1 a 6): ', 1, 6)
    legajo_numero = pedir_texto('Numero de legajo: ')
    tipo_prueba = pedir_tipo_prueba

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
    print(f'Total a cobrar: {total} Gs.')

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
# [D] Mostrar pruebas
# -----------------------------
def mostrar_pruebas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, fecha, legajo, tipo_prueba, cantidad, total
        FROM pruebas
        ORDER BY id DESC
    ''')

    filas = cursor.fetchall()
    conn.close()

    if not filas:
        print('\nNo hay pruebas cargadas.')
        return
    
    print('\nID |  Fecha     | Legajo | Tipo | Cant | Total')
    print('-' * 50)
    for f in filas:
        print(f'{f[0]:<3}| {f[1]:<10} | {f[2]:<6} | {f[3]:<4} | {f[4]:<4} | {f[5]}')

# -----------------------------
# [E] Editar prueba
# -----------------------------
def editar_prueba():
    mostrar_pruebas()

    prueba_id = pedir_entero('\nIngrese el ID a editar: ', 1)
    nueva_cantidad = pedir_entero(
        'Nueva cantidad de pruebas (1 a 6): ', 1, 6
    )

    nuevo_total = nueva_cantidad * PRECIO_POR_PRUEBA

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE pruebas
        SET cantidad = ?, total = ?
        WHERE id = ?
    ''', (nueva_cantidad, nuevo_total, prueba_id))

    conn.commit()
    conn.close()

    print('\nPrueba actualizada correctamente.')

# -----------------------------
# [F] Eliminar prueba
# -----------------------------
def eliminar_prueba():
    mostrar_pruebas()

    prueba_id = pedir_entero('\nIngrese el ID a eliminar: ', 1)

    confirmacion = pedir_texto(
        'Escriba "SI" para confirmar eliminacion: '
    ).upper()

    if confirmacion != 'SI':
        print('Eliminacion cancelada.')
        return
    
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM pruebas WHERE id = ?',
        (prueba_id,)
    )

    conn.commit()
    conn.close()

    print('\nPrueba eliminada correctamente.')

# -----------------------------
# [G] Total del mes
# -----------------------------
def total_del_mes():
    mes = pedir_texto('\nIngrese mes (MM): ')
    anio = pedir_texto('\nIngrese el año (YYYY): ')

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

        elif option == 'b':
            print('\nFuncion no implementada.')

        elif option == 'c':
            total_del_dia()

        elif option == 'd':
            mostrar_pruebas()

        elif option == 'e':
            editar_prueba()

        elif option == 'f':
            eliminar_prueba()

        elif option == 'g':
            total_del_mes()

        else:
            print('\nOpcion no valida, intente de nuevo...')

if __name__ == '__main__':
    main()