import tkinter
import events as ev


class app:

    def __init__(self, window):
        self.wind = window
        self.wind.title("Expense Tracker")

        # Crea un frame así todo estetico
        frame = tkinter.LabelFrame(self.wind, text="Register a new slime")
        frame.grid(row=0, column=0, columnspan=3, pady=20)

        # Entrada para el nombre del slime
        tkinter.Label(frame, text="Name: ").grid(row=1, column=0)
        self.slime_name = tkinter.Entry(frame)
        self.slime_name.focus()
        self.slime_name.grid(row=1, column=1)

        # Entrada para el valor del slime
        tkinter.Label(frame, text="Value: ").grid(row=2, column=0)
        self.slime_value = tkinter.Entry(frame)
        self.slime_value.grid(row=2, column=1)

        # Botón para añadir a la base de datos un slime
        add_slime_btn = tkinter.Button(frame, text="Save Slime")
        add_slime_btn.bind(
            "<Button-1>", 
            lambda _ : ev.add_slime(self.slime_name.get(), self.slime_value.get(), self.info_label)
        )
        add_slime_btn.grid(row=3, columnspan=2, sticky="we")

        # Label del estado del programa (?)
        self.info_label = tkinter.Label(frame, text="Do something, come on")
        self.info_label.grid(row=4, columnspan=2, sticky="we")

window = tkinter.Tk()
application = app(window)
window.mainloop()
