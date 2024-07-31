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

def perform_add_record(table, tree, values, register_id, en_name, en_amount):
    if not validate_fields([en_name.get(), en_amount.get()]):
        return

    record_name = en_name.get().upper()
    try:
        record_amount = int(en_amount.get())
    except ValueError:
        return

    query = f"""
    SELECT id, {core.comma_separated_string(values[1:])} FROM {table} WHERE register_id = ?
    """
    core.create_record(table, values, (register_id, record_name, record_amount))
    core.fill_table(tree, query, register_id)
    en_name.delete(0, tkinter.END)
    en_amount.delete(0, tkinter.END)

def add_record(root, tree, table, values, register_id):
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
        table, tree, values, register_id, en_name, en_amount)
    )
    add_button.pack()
