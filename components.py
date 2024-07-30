"""
Este archivo contiene las definiciones de la mayoría de contenidos gráficos del programa. Creo.

Hecho por Hapurobokka.
"""

import tkinter
from tkinter import ttk
import events as ev
import core

class App:
    """
    Contiene los componentes de la ventana principal
    """
    def __init__(self, cool_window):
        self.wind = cool_window
        self.wind.title("Expense Tracker")

        self.products_frame = tkinter.LabelFrame(self.wind, text="Ventas de productos")
        self.products_frame.grid(row=0, column=2)

        # Vamos a ir cambiando estas labels poco a poco
        tkinter.Label(self.wind, text="Premios de maquinas").grid(row=0, column=0)
        tkinter.Label(self.wind, text="Reposiciones de maquinas").grid(row=0, column=1)
        tkinter.Label(self.wind, text="Gastos").grid(row=2, column=1, pady=10)

        # Crea los treeviews
        self.machine_tree = ttk.Treeview(columns=["name", "amount"], height=10)
        self.replenish_tree = ttk.Treeview(columns=["name", "amount"])
        self.expenses_tree = ttk.Treeview(columns=["name", "amount"])
        self.products_sales_tree = ttk.Treeview(columns=["product_name", "in_product", "out_product", "profits"])

        tkinter.Button(self.wind, text="Ver productos", command = lambda: ev.show_products(self.wind)).grid(row=2, column=2)
        
        # Los llena con datos de la base de datos
        self.setup_simple_tree(self.machine_tree, 
                               'machine_table',
                               ['id', 'machine_name', 'amount'], 
                               (1, 0))
        self.setup_simple_tree(self.replenish_tree,
                               'replenishments',
                               ['id', 'machine_name', 'amount'],
                               (1, 1),
                               (20, 0))
        self.setup_simple_tree(self.expenses_tree,
                               'expenses',
                               ['id', 'concept', 'amount'],
                               (3, 1),
                               (20, 0))
        self.setup_products_tree()

    def setup_simple_tree(self, tree, table, values, pos, padding=(0, 0)):
        tree.grid(row=pos[0], column=pos[1], padx=padding[0], pady=padding[1]) 

        tree.heading("#0", text="ID", anchor=tkinter.CENTER)
        tree.heading("name", text="Nombre", anchor=tkinter.CENTER)
        tree.heading("amount", text="Cantidad", anchor=tkinter.CENTER)

        tree.column("#0", width=40)
        tree.column("name", width=75)
        tree.column("amount", width=90)

        query = f'SELECT {core.comma_separated_string(values)} FROM {table} WHERE register_id = ?'

        core.fill_table(tree, query, 10)

    def setup_products_tree(self):
        self.products_sales_tree.grid(row=1, column=2, padx=20)

        self.products_sales_tree.heading("#0", text="ID", anchor=tkinter.CENTER)
        self.products_sales_tree.heading("product_name", text="Nombre", anchor=tkinter.CENTER)
        self.products_sales_tree.heading("in_product", text="Inicial", anchor=tkinter.CENTER)
        self.products_sales_tree.heading("out_product", text="Final", anchor=tkinter.CENTER)
        self.products_sales_tree.heading("profits", text="Ganancias", anchor=tkinter.CENTER)

        self.products_sales_tree.column("#0", width=40)
        self.products_sales_tree.column("product_name", width=200)
        self.products_sales_tree.column("in_product", width=70)
        self.products_sales_tree.column("out_product", width=70)
        self.products_sales_tree.column("profits", width=90)

        query = f"""
        SELECT ps.id, p.product_name, ps.in_product, ps.out_product, ps.profits
        FROM products_sales ps 
        JOIN products p ON p.id = ps.product_id
        WHERE ps.register_id = ?
        """

        core.fill_table(self.products_sales_tree, query, 10)

window = tkinter.Tk()
application = App(window)
window.mainloop()
