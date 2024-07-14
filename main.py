import tkinter
import sqlite3

DATABASE = "database.db"

# DONE
def run_query(query, parameters=()) -> sqlite3.Cursor:
    "Runs a query for the external database"
    with sqlite3.connect(DATABASE) as conn:
        cursor: sqlite3.Cursor = conn.cursor()
        result: sqlite3.Cursor = cursor.execute(query, parameters)
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
    return request_data(f'SELECT id FROM {table} WHERE {row} = ?', (data, ))[0][0]


def get_total_machine_prices(acc, db_rows):
    "Gets the total of prices given by machines for the current day and shift"
    if len(db_rows) != 0:
        return get_total_machine_prices(acc + db_rows[0][4], db_rows[1:])
    else:
        return acc


def ask_for_information(information, table, row):
    """
    Asks for input on the given data. If it already exists in the table, returns it's id.
    Otherwise, asks if the user wants to add it to the table"""
    current_info = input(f"{information.upper()}: ")

    if not check_if_in_database(table, row, current_info):
        print(f"{information} no registrado. ¿Quiere añadirlo a la base de datos?")

        if input("> ") != "y":
            return None

        add_data(f'INSERT INTO {table} VALUES (NULL, ?)', (current_info, ))
        print(f"{information} añadido.")

    return search_id(table, row, current_info)

# ------------------------------------------------------------------------------

def main(date_id, shift_id, employee_id):
    print("Por favor introduza la siguiente información.")
    if date_id == None:
        return main(ask_for_information('fecha', 'dates', 'date'), shift_id, employee_id)

    if shift_id == None:
        print("Por favor introduzca un turno: ")
        current_shift_id = int(input("TURNO: "))
        return main(date_id, current_shift_id, employee_id)

    if employee_id == None:
        return main(date_id, shift_id, ask_for_information('empleado', 'employees', 'employee_name'))

    print(date_id, shift_id, employee_id)


if __name__ == "__main__": main(None, None, None)
