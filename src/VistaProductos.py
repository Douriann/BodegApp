import customtkinter as ctk

class VistaProductos(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Título de la sección
        self.label_titulo = ctk.CTkLabel(self, text="Inventario de Productos", font=("Roboto", 24))
        self.label_titulo.pack(pady=20)

        # Ejemplo de widget específico de esta ventana
        self.btn_nuevo = ctk.CTkButton(self, text="Nuevo Producto", command=self.crear_producto)
        self.btn_nuevo.pack(pady=10)

        # Aquí puedes agregar tablas, entradas de texto, etc.

    # --- MÉTODOS ESPECÍFICOS DE PRODUCTOS ---
    def crear_producto(self):
        # Esta lógica vive SOLO aquí. No ensucia el main.py
        print("Abriendo formulario para crear producto...")
        # Aquí iría tu lógica de base de datos o validación