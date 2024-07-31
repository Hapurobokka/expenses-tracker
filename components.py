"""
Este archivo contiene las definiciones de la mayoría de contenidos gráficos del programa. Creo.

Hecho por Hapurobokka.
"""

import tkinter
from tkinter import ttk
import events as ev
import core

REGISTER_ID = 10

def spawn_edit_window(tree_container, root, register_id):
    """Crea una ventana que permite editar una entrada de una tabla"""
    if not ev.check_valid_selection(tree_container["tree"]):
        return
    record_id = tree_container["tree"].item(tree_container["tree"].selection())['text']
    old_name = tree_container["tree"].item(tree_container["tree"].selection())['values'][0]
    old_amount = tree_container["tree"].item(tree_container["tree"].selection())['values'][1]

    edit_wind = tkinter.Toplevel(root)
    edit_wind.title("Editar registro")

    tkinter.Label(edit_wind, text="Nombre anterior: ").grid(row=0, column=1)
    tkinter.Entry(edit_wind,
                  textvariable=tkinter.StringVar(edit_wind, value=old_name),
                  state="readonly").grid(row=0, column=2)

    tkinter.Label(edit_wind, text="Nuevo nombre: ").grid(row=1, column=1)
    new_name = tkinter.Entry(edit_wind)
    new_name.grid(row=1, column=2)

    tkinter.Label(edit_wind, text="Old Price: ").grid(row=2, column=1)
    tkinter.Entry(edit_wind,
                  textvariable=tkinter.StringVar(edit_wind, value=old_amount),
                  state="readonly").grid(row=2, column=2)

    tkinter.Label(edit_wind, text="New Price: ").grid(row=3, column=1)
    new_amount = tkinter.Entry(edit_wind)
    new_amount.grid(row=3, column=2)

    btn_edit = tkinter.Button(edit_wind, text="Editar")
    btn_edit.bind("<Button-1>",
                  lambda _ : ev.perform_alter_record(
                      edit_wind, tree_container, record_id, register_id, [new_name, new_amount]
                  ))
    btn_edit.grid(row=4, column=2, sticky="we")

def spawn_add_window(root, tree_container, register_id):
    """Crea una ventana que le pide al usuario los datos para añadir un dato a una tabla"""
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
    add_button.bind("<Button-1>", lambda _: ev.perform_add_record(
        tree_container, register_id, en_name, en_amount)
    )
    add_button.pack()

def show_products(window):
    """Crea una nueva ventana que muestra que productos hay disponibles en la base de datos"""
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

def setup_products_tree(tree):
    """Coloca el arbol de productos de manera correcta en la ventana"""
    tree.grid(row=1, column=0)

    tree.heading("#0", text="ID", anchor=tkinter.CENTER)
    tree.heading("product_name", text="Nombre", anchor=tkinter.CENTER)
    tree.heading("in_product", text="Inicial", anchor=tkinter.CENTER)
    tree.heading("out_product", text="Final", anchor=tkinter.CENTER)
    tree.heading("profits", text="Ganancias", anchor=tkinter.CENTER)

    tree.column("#0", width=40)
    tree.column("product_name", width=200)
    tree.column("in_product", width=70)
    tree.column("out_product", width=70)
    tree.column("profits", width=90)

    query = """
    SELECT ps.id, p.product_name, ps.in_product, ps.out_product, ps.profits
    FROM products_sales ps 
    JOIN products p ON p.id = ps.product_id
    WHERE ps.register_id = ?
    """

    core.fill_table(tree, query, REGISTER_ID)


def setup_simple_tree(tree, table, values):
    """Define todos los elementos de un arbol simple"""
    tree.grid(row=1, column=0, sticky="nsew", columnspan=3)

    tree.heading("#0", text="ID", anchor=tkinter.CENTER)
    tree.heading("name", text="Nombre", anchor=tkinter.CENTER)
    tree.heading("amount", text="Cantidad", anchor=tkinter.CENTER)

    tree.column("#0", width=40)
    tree.column("name", width=75)
    tree.column("amount", width=90)

    query = f'SELECT {core.comma_separated_string(values)} FROM {table} WHERE register_id = ?'

    core.fill_table(tree, query, REGISTER_ID)


def create_tree_container(root,
                          frame_text: str,
                          table: str,
                          table_values: list[str]):
    """Crea un contenedor para un arbol simple"""
    tree_container = {}

    tree_container["table"] = table
    tree_container["table_values"] = table_values

    tree_container["frame"] = tkinter.Frame(root)

    tree_container["label"] = tkinter.Label(tree_container["frame"], text=frame_text)
    tree_container["label"].grid(row=0, column=0, columnspan=3)

    tree_container["tree"] = ttk.Treeview(tree_container["frame"], columns=["name", "amount"])
    tree_container["tree"].grid(row=0, column=1, columnspan=3)

    vscroll = tkinter.Scrollbar(tree_container["frame"],
                                orient="vertical",
                                command=tree_container["tree"].yview)

    vscroll.grid(row=1, column=3, sticky="ns")
    tree_container["tree"].configure(yscrollcommand=vscroll.set)

    tree_container["buttons"] = []

    tree_container["buttons"].append(tkinter.Button(tree_container["frame"], text="Añadir"))
    tree_container["buttons"].append(tkinter.Button(tree_container["frame"], text="Eliminar"))
    tree_container["buttons"].append(tkinter.Button(tree_container["frame"], text="Editar"))

    tree_container["buttons"][0].grid(row=2, column=0)
    tree_container["buttons"][1].grid(row=2, column=1)
    tree_container["buttons"][2].grid(row=2, column=2)

    tree_container["buttons"][0].bind("<Button-1>",
                                      lambda _: spawn_add_window(root, tree_container, REGISTER_ID))
    tree_container["buttons"][1].bind("<Button-1>",
                                      lambda _: ev.erase_record(tree_container, REGISTER_ID))
    tree_container["buttons"][2].bind("<Button-1>",
                                      lambda _: spawn_edit_window(tree_container, root, REGISTER_ID))

    setup_simple_tree(tree_container["tree"], table, table_values)

    return tree_container

def entry_point(root):
    """Punto de entrada para el programa"""
    root.title("Expense Tracker")

    machine_container = create_tree_container(root,
                                              "Premios de maquinas",
                                              'machine_table',
                                              ['id', 'machine_name', 'amount'])
    replenish_container = create_tree_container(root,
                                                "Reposiciones de maquinas",
                                                'replenishments',
                                                ['id', 'machine_name', 'amount'])
    expenses_container = create_tree_container(root,
                                               "Gastos",
                                               'expenses',
                                               ['id', 'concept', 'amount'])

    machine_container["frame"].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    replenish_container["frame"].grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    expenses_container["frame"].grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    # Creando frames
    products_sales_frame = tkinter.Frame(root)
    products_sales_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    # Creando labels
    tkinter.Label(products_sales_frame, text="Ventas productos").grid(row=0, column=0)

    # Crea los treeviews
    products_sales_tree = ttk.Treeview(products_sales_frame, columns=["product_name",
                                                                      "in_product",
                                                                      "out_product",
                                                                      "profits"])

    # Acomodamos nuestro único botón lol
    btn_products = tkinter.Button(products_sales_frame, text="Ver productos")
    btn_products.grid(row=2, column=0)
    btn_products.bind("<Button-1>", lambda _: show_products(root))

    # Función propia porque no mames
    setup_products_tree(products_sales_tree)

window = tkinter.Tk()
entry_point(window)
window.mainloop()
