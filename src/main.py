"""
Definición de la ventana principal del programa. Ahora con clases.

Hecho por Hapurobokka
"""

import tkinter as tk
from containers import TreeContainer, ProductsContainer, TotalsContainer
import core
import events as ev


class App:
    """Punto de inicio del programa"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.register_id = self.__get_latest_register()
        self.containers = self.__create_containers()
        self.totals_container = TotalsContainer(
            self.register_id,
            self.containers["machine_container"].total_var,
            self.containers["replenish_container"].total_var,
            self.containers["bussiness_container"].total_var,
            self.containers["products_container"].total_var,
        )
        self.register_info = self.__get_register_info()

    def __get_latest_register(self) -> int:
        """Obtiene la última id de registro de la base de datos"""
        query = """
        SELECT * FROM registers
        ORDER BY id DESC
        LIMIT 1
        """

        return core.request_data(query)[0][0]

    def __create_containers(self) -> dict[str, TreeContainer | ProductsContainer]:
        containers: dict[str, TreeContainer | ProductsContainer] = {}

        containers["machine_container"] = TreeContainer(
            self.root,
            "machine_table",
            ["id", "machine_name", "amount"],
        )
        containers["replenish_container"] = TreeContainer(
            self.root,
            "replenishments",
            ["id", "machine_name", "amount"],
        )
        containers["bussiness_container"] = TreeContainer(
            self.root,
            "expenses",
            ["id", "concept", "amount"],
        )
        containers["products_container"] = ProductsContainer(
            self.root,
            "products_sales",
            ["id", "product_id", "in_product", "out_product", "profits"],
        )

        return containers

    def __get_register_info(self) -> dict[str, tk.StringVar]:
        data_query = """
        SELECT e.employee_name, s.shift_name, d.date
        FROM registers r
        JOIN employees e ON e.id = r.employee_id
        JOIN shifts s ON s.id = r.shift_id
        JOIN dates d ON d.id = r.date_id
        WHERE r.id = ?
        """

        data = core.request_data(data_query, (self.register_id,))[0]
        register_info: dict[str, tk.StringVar] = {}

        # usamos mucho diccionarios ou yeah
        register_info["employee"] = tk.StringVar(self.root, value=data[0])
        register_info["shift"] = tk.StringVar(self.root, value=data[1])
        register_info["date"] = tk.StringVar(self.root, value=data[2])

        return register_info

    def __create_controlers_frame(self):
        controlers_frame = tk.Frame(self.root)
        employees_button = tk.Button(controlers_frame, text="Mostrar empleados")
        employees_button.grid(row=0, column=0)
        employees_button.bind(
            "<Button-1>",
            lambda _: ev.show_table_window(
                "employees",
                ["id", "employee_name"],
                "Ver empleados",
                "employee",
                "Empleado",
            ),
        )

        return controlers_frame

    def __create_register_display(self):
        """Crea un frame donde se mostrara la información del register_id actual"""
        frame = tk.Frame(self.root)

        # usa frames o label frames siempre que puedas, de hecho son utiles
        employee_frame = tk.LabelFrame(frame, text="Empleado")
        employee_frame.grid(row=0, column=0)
        tk.Label(employee_frame, textvariable=self.register_info["employee"]).grid(
            row=0, column=0
        )

        shift_frame = tk.LabelFrame(frame, text="Turno")
        shift_frame.grid(row=0, column=1)
        tk.Label(shift_frame, textvariable=self.register_info["shift"]).grid(
            row=0, column=0
        )

        date_frame = tk.LabelFrame(frame, text="Fecha")
        date_frame.grid(row=0, column=2)
        tk.Label(date_frame, textvariable=self.register_info["date"]).grid(
            row=0, column=0
        )

        return frame

    def render(self) -> None:
        """Renderiza la ventana"""
        self.root.title("Expense Tracker")

        self.containers["machine_container"].render(
            "Premios de maquinas", self.register_id
        )
        self.containers["replenish_container"].render(
            "Reposiciones de maquinas", self.register_id
        )
        self.containers["bussiness_container"].render(
            "Gastos del negocio", self.register_id
        )
        self.containers["products_container"].render(
            "Productos vendidos", self.register_id
        )

        tk.Button(
            text="Añadir nuevo registro",
            command=lambda: ev.spawn_add_register_window(
                self.containers, self.totals_container
            ),
        ).grid(row=0, column=0)

        register_display_frame = self.__create_register_display()
        register_display_frame.grid(row=0, column=1)

        controlers_frame = self.__create_controlers_frame()
        controlers_frame.grid(row=0, column=2)

        self.containers["machine_container"].frame.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsew"
        )
        self.containers["replenish_container"].frame.grid(
            row=2, column=0, padx=10, pady=10, sticky="nsew"
        )
        self.containers["bussiness_container"].frame.grid(
            row=1, column=1, padx=10, pady=10, sticky="nsew"
        )
        self.containers["products_container"].frame.grid(
            row=1, column=2, padx=10, pady=10, sticky="nsew"
        )

        # y llenamos las entradas
        self.totals_container.fill_entries(self.register_id)
        self.totals_container.frame.grid(row=2, column=1, columnspan=2)


window = tk.Tk()
app = App(window)
app.render()
window.mainloop()
