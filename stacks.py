"""
Un par de funciones de ayuda que no sabía donde poner.

Por Hapurobokka
"""

import tkinter as tk
from dataclasses import dataclass


@dataclass
class LabelPair:
    """Un par de una tk.label y una tk.entry, o dos tk.labels"""

    element_1: tk.Label
    element_2: tk.Entry | tk.Label

    def place(self, label_pos, entry_pos):
        """Coloca el elemento en la posición asignada"""
        self.element_1.grid(row=label_pos[0], column=label_pos[1])
        self.element_2.grid(row=entry_pos[0], column=entry_pos[1])


class DisplayStack:
    """Muchos LabelPairs colocados encima de otro, o algo así"""
    def __init__(
        self,
        root: tk.Frame,
        label_name: str,
        elements: list[dict],
        label_width: int = 19,
        entry_width: int = 10,
    ):
        self.stack = {}
        self.label_frame = tk.LabelFrame(root, text=label_name)

        for elem in elements:
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

                pair = LabelPair(label, entry)

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
                self.stack[elem["name"]] = pair
