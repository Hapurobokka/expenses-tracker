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

    query = f'SELECT * FROM products'

    core.fill_table(products_tree, query)
