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
    """
    El contenedor simple adaptado para mostrar ventas de productos.
    No recomendaria crear varios de estos.
    """

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
    """Contiene las sumas totales de varios valores de las tablas"""

    def __init__(
        self,
        frame: tk.Frame,
        machine_container: TreeContainer,
        replenish_container: TreeContainer,
        bussiness_container: TreeContainer,
        products_container: ProductsContainer,
    ) -> None:
        self.machine_container = machine_container
        self.replenish_container = replenish_container
        self.bussiness_container = bussiness_container
        self.products_container = products_container

        # Y definimos nuestro total en un inicio
        self.total_expenses = tk.IntVar(frame, value=0)
        self.total_profits = tk.IntVar(frame, value=0)
        self.expected_funds = tk.IntVar(frame, value=0)
        self.balance = tk.IntVar(frame, value=0)
        self.difference = tk.IntVar(frame, value=0)

        # Definimos traces para cada uno de estos valores
        self.add_traces_to_vars()

        self.expenses_label = tk.LabelFrame(frame, text="Gastos")
        self.profits_label = tk.LabelFrame(frame, text="Ingresos")
        self.report_label = tk.LabelFrame(frame, text="Reporte de turno")

        self.machine_total = tk.Entry(
            self.expenses_label,
            state="readonly",
            textvariable=self.machine_container.total_var,
            width=10,
        )
        self.replenish_total = tk.Entry(
            self.expenses_label,
            state="readonly",
            textvariable=self.replenish_container.total_var,
            width=10,
        )
        self.bussiness_total = tk.Entry(
            self.expenses_label,
            state="readonly",
            textvariable=self.bussiness_container.total_var,
            width=10,
        )

        self.products_total = tk.Entry(
            self.profits_label,
            state="readonly",
            textvariable=self.products_container.total_var,
            width=10,
        )

        self.display_expected_funds = tk.Entry(
            self.report_label,
            state="readonly",
            textvariable=self.expected_funds,
            width=10,
        )

        self.display_reported_funds = tk.Entry(self.report_label, width=10)

        self.display_difference = tk.Entry(
            self.report_label,
            state="readonly",
            textvariable=self.difference,
            width=10,
        )

        self.display_balance = tk.Entry(
            self.report_label,
            state="readonly",
            textvariable=self.balance,
            width=10,
        )

        self.initial_fund = tk.Entry(self.profits_label, width=10)
        self.additional_fund = tk.Entry(self.profits_label, width=10)

        self.place_expenses()
        self.place_profits()
        self.place_report()

    def place_expenses(self):
        self.expenses_label.grid(row=0, column=0, padx=5)

        tk.Label(
            self.expenses_label, text="Maquinas (Premios)", anchor="w", width=19
        ).grid(row=1, column=0)

        tk.Label(
            self.expenses_label, text="Maquinas (Reposiciones)", anchor="w", width=19
        ).grid(row=2, column=0)

        tk.Label(
            self.expenses_label, text="Gastos miscelaneos", anchor="w", width=19
        ).grid(row=3, column=0)

        tk.Label(self.expenses_label, text="Total", anchor="w", width=19).grid(
            row=4, column=0
        )

        tk.Label(
            self.expenses_label, textvariable=self.total_expenses, anchor="w", width=10
        ).grid(row=4, column=1)

        self.machine_total.grid(row=1, column=1)
        self.replenish_total.grid(row=2, column=1)
        self.bussiness_total.grid(row=3, column=1)

    def place_profits(self):
        self.profits_label.grid(row=0, column=1, padx=5)

        tk.Label(self.profits_label, text="Fondo inicial", anchor="w", width=16).grid(
            row=1, column=0
        )
        self.initial_fund.bind(
            "<KeyRelease>", lambda *args: self.update_total_profits(*args)
        )
        self.initial_fund.grid(row=1, column=1)

        tk.Label(
            self.profits_label, text="Fondos adicionales", anchor="w", width=16
        ).grid(row=2, column=0)

        self.additional_fund.bind(
            "<KeyRelease>", lambda *args: self.update_total_profits(*args)
        )
        self.additional_fund.grid(row=2, column=1)

        tk.Label(
            self.profits_label, text="Ventas de productos", anchor="w", width=16
        ).grid(row=3, column=0)
        self.products_total.grid(row=3, column=1)

        tk.Label(self.profits_label, text="Total", anchor="w", width=16).grid(
            row=4, column=0
        )
        tk.Label(
            self.profits_label, textvariable=self.total_profits, anchor="w", width=10
        ).grid(row=4, column=1)

    def place_report(self):
        self.report_label.grid(row=0, column=2, padx=5)

        tk.Label(self.report_label, text="Fondo esperado", anchor="w", width=13).grid(
            row=1, column=0
        )
        self.display_expected_funds.grid(row=1, column=1)

        tk.Label(self.report_label, text="Fondo reportado", anchor="w", width=13).grid(
            row=2, column=0
        )
        self.display_reported_funds.grid(row=2, column=1)
        self.display_reported_funds.bind(
            "<KeyRelease>", lambda *args: self.update_final_reports(*args)
        )

        tk.Label(self.report_label, text="Diferencia", anchor="w", width=13).grid(
            row=3, column=0
        )
        self.display_difference.grid(row=3, column=1)

        tk.Label(self.report_label, text="Balance", anchor="w", width=13).grid(
            row=4, column=0
        )
        self.display_balance.grid(row=4, column=1)

    def add_traces_to_vars(self):
        self.machine_container.total_var.trace_add(
            "write", lambda *args: self.update_total_expenses(self.machine_total)
        )
        self.replenish_container.total_var.trace_add(
            "write", lambda *args: self.update_total_expenses(self.replenish_total)
        )
        self.bussiness_container.total_var.trace_add(
            "write", lambda *args: self.update_total_expenses(self.bussiness_total)
        )
        self.products_container.total_var.trace_add(
            "write", lambda *args: self.update_total_profits(*args)
        )

    def update_total_profits(self, *args):
        try:
            initial_funds = int(self.initial_fund.get())
        except ValueError:
            initial_funds = 0

        try:
            additional_funds = int(self.additional_fund.get())
        except ValueError:
            additional_funds = 0

        self.total_profits.set(
            self.products_container.total_var.get() + initial_funds + additional_funds
        )

        self.update_entry(self.products_total)
        self.update_final_reports(initial_funds)

    def update_total_expenses(self, entry):
        "Actualiza el valor total de los gastos"
        self.total_expenses.set(
            self.machine_container.total_var.get()
            + self.replenish_container.total_var.get()
            + self.bussiness_container.total_var.get()
        )

        self.update_entry(entry)
        self.update_final_reports()

    # FIXME: balance no funciona cuando escribimos en el campo del fondo inicial
    def update_final_reports(self, initial_funds=0, *args):
        try:
            reported_funds = int(self.display_reported_funds.get())
        except ValueError:
            reported_funds = 0

        self.expected_funds.set(self.total_profits.get() - self.total_expenses.get())
        self.difference.set(self.expected_funds.get() - reported_funds)
        self.balance.set(self.expected_funds.get() - initial_funds)

        self.update_entry(self.display_expected_funds)
        self.update_entry(self.display_difference)
        self.update_entry(self.display_balance)

    def update_entry(self, entry, *args):
        entry.config(state="normal")

        entry.config(state="readonly")


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

    total_expenses_frame.grid(row=1, column=1, columnspan=2)


window = tk.Tk()
entry_point(window)
window.mainloop()
