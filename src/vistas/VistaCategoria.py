import customtkinter as ctk
from servicios.ServCategoria import ServCategoria
from modelos.Categoria import Categoria

class VistaCategoria(ctk.CTkToplevel):
    def __init__(self, parent, callback_actualizar):
        super().__init__(parent)
        self.title("Gestión de Categorías")
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

        self.entry_nom_categoria = ctk.CTkEntry(
            self, width=300, height=40,
            placeholder_text="Nombre de la Categoría",
            border_width=2,
            border_color=self.color_morado,
            fg_color="transparent",
            text_color=("#333333", "white"),
            font=("Segoe UI", 12)
        )
        self.entry_nom_categoria.pack(pady=(30, 10))
        self.btn_crear_categoria = ctk.CTkButton(
            self, text="Crear Categoría",
            width=200, height=40,
            fg_color=self.color_morado,
            hover_color=self.color_morado_hover,
            command=self.crear_categoria
        )
        self.btn_crear_categoria.pack(pady=(10, 20))
    def crear_categoria(self):
        nombre_categoria = self.entry_nom_categoria.get().strip()
        if not nombre_categoria:
            print("El nombre de la categoría no puede estar vacío.")
            return

        servicio_categoria = ServCategoria()
        nueva_categoria_id = servicio_categoria.crear_categoria(nombre_categoria)
        if nueva_categoria_id == -1:
            print("Error al crear la categoría. Puede que ya exista.")
        else:
            self.callback_actualizar()
            self.destroy()