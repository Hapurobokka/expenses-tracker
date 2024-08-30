"""
Un par de funciones de ayuda que no sabía donde poner.

Por Hapurobokka
"""

import tkinter as tk
from dataclasses import dataclass

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
