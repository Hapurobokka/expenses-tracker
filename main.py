"""
Archivo principal del programa de momento. Ahora usamos clases como una persona normal.

Por Hapurobokka.
"""

import tkinter as tk
from tkinter import ttk
import core
import events as ev
from dataclasses import dataclass


REGISTER_ID = 1


@dataclass
class LabelEntryPair:
    label: tk.Label
    entry: tk.Entry

    def place(self, label_pos, entry_pos):
        self.label.grid(row=label_pos[0], column=label_pos[1])
        self.entry.grid(row=entry_pos[0], column=entry_pos[1])


@dataclass
class LabelPair:
    label1: tk.Label
    label2: tk.Label

    def place(self, label1_pos, label2_pos):
        self.label1.grid(row=label1_pos[0], column=label1_pos[1])
        self.label2.grid(row=label2_pos[0], column=label2_pos[1])


class DisplayStack:

    def __init__(self, root, elements, label_width=19, entry_width=10):
        self.label_frame = tk.LabelFrame(root, text=elements[0])
        self.stack = []

        for elem in elements[1:]:
            pair = None

            if elem["type"] == "LabelEntryPair":
                label = tk.Label(
                    master=self.label_frame,
                    text=elem["label_text"],
                    anchor="w",
                    width=label_width,
                )

                entry = tk.Entry(
                    master=self.label_frame,
                    state=elem["state"],
                    textvariable=elem["textvariable"],
                    width=entry_width,
                )

                pair = LabelEntryPair(label, entry)

            elif elem["type"] == "LabelPair":
                label1 = tk.Label(
                    master=self.label_frame,
                    text=elem["label_text"],
                    anchor="w",
                    width=label_width,
                )

                label2 = tk.Label(
                    master=self.label_frame,
                    textvariable=elem["textvariable"],
                    anchor="w",
                    width=entry_width,
                )

                pair = LabelPair(label1, label2)

            if pair is not None:
                pair.place(elem["position"][0], elem["position"][1])
                self.stack.append(pair)


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
        self.tree = ttk.Treeview(self.frame, columns=("name", "amount"))

        # Añadiendo y configurando botones
        self.btn_add = tk.Button(self.frame, text="Añadir")
        self.btn_erase = tk.Button(self.frame, text="Eliminar")
        self.btn_edit = tk.Button(self.frame, text="Editar")

        self.setup_buttons(REGISTER_ID)

        # Definiendo el valor de la suma total de las columnas de la tabla

    def setup_tree(self, register_id):
        """Dispone las columnas y posición del Treeview, además de llenarlo por primera vez"""
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
        """Actualiza el valor de la variable que cuenta el total de la tabla"""
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
        self.frame = frame

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
        
        self.expenses_stack = DisplayStack(
            self.frame,
            [
                "Gastos",
                {
                    "type": "LabelEntryPair",
                    "label_text": "Maquinas (Premios)",
                    "state": "readonly",
                    "textvariable": machine_container.total_var,
                    "position": [(0, 0), (0, 1)],
                },
                {
                    "type": "LabelEntryPair",
                    "label_text": "Maquinas (Reposiciones)",
                    "state": "readonly",
                    "textvariable": replenish_container.total_var,
                    "position": [(1, 0), (1, 1)],
                },
                {
                    "type": "LabelEntryPair",
                    "label_text": "Gastos Miscelaneos",
                    "state": "readonly",
                    "textvariable": bussiness_container.total_var,
                    "position": [(2, 0), (2, 1)],
                },
                {
                    "type": "LabelPair",
                    "label_text": "Total",
                    "textvariable": self.total_expenses,
                    "position": [(3, 0), (3, 1)],
                },
            ]
        )

        self.profits_stack = DisplayStack(
            self.frame,
            [
                "Ingresos",
                {
                    "type": "LabelEntryPair",
                    "label_text": "Fondo inicial",
                    "state": "normal",
                    "textvariable": 1,
                    "position": [(0, 0), (0, 1)],
                },
                {
                    "type": "LabelEntryPair",
                    "label_text": "Fondo adicional",
                    "state": "normal",
                    "textvariable": 2,
                    "position": [(1, 0), (1, 1)],
                },
                {
                    "type": "LabelEntryPair",
                    "label_text": "Ventas de productos",
                    "state": "readonly",
                    "textvariable": products_container.total_var,
                    "position": [(2, 0), (2, 1)],
                },
                {
                    "type": "LabelPair",
                    "label_text": "Total",
                    "textvariable": self.total_profits,
                    "position": [(3, 0), (3, 1)],
                },
            ],
            label_width=16,
        )

        self.report_stack = DisplayStack(
            self.frame,
            [
                "Ingresos",
                {
                    "type": "LabelEntryPair",
                    "label_text": "Fondo esperado",
                    "state": "readonly",
                    "textvariable": self.expected_funds,
                    "position": [(0, 0), (0, 1)],
                },
                {
                    "type": "LabelEntryPair",
                    "label_text": "Fondo reportado",
                    "state": "normal",
                    "textvariable": 3,
                    "position": [(1, 0), (1, 1)],
                },
                {
                    "type": "LabelEntryPair",
                    "label_text": "Diferencia",
                    "state": "readonly",
                    "textvariable": self.difference,
                    "position": [(2, 0), (2, 1)],
                },
                {
                    "type": "LabelEntryPair",
                    "label_text": "Balance",
                    "state": "readonly",
                    "textvariable": self.balance,
                    "position": [(3, 0), (3, 1)],
                },
            ],
            label_width=13,
        )

        self.profits_stack.stack[0].entry.bind(
            "<KeyRelease>", self.update_total_profits
        )
        self.profits_stack.stack[1].entry.bind(
            "<KeyRelease>", self.update_total_profits
        )
        self.report_stack.stack[1].entry.bind("<KeyRelease>", self.update_final_reports)

    def add_traces_to_vars(self):
        """Añade callbacks a distintas variables de TKInter para que se actualicen al toque"""
        self.machine_container.total_var.trace_add(
            "write",
            lambda *args: self.update_total_expenses(
                self.expenses_stack.stack[0].entry
            ),
        )
        self.replenish_container.total_var.trace_add(
            "write",
            lambda *args: self.update_total_expenses(
                self.expenses_stack.stack[1].entry
            ),
        )
        self.bussiness_container.total_var.trace_add(
            "write",
            lambda *args: self.update_total_expenses(
                self.expenses_stack.stack[2].entry
            ),
        )
        self.products_container.total_var.trace_add("write", self.update_total_profits)

    def update_total_profits(self, *args):
        """Actualiza los totales de los ingresos del producto"""
        try:
            initial_funds = int(self.profits_stack.stack[0].entry.get())
        except ValueError:
            initial_funds = 0

        try:
            additional_funds = int(self.profits_stack.stack[1].entry.get())
        except ValueError:
            additional_funds = 0

        self.total_profits.set(
            self.products_container.total_var.get() + initial_funds + additional_funds
        )

        self.update_entry(self.profits_stack.stack[2].entry)
        self.update_final_reports()

    def update_total_expenses(self, entry):
        "Actualiza el valor total de los gastos"
        self.total_expenses.set(
            self.machine_container.total_var.get()
            + self.replenish_container.total_var.get()
            + self.bussiness_container.total_var.get()
        )

        self.update_entry(entry)
        self.update_final_reports()

    def update_final_reports(self, *args):
        """Actualiza la sección de reportes finales de la ventana principal"""
        try:
            reported_funds = int(self.report_stack.stack[1].entry.get())
        except ValueError:
            reported_funds = 0

        try:
            initial_funds = int(self.profits_stack.stack[1].entry.get())
        except ValueError:
            initial_funds = 0

        self.expected_funds.set(self.total_profits.get() - self.total_expenses.get())
        self.difference.set(reported_funds - self.expected_funds.get())
        self.balance.set(self.expected_funds.get() - initial_funds)

        self.update_entry(self.report_stack.stack[0].entry)
        self.update_entry(self.report_stack.stack[2].entry)
        self.update_entry(self.report_stack.stack[3].entry)

    def update_entry(self, entry, *args):
        """Actualiza una entrada de solo lectura"""
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

    totals_container.frame.grid(row=1, column=1, columnspan=2)
    totals_container.expenses_stack.label_frame.grid(row=0, column=0, padx=5)
    totals_container.profits_stack.label_frame.grid(row=0, column=1, padx=5)
    totals_container.report_stack.label_frame.grid(row=0, column=2, padx=5)

window = tk.Tk()
entry_point(window)
window.mainloop()
