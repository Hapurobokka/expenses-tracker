"""
Archivo principal del programa, de momento.

Hecho por Hapurobokka.
"""
# import tkinter
import sqlite3

DATABASE = "database.db"


# DONE
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


def delete_data(undesired_data):
    "Deletes the record matching the id"
    query = "DELETE FROM machine_table WHERE id = ?"
    run_query(query, (undesired_data, ))


def check_if_in_database(table_to_check, column_to_check, data):
    "Check if the given data exists in a table"
    return request_data(f"SELECT * FROM {table_to_check} WHERE {column_to_check} = ?", (data, ))


def search_id(table, row, data):
    "Returns the id for the given data"
    try:
        return request_data(f'SELECT id FROM {table} WHERE {row} = ?', (data, ))[0][0]
    except IndexError:
        return None

# ------------------------------------------------------------------------------

def get_total_machine_prices(acc, db_rows):
    "Gets the total of prices given by machines for the current day and shift"
    if len(db_rows) != 0:
        return get_total_machine_prices(acc + db_rows[0][4], db_rows[1:])

    return acc


def test_machine_entry(entry: list[str]) -> bool:
    """
    Tests if the entry for the any of the machine tables (machine_table or replenishments) is valid
    """
    if len(entry) != 2:
        return False

    if len(entry[0]) != 2:
        return False

    if not str.isalpha(entry[0][0]) and not str.isnumeric(entry[0][1]):
        return False

    if not str.isnumeric(entry[1]):
        return False

    return True


def format_machine_entry(prompt: str):
    """
    Gets a prompt, then splits it through the whitespace and uses a function to
    check if it conforts to the format. If not, returns false. Otherwise, capitalizes it and
    returns a tuple"""
    unformated_entry = prompt.split()

    if not test_machine_entry(unformated_entry):
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
    print("Ahora mismo esta trabajando con {}".format(table))
    print("Introduce un texto del estilo 'nombre_maquina cantidad'. Ejemplo 'a2 200'.")
    print("Cuando quiera termina escriba '.exit'.")

    entry = ""
    while True:
        entry = input("> ")

        if entry == ".exit":
            break

        insert_into_machine_table(entry, table, register_id)

# ------------------------------------------------------------------------------

def check_registers(current_register):
    """
    Compares the given register with the database. If it's already there returns it's id.
    Otherwise, it prompts the user to add it."""
    searched_register = request_data('SELECT id FROM registers WHERE date_id = ? AND shift_id = ? '
                                     + 'AND employee_id = ?', current_register)

    if not searched_register:
        print("Este turno parece no estar registrado en la base de datos, ¿quiere registrarlo?")

        if input("> ") != "y":
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

    if not check_if_in_database(table, row, current_info):
        print(f"{information} no registrado. ¿Quiere añadirlo a la base de datos?")

        if input("> ") != "y":
            return bundled_info

        add_data(f'INSERT INTO {table} VALUES (NULL, ?)', (current_info, ))
        print(f"{information} añadido.")

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

def get_numeric_input():
    """
    Prompts the user to insert text. If it's not a number, recurs"""
    try:
        good_input = int(input("> "))
    except ValueError:
        print("Ingresa un número por favor")
        return get_numeric_input()

    return good_input

def main_menu(register_id):
    """
    Shows the main menu and asks the user to enter a command"""
    print("\n¿Qué necesita hacer?")
    print("1. Insertar premios de maquinas")
    print("2. Insertar reposiciones")
    print("3. Insertar ventas de productos")
    print("4. Insertar un gasto")
    print("5. Insertar fondos o dinero entrante")
    print("6. Generar reporte del turno")
    print("7. Terminar turno")
    print("8. Salir del programa\n")
    command = get_numeric_input()

    match command:
        case 1:
            get_prompts_for_machine_table(register_id, 'machine_table')
        case 2:
            get_prompts_for_machine_table(register_id, 'replenishments')
        case x_1 if x_1 in range(3, 8):
            print("No implementado xd")
        case 8:
            return True

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
