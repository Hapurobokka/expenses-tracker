"""
Eventos para cuando pulsemos un bóton. Odio escribir interfaces gráficas.

Creado por Hapurobokka
"""

import tkinter
from tkinter import ttk
import core

def validate_fields(fields: list):
    """ Valida que todos los elementos de la lista tengan una longitud diferente a 0"""
    return all(lambda x: len(x) != 0 for x in fields)

def perform_add_record(tree_container, register_id, en_name, en_amount):
    """Realiza la transacción de añadir un elemento a una tabla"""
    if not validate_fields([en_name.get(), en_amount.get()]):
        return

    record_name = en_name.get().upper()
    try:
        record_amount = int(en_amount.get())
    except ValueError:
        return

    query = f"""
    SELECT id, {core.comma_separated_string(tree_container["table_values"][1:])} 
    FROM {tree_container["table"]} WHERE register_id = ?
    """
    core.create_record(tree_container["table"],
                       ['register_id', *tree_container["table_values"][1:]],
                       (register_id, record_name, record_amount))
    core.fill_table(tree_container["tree"], query, register_id)
    en_name.delete(0, tkinter.END)
    en_amount.delete(0, tkinter.END)

def check_valid_selection(tree: ttk.Treeview):
    """Revisa si hay un elemento seleccionado en el Treeview pasado como argumento"""
    try:
        selected_item = tree.selection()
        _ = tree.item(selected_item)['values'][0] # type: ignore
    except IndexError:
        return False

    return True

def erase_record(tree_container, register_id):
    """Borra una entrada de la lista"""
    if not check_valid_selection(tree_container["tree"]):
        return
    record_id = tree_container["tree"].item(tree_container["tree"].selection())['text']
    core.delete_record(tree_container["table"], record_id)
    query = f"""
    SELECT id, {core.comma_separated_string(tree_container["table_values"][1:])} 
    FROM {tree_container["table"]} WHERE register_id = ?
    """
    core.fill_table(tree_container["tree"], query, register_id)

def perform_alter_record(edit_wind,
                         tree_container,
                         record_id,
                         register_id,
                         buttons):
    """Realiza la transaccón de editar un elemento en la tabla"""
    if not validate_fields([buttons[0].get(), buttons[1].get()]):
        return

    new_name = buttons[0].get().upper()
    try:
        new_amount = int(buttons[1].get())
    except ValueError:
        return

    query = f"""UPDATE {tree_container["table"]}
    SET {tree_container["table_values"][1]} = ?, {tree_container["table_values"][2]} = ? 
    WHERE id = ?"""

    core.run_query(query, (new_name, new_amount, record_id))
    edit_wind.destroy()

    query2 = f"""
    SELECT id, {core.comma_separated_string(tree_container["table_values"][1:])} 
    FROM {tree_container["table"]} WHERE register_id = ?
    """
    print(core.request_data(query2, (10, )))
    core.fill_table(tree_container["tree"], query2, register_id)
