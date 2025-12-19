import customtkinter as ctk

class VistaNuevaTransac(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # 1. Configuración básica de la ventana emergente
        self.title("Nueva Transacción")
        self.geometry("400x350")
        self.resizable(False, False)
        
        # Hacemos que la ventana aparezca siempre al frente
        self.attributes("-topmost", True)

        # 2. Widgets del Formulario
        self.label_titulo = ctk.CTkLabel(self, text="Registrar Movimiento", font=("Roboto", 20, "bold"))
        self.label_titulo.pack(pady=20)

        # Campo: Descripción
        self.entry_desc = ctk.CTkEntry(self, placeholder_text="Descripción (ej. Venta Teclado)", width=300)
        self.entry_desc.pack(pady=10)

        # Campo: Monto
        self.entry_monto = ctk.CTkEntry(self, placeholder_text="Monto (ej. 50.00)", width=300)
        self.entry_monto.pack(pady=10)

        # Campo: Tipo (Ingreso/Gasto)
        self.combo_tipo = ctk.CTkComboBox(self, values=["Ingreso (+)", "Gasto (-)"], width=300)
        self.combo_tipo.pack(pady=10)

        # 3. Botones de Acción
        self.btn_guardar = ctk.CTkButton(self, text="Guardar", command=self.guardar_datos, fg_color="#2CC985", hover_color="#26A46E")
        self.btn_guardar.pack(pady=20)

        self.btn_cancelar = ctk.CTkButton(self, text="Cancelar", command=self.destroy, fg_color="transparent", border_width=1)
        self.btn_cancelar.pack(pady=(0, 20))

    def guardar_datos(self):
        # Aquí capturas los datos
        desc = self.entry_desc.get()
        monto = self.entry_monto.get()
        tipo = self.combo_tipo.get()

        print(f"Guardando: {desc} | {monto} | {tipo}")
        
        # Aquí iría la lógica para guardarlo en BD o actualizar la tabla anterior
        
        # Al finalizar, cerramos la ventana
        self.destroy()