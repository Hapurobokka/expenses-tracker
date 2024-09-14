"""
Archivo principal del programa de momento. Ahora usamos clases como una persona normal.

Por Hapurobokka.
"""

import tkinter as tk
from containers import TreeContainer, ProductsContainer, TotalsContainer
import events as ev


REGISTER_ID = 7


def entry_point(root, register_id):
    """Punto de entrada para el programa"""
    root.title("Expense Tracker")

    total_expenses_frame = tk.Frame(root)

    containers = {}

    containers["machine_container"] = TreeContainer(
        register_id,
        root,
        "Premios de maquinas",
        "machine_table",
        ["id", "machine_name", "amount"],
    )
    containers["replenish_container"] = TreeContainer(
        register_id,
        root,
        "Reposiciones de maquinas",
        "replenishments",
        ["id", "machine_name", "amount"],
    )
    containers["bussiness_container"] = TreeContainer(
        register_id, root, "Gastos del negocio", "expenses", ["id", "concept", "amount"]
    )

    containers["products_container"] = ProductsContainer(
        register_id,
        root,
        "Productos vendidos",
        "products_sales",
        ["id", "product_id", "in_product", "out_product", "profits"],
    )

    containers["totals_container"] = TotalsContainer(
        register_id,
        total_expenses_frame,
        containers["machine_container"].total_var,
        containers["replenish_container"].total_var,
        containers["bussiness_container"].total_var,
        containers["products_container"].total_var,
    )

    containers["machine_container"].setup_tree(register_id)
    containers["replenish_container"].setup_tree(register_id)
    containers["bussiness_container"].setup_tree(register_id)
    containers["products_container"].setup_tree(register_id)

    tk.Button(
        text="Añadir nuevo registro",
        command=lambda: ev.spawn_add_register_window(containers, root),
    ).grid(row=0, column=0)

    containers["machine_container"].frame.grid(
        row=1, column=0, padx=10, pady=10, sticky="nsew"
    )
    containers["replenish_container"].frame.grid(
        row=2, column=0, padx=10, pady=10, sticky="nsew"
    )
    containers["bussiness_container"].frame.grid(
        row=1, column=1, padx=10, pady=10, sticky="nsew"
    )
    containers["products_container"].frame.grid(
        row=1, column=2, padx=10, pady=10, sticky="nsew"
    )

    containers["totals_container"].fill_entries(register_id)
    containers["totals_container"].frame.grid(row=2, column=1, columnspan=2)


window = tk.Tk()
entry_point(window, REGISTER_ID)
window.mainloop()
