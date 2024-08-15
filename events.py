"""
Eventos para cuando pulsemos un bóton. Odio escribir interfaces gráficas.

Creado por Hapurobokka
"""

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
import core


REGISTER_ID = 10


@dataclass
class SimpleContainer:
    table: str
    table_values: list[str]
    tree: ttk.Treeview
    fill_query: str


def validate_number_input(action, value_if_allowed):
    if value_if_allowed.isdigit():
        return True

    return False


def validate_fields(fields: list):
    """Valida que todos los elementos de la lista tengan una longitud diferente a 0"""
    return all(len(x) != 0 for x in fields)


def perform_add_record(container, en_name, en_amount, register_id=None):
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


def check_valid_selection(tree: ttk.Treeview):
    """Revisa si hay un elemento seleccionado en el Treeview pasado como argumento"""
    try:
        selected_item = tree.selection()
        _ = tree.item(selected_item)["values"][0]  # type: ignore
    except IndexError:
        return False

    return True


def perform_erase_record(container, register_id=None):
    """Borra una entrada de la lista"""
    if not check_valid_selection(container.tree):
        return

    record_id = container.tree.item(container.tree.selection())["text"]

    core.delete_record(container.table, "id", record_id)
    core.fill_table(container, register_id)


def perform_alter_record(edit_wind, container, record_id, buttons, register_id=None):
    """Realiza la transaccón de editar un elemento en la tabla"""
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


def get_profits(combo, fields):
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


def create_profits(combo, entry, entry_var, fields):
    """Muestra la cantidad de ingresos que se van a obtener de la venta de
    cierta cantidad de productos"""
    if not validate_fields([combo.get(), fields[0].get(), fields[1].get()]):
        return

    profits = get_profits(combo, fields)

    entry.config(state="normal")
    entry_var.set(profits)
    entry.config(state="readonly")


def add_products_record(combo, fields, container, register_id):
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


def spawn_product_report_window(container, root, register_id):
    """Crea la ventana que permite añadir un reporte de ventas de un producto"""
    query = "SELECT product_name FROM products"

    new_win = tk.Toplevel(root)

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

    frozen_var = tk.StringVar(new_win, value="0")
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


def recur_erase_record(container, assoc_container, register_id):
    """
    Elimina una entrada de una 'tabla superior' (una que no posee registros de turno)
    y todas sus entradas de forma recursiva de otras tablas
    """
    if not check_valid_selection(container.tree):
        return

    record_id = container.tree.item(container.tree.selection())["text"]

    core.delete_record(container.table, "id", record_id)
    core.delete_record(assoc_container.table, "product_id", record_id)

    core.fill_table(container)
    core.fill_table(assoc_container, register_id)


def spawn_add_window(container, root, register_id=None):
    """Crea una ventana que le pide al usuario los datos para añadir un dato a una tabla"""
    add_window = tk.Toplevel(root)
    add_window.title("Crear nuevo registro")

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


def spawn_edit_window(container, root, register_id=None):
    """Crea una ventana que permite editar una entrada de una tabla"""
    if not check_valid_selection(container.tree):
        return

    record_id = container.tree.item(container.tree.selection())["text"]
    old_name = container.tree.item(container.tree.selection())["values"][0]
    old_amount = container.tree.item(container.tree.selection())["values"][1]

    edit_wind = tk.Toplevel(root)
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


def show_products(assoc_container, root: tk.Tk):
    """Crea una nueva ventana que muestra que productos hay disponibles en la base de datos"""
    product_wind = tk.Toplevel(root)
    product_wind.title("Lista de productos en venta")

    product_wind_container = SimpleContainer(
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
        lambda _: spawn_add_window(product_wind_container, root),
    )
    btn_1.grid(row=1, column=0)

    btn_2 = tk.Button(product_wind, text="Borrar")
    btn_2.bind(
        "<Button-1>",
        lambda _: recur_erase_record(
            product_wind_container,
            assoc_container,
            REGISTER_ID,
        ),
    )
    btn_2.grid(row=1, column=1)

    btn_3 = tk.Button(product_wind, text="Editar")
    btn_3.bind("<Button-1>", lambda _: spawn_edit_window(root, product_wind_container))
    btn_3.grid(row=1, column=2)

    core.fill_table(product_wind_container)
