"""
Eventos para cuando pulsemos un bóton. Odio escribir interfaces gráficas.

Creado por Hapurobokka
"""

import re
import tkinter
from tkinter import ttk
import core


def validate_fields(fields: list):
    """Valida que todos los elementos de la lista tengan una longitud diferente a 0"""
    return all(lambda x: len(x) != 0 for x in fields)


def perform_add_record(container, en_name, en_amount, register_id=None):
    """Realiza la transacción de añadir un elemento a una tabla"""
    if not validate_fields([en_name.get(), en_amount.get()]):
        return

    record_name = en_name.get().upper()
    try:
        record_amount = int(en_amount.get())
    except ValueError:
        return

    if container["table"] == "products":
        core.create_record(
            container["table"],
            container["table_values"][1:],
            (record_name, record_amount),
        )
    else:
        core.create_record(
            container["table"],
            ["register_id", *container["table_values"][1:]],
            (register_id, record_name, record_amount),
        )

    core.fill_table(container, container["fill_query"], register_id)

    en_name.delete(0, tkinter.END)
    en_amount.delete(0, tkinter.END)



def check_valid_selection(tree: ttk.Treeview):
    """Revisa si hay un elemento seleccionado en el Treeview pasado como argumento"""
    try:
        selected_item = tree.selection()
        _ = tree.item(selected_item)["values"][0]  # type: ignore
    except IndexError:
        return False

    return True


def erase_record(container, register_id=None):
    """Borra una entrada de la lista"""
    if not check_valid_selection(container["tree"]):
        return

    record_id = container["tree"].item(container["tree"].selection())["text"]

    core.delete_record(container["table"], "id", record_id)
    core.fill_table(container, container["fill_query"], register_id)


def perform_alter_record(edit_wind, container, record_id, buttons, register_id=None):
    """Realiza la transaccón de editar un elemento en la tabla"""
    if not validate_fields([buttons[0].get(), buttons[1].get()]):
        return

    new_name = buttons[0].get().upper()
    try:
        new_amount = int(buttons[1].get())
    except ValueError:
        return

    query = f"""UPDATE {container["table"]}
    SET {container["table_values"][1]} = ?, {container["table_values"][2]} = ? 
    WHERE id = ?"""

    core.run_query(query, (new_name, new_amount, record_id))
    edit_wind.destroy()

    core.fill_table(container, container["fill_query"], register_id)


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


def add_products_record(combo, fields, tree, register_id):
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

    query = """
    SELECT ps.id, p.product_name, ps.in_product, ps.out_product, ps.profits
    FROM products_sales ps
    JOIN products p ON p.id = ps.product_id
    WHERE ps.register_id = ?
    """

    core.fill_table(tree, query, register_id)


def recur_erase_record(container, assoc_container, register_id):
    """
    Elimina una entrada de una 'tabla superior' (una que no posee registros de turno)
    y todas sus entradas de forma recursiva de otras tablas
    """
    if not check_valid_selection(container["tree"]):
        return

    record_id = container["tree"].item(container["tree"].selection())["text"]

    core.delete_record(container["table"], "id", record_id)
    core.delete_record(assoc_container["table"], "product_id", record_id)

    core.fill_table(container, container["fill_query"])
    core.fill_table(assoc_container, assoc_container["fill_query"], register_id)
