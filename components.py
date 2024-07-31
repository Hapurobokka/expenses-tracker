"""
Este archivo contiene las definiciones de la mayoría de contenidos gráficos del programa. Creo.

Hecho por Hapurobokka.
"""

import tkinter
from tkinter import ttk
import events as ev
import core

REGISTER_ID = 10

def setup_products_tree(tree):
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

    query = f"""
    SELECT ps.id, p.product_name, ps.in_product, ps.out_product, ps.profits
    FROM products_sales ps 
    JOIN products p ON p.id = ps.product_id
    WHERE ps.register_id = ?
    """

    core.fill_table(tree, query, REGISTER_ID)


def setup_simple_tree(tree, table, values):
    tree.grid(row=1, column=0, sticky="nsew", columnspan=3) 

    tree.heading("#0", text="ID", anchor=tkinter.CENTER)
    tree.heading("name", text="Nombre", anchor=tkinter.CENTER)
    tree.heading("amount", text="Cantidad", anchor=tkinter.CENTER)

    tree.column("#0", width=40)
    tree.column("name", width=75)
    tree.column("amount", width=90)

    query = f'SELECT {core.comma_separated_string(values)} FROM {table} WHERE register_id = ?'

    core.fill_table(tree, query, REGISTER_ID)


def create_tree_container(root, frame_pos: tuple[int, int], frame_text: str, table: str, table_values: list[str]):
    tree_container = {}

    tree_container["table"] = table
    tree_container["table_values"] = table_values

    tree_container["frame"] = tkinter.Frame(root)
    tree_container["frame"].grid(
        row=frame_pos[0], column=frame_pos[1], padx=10, pady=10, sticky="nsew"
    )

    tree_container["label"] = tkinter.Label(tree_container["frame"], text=frame_text)
    tree_container["label"].grid(row=0, column=0, columnspan=3)

    tree_container["tree"] = ttk.Treeview(tree_container["frame"], columns=["name", "amount"])
    tree_container["tree"].grid(row=0, column=1, columnspan=3)

    tree_container["buttons"] = []

    tree_container["buttons"].append(tkinter.Button(tree_container["frame"], text="Añadir"))
    tree_container["buttons"].append(tkinter.Button(tree_container["frame"], text="Eliminar"))
    tree_container["buttons"].append(tkinter.Button(tree_container["frame"], text="Editar"))

    tree_container["buttons"][0].grid(row=2, column=0)
    tree_container["buttons"][1].grid(row=2, column=1)
    tree_container["buttons"][2].grid(row=2, column=2)

    tree_container["buttons"][0].bind("<Button-1>", lambda _: ev.add_record(root, tree_container, REGISTER_ID))
    tree_container["buttons"][1].bind("<Button-1>", lambda _: ev.erase_record(tree_container, REGISTER_ID))
    tree_container["buttons"][2].bind("<Button-1>", lambda _: ev.alter_record(tree_container, root, REGISTER_ID))

    setup_simple_tree(tree_container["tree"], table, table_values)

    return tree_container

def entry_point(root):
    root.title("Expense Tracker")

    machine_container = create_tree_container(root,
                                              (0, 0),
                                              "Premios de maquinas",
                                              'machine_table',
                                              ['id', 'machine_name', 'amount'])
    replenish_container = create_tree_container(root,
                                                (0, 1),
                                                "Reposiciones de maquinas",
                                                'replenishments',
                                                ['id', 'machine_name', 'amount'])
    expenses_container = create_tree_container(root,
                                               (1, 1),
                                               "Gastos",
                                               'expenses',
                                               ['id', 'concept', 'amount'])

    # Creando frames
    products_sales_frame = tkinter.Frame(root)
    products_sales_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    # Creando labels 
    tkinter.Label(products_sales_frame, text="Ventas productos").grid(row=0, column=0)

    # Crea los treeviews
    products_sales_tree = ttk.Treeview(products_sales_frame, columns=["product_name", "in_product", "out_product", "profits"])

    # Acomodamos nuestro único botón lol
    btn_products = tkinter.Button(products_sales_frame, text="Ver productos")
    btn_products.grid(row=2, column=0)
    btn_products.bind("<Button-1>", lambda _: ev.show_products(root))

    # Función propia porque no mames
    setup_products_tree(products_sales_tree)

window = tkinter.Tk()
entry_point(window)
window.mainloop()
