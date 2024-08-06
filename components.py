"""
Este archivo contiene las definiciones de la mayoría de contenidos gráficos del
programa. Creo.

Hecho por Hapurobokka.
"""

import tkinter
from tkinter import ttk
import events as ev
import core


REGISTER_ID = 10


def spawn_product_report_window(root, tree):
    """Crea la ventana que permite añadir un reporte de ventas de un producto"""
    query = 'SELECT product_name FROM products'

    new_win = tkinter.Toplevel(root)

    tkinter.Label(new_win, text="Producto").grid(row=0, column=0)
    tkinter.Label(new_win, text="Entrada").grid(row=0, column=1)
    tkinter.Label(new_win, text="Salida").grid(row=0, column=2)
    tkinter.Label(new_win, text="Ingresos").grid(row=0, column=3)

    combo = ttk.Combobox(new_win, values=[i[0] for i in core.request_data(query)])
    combo.grid(row=1, column=0)

    entry_1 = tkinter.Entry(new_win)
    entry_1.grid(row=1, column=1)
    entry_2 = tkinter.Entry(new_win)
    entry_2.grid(row=1, column=2)

    frozen_var = tkinter.StringVar(new_win, value="0")
    frozen = tkinter.Entry(new_win, textvariable=frozen_var, state="readonly")
    frozen.grid(row=1, column=3)

    add_button = tkinter.Button(new_win, text="Añadir")
    add_button.grid(row=3, column=1, sticky="ew", columnspan=2, pady=10)

    combo.bind(
        "<FocusOut>", lambda _: ev.create_profits(combo, frozen, frozen_var, [entry_1, entry_2])
    )
    entry_1.bind(
        "<FocusOut>", lambda _: ev.create_profits(combo, frozen, frozen_var, [entry_1, entry_2])
    )
    entry_2.bind(
        "<FocusOut>", lambda _: ev.create_profits(combo, frozen, frozen_var, [entry_1, entry_2])
    )

    add_button.bind(
        "<Button-1>", lambda _: ev.add_products_record(combo, [entry_1, entry_2], tree, REGISTER_ID)
    )


def spawn_edit_window(root, tree_container, register_id):
    """Crea una ventana que permite editar una entrada de una tabla"""
    if not ev.check_valid_selection(tree_container["tree"]):
        return

    record_id = tree_container["tree"].item(tree_container["tree"].selection())['text']
    old_name = tree_container["tree"].item(tree_container["tree"].selection())['values'][0]
    old_amount = tree_container["tree"].item(tree_container["tree"].selection())['values'][1]

    edit_wind = tkinter.Toplevel(root)
    edit_wind.title("Editar registro")

    tkinter.Label(edit_wind, text="Nombre anterior: ").grid(row=0, column=1)
    tkinter.Entry(edit_wind,
                  textvariable=tkinter.StringVar(edit_wind, value=old_name),
                  state="readonly").grid(row=0, column=2)

    tkinter.Label(edit_wind, text="Nuevo nombre: ").grid(row=1, column=1)
    new_name = tkinter.Entry(edit_wind)
    new_name.grid(row=1, column=2)

    tkinter.Label(edit_wind, text="Old Price: ").grid(row=2, column=1)
    tkinter.Entry(edit_wind,
                  textvariable=tkinter.StringVar(edit_wind, value=old_amount),
                  state="readonly").grid(row=2, column=2)


    tkinter.Label(edit_wind, text="New Price: ").grid(row=3, column=1)
    new_amount = tkinter.Entry(edit_wind)
    new_amount.grid(row=3, column=2)

    btn_edit = tkinter.Button(edit_wind, text="Editar")
    btn_edit.bind(
        "<Button-1>",
        lambda _ : ev.perform_alter_record(
            edit_wind, tree_container, record_id, [new_name, new_amount], register_id
        ))
    btn_edit.grid(row=4, column=2, sticky="we")


def spawn_add_window(root, tree_container, register_id=None):
    """Crea una ventana que le pide al usuario los datos para añadir un dato a una tabla"""
    add_window = tkinter.Toplevel(root)
    add_window.title("Crear nuevo registro")

    tkinter.Label(add_window, text="Nombre").pack()

    en_name = tkinter.Entry(add_window)
    en_name.focus()
    en_name.pack()

    tkinter.Label(add_window, text="Cantidad").pack()

    en_amount = tkinter.Entry(add_window)
    en_amount.pack()

    add_button = tkinter.Button(add_window, text="Añadir")
    add_button.bind("<Button-1>", lambda _: ev.perform_add_record(
        tree_container, en_name, en_amount, register_id
    ))
    add_button.pack()


def show_products(root, assoc_container):
    """Crea una nueva ventana que muestra que productos hay disponibles en la base de datos"""

    fill_query = 'SELECT * FROM products'

    product_wind = tkinter.Toplevel(root)
    product_wind.title("Lista de productos en venta")

    products_tree = ttk.Treeview(product_wind, columns=["name", "price"])

    products_tree.heading("#0", text="ID", anchor=tkinter.CENTER)
    products_tree.heading("name", text="Nombre", anchor=tkinter.CENTER)
    products_tree.heading("price", text="Precio", anchor=tkinter.CENTER)

    products_tree.column("#0", width=40)
    products_tree.column("name", width=75)
    products_tree.column("price", width=90)
    products_tree.grid(row=0, column=0, columnspan=3, sticky="nsew")

    vscroll = tkinter.Scrollbar(product_wind,
                                orient="vertical",
                                command=products_tree.yview)

    vscroll.grid(row=0, column=4, sticky="ns")
    products_tree.configure(yscrollcommand=vscroll.set)

    btn_1 = tkinter.Button(product_wind, text="Añadir")
    btn_1.bind(
        "<Button-1>",
        lambda _: spawn_add_window(
            root,
            {
                "table": "products",
                "table_values": ["product_name", "price"],
                "tree": products_tree,
                "fill_query": fill_query
            }
        )
    )
    btn_1.grid(row=1, column=0)

    btn_2 = tkinter.Button(product_wind, text="Borrar")
    btn_2.bind(
        "<Button-1>",
        lambda _: ev.recur_erase_record(
            {
                "table": "products",
                "table_values": ["product_name", "price"],
                "tree": products_tree,
                "fill_query": fill_query
            },
            assoc_container,
            REGISTER_ID
        )
    )
    btn_2.grid(row=1, column=1)

    btn_3 = tkinter.Button(product_wind, text="Editar")
    btn_3.grid(row=1, column=2)

    core.fill_table(products_tree, fill_query)


def setup_products_tree(tree, fill_query):
    """Coloca el arbol de productos de manera correcta en la ventana"""
    tree.grid(row=1, column=0)

    tree.heading("#0", text="ID", anchor=tkinter.CENTER)
    tree.heading("product_name", text="Nombre", anchor=tkinter.CENTER)
    tree.heading("in_product", text="Inicial", anchor=tkinter.CENTER)
    tree.heading("out_product", text="Final", anchor=tkinter.CENTER)
    tree.heading("profits", text="Ganancias", anchor=tkinter.CENTER)

    tree.column("#0", width=40)
    tree.column("product_name", width=200)
    tree.column("in_product", width=70)
    tree.column("out_product", width=70)
    tree.column("profits", width=90)

    core.fill_table(tree, fill_query, REGISTER_ID)


def setup_simple_tree(tree, fill_query):
    """Define todos los elementos de un arbol simple"""
    tree.grid(row=1, column=0, sticky="nsew", columnspan=3)

    tree.heading("#0", text="ID", anchor=tkinter.CENTER)
    tree.heading("name", text="Nombre", anchor=tkinter.CENTER)
    tree.heading("amount", text="Cantidad", anchor=tkinter.CENTER)

    tree.column("#0", width=40)
    tree.column("name", width=75)
    tree.column("amount", width=90)

    core.fill_table(tree, fill_query, REGISTER_ID)


def create_products_container(root):
    """Crea un contenedor para la tabla de ventas de productos"""
    container = {}

    container["fill_query"] = """
    SELECT ps.id, p.product_name, ps.in_product, ps.out_product, ps.profits
    FROM products_sales ps
    JOIN products p ON p.id = ps.product_id
    WHERE ps.register_id = ?
    """

    container["table"] = 'products_sales'
    container["table_values"] = ['id', 'product_id',
                                 'in_product', 'out_product', 'profits']

    container["frame"] = tkinter.Frame(root)

    container["label"] = tkinter.Label(container["frame"], text="Venta de productos")
    container["label"].grid(row=0, column=0, columnspan=4)

    container["tree"] = ttk.Treeview(container["frame"], columns=["product_name", "in_product",
                                                                  "out_product", "profits"])
    container["tree"].grid(row=0, column=1, columnspan=4)

    vscroll = tkinter.Scrollbar(container["frame"],
                                orient="vertical",
                                command=container["tree"].yview)

    vscroll.grid(row=1, column=4, sticky="ns")
    container["tree"].configure(yscrollcommand=vscroll.set)

    container["buttons"] = []

    container["buttons"].append(tkinter.Button(container["frame"], text="Añadir"))
    container["buttons"].append(tkinter.Button(container["frame"], text="Eliminar"))
    container["buttons"].append(tkinter.Button(container["frame"], text="Ver productos"))

    container["buttons"][0].grid(row=2, column=0, sticky="ew")
    container["buttons"][1].grid(row=2, column=1, sticky="ew")
    container["buttons"][2].grid(row=2, column=2, sticky="ew")

    container["buttons"][0].bind(
        "<Button-1>", lambda _: spawn_product_report_window(root, container["tree"])
    )
    container["buttons"][1].bind("<Button-1>",
                                      lambda _: ev.erase_record(container, REGISTER_ID))
    container["buttons"][2].bind("<Button-1>", lambda _: show_products(root, container))

    setup_products_tree(container["tree"], container["fill_query"])

    return container


def create_tree_container(root, frame_text, table, table_values):
    """Crea un contenedor para un arbol simple"""
    container = {}
    container["fill_query"] = f"""
    SELECT {core.comma_separated_string(table_values)} 
    FROM {table}
    WHERE register_id = ?"""

    container["table"] = table
    container["table_values"] = table_values

    container["frame"] = tkinter.Frame(root)

    container["label"] = tkinter.Label(container["frame"], text=frame_text)
    container["label"].grid(row=0, column=0, columnspan=3)

    container["tree"] = ttk.Treeview(container["frame"], columns=["name", "amount"])
    container["tree"].grid(row=0, column=1, columnspan=3)

    vscroll = tkinter.Scrollbar(
        container["frame"],
        orient="vertical",
        command=container["tree"].yview
    )

    vscroll.grid(row=1, column=3, sticky="ns")
    container["tree"].configure(yscrollcommand=vscroll.set)

    container["buttons"] = []

    container["buttons"].append(tkinter.Button(container["frame"], text="Añadir"))
    container["buttons"].append(tkinter.Button(container["frame"], text="Eliminar"))
    container["buttons"].append(tkinter.Button(container["frame"], text="Editar"))

    container["buttons"][0].grid(row=2, column=0)
    container["buttons"][1].grid(row=2, column=1)
    container["buttons"][2].grid(row=2, column=2)

    container["buttons"][0].bind(
        "<Button-1>", lambda _: spawn_add_window(root, container, REGISTER_ID
     ))
    container["buttons"][1].bind(
        "<Button-1>", lambda _: ev.erase_record(container, REGISTER_ID)
    )
    container["buttons"][2].bind(
        "<Button-1>", 
        lambda _: spawn_edit_window(root, container, REGISTER_ID
    ))

    setup_simple_tree(container["tree"], container["fill_query"])

    return container


def entry_point(root):
    """Punto de entrada para el programa"""
    root.title("Expense Tracker")

    machine_container = create_tree_container(root,
                                              "Premios de maquinas",
                                              'machine_table',
                                              ['id', 'machine_name', 'amount'])
    replenish_container = create_tree_container(root,
                                                "Reposiciones de maquinas",
                                                'replenishments',
                                                ['id', 'machine_name', 'amount'])
    expenses_container = create_tree_container(root,
                                               "Gastos",
                                               'expenses',
                                               ['id', 'concept', 'amount'])

    products_sales_container = create_products_container(root)

    machine_container["frame"].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    replenish_container["frame"].grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    expenses_container["frame"].grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    products_sales_container["frame"].grid(row=0, column=2, padx=10, pady=10, sticky="nsew")


window = tkinter.Tk()
entry_point(window)
window.mainloop()
