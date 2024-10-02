"""
La clase que define el contenedor de totales del turno.

Hecho por Hapurobokka.
"""

import tkinter as tk
from stacks import create_stack
from events import capture_report
from core import request_data

class TotalsContainer:
    """Contiene las sumas totales de varios valores de las tablas"""

    def __init__(
        self,
        register_id: int,
        machine_variable: tk.IntVar,
        replenish_variable: tk.IntVar,
        bussiness_variable: tk.IntVar,
        products_variable: tk.IntVar,
    ) -> None:
        self.frame = tk.Frame()

        self.containers_variables = {
            "machine_variable": machine_variable,
            "replenish_variable": replenish_variable,
            "bussiness_variable": bussiness_variable,
            "products_variable": products_variable,
        }

        self.total_variables = {
            "total_expenses": tk.IntVar(self.frame, value=0),
            "total_profits": tk.IntVar(self.frame, value=0),
            "expected_funds": tk.IntVar(self.frame, value=0),
            "balance": tk.IntVar(self.frame, value=0),
            "difference": tk.IntVar(self.frame, value=0),
        }

        # Definimos traces para cada uno de estos valores
        self.add_traces_to_vars()

        self.expenses_stack = create_stack(
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
            (0, 0)
        )

        self.profits_stack = create_stack(
            self.frame,
            "Ingresos",
            [
                {
                    "name": "initial_funds",
                    "type": "LabelEntryPair",
                    "label_text": "Fondo inicial",
                    "state": "normal",
                    "textvariable": None,
                    "position": [(0, 0), (0, 1)],
                },
                {
                    "name": "additional_funds",
                    "type": "LabelEntryPair",
                    "label_text": "Fondo adicional",
                    "state": "normal",
                    "textvariable": None,
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
            (0, 1),
            label_width=16,
        )

        self.report_stack = create_stack(
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
                    "textvariable": None,
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
            (0, 2),
            label_width=13,
        )

        btn_capture = tk.Button(self.frame, text="Capturar datos")
        btn_capture.grid(row=1, column=1, pady=5)
        btn_capture.bind("<Button-1>", lambda *_: capture_report(self, register_id))

        self.profits_stack["initial_funds"].entry.bind(
            "<KeyRelease>", lambda *_: self.update_total_profits()
        )
        self.profits_stack["additional_funds"].entry.bind(
            "<KeyRelease>", lambda *_: self.update_total_profits()
        )
        self.report_stack["reported_funds"].entry.bind(
            "<KeyRelease>", lambda *_: self.update_final_reports()
        )

    def add_traces_to_vars(self) -> None:
        """Añade callbacks a distintas variables de TKInter para que se actualicen al toque"""
        self.containers_variables["machine_variable"].trace_add(
            "write",
            lambda *_: self.update_total_expenses(
                self.expenses_stack["machine_prices"].entry
            ),
        )
        self.containers_variables["replenish_variable"].trace_add(
            "write",
            lambda *_: self.update_total_expenses(
                self.expenses_stack["machine_replenishments"].entry
            ),
        )
        self.containers_variables["bussiness_variable"].trace_add(
            "write",
            lambda *_: self.update_total_expenses(
                self.expenses_stack["misc_expenses"].entry
            ),
        )
        self.containers_variables["products_variable"].trace_add(
            "write", lambda *_: self.update_total_profits()
        )

    def update_total_profits(self) -> None:
        """Actualiza los totales de los ingresos del producto"""
        try:
            initial_funds = int(
                self.profits_stack["initial_funds"].entry.get()
            )
        except ValueError:
            initial_funds = 0

        try:
            additional_funds = int(
                self.profits_stack["additional_funds"].entry.get()
            )
        except ValueError:
            additional_funds = 0

        self.total_variables["total_profits"].set(
            self.containers_variables["products_variable"].get()
            + initial_funds
            + additional_funds
        )

        self.update_entry(self.profits_stack["products_profits"].entry)
        self.update_final_reports()

    def update_total_expenses(self, entry: tk.Entry) -> None:
        "Actualiza el valor total de los gastos"
        self.total_variables["total_expenses"].set(
            self.containers_variables["machine_variable"].get()
            + self.containers_variables["replenish_variable"].get()
            + self.containers_variables["bussiness_variable"].get()
        )

        self.update_entry(entry)
        self.update_final_reports()

    def update_final_reports(self) -> None:
        """Actualiza la sección de reportes finales de la ventana principal"""
        try:
            reported_funds = int(
                self.report_stack["reported_funds"].entry.get()
            )
        except ValueError:
            reported_funds = 0

        try:
            initial_funds = int(
                self.profits_stack["initial_funds"].entry.get()
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

        self.update_entry(self.report_stack["expected_funds"].entry)
        self.update_entry(self.report_stack["difference"].entry)
        self.update_entry(self.report_stack["balance"].entry)

    def fill_entries(self, register_id: int) -> None:
        """
        Fills the text fields in our container with data captured for the current
        register id"""

        fill_query = """
        SELECT initial_funds, extra_funds, reported_funds
        FROM daily_reports
        WHERE register_id = ?
        """

        self.profits_stack["initial_funds"].entry.delete(0, tk.END)
        self.profits_stack["additional_funds"].entry.delete(0, tk.END)
        self.report_stack["reported_funds"].entry.delete(0, tk.END)

        self.update_total_profits()

        try:
            entry_values = request_data(fill_query, (register_id,))[0]
        except IndexError:
            return

        if entry_values == ():
            return

        self.profits_stack["initial_funds"].entry.insert(0, entry_values[0])
        self.profits_stack["additional_funds"].entry.insert(
            0, entry_values[1]
        )
        self.report_stack["reported_funds"].entry.insert(0, entry_values[2])

    def update_entry(self, entry: tk.Entry) -> None:
        """Actualiza una entrada de solo lectura"""
        entry.config(state="normal")

        entry.config(state="readonly")
