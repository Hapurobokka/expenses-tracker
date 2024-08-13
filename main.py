"""
Archivo principal del programa de momento. Ahora usamos clases como una persona normal.

Por Hapurobokka.
"""

import tkinter as tk
from tkinter import ttk
import core
import events as ev


REGISTER_ID = 10


class TreeContainer:
    """Clase que contiene un Frame con un Treeview y varios botones para operar con el"""

    def __init__(self, root, frame_text, table, table_values) -> None:
        # Valores que seran usados para hacer queries a la base de datos
        self.root = root
        self.table = table
        self.table_values = table_values

        # Esta query se usara para llenar el treeview que contiene este objeto
        self.fill_query = f"""
        SELECT {core.comma_separated_string(self.table_values)} 
        FROM {self.table}
        WHERE register_id = ?"""

        # Creamos un frame para acomodar todos los elementos del contenedor
        self.frame = tk.Frame(root)

        self.frame_label = tk.Label(self.frame, text=frame_text)
        self.frame_label.grid(row=0, column=0, columnspan=3)

        self.total_var = tk.IntVar(root, value=0)

        # Creamos el treeview

        # Añadiendo y configurando botones
        self.btn_add = tk.Button(self.frame, text="Añadir")
        self.btn_erase = tk.Button(self.frame, text="Eliminar")
        self.btn_edit = tk.Button(self.frame, text="Editar")

        self.setup_buttons(REGISTER_ID)

        # Definiendo el valor de la suma total de las columnas de la tabla

    def setup_tree(self, register_id):
        """Dispone las columnas y posición del Treeview, además de llenarlo por primera vez"""
        self.tree = ttk.Treeview(self.frame, columns=("name", "amount"))
        self.tree.grid(row=1, column=0, sticky="nsew", columnspan=3)

        self.tree.heading("#0", text="ID", anchor=tk.CENTER)
        self.tree.heading("name", text="Nombre", anchor=tk.CENTER)
        self.tree.heading("amount", text="Cantidad", anchor=tk.CENTER)

        self.tree.column("#0", width=40)
        self.tree.column("name", width=75)
        self.tree.column("amount", width=90)

        core.fill_table(self, register_id)

        self.setup_scrollbar()

    def setup_scrollbar(self):
        """Coloca una scrollbar en el Treeview del contenedor"""
        vscroll = tk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)

        vscroll.grid(row=1, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=vscroll.set)

    def setup_buttons(self, register_id):
        """Coloca los botones en su sitio y les asigna eventos"""
        self.btn_add.grid(row=2, column=0)
        self.btn_add.bind(
            "<Button-1>", lambda _: ev.spawn_add_window(self, self.root, register_id)
        )

        self.btn_edit.grid(row=2, column=1)
        self.btn_edit.bind(
            "<Button-1>", lambda _: ev.spawn_edit_window(self, self.root, register_id)
        )

        self.btn_erase.grid(row=2, column=2)
        self.btn_erase.bind(
            "<Button-1>", lambda _: ev.perform_erase_record(self, register_id)
        )

    def update_total_var(self, register_id):
        self.total_var.set(core.get_total_amount(self.table, "amount", register_id))


class ProductsContainer(TreeContainer):

    def __init__(self, root, frame_text, table, table_values) -> None:
        super().__init__(root, frame_text, table, table_values)
        self.fill_query = """
        SELECT ps.id, p.product_name, ps.in_product, ps.out_product, ps.profits
        FROM products_sales ps
        JOIN products p ON p.id = ps.product_id
        WHERE ps.register_id = ?
        """

    def setup_tree(self, register_id):
        """Dispone las columnas y posición del Treeview, además de llenarlo por primera vez"""
        self.tree = ttk.Treeview(
            self.frame,
            columns=["product_name", "in_product", "out_product", "profits"],
        )
        self.tree.grid(row=1, column=0, sticky="nsew", columnspan=3)

        self.tree.heading("#0", text="ID", anchor=tk.CENTER)
        self.tree.heading("product_name", text="Nombre", anchor=tk.CENTER)
        self.tree.heading("in_product", text="Inicial", anchor=tk.CENTER)
        self.tree.heading("out_product", text="Final", anchor=tk.CENTER)
        self.tree.heading("profits", text="Ganancias", anchor=tk.CENTER)

        self.tree.column("#0", width=40)
        self.tree.column("product_name", width=200)
        self.tree.column("in_product", width=70)
        self.tree.column("out_product", width=70)
        self.tree.column("profits", width=90)

        core.fill_table(self, register_id)

        self.setup_scrollbar()

    def setup_buttons(self, register_id):
        """Coloca los botones en su sitio y les asigna eventos"""
        self.btn_add.grid(row=2, column=0)
        self.btn_add.bind(
            "<Button-1>",
            lambda _: ev.spawn_product_report_window(self, self.root, register_id),
        )

        self.btn_edit.grid(row=2, column=1)
        self.btn_edit["text"] = "Mostrar productos"
        self.btn_edit.bind("<Button-1>", lambda _: ev.show_products(self, self.root))

        self.btn_erase.grid(row=2, column=2)
        self.btn_erase.bind(
            "<Button-1>", lambda _: ev.perform_erase_record(self, register_id)
        )

    def update_total_var(self, register_id):
        self.total_var.set(core.get_total_amount(self.table, "profits", register_id))


class TotalsContainer:

    def __init__(
        self,
        frame: tk.Frame,
        machine_container: TreeContainer,
        replenish_container: TreeContainer,
        bussiness_container: TreeContainer,
        products_container: ProductsContainer,
    ) -> None:
        self.frame = frame

        self.machine_container = machine_container
        self.replenish_container = replenish_container
        self.bussiness_container = bussiness_container
        self.products_container = products_container

        # Y definimos nuestro total en un inicio
        self.total_expenses = tk.IntVar(frame, value=0)

        # Definimos traces para cada uno de estos valores
        self.add_traces_to_vars()

        self.machine_total = tk.Entry(
            frame,
            state="readonly",
            textvariable=self.machine_container.total_var,
        )
        self.replenish_total = tk.Entry(
            frame,
            state="readonly",
            textvariable=self.replenish_container.total_var,
        )
        self.bussiness_total = tk.Entry(
            frame, state="readonly", textvariable=self.bussiness_container.total_var
        )

        self.products_total = tk.Entry(
            frame,
            state="readonly",
            textvariable=self.products_container.total_var,
        )

        self.initial_fund = tk.Entry(frame)
        self.additional_fund = tk.Entry(frame)

        self.place_expenses()
        self.place_profits()

    def place_expenses(self):
        tk.Label(self.frame, text="Gastos", anchor="center", width=19).grid(
            row=0, column=0, columnspan=2
        )

        tk.Label(self.frame, text="Maquinas (Premios)", anchor="w", width=19).grid(
            row=1, column=0
        )

        tk.Label(self.frame, text="Maquinas (Reposiciones)", anchor="w", width=19).grid(
            row=2, column=0
        )

        tk.Label(self.frame, text="Gastos miscelaneos", anchor="w", width=19).grid(
            row=3, column=0
        )

        tk.Label(self.frame, text="Total", anchor="w", width=19).grid(row=4, column=0)
        tk.Label(
            self.frame, textvariable=self.total_expenses, anchor="w", width=19
        ).grid(row=4, column=1)
        self.machine_total.grid(row=1, column=1)
        self.replenish_total.grid(row=2, column=1)
        self.bussiness_total.grid(row=3, column=1)

    def place_profits(self):
        tk.Label(self.frame, text="Ingresos", anchor="center", width=19).grid(
            row=0, column=2, columnspan=2
        )

        tk.Label(self.frame, text="Ventas de productos", anchor="w", width=19).grid(
            row=1, column=2
        )
        self.products_total.grid(row=1, column=3)

        tk.Label(self.frame, text="Fondo inicial", anchor="w", width=19).grid(
            row=2, column=2
        )
        self.initial_fund.grid(row=2, column=3)

        tk.Label(self.frame, text="Fondos adicionales", anchor="w", width=19).grid(
            row=3, column=2
        )
        self.additional_fund.grid(row=3, column=3)

    def add_traces_to_vars(self):
        self.machine_container.total_var.trace_add(
            "write", lambda *args: self.update_entry(self.machine_total, *args)
        )
        self.replenish_container.total_var.trace_add(
            "write",
            lambda *args: self.update_entry(self.replenish_total, *args),
        )
        self.bussiness_container.total_var.trace_add(
            "write",
            lambda *args: self.update_entry(self.bussiness_total, *args),
        )
        self.products_container.total_var.trace_add(
            "write", lambda *args: self.update_entry(self.products_total, *args)
        )

    def update_entry(self, entry, *args):
        entry.config(state="normal")

        entry.config(state="readonly")

        if entry == self.products_total:
            pass

        self.update_total_expenses()

    def update_total_expenses(self):
        "Actualiza el valor total de los gastos"
        self.total_expenses.set(
            self.machine_container.total_var.get()
            + self.replenish_container.total_var.get()
            + self.bussiness_container.total_var.get()
        )


def entry_point(root):
    """Punto de entrada para el programa"""
    root.title("Expense Tracker")

    total_expenses_frame = tk.Frame(root)

    machine_container = TreeContainer(
        root,
        "Premios de maquinas",
        "machine_table",
        ["id", "machine_name", "amount"],
    )
    replenish_container = TreeContainer(
        root,
        "Reposiciones de maquinas",
        "replenishments",
        ["id", "machine_name", "amount"],
    )
    bussiness_container = TreeContainer(
        root, "Gastos del negocio", "expenses", ["id", "concept", "amount"]
    )

    products_container = ProductsContainer(
        root,
        "Productos vendidos",
        "products_sales",
        ["id", "product_id", "in_product", "out_product", "profits"],
    )

    totals_container = TotalsContainer(
        total_expenses_frame,
        machine_container,
        replenish_container,
        bussiness_container,
        products_container,
    )

    machine_container.setup_tree(REGISTER_ID)
    replenish_container.setup_tree(REGISTER_ID)
    bussiness_container.setup_tree(REGISTER_ID)
    products_container.setup_tree(REGISTER_ID)

    machine_container.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    replenish_container.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    bussiness_container.frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    products_container.frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    totals_container.frame.grid(row=1, column=1)


window = tk.Tk()
entry_point(window)
window.mainloop()
