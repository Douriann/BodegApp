import customtkinter as ctk
from servicios.ServCategoria import ServCategoria
from modelos.Categoria import Categoria

class VentanaVerificacion(ctk.CTkToplevel):
    """Ventana de aviso personalizada para Éxito o Error."""
    def __init__(self, parent, titulo, mensaje, es_error=False, on_close=None):
        super().__init__(parent)
        self.title("Aviso")
        self.geometry("350x220")
        self.attributes("-topmost", True)
        self.grab_set() 
        self.resizable(False, False)
        self.on_close = on_close
        
        color_tema = "#E74C3C" if es_error else "#ab3df4"
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 175
        y = (self.winfo_screenheight() // 2) - 110
        self.geometry(f"350x220+{x}+{y}")

        self.main_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color=color_tema)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.lbl_titulo = ctk.CTkLabel(
            self.main_frame, text=titulo, 
            font=("Segoe UI", 18, "bold"), text_color=color_tema
        )
        self.lbl_titulo.pack(pady=(20, 5))

        self.lbl_msj = ctk.CTkLabel(
            self.main_frame, text=mensaje, 
            font=("Segoe UI", 13), text_color=("#333333", "#D1D1D1"),
            wraplength=280
        )
        self.lbl_msj.pack(pady=10, padx=20)

        self.btn_ok = ctk.CTkButton(
            self.main_frame, text="Entendido", 
            fg_color=color_tema, hover_color="#555555",
            width=120, height=35, font=("Segoe UI", 13, "bold"),
            command=self._on_ok
        )
        self.btn_ok.pack(pady=(10, 20))

    def _on_ok(self):
        if self.on_close:
            self.on_close()
        self.destroy()

class VistaCategoria(ctk.CTkToplevel):
    def __init__(self, parent, callback_actualizar):
        super().__init__(parent)
        self.title("Gestión de Categorías")
        self.after(10, lambda: self.state('normal'))
        self.attributes("-topmost", True) 
        
        anchoVist = 400
        altoVist = 200
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
            VentanaVerificacion(self, "Error", "El nombre de la categoría no puede estar vacío.", es_error=True)
            return

        servicio_categoria = ServCategoria()
        nueva_categoria_id = servicio_categoria.crear_categoria(nombre_categoria)
        if nueva_categoria_id == -1 or nueva_categoria_id == 0:
            VentanaVerificacion(self, "Error", "Error al crear la categoría. Puede que ya exista.", es_error=True)
        else:
            def cerrar_y_actualizar():
                self.callback_actualizar()
                self.destroy()
            VentanaVerificacion(
                self, "Éxito", "Categoría creada exitosamente, con id: " + str(nueva_categoria_id),
                es_error=False, on_close=cerrar_y_actualizar
            )