import customtkinter as ctk
from tkinter import ttk # Necesario para el Treeview
import tkinter as tk

# Asegúrate de importar tu DAO
# (Ajusta la ruta si 'consultas' está en otro lado)
from servicios.ProductoDAO import ProductoDAO

class VistaProductos(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- 1. Título ---
        self.label_titulo = ctk.CTkLabel(self, text="Inventario de Productos", font=("Roboto", 24))
        self.label_titulo.pack(pady=20)

        # --- 2. Botón Nuevo ---
        self.btn_nuevo = ctk.CTkButton(self, text="Nuevo Producto", command=self.crear_producto)
        self.btn_nuevo.pack(pady=10)

        # --- 3. Configuración del Estilo de la Tabla (Treeview) ---
        # Esto es necesario porque el Treeview nativo es blanco/gris por defecto
        style = ttk.Style()
        style.theme_use("clam") # 'clam' permite modificar colores más fácilmente
        
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        rowheight=30)
        
        style.map('Treeview', background=[('selected', '#1f538d')]) # Color al seleccionar fila

        # --- 4. Crear el Frame para la Tabla (para incluir scrollbar) ---
        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=20)

        # --- 5. Definir columnas ---
        # Escogemos las columnas más relevantes para mostrar en el resumen
        columns = ("id", "nombre", "precio_venta", "stock", "estatus")
        
        self.tree = ttk.Treeview(frame_tabla, columns=columns, show="headings")
        
        # Configurar cabeceras
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Producto")
        self.tree.heading("precio_venta", text="Precio Venta")
        self.tree.heading("stock", text="Stock Actual")
        self.tree.heading("estatus", text="Estatus")

        # Configurar ancho de columnas
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre", width=200, anchor="w")
        self.tree.column("precio_venta", width=100, anchor="center")
        self.tree.column("stock", width=100, anchor="center")
        self.tree.column("estatus", width=80, anchor="center")

        # Scrollbar vertical
        scrollbar = ctk.CTkScrollbar(frame_tabla, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Empaquetado
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # --- 6. Cargar datos al iniciar ---
        self.cargar_datos()


    def crear_producto(self):
        print("Abriendo formulario para crear producto...")


    def cargar_datos(self):
        """
        Consulta la base de datos y llena el Treeview con OBJETOS.
        """
        # 1. Limpiar tabla actual (por si refrescas)
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 2. Instanciar DAO y buscar datos
        dao = ProductoDAO()
        lista_productos = dao.consultar_todos() # Esto devuelve lista de OBJETOS Producto

        # 3. Insertar datos
        for p in lista_productos:
            # Como ahora 'p' es un Objeto, usamos notación de punto (.)
            # Fíjate que fácil es leer esto comparado con p[1], p[8]...
            val_estatus = "Activo" if p.estatus == 1 else "Inactivo"

            self.tree.insert("", "end", values=(
                p.id_producto,
                p.nombre_producto,
                f"${p.precio_venta:,.2f}", # Formato de moneda
                p.stock_actual,
                val_estatus
            ))

        print(f"Datos cargados: {len(lista_productos)} registros.")