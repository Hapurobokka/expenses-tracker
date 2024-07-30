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

def setup_simple_tree(tree, table, values, pos, padding=(0, 0)):
    tree.grid(row=pos[0], column=pos[1], padx=padding[0], pady=padding[1]) 

    tree.heading("#0", text="ID", anchor=tkinter.CENTER)
    tree.heading("name", text="Nombre", anchor=tkinter.CENTER)
    tree.heading("amount", text="Cantidad", anchor=tkinter.CENTER)

    tree.column("#0", width=40)
    tree.column("name", width=75)
    tree.column("amount", width=90)

    query = f'SELECT {core.comma_separated_string(values)} FROM {table} WHERE register_id = ?'

    core.fill_table(tree, query, REGISTER_ID)

def entry_point(root):
    root.title("Expense Tracker")

    machine_frame = tkinter.Frame(root)
    machine_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    replenish_frame = tkinter.Frame(root)
    replenish_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    expenses_frame = tkinter.Frame(root)
    expenses_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    products_sales_frame = tkinter.Frame(root)
    products_sales_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    # Vamos a ir cambiando estas labels poco a poco
    tkinter.Label(machine_frame, text="Premios de maquinas").grid(row=0, column=0)
    tkinter.Label(replenish_frame, text="Reposiciones de maquinas").grid(row=0, column=0)
    tkinter.Label(expenses_frame, text="Gastos").grid(row=0, column=0)
    tkinter.Label(products_sales_frame, text="Ventas productos").grid(row=0, column=0)

    # Crea los treeviews
    machine_tree = ttk.Treeview(machine_frame, columns=["name", "amount"])
    replenish_tree = ttk.Treeview(replenish_frame, columns=["name", "amount"])
    expenses_tree = ttk.Treeview(expenses_frame, columns=["name", "amount"])
    products_sales_tree = ttk.Treeview(products_sales_frame, columns=["product_name", "in_product", "out_product", "profits"])

    btn_products = tkinter.Button(products_sales_frame, text="Ver productos")
    btn_products.grid(row=2, column=0)
    btn_products.bind("<Button-1>", lambda _: ev.show_products(root))

    # Los llena con datos de la base de datos
    setup_simple_tree(machine_tree, 'machine_table', ['id', 'machine_name', 'amount'], (1, 0))
    setup_simple_tree(replenish_tree, 'replenishments', ['id', 'machine_name', 'amount'], (1, 0))
    setup_simple_tree(expenses_tree, 'expenses', ['id', 'concept', 'amount'], (1, 0))
    # Función propia porque no mames
    setup_products_tree(products_sales_tree)

window = tkinter.Tk()
entry_point(window)
window.mainloop()
