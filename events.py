from os import pread
import tkinter
from tkinter import ttk
import core

def validate_fields(fields: list):
    f = lambda x: len(x) != 0
    return all(f(x) for x in fields)

def add_slime(name, value, label):
    if not validate_fields([name, value]):
        label["text"] = "Both fields are required"
        return

    label["text"] = "Everything is alright"

def show_products(window):
    product_wind = tkinter.Toplevel(window)
    product_wind.title("Lista de productos en venta")

    products_tree = ttk.Treeview(product_wind, columns=["name", "price"])

    products_tree.heading("#0", text="ID", anchor=tkinter.CENTER)
    products_tree.heading("name", text="Nombre", anchor=tkinter.CENTER)
    products_tree.heading("price", text="Precio", anchor=tkinter.CENTER)

    products_tree.column("#0", width=40)
    products_tree.column("name", width=75)
    products_tree.column("price", width=90)
    products_tree.grid(row=0, column=0)

    query = 'SELECT * FROM products'

    core.fill_table(products_tree, query)

def perform_add_record(tree_container, register_id, en_name, en_amount):
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

def add_record(root, tree_container, register_id):
    add_window = tkinter.Toplevel(root)
    add_window.title("Crear nuevo registro")

    tkinter.Label(add_window, text="Nombre").pack()

    en_name = tkinter.Entry(add_window)
    en_name.focus()
    en_name.pack()

    tkinter.Label(add_window, text="Cantidad").pack()

    en_amount = tkinter.Entry(add_window)
    en_amount.pack()

    add_button = tkinter.Button(add_window, text="Añadir")
    add_button.bind("<Button-1>", lambda _: perform_add_record(
        tree_container, register_id, en_name, en_amount)
    )
    add_button.pack()

def check_valid_selection(tree: ttk.Treeview):
    try:
        selected_item = tree.selection() 
        _ = tree.item(selected_item)['values'][0] # type: ignore
    except IndexError:
        return False

    return True

def erase_record(tree_container, register_id):
    if not check_valid_selection(tree_container["tree"]):
        return
    id = tree_container["tree"].item(tree_container["tree"].selection())['text']
    core.delete_record(tree_container["table"], id)
    query = f"""
    SELECT id, {core.comma_separated_string(tree_container["table_values"][1:])} 
    FROM {tree_container["table"]} WHERE register_id = ?
    """
    core.fill_table(tree_container["tree"], query, register_id)

def perform_alter_record(edit_wind, tree_container, id, register_id, en_new_name, en_new_amount):
    if not validate_fields([en_new_name.get(), en_new_amount.get()]):
        return

    new_name = en_new_name.get().upper()
    try:
        new_amount = int(en_new_amount.get())
    except ValueError:
        return

    query = f"""UPDATE {tree_container["table"]}
    SET {tree_container["table_values"][1]} = ?, {tree_container["table_values"][2]} = ? 
    WHERE id = ?"""

    core.run_query(query, (new_name, new_amount, id))
    edit_wind.destroy()

    query2 = f"""
    SELECT id, {core.comma_separated_string(tree_container["table_values"][1:])} 
    FROM {tree_container["table"]} WHERE register_id = ?
    """
    core.fill_table(tree_container["tree"], query2, register_id)

def alter_record(tree_container, root, register_id):
    if not check_valid_selection(tree_container["tree"]):
        return
    id = tree_container["tree"].item(tree_container["tree"].selection())['text']
    old_name = tree_container["tree"].item(tree_container["tree"].selection())['values'][0]
    old_amount = tree_container["tree"].item(tree_container["tree"].selection())['values'][1]

    edit_wind = tkinter.Toplevel(root)
    edit_wind.title("Editar registro")

    tkinter.Label(edit_wind, text="Nombre anterior: ").grid(row=0, column=1)
    tkinter.Entry(edit_wind, textvariable=tkinter.StringVar(edit_wind, value=old_name), state="readonly").grid(row=0, column=2)

    tkinter.Label(edit_wind, text="Nuevo nombre: ").grid(row=1, column=1)
    new_name = tkinter.Entry(edit_wind)
    new_name.grid(row=1, column=2)

    tkinter.Label(edit_wind, text="Old Price: ").grid(row=2, column=1)
    tkinter.Entry(edit_wind, textvariable=tkinter.StringVar(edit_wind, value=old_amount), state="readonly").grid(row=2, column=2)

    tkinter.Label(edit_wind, text="New Price: ").grid(row=3, column=1)
    new_amount = tkinter.Entry(edit_wind)
    new_amount.grid(row=3, column=2)

    btn_edit = tkinter.Button(edit_wind, text="Editar")
    btn_edit.bind("<Button-1>", lambda _ : perform_alter_record(edit_wind, tree_container, id, register_id, new_name, new_amount))
    btn_edit.grid(row=4, column=2, sticky="we")
