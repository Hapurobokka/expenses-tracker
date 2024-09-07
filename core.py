"""
Operaciones donde usamos la base de datos. No se usar bases de datos.

Por Hapurobokka.
"""

import sqlite3
import tkinter

DATABASE = "database.sqlite3"


def run_query(query, parameters=()) -> sqlite3.Cursor:
    """Runs a query for the external database"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, parameters)
        conn.commit()
    return result


def request_data(query, parameters=()) -> list[tuple]:
    """Queries the database for the solicited information, then returns a list of tuples"""
    some_cursor = run_query(query, parameters)
    return some_cursor.fetchall()


def comma_separated_string(lst: list) -> str:
    """Takes a list as an argument. Joins all of it's elements with a comma and space"""
    values_string = ", ".join(lst)

    return values_string


def create_values_string(times, char="?"):
    """
    Devuelve una string que contiene char la cantidad de veces indicada por times
    """
    char_list = []
    for _ in range(times):
        char_list.append(char)
    return ", ".join(char_list)


def create_insert_query(table, table_values):
    """Crea una query apropiada para introducir valores en una tabla"""

    return f"""
    INSERT INTO {table} ({comma_separated_string(table_values)})
    VALUES ({create_values_string(len(table_values))})
    """


def create_record(table, table_values, values):
    """Crea una entrada en la tabla indicada usando los valores pasados como argumento"""
    query = create_insert_query(table, table_values)
    run_query(query, values)


def delete_record(table, key, value):
    """Borra una entrada de una tabla utilizando su ID"""
    run_query(f"DELETE FROM {table} WHERE {key} = {value}")


def tuples_to_vector(some_tuples):
    """
    Toma una lista de tuplas y devuelve una lista que contiene solo el primer valor de todas
    ellas"""
    return [tup[0] for tup in some_tuples]


def get_total_amount(table, selection, register_id):
    """Queries the database for a list of values and then adds them all"""
    query = f"SELECT {selection} FROM {table} WHERE register_id = ?"
    values = request_data(query, (register_id,))

    if not values:
        return 0

    return sum(tuples_to_vector(values))


def fill_table(container, register_id: int | None = None) -> None:
    """Queries the database for data and writes in on a treeview"""
    for element in container.tree.get_children():
        container.tree.delete(element)

    if register_id is None:
        db_rows = run_query(container.fill_query)
    else:
        db_rows = run_query(container.fill_query, (register_id,))

    for row in db_rows:
        container.tree.insert("", tkinter.END, text=row[0], values=row[1:])

    if container.table == "products":
        return

    container.update_total_var(register_id)


def fill_entries(container, register_id: int) -> None:
    """Fills the text fields in our container with data captured for the current register id"""
    fill_query = """
    SELECT initial_funds, extra_funds, reported_funds
    FROM daily_reports
    WHERE id = ?
    """

    entry_values = request_data(fill_query, (register_id,))[0]

    if entry_values == ():
        return

    container.profits_stack.stack["initial_funds"].element_2.insert(0, entry_values[0])
    container.profits_stack.stack["additional_funds"].element_2.insert(
        0, entry_values[1]
    )
    container.report_stack.stack["reported_funds"].element_2.insert(0, entry_values[2])
