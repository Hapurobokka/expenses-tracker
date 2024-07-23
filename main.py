"""
Archivo principal del programa, de momento.

Hecho por Hapurobokka.
"""
# import tkinter
import sqlite3

DATABASE = "database.db"

# ------------------------------------------------------------------------------
# DATABASE QUERYING SECTION

def run_query(query, parameters=()) -> sqlite3.Cursor:
    "Runs a query for the external database"
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, parameters)
        conn.commit()
    return result


def request_data(query, parameters):
    "Queries the database for the solicitaded information, then returns a list of tuples"
    some_cursor = run_query(query, parameters)
    return some_cursor.fetchall()


def add_data(query, desired_data):
    "Adds the data passed as arguments into the database"
    run_query(query, desired_data)


def delete_data(table, data_id):
    "Deletes the record matching the id"
    query = f"DELETE FROM {table} WHERE id = ?"
    run_query(query, (data_id, ))


def check_if_in_database(table_to_check, column_to_check, data):
    "Check if the given data exists in a table"
    record = request_data(f"SELECT * FROM {table_to_check} WHERE {column_to_check} = ?", (data, ))

    if not record:
        print("No se ha encontrado una coincidencia en la base de datos")

    return record


def search_id(table, row, data):
    "Returns the id for the given data"
    try:
        return request_data(f'SELECT id FROM {table} WHERE {row} = ?', (data, ))[0][0]
    except IndexError:
        return None


def show_all_records(table, register_id):
    """
    Shows all the records in a table with a given register id"""
    record_list = request_data(f'SELECT * FROM {table} WHERE register_id = ?', (register_id, ))

    print("\n")
    for record in record_list:
        display_record(record)


def display_record(record):
    """
    Properly displays a record"""
    record_length = len(record)
    print(f"ID: {record[0]} | NOMBRE: {record[record_length - 2]} |"
          + f"INT: {record[record_length - 1]}")


def add_record(concepts, table, register_id):
    """
    Adds a record to the database"""
    print(f"\nInserte nombre y {concepts[0]} del {concepts[1]}")
    record_name = input("NOMBRE: ")
    record_int = get_numeric_input(f"{concepts[0].upper()}: ")

    print(f"¿Quiere añadir este {concepts[1]}?")
    print(f"NOMBRE: {record_name} | {concepts[0].upper()}: {record_int}")

    if not ask_confirmation():
        return

    if table == 'products':
        add_data(f'INSERT INTO {table} VALUES (NULL, ?, ?)', (record_name, record_int))
    else:
        add_data(f'INSERT INTO {table} VALUES (NULL, ?, ?, ?)',
                 (register_id, record_name, record_int))

    print(f"{concepts[1]} añadido de forma exitosa")


def remove_record(concept, table):
    """
    Removes a record from the database"""
    print(f"Indique la id del {concept} que quiere eliminar.")
    print("(Puede verla en el menù anterior)")
    record_id = get_numeric_input("ID: ")

    record = check_if_in_database(table, 'id', record_id)[0]

    if not record:
        return

    print(f"¿Esta seguro de que quiere borrar este {concept}?")
    display_record(record)

    if not ask_confirmation():
        return

    delete_data(table, record_id)
    print(f"{concept.capitalize()} eliminado correctamente")


def edit_record(table, row_1, row_2, format_fun=None):
    """
    Edits a record in a table with the rows: id, record_id, _name, amount"""
    update_query = f"UPDATE {table} set {row_1} = ?, {row_2} = ? WHERE id = ?"

    record_id = get_numeric_input("ID: ")

    try:
        record = check_if_in_database(table, 'id', record_id)[0]
    except IndexError:
        print("ID no existente")
        return

    display_record(record)

    print("Inserte los nuevos valores")

    new_name = input("NOMBRE: ")
    new_int = get_numeric_input("CANTIDAD: ")

    if format_fun:
        if not format_fun(new_name):
            print("Formato incorrecto. Registro no actualizado.")
            return

    print("¿Esta seguro de que quiere editar con estos valores?")
    print(f"NOMBRE: {new_name} | PRECIO: {new_int}")

    if not ask_confirmation():
        return

    run_query(update_query, (new_name.upper(), new_int, record_id))
    print("\nRegistro actualizado\n")

# ------------------------------------------------------------------------------
# MACHINES TABLES SECTION

def get_total_machine_prices(acc, db_rows):
    "Gets the total of prices given by machines for the current day and shift"
    if len(db_rows) != 0:
        return get_total_machine_prices(acc + db_rows[0][4], db_rows[1:])

    return acc


def test_machine_name(entry: str) -> bool:
    """
    Tests if the entry for the any of the machine tables (machine_table or replenishments) is valid
    """
    if len(entry) != 2:
        return False

    if not str.isalpha(entry[0]) and not str.isnumeric(entry[1]):
        return False

    return True


def format_machine_entry(prompt):
    """
    Gets a prompt, then splits it through the whitespace and uses a function to
    check if it conforts to the format. If not, returns false. Otherwise, capitalizes it and
    returns a tuple"""
    unformated_entry = prompt.split()

    if not test_machine_name(unformated_entry):
        return False

    if not str.isnumeric(unformated_entry[1]):
        return False

    formated_entry = [x.upper() for x in unformated_entry]
    return (formated_entry[0], int(formated_entry[1]))


def insert_into_machine_table(prompt, table, register):
    """
    Inserts the given prompt, correctly formated, into the given table from these
    two: machine_table, replenishments"""
    entry = format_machine_entry(prompt)

    if not entry:
        print("ENTRADA INCORRECTA. REVISE SI ESTA ESCRITA CORRECTAMENTE.")
        return

    add_data(f'INSERT INTO {table} VALUES (NULL, ?, ?, ?)', (register, *entry))
    print("ENTRADA AÑADIDA CORRECTAMENTE")


def get_prompts_for_machine_table(register_id, table):
    """
    Gets in a loop entries for a machine table."""
    print(f"\nAhora mismo esta trabajando con {table}")
    print("Introduce un texto del estilo 'nombre_maquina cantidad'. Ejemplo 'a2 200'.")
    print("Cuando quiera termina escriba '.exit'.\n")

    entry = ""
    while True:
        entry = input("> ")

        if entry == ".exit":
            break

        insert_into_machine_table(entry, table, register_id)


def machine_submenu(register_id):
    """
    Submenu for all operations related with machines"""
    while True:
        print("\nSelecciona un comando:")
        print("1. Ver premios de maquinas y reposiciones")
        print("2. Insertar premios de maquinas")
        print("3. Insertar reposiciones")
        print("4. Eliminar premio")
        print("5. Eliminar reposición")
        print("6. Editar precios de maquinas")
        print("7. Editar reposiciones")
        print("8. Salir\n")

        command = get_numeric_input("> ")
        print("\n")

        match command:
            case 1:
                print("MAQUINAS")
                show_all_records('machine_table', register_id)

                print("\n--------------------------------------------------------------")

                print("REPOSICIONES")
                show_all_records('replenishments', register_id)
            case 2:
                get_prompts_for_machine_table(register_id, 'machine_table')
            case 3:
                get_prompts_for_machine_table(register_id, 'replenishments')
            case 4:
                remove_record('premio', 'machine_table')
            case 5:
                remove_record('reposición', 'replenishments')
            case 6:
                edit_record('machine_table', 'machine_name', test_machine_name)
            case 7:
                edit_record('replenishments', 'machine_name', test_machine_name)
            case 8:
                break

# ------------------------------------------------------------------------------
# REGISTER CHECKING SECTION (si fuera mejor programador seria MUCHO menos)

def check_registers(current_register):
    """
    Compares the given register with the database. If it's already there returns it's id.
    Otherwise, it prompts the user to add it."""
    searched_register = request_data('SELECT id FROM registers WHERE date_id = ? AND shift_id = ? '
                                     + 'AND employee_id = ?', current_register)

    if not searched_register:
        print("Este turno parece no estar registrado en la base de datos, ¿quiere registrarlo?")

        if not ask_confirmation():
            return False

        add_data('INSERT INTO registers VALUES (NULL, ?, ?, ?)', current_register)
        return False

    return searched_register[0][0]


def get_current_register_info(register_id):
    """
    Returns a tuple with the information of the current register.
    If there are no coincidences, returns an empty tuple."""
    query = """
    SELECT d.date, s.shift, e.employee_name
    FROM registers r
    JOIN dates d ON d.id = r.date_id
    JOIN shifts s ON s.id = r.shift_id
    JOIN employees e on e.id = r.employee_id
    WHERE r.id = ?"""

    try:
        return request_data(query, (register_id, ))[0]
    except IndexError:
        return (None, None, None)


def ask_for_information(bundled_info):
    """
    Asks for input on the given data. If it already exists in the table, returns it's id.
    Otherwise, asks if the user wants to add it to the table"""
    table, row, information = bundled_info
    current_info = input(f"{information.upper()}: ")

    if not check_if_in_database(table, row, current_info) and table != 'shifts':
        print(f"{information} no registrado. ¿Quiere añadirlo a la base de datos?")

        if not ask_confirmation():
            return bundled_info

        add_data(f'INSERT INTO {table} VALUES (NULL, ?)', (current_info, ))
        print(f"{information} añadido.")

    elif not check_if_in_database(table, row, current_info) and table == "shifts":
        print("Turno no existente. Por favor elija entre [Mañana, Tarde, Noche]")
        return bundled_info

    return search_id(table, row, current_info)


def show_current_register_info(register_id):
    """
    Prints to the screen the information of the current register"""
    current_register_info = get_current_register_info(register_id)
    print(f"Hoy es {current_register_info[0].capitalize()}.") # type: ignore
    print(f"En el turno de la {current_register_info[1].capitalize()}.") # type: ignore
    print(f"Y esta trabajando {current_register_info[2].capitalize()}.") # type: ignore


def get_current_shift_information(requested_info):
    """
    Uses the requested information to return a tuple with the id's of the current shift"""
    current_information = []
    for info in requested_info:
        if isinstance(info, tuple):
            current_information.append(ask_for_information(info))
        else:
            current_information.append(info)

    if not all(isinstance(x, int) for x in current_information):
        return get_current_shift_information(current_information)

    return tuple(current_information)


def get_current_shift_id(required_info):
    """
    Uses the requiered info to get a tuple with this shift id's and gets it's id on the registers"""
    current_shift_info = get_current_shift_information(required_info)
    current_shift_id = None
    while not current_shift_id:
        current_shift_id = check_registers(current_shift_info)

    return current_shift_id

# ------------------------------------------------------------------------------
# PRODUCTS SECTION

def check_if_product_register(product_register_id):
    """
    Checks if the current day has sales of a given product"""
    query = """
    SELECT ps.id, ps.register_id, p.product_name, ps.in_product, ps.out_product, ps.profits
    FROM products_sales ps
    JOIN products p ON p.id = ps.product_id
    WHERE ps.id = ?;
    """
    register = request_data(query, (product_register_id, ))

    if not register:
        print("No existe un registro de productos con esa id en la base de datos.")
        return None

    return register[0]


def display_product(product):
    """
    Shows a product in a formated way"""
    print(f"ID: {product[0]} | NOMBRE: {product[1].capitalize()} | PRECIO: {product[2]}")


def display_register(register):
    """Shows a product register in a formated way"""
    print(f"ID: {register[0]} | PRODUCTO: {register[2].capitalize()} | IN: {register[3]} "
          + f"| OUT: {register[4]} | GANANCIA: {register[5]}")


def show_all_product_registers(register_id):
    """
    Shows all of the products registers"""
    query = """
SELECT ps.id, ps.register_id, p.product_name, ps.in_product, ps.out_product, ps.profits
FROM products_sales ps
JOIN products p ON p.id = ps.product_id
WHERE ps.register_id = ?;
    """
    registers_list = request_data(query, (register_id, ))

    for register in registers_list:
        display_register(register)


def fill_product_row(register_id):
    """
    Fills a row of the producs_sales table with the reported amounts.
    Also calculates the profit."""
    query = 'INSERT INTO products_sales VALUES (NULL, ?, ?, ?, ?, ?)'

    print("Indica la id del producto que quieres reportar")
    print("(Puede verla seleccionando 'Mostrar lista de productos' en el menù anterior)")
    product_id = get_numeric_input("ID: ")

    try:
        product = check_if_in_database('products', 'id', product_id)[0]
    except IndexError:
        print("ID no existente.")
        return

    _, product_name, product_price = product

    print(f"Indique que cantidad de {product_name} tenía en stock")
    in_product = get_numeric_input("> ")

    print(f"Indique con que cantidad de {product_name} termino el turno")
    out_product = get_numeric_input("> ")

    profit = (in_product - out_product) * product_price

    print(f"Este es el reporte de {product_name}")
    display_register((register_id, product_id, in_product, out_product, profit))

    print("\n¿Esta seguro que quiere registrarlo? [y/n]")

    if not ask_confirmation():
        return

    add_data(query, (register_id, product_id, in_product, out_product, profit))


def edit_product_row():
    """
    Edits a row from the products_sales tables"""
    query = """UPDATE products_sales
    SET in_product = ?, out_product = ?, profits = ?
    WHERE id = ?"""

    print("Indica la id del registro a editar")
    print("(Puede verla seleccionando 'Mostrar lista de registros' en el menù anterior)")

    product_register_id = get_numeric_input("ID: ")

    product_register = check_if_product_register(product_register_id)

    if not product_register:
        return

    product_price = request_data('SELECT price FROM products WHERE product_name = ?',
                                 (product_register[2], ))[0][0]

    display_register(product_register)

    print("Inserte los nuevos valores")

    new_in_product = get_numeric_input("IN: ")
    new_out_product = get_numeric_input("OUT: ")
    new_profit = (new_in_product - new_out_product) * product_price

    print("¿Esta seguro de que quiere editar este registro con estos valores?")
    display_register((product_register[0], None, product_register[2],
                      new_in_product, new_out_product, new_profit))

    if not ask_confirmation():
        return

    run_query(query, (new_in_product, new_out_product, new_profit, product_register_id))
    print("\nRegistro actualizado\n")


def show_all_products():
    """
    Shows all products on the database"""
    products_list = request_data('SELECT * FROM products', ())

    for product in products_list:
        display_product(product)


def products_submenu(register_id):
    """
    Submenu for all operations concerning the products table"""
    while True:
        print("\nSelecciona un comando:")
        print("1. Mostrar lista de productos")
        print("2. Añadir un producto")
        print("3. Eliminar un producto")
        print("4. Cambiar precio de un producto")
        print("5. Reportar ventas del turno de hoy")
        print("6. Editar ventas del turno de hoy")
        print("7. Mostrar ventas de hoy")
        print("8. Salir\n")

        command = get_numeric_input("> ")

        match command:
            case 1:
                show_all_products()
            case 2:
                add_record(('precio', 'Producto'), 'products', register_id)
            case 3:
                remove_record('Producto', 'products')
            case 4:
                edit_record('products', 'product_name', 'price', register_id)
            case 5:
                fill_product_row(register_id)
            case 6:
                edit_product_row()
            case 7:
                show_all_product_registers(register_id)
            case 8:
                break

# ------------------------------------------------------------------------------
# EXPENSES SECTION

def expenses_submenu(register_id):
    """
    Submenu for all operation about expenses"""
    while True:
        print("\nSelecciona un comando:")
        print("1. Mostrar todos los gastos")
        print("2. Añadir un gasto")
        print("3. Borrar un gasto")
        print("4. Editar un gasto")
        print("5. Salir\n")

        command = get_numeric_input("> ")

        match command:
            case 1:
                show_all_records('expenses', register_id)
            case 2:
                add_record(('cantidad', 'Gasto'), 'expenses', register_id)
            case 3:
                remove_record('Gasto', 'expenses')
            case 4:
                edit_record('expenses', 'concept', 'amount')
            case 5:
                break
# ------------------------------------------------------------------------------
# FUNDS SECTION

def insert_funds(archive):
    if "funds" in archive:
        print("¿Quiere editar los fondos iniciales de este turno?")

        if not ask_confirmation():
            return archive

        print("Inserte los nuevos fondos")
        archive["funds"] = get_numeric_input("FONDOS: ")
        print("Fondos actualizados")
        return archive

    print("Indique los fondos iniciales del turno: ")
    archive["funds"] = get_numeric_input("FONDOS: ")
    print("Fondos establecidos")
    return archive

# ------------------------------------------------------------------------------
# SHIFTS END SECTION

# ------------------------------------------------------------------------------
# MAIN MENU SECTION

def get_numeric_input(prompt):
    """
    Prompts the user to insert text. If it's not a number, recurs"""
    try:
        good_input = int(input(prompt))
    except ValueError:
        print("Ingresa un número por favor")
        return get_numeric_input(prompt)

    return good_input


def ask_confirmation():
    "Asks the user for confirmation"
    command = input("> ")

    if command != "y":
        print("OPERACIÓN NO REALIZADA")
        return False

    return True


def main_menu(register_id):
    """
    Shows the main menu and asks the user to enter a command"""
    print("\n¿Qué necesita hacer?")
    print("1. Insertar fondos o dinero entrante")
    print("2. Administrar maquinas")
    print("3. Administrar productos")
    print("4. Administrar gastos")
    print("5. Generar reporte del turno")
    print("6. Terminar turno")
    print("7. Salir del programa\n")
    command = get_numeric_input("> ")

    match command:
        case 1:
            print("Por implementar")
        case 2:
            machine_submenu(register_id)
        case 3:
            products_submenu(register_id)
        case 4:
            expenses_submenu(register_id)
        case x_1 if x_1 in range(5, 7):
            print("No implementado xd")
        case 7:
            return True
        case _:
            print("Comando desconocido")

    return False


def main():
    "The program's entry point"
    requested_info = [('dates', 'date', 'fecha'),
                      ('shifts', 'shift', 'turno'),
                      ('employees', 'employee_name', 'empleado')]
    register_id = get_current_shift_id(requested_info)
    has_the_program_ended = False

    show_current_register_info(register_id)

    while not has_the_program_ended:
        has_the_program_ended = main_menu(register_id)


if __name__ == "__main__":
    main()
