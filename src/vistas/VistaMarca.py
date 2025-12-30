import customtkinter as ctk
from servicios.ServMarca import ServMarca
from modelos.Marca import Marca

class VistaMarca(ctk.CTkToplevel):
    def __init__(self, parent, callback_actualizar):
        super().__init__(parent)
        self.title("Gestión de Marcas")
        self.after(10, lambda: self.state('normal'))
        self.attributes("-topmost", True) 
        
        anchoVist = 400
        altoVist = 500
        self.update_idletasks()
        anchoPant = self.winfo_screenwidth()
        altoPant = self.winfo_screenheight()
        x = (anchoPant // 2) - (anchoVist // 2)
        y = (altoPant // 2) - (altoVist // 2)
        self.geometry(f"{anchoVist}x{altoVist}+{x}+{y}")

        self.callback_actualizar = callback_actualizar
        self.color_morado = "#ab3df4"
        self.color_morado_hover = "#8e24aa"
        self.color_error = "#E74C3C" # Rojo para errores

        self.entry_nom_marca = ctk.CTkEntry(
            self, width=300, height=40,
            placeholder_text="Nombre de la Marca",
            border_width=2,
            border_color=self.color_morado,
            fg_color="transparent",
            text_color=("#333333", "white"),
            font=("Segoe UI", 12)
        )
        self.entry_nom_marca.pack(pady=(30, 10))
        self.btn_crear_marca = ctk.CTkButton(
            self, text="Crear Marca",
            width=200, height=40,
            fg_color=self.color_morado,
            hover_color=self.color_morado_hover,
            command=self.crear_marca
        )
        self.btn_crear_marca.pack(pady=(10, 20))
    def crear_marca(self):
        nombre_marca = self.entry_nom_marca.get().strip()
        if not nombre_marca:
            print("El nombre de la marca no puede estar vacío.")
            return

        servicio_marca = ServMarca()
        nueva_marca_id = servicio_marca.crear_marca(nombre_marca)
        if nueva_marca_id == -1:
            print("Error al crear la marca. Puede que ya exista.")
        else:
            self.callback_actualizar()
            self.destroy()