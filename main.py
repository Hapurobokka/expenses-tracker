""",
Archivo principal del programa de momento. Ahora usamos clases como una persona normal.

Por Hapurobokka.
"""

import tkinter as tk
from containers import *


REGISTER_ID = 1


def entry_point(root):
    """Punto de entrada para el programa"""
    root.title("Expense Tracker")

    total_expenses_frame = tk.Frame(root)

    machine_container = TreeContainer(
        REGISTER_ID,
        root,
        "Premios de maquinas",
        "machine_table",
        ["id", "machine_name", "amount"],
    )
    replenish_container = TreeContainer(
        REGISTER_ID,
        root,
        "Reposiciones de maquinas",
        "replenishments",
        ["id", "machine_name", "amount"],
    )
    bussiness_container = TreeContainer(
        REGISTER_ID, root, "Gastos del negocio", "expenses", ["id", "concept", "amount"]
    )

    products_container = ProductsContainer(
        REGISTER_ID,
        root,
        "Productos vendidos",
        "products_sales",
        ["id", "product_id", "in_product", "out_product", "profits"],
    )

    totals_container = TotalsContainer(
        total_expenses_frame,
        machine_container,
        replenish_container,
        bussiness_container,
        products_container,
    )

    machine_container.setup_tree(REGISTER_ID)
    replenish_container.setup_tree(REGISTER_ID)
    bussiness_container.setup_tree(REGISTER_ID)
    products_container.setup_tree(REGISTER_ID)

    machine_container.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    replenish_container.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    bussiness_container.frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    products_container.frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    totals_container.frame.grid(row=1, column=1, columnspan=2)
    totals_container.expenses_stack.label_frame.grid(row=0, column=0, padx=5)
    totals_container.profits_stack.label_frame.grid(row=0, column=1, padx=5)
    totals_container.report_stack.label_frame.grid(row=0, column=2, padx=5)


window = tk.Tk()
entry_point(window)
window.mainloop()
