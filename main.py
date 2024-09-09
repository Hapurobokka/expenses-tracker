"""
Archivo principal del programa de momento. Ahora usamos clases como una persona normal.

Por Hapurobokka.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from containers import TreeContainer, ProductsContainer, TotalsContainer
import events as ev
import core


REGISTER_ID = 1


def get_id(table, field, value):
    try:
        id = core.request_data(f"SELECT id FROM {table} WHERE {field} = ?", (value,))[
            0
        ][0]
    except IndexError:
        return None

    return id


# TODO Hacer esto
def create_register(employee_entry, date_entry, shift_entry):
    if not ev.validate_fields(
        [employee_entry.get(), date_entry.get(), shift_entry.get()]
    ):
        return

    employee = employee_entry.get()
    date = date_entry.get()
    shift = shift_entry.get()

    print(employee, date, shift)

    employee_id = get_id("employees", "employee_name", employee)
    date_id = get_id("dates", "date", date)
    shift_id = get_id("shifts", "shift_name", shift)

    print(employee_id, date_id, shift_id)

    if employee_id is None or shift_id is None:
        return

    if date_id is None:
        confirm = messagebox.askyesno(
            "Confirmación",
            f"{date} aún no tiene turnos, ¿quieres añadir la fecha a la base de datos?",
        )

        if not confirm:
            return

        core.run_query("INSERT INTO date VALUES (NULL, ?)", (date,))
        date_id = get_id("dates", "date", date)

    register_query = """
    SELECT id
    FROM registers
    WHERE employee_id = ? AND date_id = ? AND shift_id = ?
    """

    try:
        register_id = core.request_data(register_query, (employee_id, date_id, shift_id))[0][0]
    except IndexError:
        core.create_record(
            "registers",
            ["employee_id", "date_id", "shift_id"],
            (employee_id, date_id, shift_id),
        )
        register_id = core.request_data(register_query, (employee_id, date_id, shift_id))[0][0]

    print("El register_id es", register_id)

    entry_point(window, register_id)


def spawn_add_register_window():
    """
    Crea la ventana que se encarga de crear un nuevo turno

    Esto esta en main porque básicamente me puede joder
    """
    wind = tk.Toplevel()
    wind.title("Crear un nuevo turno")

    employee = ttk.Combobox(
        wind,
        values=[i[0] for i in core.request_data("SELECT employee_name FROM employees")],
    )
    date = tk.Entry(wind)
    shift = ttk.Combobox(
        wind,
        values=[i[0] for i in core.request_data("SELECT shift_name FROM shifts")],
    )

    tk.Label(wind, text="Empleado").grid(row=0, column=0)
    employee.grid(row=1, column=0)
    tk.Label(wind, text="Turno").grid(row=0, column=1)
    shift.grid(row=1, column=1)
    tk.Label(wind, text="Fecha").grid(row=0, column=2)
    date.grid(row=1, column=2)

    tk.Button(
        wind, text="Confirmar", command=lambda: create_register(employee, date, shift)
    ).grid(row=2, column=1)


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

    tk.Button(text="Añadir nuevo registro", command=spawn_add_register_window).grid(
        row=0, column=0
    )

    machine_container.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    replenish_container.frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
    bussiness_container.frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    products_container.frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

    totals_container.frame.grid(row=2, column=1, columnspan=2)


window = tk.Tk()
entry_point(window, REGISTER_ID)
window.mainloop()
