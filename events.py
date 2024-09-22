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
    entries: list[tk.Entry],
    register_id: int | None = None,
) -> None:
    """Realiza la transacción de añadir un elemento a una tabla"""
    if not validate_fields([x.get() for x in entries]):
        return

    values = []
    for entry in entries:
        val = entry.get()

        try:
            values.append(int(val))
        except ValueError:
            values.append(val.upper())

    if container.table in ["products", "employees"]:
        core.create_record(
            container.table,
            container.table_values[1:],
            tuple(values),
        )
    else:
        core.create_record(
            container.table,
            ["register_id", *container.table_values[1:]],
            (register_id, *values),
        )

    core.fill_table(container, register_id)

    for entry in entries:
        entry.delete(0, tk.END)

    entries[0].focus()


def check_valid_selection(tree: ttk.Treeview) -> bool:
    """Revisa si hay un elemento seleccionado en el Treeview pasado como argumento"""
    try:
        selected_item = tree.selection()[0]
        _ = tree.item(selected_item)["values"][0]
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
    container: SimpleContainer | TreeContainer,
    columns: list[str],
    entries: list[tk.Entry],
    record_id: int,
    register_id: int | None = None,
) -> None:
    """Realiza la transacción de editar un elemento en la tabla"""
    if not validate_fields([x.get() for x in entries]):
        return

    values = []
    for entry in entries:
        val = entry.get()

        if val.isdigit():
            values.append(int(val))
        else:
            values.append(val.upper())

    query = f"""
    UPDATE {container.table}
    SET {core.create_query_placeholder(columns)}
    WHERE id = ?"""

    core.run_query(query, (*values, record_id))
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
    labels: tuple[str, str] | str,
    register_id: int | None = None,
) -> None:
    """Crea una ventana que le pide al usuario los datos para añadir un dato a una tabla"""
    add_window = tk.Toplevel()
    add_window.title("Crear nueva entrada")

    entries = []

    if isinstance(labels, str):
        tk.Label(add_window, text=labels).pack()
        entry = tk.Entry(add_window)
        entry.pack()
        entries.append(entry)
    else:
        for name in labels:
            tk.Label(add_window, text=name).pack()
            entry = tk.Entry(add_window)
            entry.pack()
            entries.append(entry)

    entries[0].focus()

    add_button = tk.Button(add_window, text="Añadir")
    add_button.bind(
        "<Button-1>",
        lambda _: perform_add_record(container, entries, register_id),
    )
    add_button.pack()


def spawn_edit_window(
    container: TreeContainer | SimpleContainer,
    fields: list[str] | str,
    register_id: int | None = None,
) -> None:
    """Crea una ventana que permite editar una entrada de una tabla"""
    if not check_valid_selection(container.tree):
        return

    edit_wind = tk.Toplevel()
    edit_wind.title("Editar registro")

    selected_values = container.tree.item(container.tree.selection()[0])
    record_id = int(selected_values["text"])

    entries = []

    if isinstance(fields, str):
        tk.Label(edit_wind, text=f"{fields}").pack()
        entry = tk.Entry(edit_wind)
        entry.pack()
        entries.append(entry)
    else:
        for field in fields:
            tk.Label(edit_wind, text=f"{field}").pack()
            entry = tk.Entry(edit_wind)
            entry.pack()
            entries.append(entry)

    btn_edit = tk.Button(edit_wind, text="Editar")
    btn_edit.bind(
        "<Button-1>",
        lambda _: perform_alter_record(
            edit_wind,
            container,
            container.table_values[1:],
            entries,
            record_id,
            register_id,
        ),
    )
    btn_edit.pack()


def create_table_tree(table_container: SimpleContainer, columns, columns_name):
    """Crea el treeview de un contenedor simple (o probablemente de cualquier otro contendor)"""
    table_container.tree.heading("#0", text="ID", anchor=tk.CENTER)
    table_container.tree.column("#0", width=40)

    if isinstance(columns_name, str):
        table_container.tree.heading(columns, text=columns_name, anchor=tk.CENTER)  # type: ignore
        table_container.tree.column(columns, width=75)
        return

    cols_len = 0
    for column in columns:
        table_container.tree.heading(
            column, text=columns_name[cols_len], anchor=tk.CENTER
        )
        table_container.tree.column(column, width=75)

        cols_len += 1


def setup_table_window(table_container, table_wind, columns_name):
    """Coloca los controles de la ventana del SimpleContainer"""
    table_container.tree.grid(row=0, column=0, columnspan=3, sticky="nsew")

    vscroll = tk.Scrollbar(
        table_wind, orient="vertical", command=table_container.tree.yview
    )
    table_container.tree.configure(yscrollcommand=vscroll.set)

    btn_1 = tk.Button(table_wind, text="Añadir")
    btn_1.bind(
        "<Button-1>",
        lambda _: spawn_add_window(table_container, columns_name),
    )
    btn_1.grid(row=1, column=0)

    btn_2 = tk.Button(table_wind, text="Borrar")
    btn_2.bind("<Button-1>", lambda _: delete_record_on_click(table_container))
    btn_2.grid(row=1, column=1)

    btn_3 = tk.Button(table_wind, text="Editar")
    btn_3.bind("<Button-1>", lambda _: spawn_edit_window(table_container, columns_name))
    btn_3.grid(row=1, column=2)


def show_table(
    table: str,
    table_values: list[str],
    message: str,
    columns: tuple[str, str] | str,
    columns_name: tuple[str, str] | str,
) -> None:
    """
    Crea una ventana con controles para editar una tabla sin columna de register_id

    Para estas tablas usamos un SimpleContainer en lugar del TreeContainer habitual."""
    from containers import SimpleContainer

    table_wind = tk.Toplevel()
    table_wind.title(message)

    table_container = SimpleContainer(
        table_wind,
        table,
        table_values,
        ttk.Treeview(table_wind, columns=columns),
        f"SELECT * FROM {table}",
    )

    create_table_tree(table_container, columns, columns_name)
    setup_table_window(table_container, table_wind, columns_name)

    core.fill_table(table_container)


def capture_report(container: TotalsContainer, register_id: int):
    """Captura los valores del TotalsContainer en el registro asociado"""
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
    containers: dict[str, TreeContainer | ProductsContainer],
    totals_container: TotalsContainer,
    register_id: int,
) -> None:
    """Vuelve a llenar todos los contenedores con el nuevo register_id"""
    core.fill_table(containers["machine_container"], register_id)
    core.fill_table(containers["replenish_container"], register_id)
    core.fill_table(containers["bussiness_container"], register_id)
    core.fill_table(containers["products_container"], register_id)

    totals_container.fill_entries(register_id)


def create_register(
    entries: dict[str, tk.Entry],
    containers: dict[str, TreeContainer | ProductsContainer],
    totals_container: TotalsContainer,
    root: tk.Toplevel,
):
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

    refill_containers(containers, totals_container, register_id[0][0])
    root.destroy()


def spawn_add_register_window(
    containers: dict[str, TreeContainer | ProductsContainer],
    totals_container: TotalsContainer,
):
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
            i[0]
            for i in core.request_data(
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
        command=lambda: create_register(entries, containers, totals_container, wind),
    ).grid(row=2, column=1)
