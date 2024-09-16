"""
Definiciones de clase en otro lugar para que todo sirva bien

Por Hapurobokka
"""

from dataclasses import dataclass

import tkinter as tk
from tkinter import ttk
import core
import events as ev
from stacks import DisplayStack


class TreeContainer:
    """Clase que contiene un Frame con un Treeview y varios botones para operar con el"""

    def __init__(self, register_id, root, frame_text, table, table_values) -> None:
        # Valores que seran usados para hacer queries a la base de datos
        self.table = table
        self.table_values = table_values

        # Esta query se usara para llenar el treeview que contiene este objeto
        self.fill_query = f"""
        SELECT {core.comma_separated_string(self.table_values)}
        FROM {self.table}
        WHERE register_id = ?"""

        # Creamos un frame para acomodar todos los elementos del contenedor
        self.frame = tk.Frame(root)

        # Creamos un frame label que es solo una label literalmente
        tk.Label(self.frame, text=frame_text).grid(row=0, column=0, columnspan=3)

        self.total_var = tk.IntVar(root, value=0)

        # Creamos el treeview
        self.tree = ttk.Treeview(self.frame, columns=("name", "amount"))

        # Añadiendo y configurando botones
        self.buttons = {
            "btn_add": tk.Button(self.frame, text="Añadir"),
            "btn_erase": tk.Button(self.frame, text="Eliminar"),
            "btn_edit": tk.Button(self.frame, text="Editar"),
        }

        self.setup_buttons(register_id)

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
        self.buttons["btn_add"].grid(row=2, column=0)
        self.buttons["btn_add"].bind(
            "<Button-1>", lambda _: ev.spawn_add_window(self, register_id)
        )

        self.buttons["btn_edit"].grid(row=2, column=1)
        self.buttons["btn_edit"].bind(
            "<Button-1>", lambda _: ev.spawn_edit_window(self, register_id)
        )

        self.buttons["btn_erase"].grid(row=2, column=2)
        self.buttons["btn_erase"].bind(
            "<Button-1>", lambda _: ev.delete_record_on_click(self, register_id)
        )

    def update_total_var(self, register_id):
        """Actualiza el valor de la variable que cuenta el total de la tabla"""
        self.total_var.set(core.get_total_amount(self.table, "amount", register_id))


class ProductsContainer(TreeContainer):
    """
    El contenedor simple adaptado para mostrar ventas de productos.
    No recomendaria crear varios de estos.
    """

    def __init__(self, register_id, root, frame_text, table, table_values) -> None:
        super().__init__(register_id, root, frame_text, table, table_values)
        self.frame_text = "Productos vendidos"
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
        self.buttons["btn_add"].grid(row=2, column=0)
        self.buttons["btn_add"].bind(
            "<Button-1>",
            lambda _: ev.spawn_product_report_window(self, register_id),
        )

        self.buttons["btn_edit"].grid(row=2, column=1)
        self.buttons["btn_edit"]["text"] = "Mostrar productos"
        self.buttons["btn_edit"].bind(
            "<Button-1>",
            lambda _: ev.show_table(
                "products",
                ["id", "product_name", "price"],
                "Ver productos en venta",
                ("name", "price"),
                ("Nombre", "Precio"),
            ),
        )

        self.buttons["btn_erase"].grid(row=2, column=2)
        self.buttons["btn_erase"].bind(
            "<Button-1>", lambda _: ev.delete_record_on_click(self, register_id)
        )

    def update_total_var(self, register_id):
        self.total_var.set(core.get_total_amount(self.table, "profits", register_id))


class TotalsContainer:
    """Contiene las sumas totales de varios valores de las tablas"""

    def __init__(
        self,
        register_id: int,
        frame: tk.Frame,
        machine_variable: tk.IntVar,
        replenish_variable: tk.IntVar,
        bussiness_variable: tk.IntVar,
        products_variable: tk.IntVar,
    ) -> None:
        self.frame = frame

        self.containers_variables = {
            "machine_variable": machine_variable,
            "replenish_variable": replenish_variable,
            "bussiness_variable": bussiness_variable,
            "products_variable": products_variable,
        }

        # Y definimos nuestro total en un inicio

        self.total_variables = {
            "total_expenses": tk.IntVar(frame, value=0),
            "total_profits": tk.IntVar(frame, value=0),
            "expected_funds": tk.IntVar(frame, value=0),
            "balance": tk.IntVar(frame, value=0),
            "difference": tk.IntVar(frame, value=0),
        }

        # Definimos traces para cada uno de estos valores
        self.add_traces_to_vars()

        self.expenses_stack = DisplayStack(
            self.frame,
            "Gastos",
            [
                {
                    "name": "machine_prices",
                    "type": "LabelEntryPair",
                    "label_text": "Maquinas (Premios)",
                    "state": "readonly",
                    "textvariable": self.containers_variables["machine_variable"],
                    "position": [(0, 0), (0, 1)],
                },
                {
                    "name": "machine_replenishments",
                    "type": "LabelEntryPair",
                    "label_text": "Maquinas (Reposiciones)",
                    "state": "readonly",
                    "textvariable": self.containers_variables["replenish_variable"],
                    "position": [(1, 0), (1, 1)],
                },
                {
                    "name": "misc_expenses",
                    "type": "LabelEntryPair",
                    "label_text": "Gastos Miscelaneos",
                    "state": "readonly",
                    "textvariable": self.containers_variables["bussiness_variable"],
                    "position": [(2, 0), (2, 1)],
                },
                {
                    "name": "total_expenses",
                    "type": "LabelPair",
                    "label_text": "Total",
                    "textvariable": self.total_variables["total_expenses"],
                    "position": [(3, 0), (3, 1)],
                },
            ],
        )

        self.profits_stack = DisplayStack(
            self.frame,
            "Ingresos",
            [
                {
                    "name": "initial_funds",
                    "type": "LabelEntryPair",
                    "label_text": "Fondo inicial",
                    "state": "normal",
                    "textvariable": 1,
                    "position": [(0, 0), (0, 1)],
                },
                {
                    "name": "additional_funds",
                    "type": "LabelEntryPair",
                    "label_text": "Fondo adicional",
                    "state": "normal",
                    "textvariable": 2,
                    "position": [(1, 0), (1, 1)],
                },
                {
                    "name": "products_profits",
                    "type": "LabelEntryPair",
                    "label_text": "Ventas de productos",
                    "state": "readonly",
                    "textvariable": self.containers_variables["bussiness_variable"],
                    "position": [(2, 0), (2, 1)],
                },
                {
                    "name": "total_profits",
                    "type": "LabelPair",
                    "label_text": "Total",
                    "textvariable": self.total_variables["total_profits"],
                    "position": [(3, 0), (3, 1)],
                },
            ],
            label_width=16,
        )

        self.report_stack = DisplayStack(
            self.frame,
            "Ingresos",
            [
                {
                    "name": "expected_funds",
                    "type": "LabelEntryPair",
                    "label_text": "Fondo esperado",
                    "state": "readonly",
                    "textvariable": self.total_variables["expected_funds"],
                    "position": [(0, 0), (0, 1)],
                },
                {
                    "name": "reported_funds",
                    "type": "LabelEntryPair",
                    "label_text": "Fondo reportado",
                    "state": "normal",
                    "textvariable": 3,
                    "position": [(1, 0), (1, 1)],
                },
                {
                    "name": "difference",
                    "type": "LabelEntryPair",
                    "label_text": "Diferencia",
                    "state": "readonly",
                    "textvariable": self.total_variables["difference"],
                    "position": [(2, 0), (2, 1)],
                },
                {
                    "name": "balance",
                    "type": "LabelEntryPair",
                    "label_text": "Balance",
                    "state": "readonly",
                    "textvariable": self.total_variables["balance"],
                    "position": [(3, 0), (3, 1)],
                },
            ],
            label_width=13,
        )

        btn_capture = tk.Button(frame, text="Capturar datos")
        btn_capture.grid(row=1, column=1, pady=5)
        btn_capture.bind("<Button-1>", lambda *_: ev.capture_report(self, register_id))

        self.profits_stack.stack["initial_funds"].element_2.bind(
            "<KeyRelease>", lambda *_: self.update_total_profits()
        )
        self.profits_stack.stack["additional_funds"].element_2.bind(
            "<KeyRelease>", lambda *_: self.update_total_profits()
        )
        self.report_stack.stack["reported_funds"].element_2.bind(
            "<KeyRelease>", lambda *_: self.update_final_reports()
        )

        self.expenses_stack.label_frame.grid(row=0, column=0, padx=5)
        self.profits_stack.label_frame.grid(row=0, column=1, padx=5)
        self.report_stack.label_frame.grid(row=0, column=2, padx=5)

    def add_traces_to_vars(self):
        """Añade callbacks a distintas variables de TKInter para que se actualicen al toque"""
        self.containers_variables["machine_variable"].trace_add(
            "write",
            lambda *_: self.update_total_expenses(
                self.expenses_stack.stack["machine_prices"].element_2
            ),
        )
        self.containers_variables["replenish_variable"].trace_add(
            "write",
            lambda *_: self.update_total_expenses(
                self.expenses_stack.stack["machine_replenishments"].element_2
            ),
        )
        self.containers_variables["bussiness_variable"].trace_add(
            "write",
            lambda *_: self.update_total_expenses(
                self.expenses_stack.stack["misc_expenses"].element_2
            ),
        )
        self.containers_variables["products_variable"].trace_add(
            "write", lambda *_: self.update_total_profits()
        )

    def update_total_profits(self):
        """Actualiza los totales de los ingresos del producto"""
        try:
            initial_funds = int(
                self.profits_stack.stack["initial_funds"].element_2.get()
            )
        except ValueError:
            initial_funds = 0

        try:
            additional_funds = int(
                self.profits_stack.stack["additional_funds"].element_2.get()
            )
        except ValueError:
            additional_funds = 0

        self.total_variables["total_profits"].set(
            self.containers_variables["products_variable"].get()
            + initial_funds
            + additional_funds
        )

        self.update_entry(self.profits_stack.stack["products_profits"].element_2)
        self.update_final_reports()

    def update_total_expenses(self, entry):
        "Actualiza el valor total de los gastos"
        self.total_variables["total_expenses"].set(
            self.containers_variables["machine_variable"].get()
            + self.containers_variables["replenish_variable"].get()
            + self.containers_variables["bussiness_variable"].get()
        )

        self.update_entry(entry)
        self.update_final_reports()

    def update_final_reports(self):
        """Actualiza la sección de reportes finales de la ventana principal"""
        try:
            reported_funds = int(
                self.report_stack.stack["reported_funds"].element_2.get()
            )
        except ValueError:
            reported_funds = 0

        try:
            initial_funds = int(
                self.profits_stack.stack["initial_funds"].element_2.get()
            )
        except ValueError:
            initial_funds = 0

        self.total_variables["expected_funds"].set(
            self.total_variables["total_profits"].get()
            - self.total_variables["total_expenses"].get()
        )
        self.total_variables["difference"].set(
            reported_funds - self.total_variables["expected_funds"].get()
        )
        self.total_variables["balance"].set(
            self.total_variables["expected_funds"].get() - initial_funds
        )

        self.update_entry(self.report_stack.stack["expected_funds"].element_2)
        self.update_entry(self.report_stack.stack["difference"].element_2)
        self.update_entry(self.report_stack.stack["balance"].element_2)

    def fill_entries(self, register_id: int) -> None:
        """
        Fills the text fields in our container with data captured for the current
        register id"""

        fill_query = """
        SELECT initial_funds, extra_funds, reported_funds
        FROM daily_reports
        WHERE register_id = ?
        """

        self.profits_stack.stack["initial_funds"].element_2.delete(0, tk.END)
        self.profits_stack.stack["additional_funds"].element_2.delete(0, tk.END)
        self.report_stack.stack["reported_funds"].element_2.delete(0, tk.END)

        self.update_total_profits()

        try:
            entry_values = core.request_data(fill_query, (register_id,))[0]
        except IndexError:
            return

        if entry_values == ():
            return

        self.profits_stack.stack["initial_funds"].element_2.insert(0, entry_values[0])
        self.profits_stack.stack["additional_funds"].element_2.insert(
            0, entry_values[1]
        )
        self.report_stack.stack["reported_funds"].element_2.insert(0, entry_values[2])

    def update_entry(self, entry):
        """Actualiza una entrada de solo lectura"""
        entry.config(state="normal")

        entry.config(state="readonly")


@dataclass
class SimpleContainer:
    """Clase básica para almacenar contendores simples"""

    root_win: tk.Tk | tk.Toplevel
    table: str
    table_values: list[str]
    tree: ttk.Treeview
    fill_query: str
