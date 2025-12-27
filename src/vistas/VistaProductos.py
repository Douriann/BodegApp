import customtkinter as ctk
from tkinter import ttk # Necesario para el Treeview
import tkinter as tk

# Importar el DAO y el modelo Producto
from servicios.ProductoDAO import ProductoDAO
from modelos.Producto import Producto

# Importar la vista de modificación de producto
from vistas.VistaModifProducto import VistaModifProducto
from vistas.VistaCrearProduto import VistaCrearProduto



class VistaProductos(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.marcas_dict = self._cargar_diccionario_marcas()
        
        # --- 1. Título ---
        self.label_titulo = ctk.CTkLabel(self, text="Inventario de Productos", font=("Roboto", 24))
        self.label_titulo.pack(pady=20)

        # --- 2. Botón Nuevo ---
        self.btn_nuevo = ctk.CTkButton(self, text="Nuevo Producto", command=self.crear_producto)
        self.btn_nuevo.pack(pady=10)
        
        # --- Botón Editar ---
        self.btn_editar = ctk.CTkButton(self, text="Editar Producto", command=self.editar_producto)
        self.btn_editar.pack(pady=5)
        
        # --- Botón Eliminar ---
        self.btn_eliminar = ctk.CTkButton(self, text="Eliminar Producto", command=self.eliminar_producto)
        self.btn_eliminar.pack(pady=5)
        
        # --- NUEVO: Sección de Búsqueda ---
        frame_busqueda = ctk.CTkFrame(self)
        frame_busqueda.pack(pady=10, padx=20, fill="x")

        # Etiqueta y campo de búsqueda
        label_buscar = ctk.CTkLabel(frame_busqueda, text="Buscar por nombre:")
        label_buscar.pack(side="left", padx=10)

        self.entry_buscar = ctk.CTkEntry(frame_busqueda, width=200, placeholder_text="Ingresa nombre del producto")
        self.entry_buscar.pack(side="left", padx=10)

        # Botón Buscar
        btn_buscar = ctk.CTkButton(frame_busqueda, text="Buscar", command=self.buscar_productos)
        btn_buscar.pack(side="left", padx=10)

        # Botón Limpiar (para resetear búsqueda)
        btn_limpiar = ctk.CTkButton(frame_busqueda, text="Limpiar", command=self.cargar_datos)
        btn_limpiar.pack(side="left", padx=10)
        
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
        columns = ("id", "nombre", "marca", "precio_venta", "stock_actual", "stock_minimo")

        
        self.tree = ttk.Treeview(frame_tabla, columns=columns, show="headings")
        
        # Configurar cabeceras
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Producto")
        self.tree.heading("marca", text="Marca")
        self.tree.heading("precio_venta", text="Precio Venta")
        self.tree.heading("stock_actual", text="Stock Actual")
        self.tree.heading("stock_minimo", text="Stock Mínimo")

        # Configurar ancho de columnas
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre", width=100, anchor="w")
        self.tree.column("marca", width=100, anchor="w")
        self.tree.column("precio_venta", width=100, anchor="center")
        self.tree.column("stock_actual", width=100, anchor="center")
        self.tree.column("stock_minimo", width=80, anchor="center")

        # Scrollbar vertical
        scrollbar = ctk.CTkScrollbar(frame_tabla, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Empaquetado
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # --- 6. Cargar datos al iniciar ---
        self.cargar_datos()
        
    

    #--- Función para editar producto ---
    def editar_producto(self):
        item = self.tree.selection()
        if not item:
            tk.messagebox.showwarning("Atención", "Selecciona un producto para editar.")
            return

        valores = self.tree.item(item, "values")
        id_producto = valores[0]
        
        dao = ProductoDAO()
        productos = dao.consultar_todos()
        producto = next((p for p in productos if str(p.id_producto) == str(id_producto)), None)

        if producto:
            self.abrir_formulario_edicion(producto)

    #-- Función para eliminar producto ---
    def eliminar_producto(self):
        item = self.tree.selection()
        if not item:
            tk.messagebox.showwarning("Atención", "Selecciona un producto para eliminar.")
            return

        valores = self.tree.item(item, "values")
        id_producto = valores[0]

        confirmacion = tk.messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de que deseas eliminar este producto?")
        if not confirmacion:
            return

        dao = ProductoDAO()
        producto = next((p for p in dao.consultar_todos() if str(p.id_producto) == str(id_producto)), None)

        if producto:
            producto.estatus = 0  # ← Eliminado lógico
            if dao.modificar_producto(producto):
                self.cargar_datos()
                tk.messagebox.showinfo("Eliminado", "El producto fue eliminado correctamente.")
            else:
                tk.messagebox.showerror("Error", "No se pudo eliminar el producto.")

    
    #-- Función para abrir formulario de edición ---
    def abrir_formulario_edicion(self, producto):
        VistaModifProducto(self, producto, self.cargar_datos)

   
    # Metodo para crear producto
    def crear_producto(self):
        VistaCrearProduto(self, self.cargar_datos)

    # NUEVO: Método para buscar productos
    def buscar_productos(self):
        """
        Busca productos por nombre y actualiza la tabla.
        """
        termino = self.entry_buscar.get().strip().title()

        if not termino:
            tk.messagebox.showwarning("Atención", "Ingresa un nombre de producto para buscar.")
            return

        dao = ProductoDAO()
        resultados = dao.buscar_por_nombre(termino)

        if not resultados:
            tk.messagebox.showinfo("Sin resultados", "No se encontraron productos con ese nombre.")
        
        # Actualizar tabla con resultados
        self._actualizar_tabla(resultados)

    def _cargar_diccionario_marcas(self):
        """
        Retorna un diccionario {id_marca: nombre_marca} para mapeo rápido.
        """
        dao = ProductoDAO()
        marcas = dao.obtener_marcas()  #  (devuelve lista de tuplas)
        return {id_marca: nombre for id_marca, nombre in marcas}

    def cargar_datos(self, lista_productos=None):
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
            
            
            if p.estatus == 1:  # Mostrar solo productos activos
                # Definir la etiqueta si el stock actual es menor al mínimo
                tags = ("alerta",) if p.stock_actual < p.stock_minimo else ()
                # nueva columna marca
                nombre_marca = self.marcas_dict.get(p.id_marca, "Sin Marca")
                self.tree.insert("", "end", values=(
                    p.id_producto,
                    p.nombre_producto,
                    nombre_marca,
                    f"${p.precio_venta:,.2f}", # Formato de moneda
                    p.stock_actual,
                    p.stock_minimo,
                ), tags=tags)
                
                
        # Configurar estilo para productos con bajo stock
        self.tree.tag_configure("alerta", foreground="red")
        print(f"Datos cargados: {len(lista_productos)} registros.")

    # NUEVO: Método auxiliar para actualizar tabla 
    def _actualizar_tabla(self, lista_productos):
        """
        Consulta la base de datos y llena el Treeview con OBJETOS.
        """
        # 1. Limpiar tabla actual (por si refrescas)
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 2. Insertar datos
        for p in lista_productos:
            

            if p.estatus == 1:  # Mostrar solo productos activos
                # Definir la etiqueta si el stock actual es menor al mínimo
                tags = ("alerta",) if p.stock_actual < p.stock_minimo else ()
                # nueva columna marca
                nombre_marca = self.marcas_dict.get(p.id_marca, "Sin Marca")
                self.tree.insert("", "end", values=(
                    p.id_producto,
                    p.nombre_producto,
                    nombre_marca,
                    f"${p.precio_venta:,.2f}", # Formato de moneda
                    p.stock_actual,
                    p.stock_minimo,
                ), tags=tags)
                
                
        # Configurar estilo para productos con bajo stock
        self.tree.tag_configure("alerta", foreground="red")
        print(f"Datos cargados: {len(lista_productos)} registros.")