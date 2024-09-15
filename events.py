"""
Eventos para cuando pulsemos un bóton. Odio escribir interfaces gráficas.

Creado por Hapurobokka
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import TYPE_CHECKING

import core

if TYPE_CHECKING:
    from containers import (
        TreeContainer,
        SimpleContainer,
        ProductsContainer,
        TotalsContainer,
    )


def validate_fields(fields: list) -> bool:
    """Valida que todos los elementos de la lista tengan una longitud diferente a 0"""
    return all(len(x) != 0 for x in fields)


def perform_add_record(
    container: TreeContainer | SimpleContainer,
    en_name: tk.Entry,
    en_amount: tk.Entry,
    register_id: int | None = None,
) -> None:
    """Realiza la transacción de añadir un elemento a una tabla"""
    if not validate_fields([en_name.get(), en_amount.get()]):
        return

    record_name = en_name.get().upper()
    try:
        record_amount = int(en_amount.get())
    except ValueError:
        return

    if container.table == "products":
        core.create_record(
            container.table,
            container.table_values[1:],
            (record_name, record_amount),
        )
    else:
        core.create_record(
            container.table,
            ["register_id", *container.table_values[1:]],
            (register_id, record_name, record_amount),
        )

    core.fill_table(container, register_id)

    en_name.delete(0, tk.END)
    en_amount.delete(0, tk.END)


def check_valid_selection(tree: ttk.Treeview) -> bool:
    """Revisa si hay un elemento seleccionado en el Treeview pasado como argumento"""
    try:
        selected_item = tree.selection()
        _ = tree.item(selected_item)["values"][0]  # type: ignore
    except IndexError:
        return False

    return True


def delete_record_on_click(
    container: TreeContainer | SimpleContainer, register_id: int | None = None
) -> None:
    """Borra una entrada de la lista"""
    if not check_valid_selection(container.tree):
        return

    record_id = container.tree.item(container.tree.selection())["text"]  # type: ignore

    core.delete_record(container.table, "id", record_id)
    core.fill_table(container, register_id)


def perform_alter_record(
    edit_wind: tk.Toplevel,
    container: TreeContainer | SimpleContainer,
    record_id: int,
    buttons: list,
    register_id: int | None = None,
) -> None:
    """Realiza la transacción de editar un elemento en la tabla"""
    if not validate_fields([buttons[0].get(), buttons[1].get()]):
        return

    new_name = buttons[0].get().upper()
    try:
        new_amount = int(buttons[1].get())
    except ValueError:
        return

    query = f"""UPDATE {container.table}
    SET {container.table_values[1]} = ?, {container.table_values[2]} = ?
    WHERE id = ?"""

    core.run_query(query, (new_name, new_amount, record_id))
    edit_wind.destroy()

    core.fill_table(container, register_id)


def get_profits(combo: ttk.Combobox, fields: list) -> int:
    """Calcula la cantidad de ganancias dependiendo del producto indicado en combo
    y las cantidades iniciales y finales indicadas en fields"""
    query = "SELECT price FROM products WHERE product_name = ?"
    selected_item = combo.get()

    try:
        price = core.request_data(query, (selected_item,))[0][0]
    except IndexError:
        return 0

    try:
        in_product = int(fields[0].get())
        out_product = int(fields[1].get())
    except ValueError:
        return 0

    return (in_product - out_product) * price


def create_profits(
    combo: ttk.Combobox, entry: tk.Entry, entry_var: tk.IntVar, fields: list
) -> None:
    """Muestra la cantidad de ingresos que se van a obtener de la venta de
    cierta cantidad de productos"""
    if not validate_fields([combo.get(), fields[0].get(), fields[1].get()]):
        return

    profits = get_profits(combo, fields)

    entry.config(state="normal")
    entry_var.set(profits)
    entry.config(state="readonly")


def add_products_record(
    combo: ttk.Combobox, fields: list, container: TreeContainer, register_id: int
) -> None:
    """Añade una entrada a la tabla de ventas de productos"""
    if not validate_fields([combo.get(), fields[0].get(), fields[1].get()]):
        return

    profits = get_profits(combo, fields)
    product_id = core.request_data(
        "SELECT id FROM products WHERE product_name = ?", (combo.get(),)
    )[0][0]

    try:
        in_product = int(fields[0].get())
        out_product = int(fields[1].get())
    except ValueError:
        return

    core.create_record(
        "products_sales",
        ["register_id", "product_id", "in_product", "out_product", "profits"],
        (register_id, product_id, in_product, out_product, profits),
    )

    core.fill_table(container, register_id)


def spawn_product_report_window(container: ProductsContainer, register_id: int) -> None:
    """Crea la ventana que permite añadir un reporte de ventas de un producto"""
    query = "SELECT product_name FROM products"

    new_win = tk.Toplevel()

    tk.Label(new_win, text="Producto").grid(row=0, column=0)
    tk.Label(new_win, text="Entrada").grid(row=0, column=1)
    tk.Label(new_win, text="Salida").grid(row=0, column=2)
    tk.Label(new_win, text="Ingresos").grid(row=0, column=3)

    combo = ttk.Combobox(new_win, values=[i[0] for i in core.request_data(query)])
    combo.grid(row=1, column=0)

    entry_1 = tk.Entry(new_win)
    entry_1.grid(row=1, column=1)
    entry_2 = tk.Entry(new_win)
    entry_2.grid(row=1, column=2)

    frozen_var = tk.IntVar(new_win, value=0)
    frozen = tk.Entry(new_win, textvariable=frozen_var, state="readonly")
    frozen.grid(row=1, column=3)

    add_button = tk.Button(new_win, text="Añadir")
    add_button.grid(row=3, column=1, sticky="ew", columnspan=2, pady=10)

    combo.bind(
        "<FocusOut>",
        lambda _: create_profits(combo, frozen, frozen_var, [entry_1, entry_2]),
    )
    entry_1.bind(
        "<FocusOut>",
        lambda _: create_profits(combo, frozen, frozen_var, [entry_1, entry_2]),
    )
    entry_2.bind(
        "<FocusOut>",
        lambda _: create_profits(combo, frozen, frozen_var, [entry_1, entry_2]),
    )

    add_button.bind(
        "<Button-1>",
        lambda _: add_products_record(
            combo, [entry_1, entry_2], container, register_id
        ),
    )


# def recur_erase_record(
#     container: TreeContainer | SimpleContainer,
#     assoc_container: TreeContainer,
#     register_id: int,
# ) -> None:
#     """
#     Elimina una entrada de una 'tabla superior' (una que no posee registros de turno)
#     y todas sus entradas de forma recursiva de otras tablas
#     """
#     if not check_valid_selection(container.tree):
#         return
#
#     record_id = container.tree.item(container.tree.selection())["text"]  # type: ignore
#
#     core.delete_record(container.table, "id", record_id)
#     core.delete_record(assoc_container.table, "product_id", record_id)
#
#     core.fill_table(container)
#     core.fill_table(assoc_container, register_id)
#


def spawn_add_window(
    container: SimpleContainer | TreeContainer,
    register_id: int | None = None,
) -> None:
    """Crea una ventana que le pide al usuario los datos para añadir un dato a una tabla"""
    add_window = tk.Toplevel()
    add_window.title("Crear nueva entrada")

    tk.Label(add_window, text="Nombre").pack()

    en_name = tk.Entry(add_window)
    en_name.focus()
    en_name.pack()

    tk.Label(add_window, text="Cantidad").pack()

    en_amount = tk.Entry(add_window)
    en_amount.pack()

    add_button = tk.Button(add_window, text="Añadir")
    add_button.bind(
        "<Button-1>",
        lambda _: perform_add_record(container, en_name, en_amount, register_id),
    )
    add_button.pack()


def spawn_edit_window(
    container: TreeContainer | SimpleContainer,
    register_id: int | None = None,
) -> None:
    """Crea una ventana que permite editar una entrada de una tabla"""
    if not check_valid_selection(container.tree):
        return

    record_id = container.tree.item(container.tree.selection())["text"]  # type: ignore
    old_name = container.tree.item(container.tree.selection())["values"][0]  # type: ignore
    old_amount = container.tree.item(container.tree.selection())["values"][1]  # type: ignore

    edit_wind = tk.Toplevel()
    edit_wind.title("Editar registro")

    tk.Label(edit_wind, text="Nombre anterior: ").grid(row=0, column=1)
    tk.Entry(
        edit_wind,
        textvariable=tk.StringVar(edit_wind, value=old_name),
        state="readonly",
    ).grid(row=0, column=2)

    tk.Label(edit_wind, text="Nuevo nombre: ").grid(row=1, column=1)
    new_name = tk.Entry(edit_wind)
    new_name.grid(row=1, column=2)

    tk.Label(edit_wind, text="Old Price: ").grid(row=2, column=1)
    tk.Entry(
        edit_wind,
        textvariable=tk.StringVar(edit_wind, value=old_amount),
        state="readonly",
    ).grid(row=2, column=2)

    tk.Label(edit_wind, text="New Price: ").grid(row=3, column=1)
    new_amount = tk.Entry(edit_wind)
    new_amount.grid(row=3, column=2)

    btn_edit = tk.Button(edit_wind, text="Editar")
    btn_edit.bind(
        "<Button-1>",
        lambda _: perform_alter_record(
            edit_wind, container, record_id, [new_name, new_amount], register_id
        ),
    )
    btn_edit.grid(row=4, column=2, sticky="we")


def show_products() -> None:
    """Crea una nueva ventana que muestra que productos hay disponibles en la base de datos"""
    from containers import SimpleContainer

    product_wind = tk.Toplevel()
    product_wind.title("Lista de productos en venta")

    product_wind_container = SimpleContainer(
        product_wind,
        "products",
        ["id", "product_name", "price"],
        ttk.Treeview(product_wind, columns=["name", "price"]),
        "SELECT * FROM products",
    )

    product_wind_container.tree.heading("#0", text="ID", anchor=tk.CENTER)
    product_wind_container.tree.heading("name", text="Nombre", anchor=tk.CENTER)
    product_wind_container.tree.heading("price", text="Precio", anchor=tk.CENTER)

    product_wind_container.tree.column("#0", width=40)
    product_wind_container.tree.column("name", width=75)
    product_wind_container.tree.column("price", width=90)
    product_wind_container.tree.grid(row=0, column=0, columnspan=3, sticky="nsew")

    vscroll = tk.Scrollbar(
        product_wind, orient="vertical", command=product_wind_container.tree.yview
    )

    vscroll.grid(row=0, column=4, sticky="ns")
    product_wind_container.tree.configure(yscrollcommand=vscroll.set)

    btn_1 = tk.Button(product_wind, text="Añadir")
    btn_1.bind(
        "<Button-1>",
        lambda _: spawn_add_window(product_wind_container),
    )
    btn_1.grid(row=1, column=0)

    btn_2 = tk.Button(product_wind, text="Borrar")
    btn_2.bind("<Button-1>", lambda _: delete_record_on_click(product_wind_container))
    btn_2.grid(row=1, column=1)

    btn_3 = tk.Button(product_wind, text="Editar")
    btn_3.bind("<Button-1>", lambda _: spawn_edit_window(product_wind_container))
    btn_3.grid(row=1, column=2)

    core.fill_table(product_wind_container)


def capture_report(container: TotalsContainer, register_id: int):
    confirmation = messagebox.askyesno(
        "Confirmación", "¿Estás seguro de que quieres capturar este turno?"
    )

    if not confirmation:
        return

    query = """SELECT * FROM daily_reports WHERE register_id = ?"""
    current_register = core.request_data(query, (register_id,))

    if current_register == []:
        core.create_record(
            "daily_reports",
            [
                "register_id",
                "final_profits",
                "final_expenses",
                "total_funds",
                "initial_funds",
                "extra_funds",
                "reported_funds",
                "difference",
            ],
            (
                register_id,
                container.total_variables["total_profits"].get(),
                container.total_variables["total_expenses"].get(),
                container.total_variables["expected_funds"].get(),
                container.profits_stack.stack["initial_funds"].element_2.get(),
                container.profits_stack.stack["additional_funds"].element_2.get(),
                container.report_stack.stack["reported_funds"].element_2.get(),
                container.total_variables["difference"].get(),
            ),
        )

        return

    update_query = """
    UPDATE daily_reports
    SET 
        final_profits = ?,
        final_expenses = ?,
        total_funds = ?,
        initial_funds = ?,
        extra_funds = ?,
        reported_funds = ?,
        difference = ?
    WHERE register_id = ?;"""

    core.run_query(
        update_query,
        (
            container.total_variables["total_profits"].get(),
            container.total_variables["total_expenses"].get(),
            container.total_variables["expected_funds"].get(),
            container.profits_stack.stack["initial_funds"].element_2.get(),
            container.profits_stack.stack["additional_funds"].element_2.get(),
            container.report_stack.stack["reported_funds"].element_2.get(),
            container.total_variables["difference"].get(),
            register_id,
        ),
    )


def refill_containers(
    containers: dict,
    register_id: int,
) -> None:
    core.fill_table(containers["machine_container"], register_id)
    core.fill_table(containers["replenish_container"], register_id)
    core.fill_table(containers["bussiness_container"], register_id)
    core.fill_table(containers["products_container"], register_id)

    containers["totals_container"].fill_entries(register_id)


def create_register(entries: dict[str, tk.Entry], containers: dict, root: tk.Toplevel):
    """Creates a new register record with an employee, shift and date"""
    if not validate_fields(
        [entries["employee"].get(), entries["date"].get(), entries["shift"].get()]
    ):
        return

    employee = entries["employee"].get()
    date = entries["date"].get()
    shift = entries["shift"].get()

    employee_id = core.get_id("employees", "employee_name", employee)
    date_id = core.get_id("dates", "date", date)
    shift_id = core.get_id("shifts", "shift_name", shift)

    if employee_id is None or shift_id is None:
        return

    if date_id is None:
        confirm = messagebox.askyesno(
            "Confirmación",
            f"{date} aún no tiene turnos, ¿quieres añadir la fecha a la base de datos?",
        )

        if not confirm:
            return

        core.run_query("INSERT INTO dates VALUES (NULL, ?)", (date,))
        date_id = core.get_id("dates", "date", date)

    register_query = """
    SELECT id
    FROM registers
    WHERE employee_id = ? AND date_id = ? AND shift_id = ?
    """

    register_id = core.request_data(register_query, (employee_id, date_id, shift_id))

    if register_id == []:
        core.create_record(
            "registers",
            ["employee_id", "date_id", "shift_id"],
            (employee_id, date_id, shift_id),
        )
        register_id = core.request_data(
            register_query, (employee_id, date_id, shift_id)
        )

    refill_containers(containers, register_id[0][0])
    root.destroy()


def spawn_add_register_window(containers):
    """
    Crea la ventana que se encarga de crear un nuevo turno

    Esto esta en main porque básicamente me puede joder
    """
    wind = tk.Toplevel()
    wind.title("Crear un nuevo turno")

    entries: dict[str, ttk.Combobox | tk.Entry] = {}

    entries["employee"] = ttk.Combobox(
        wind,
        values=[
            i[0] for i in core.request_data(
                "SELECT employee_name FROM employees ORDER BY employee_name ASC"
            )
        ],
    )
    entries["date"] = tk.Entry(wind)
    entries["shift"] = ttk.Combobox(
        wind,
        values=[i[0] for i in core.request_data("SELECT shift_name FROM shifts")],
    )

    current_date = core.request_data("SELECT date('now')")[0][0]

    tk.Label(wind, text="Empleado").grid(row=0, column=0)
    entries["employee"].grid(row=1, column=0)
    tk.Label(wind, text="Turno").grid(row=0, column=1)
    entries["shift"].grid(row=1, column=1)

    tk.Label(wind, text="Fecha").grid(row=0, column=2)
    entries["date"].grid(row=1, column=2)
    entries["date"].insert(0, current_date)

    tk.Button(
        wind,
        text="Confirmar",
        command=lambda: create_register(entries, containers, wind),
    ).grid(row=2, column=1)
