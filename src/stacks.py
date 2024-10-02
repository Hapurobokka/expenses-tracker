"""
Un par de funciones de ayuda que no sabía donde poner.

Por Hapurobokka
"""

import tkinter as tk
from dataclasses import dataclass


@dataclass
class LabelPair:
    """Un par de tk.labels"""

    label_1: tk.Label
    label_2: tk.Label

    def render(self, label1_pos: tuple[int, int], label2_pos: tuple[int, int]) -> None:
        """Coloca el elemento en la posición asignada"""
        self.label_1.grid(row=label1_pos[0], column=label1_pos[1])
        self.label_2.grid(row=label2_pos[0], column=label2_pos[1])


@dataclass
class LabelEntryPair:
    """Una tk.label y una tk.entry"""

    label: tk.Label
    entry: tk.Entry

    def render(self, label_pos: tuple[int, int], entry_pos: tuple[int, int]) -> None:
        """Coloca el elemento en la posición asignada"""
        self.label.grid(row=label_pos[0], column=label_pos[1])
        self.entry.grid(row=entry_pos[0], column=entry_pos[1])


def create_stack(
    root: tk.Frame,
    label_name: str,
    elements: list[dict],
    position: tuple[int, int],
    label_width: int = 19,
    entry_width: int = 10,
):
    stack = {}
    label_frame = tk.LabelFrame(root, text=label_name)

    for elem in elements:
        pair = None

        if elem["type"] == "LabelEntryPair":
            label = tk.Label(
                master=label_frame,
                text=elem["label_text"],
                anchor="w",
                width=label_width,
            )

            entry = tk.Entry(
                master=label_frame,
                state=elem["state"],
                textvariable=elem["textvariable"],
                width=entry_width,
            )

            pair = LabelEntryPair(label, entry)

        elif elem["type"] == "LabelPair":
            label1 = tk.Label(
                master=label_frame,
                text=elem["label_text"],
                anchor="w",
                width=label_width,
            )

            label2 = tk.Label(
                master=label_frame,
                textvariable=elem["textvariable"],
                anchor="w",
                width=entry_width,
            )

            pair = LabelPair(label1, label2)

        if pair is not None:
            pair.render(elem["position"][0], elem["position"][1])
            stack[elem["name"]] = pair

    label_frame.grid(row=position[0], column=position[1], padx=5)

    return stack
