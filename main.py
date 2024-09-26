"""
Archivo principal del programa de momento. Ahora usamos clases como una persona normal.

Por Hapurobokka.
"""

import tkinter as tk
from containers import TreeContainer, ProductsContainer, TotalsContainer
import events as ev
import core


def get_register_info(root: tk.Tk, register_id: int) -> dict[str, tk.StringVar]:
    """Obtiene toda la información del register_id actual"""

    data_query = """
    SELECT e.employee_name, s.shift_name, d.date
    FROM registers r
    JOIN employees e ON e.id = r.employee_id
    JOIN shifts s ON s.id = r.shift_id
    JOIN dates d ON d.id = r.date_id
    WHERE r.id = ?
    """

    data = core.request_data(data_query, (register_id,))[0]
    register_info: dict[str, tk.StringVar] = {}

    # usamos mucho diccionarios ou yeah
    register_info["employee"] = tk.StringVar(root, value=data[0])
    register_info["shift"] = tk.StringVar(root, value=data[1])
    register_info["date"] = tk.StringVar(root, value=data[2])

    return register_info


def create_register_display(root, register_info):
    """Crea un frame donde se mostrara la información del register_id actual"""
    frame = tk.Frame(root)

    # usa frames o label frames siempre que puedas, de hecho son utiles
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


def get_lastest_register() -> int:
    """Obtiene el último register_id de la base de datos"""
    query = """
    SELECT * FROM registers
    ORDER BY id DESC
    LIMIT 1
    """

    return core.request_data(query)[0][0]


def create_controlers_frame(root):
    controlers_frame = tk.Frame(root)
    employees_button = tk.Button(controlers_frame, text="Mostrar empleados")
    employees_button.grid(row=0, column=0)
    employees_button.bind(
        "<Button-1>",
        lambda _: ev.show_table(
            "employees",
            ["id", "employee_name"],
            "Ver empleados",
            "employee",
            "Empleado",
        ),
    )

    return controlers_frame


def create_containers(
    root: tk.Tk, register_id: int
) -> dict[str, TreeContainer | ProductsContainer]:
    """Crea los contendores"""
    containers: dict[str, TreeContainer | ProductsContainer] = {}

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

    return containers


def entry_point(root: tk.Tk):
    """Punto de entrada para el programa"""
    root.title("Expense Tracker")

    register_id: int = get_lastest_register()
    register_info: dict[str, tk.StringVar] = get_register_info(root, register_id)

    containers = create_containers(root, register_id)

    # este necesitamos crearlo aparte porque no es similar a los otros tipos de contendor
    total_expenses_frame = tk.Frame(root)
    totals_container = TotalsContainer(
        register_id,
        total_expenses_frame,
        containers["machine_container"].total_var,
        containers["replenish_container"].total_var,
        containers["bussiness_container"].total_var,
        containers["products_container"].total_var,
    )

    # no recuerdo porque tenemos que llamar esto aqui
    containers["machine_container"].setup_tree(register_id)
    containers["replenish_container"].setup_tree(register_id)
    containers["bussiness_container"].setup_tree(register_id)
    containers["products_container"].setup_tree(register_id)

    tk.Button(
        text="Añadir nuevo registro",
        command=lambda: ev.spawn_add_register_window(containers, totals_container),
    ).grid(row=0, column=0)

    register_display_frame = create_register_display(root, register_info)
    register_display_frame.grid(row=0, column=1)

    controlers_frame = create_controlers_frame(root)
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

    totals_container.fill_entries(register_id)
    totals_container.frame.grid(row=2, column=1, columnspan=2)


window = tk.Tk()
entry_point(window)
window.mainloop()
