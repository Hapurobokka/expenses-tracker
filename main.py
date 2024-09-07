"""
Archivo principal del programa de momento. Ahora usamos clases como una persona normal.

Por Hapurobokka.
"""

import tkinter as tk
from containers import TreeContainer, ProductsContainer, TotalsContainer


REGISTER_ID = 2


def entry_point(root, register_id):
    """Punto de entrada para el programa"""
    root.title("Expense Tracker")

    total_expenses_frame = tk.Frame(root)

    machine_container = TreeContainer(
        register_id,
        root,
        "Premios de maquinas",
        "machine_table",
        ["id", "machine_name", "amount"],
    )
    replenish_container = TreeContainer(
        register_id,
        root,
        "Reposiciones de maquinas",
        "replenishments",
        ["id", "machine_name", "amount"],
    )
    bussiness_container = TreeContainer(
        register_id, root, "Gastos del negocio", "expenses", ["id", "concept", "amount"]
    )

    products_container = ProductsContainer(
        register_id,
        root,
        "Productos vendidos",
        "products_sales",
        ["id", "product_id", "in_product", "out_product", "profits"],
    )

    totals_container = TotalsContainer(
        register_id,
        total_expenses_frame,
        machine_container.total_var,
        replenish_container.total_var,
        bussiness_container.total_var,
        products_container.total_var,
    )

    machine_container.setup_tree(register_id)
    replenish_container.setup_tree(register_id)
    bussiness_container.setup_tree(register_id)
    products_container.setup_tree(register_id)

    machine_container.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    replenish_container.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    bussiness_container.frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    products_container.frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    totals_container.frame.grid(row=1, column=1, columnspan=2)
    totals_container.expenses_stack.label_frame.grid(row=0, column=0, padx=5)
    totals_container.profits_stack.label_frame.grid(row=0, column=1, padx=5)
    totals_container.report_stack.label_frame.grid(row=0, column=2, padx=5)


window = tk.Tk()
entry_point(window, REGISTER_ID)
window.mainloop()
