import sqlite3

DATABASE = "database.db"

def run_query(query, parameters=()) -> sqlite3.Cursor:
    "Runs a query for the external database"
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, parameters)
        conn.commit()
    return result

def request_data(query, parameters):
    "Queries the database for the solicited information, then returns a list of tuples"
    some_cursor = run_query(query, parameters)
    return some_cursor.fetchall()

def comma_separated_string(lst: list) -> str:
    """Takes a list as an argument. Joins all of it's elements with a comma and space"""
    values_string = ", ".join(lst)

    return values_string

def create_values_string(times, char='?'):
    l = []
    for _ in range(times):
        l.append(char)
    return ", ".join(l)

def create_query(table, table_values):
    return f"INSERT INTO {table} ({comma_separated_string(table_values)}) VALUES ({create_values_string(len(table_values))})"

def create_record(table, table_values, values):
    query = create_query(table, table_values)
    run_query(query, values)

def delete_record(table, id):
    run_query(f'DELETE FROM {table} WHERE id = {id}')
