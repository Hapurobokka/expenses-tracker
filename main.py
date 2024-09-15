"""
Archivo principal del programa de momento. Ahora usamos clases como una persona normal.

Por Hapurobokka.
"""

import tkinter as tk
from containers import TreeContainer, ProductsContainer, TotalsContainer
import events as ev
import core


def get_register_info(root, register_id):
    data_query = """
    SELECT e.employee_name, s.shift_name, d.date
    FROM registers r
    JOIN employees e ON e.id = r.employee_id
    JOIN shifts s ON s.id = r.shift_id
    JOIN dates d ON d.id = r.date_id
    WHERE r.id = ?
    """
    data = core.request_data(data_query, (register_id,))[0]
    register_info = {}

    register_info["employee"] = tk.StringVar(root, value=data[0])
    register_info["shift"] = tk.StringVar(root, value=data[1])
    register_info["date"] = tk.StringVar(root, value=data[2])

    return register_info


def create_register_display(root, register_info):
    frame = tk.Frame(root)

    employee_frame = tk.LabelFrame(frame, text="Empleado")
    employee_frame.grid(row=0, column=0)
    tk.Label(employee_frame, textvariable=register_info["employee"]).grid(
        row=0, column=0
    )

    shift_frame = tk.LabelFrame(frame, text="Turno")
    shift_frame.grid(row=0, column=1)
    tk.Label(shift_frame, textvariable=register_info["shift"]).grid(row=0, column=0)

    date_frame = tk.LabelFrame(frame, text="Fecha")
    date_frame.grid(row=0, column=2)
    tk.Label(date_frame, textvariable=register_info["date"]).grid(row=0, column=0)

    return frame


def get_lastest_register():
    query = """
    SELECT * FROM registers
    ORDER BY id DESC
    LIMIT 1
    """

    return core.request_data(query)[0][0]


def entry_point(root):
    """Punto de entrada para el programa"""
    root.title("Expense Tracker")

    register_id = get_lastest_register()

    register_info = get_register_info(root, register_id)

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
        command=lambda: ev.spawn_add_register_window(containers),
    ).grid(row=0, column=0)

    register_display_frame = create_register_display(root, register_info)
    register_display_frame.grid(row=0, column=1)

    controlers_frame = tk.Frame(root)
    tk.Button(controlers_frame, text="Mostrar empleados").grid(row=0, column=0)

    controlers_frame.grid(row=0, column=2)

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
entry_point(window)
window.mainloop()
