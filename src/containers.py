"""
Definiciones de clase en otro lugar para que todo sirva bien

Por Hapurobokka
"""

from dataclasses import dataclass

import tkinter as tk
from tkinter import ttk
import core
import events as ev


class TreeContainer:
    """Clase que contiene un Frame con un Treeview y varios botones para operar con el"""

    def __init__(
        self,
        root: tk.Tk,
        table: str,
        table_values: list[str],
    ) -> None:
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

        self.total_var = tk.IntVar(root, value=0)

        # Creamos el treeview
        self.tree = ttk.Treeview(self.frame, columns=("name", "amount"))

        # Añadiendo y configurando botones
        self.buttons = {
            "btn_add": tk.Button(self.frame, text="Añadir"),
            "btn_erase": tk.Button(self.frame, text="Eliminar"),
            "btn_edit": tk.Button(self.frame, text="Editar"),
        }

    def setup_tree(self, register_id: int) -> None:
        """Dispone las columnas y posición del Treeview, además de llenarlo por primera vez"""
        self.tree.grid(row=1, column=0, sticky="nsew", columnspan=3)

        # de una manera interesante treeview tiene una primer columna #0 que no podemos ignorar
        self.tree.heading("#0", text="ID", anchor=tk.CENTER)
        self.tree.heading("name", text="Nombre", anchor=tk.CENTER)
        self.tree.heading("amount", text="Cantidad", anchor=tk.CENTER)

        self.tree.column("#0", width=40)
        self.tree.column("name", width=75)
        self.tree.column("amount", width=90)

        core.fill_table(self, register_id)

    def setup_scrollbar(self) -> None:
        """Coloca una scrollbar en el Treeview del contenedor"""
        vscroll = tk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)

        vscroll.grid(row=1, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=vscroll.set)

    def setup_buttons(self, register_id: int) -> None:
        """Coloca los botones en su sitio y les asigna eventos"""
        self.buttons["btn_add"].grid(row=2, column=0)
        self.buttons["btn_add"].bind(
            "<Button-1>",
            lambda _: ev.spawn_add_window(self, ("Nombre", "Cantidad"), register_id),
        )

        self.buttons["btn_edit"].grid(row=2, column=1)
        self.buttons["btn_edit"].bind(
            "<Button-1>",
            lambda _: ev.spawn_edit_window(self, ["Nombre", "Cantidad"], register_id),
        )

        self.buttons["btn_erase"].grid(row=2, column=2)
        self.buttons["btn_erase"].bind(
            "<Button-1>", lambda _: ev.perform_delete_selected_record(self, register_id)
        )

    def update_total_var(self, register_id: int) -> None:
        """Actualiza el valor de la variable que cuenta el total de la tabla"""
        self.total_var.set(core.get_total_amount(self.table, "amount", register_id))

    def render(self, frame_text: str, register_id: int) -> None:
        """Renderiza el componente"""
        tk.Label(self.frame, text=frame_text).grid(row=0, column=0, columnspan=3)
        self.setup_buttons(register_id)
        self.setup_scrollbar()
        self.setup_tree(register_id)


class ProductsContainer(TreeContainer):
    """
    El contenedor simple adaptado para mostrar ventas de productos.
    No recomendaria crear varios de estos.
    """

    def __init__(
        self,
        root: tk.Tk,
        table: str,
        table_values: list[str],
    ) -> None:
        # todos los atributos de la clase padre nos interesan, excepto la fill_query que es especial
        super().__init__(root, table, table_values)
        self.fill_query = """
        SELECT ps.id, p.product_name, ps.in_product, ps.out_product, ps.profits
        FROM products_sales ps
        JOIN products p ON p.id = ps.product_id
        WHERE ps.register_id = ?
        """

    def setup_tree(self, register_id: int) -> None:
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

    def setup_buttons(self, register_id: int) -> None:
        """Coloca los botones en su sitio y les asigna eventos"""
        self.buttons["btn_add"].grid(row=2, column=0)

        # esta clase es su propia variante de spawn_add_window
        self.buttons["btn_add"].bind(
            "<Button-1>",
            lambda _: ev.spawn_product_report_window(self, register_id),
        )

        self.buttons["btn_edit"].grid(row=2, column=1)
        self.buttons["btn_edit"]["text"] = "Mostrar productos"
        self.buttons["btn_edit"].bind(
            "<Button-1>",
            lambda _: ev.show_table_window(
                "products",
                ["id", "product_name", "price"],
                "Ver productos en venta",
                ("name", "price"),
                ("Nombre", "Precio"),
            ),
        )

        self.buttons["btn_erase"].grid(row=2, column=2)
        self.buttons["btn_erase"].bind(
            "<Button-1>", lambda _: ev.perform_delete_selected_record(self, register_id)
        )

    def update_total_var(self, register_id: int) -> None:
        self.total_var.set(core.get_total_amount(self.table, "profits", register_id))


@dataclass
class SimpleContainer:
    """Clase básica para almacenar contendores simples"""

    root_win: tk.Tk | tk.Toplevel
    table: str
    table_values: list[str]
    tree: ttk.Treeview
    fill_query: str
