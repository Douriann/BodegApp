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
        
        # --- Botón Editar ---
        self.btn_editar = ctk.CTkButton(self, text="Editar Producto", command=self.editar_producto)
        self.btn_editar.pack(pady=5)
        
        # --- Botón Eliminar ---
        self.btn_eliminar = ctk.CTkButton(self, text="Eliminar Producto", command=self.eliminar_producto)
        self.btn_eliminar.pack(pady=5)

        
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
        columns = ("id", "nombre", "precio_venta", "stock_actual", "stock_minimo")

        
        self.tree = ttk.Treeview(frame_tabla, columns=columns, show="headings")
        
        # Configurar cabeceras
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Producto")
        self.tree.heading("precio_venta", text="Precio Venta")
        self.tree.heading("stock_actual", text="Stock Actual")
        self.tree.heading("stock_minimo", text="Stock Mínimo")

        # Configurar ancho de columnas
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre", width=200, anchor="w")
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
        ventana = ctk.CTkToplevel(self)
        ventana.title("Editar Producto")
        ventana.geometry("420x550")

        scroll_frame = ctk.CTkScrollableFrame(ventana, width=380, height=400)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        campos = {}

        def crear_campo(nombre, valor_inicial):
            label = ctk.CTkLabel(scroll_frame, text=nombre)
            label.pack(pady=(10, 0))
            entry = ctk.CTkEntry(scroll_frame, width=300)
            entry.insert(0, str(valor_inicial))
            entry.pack(pady=(0, 10)) # agrega separación entre campos
            campos[nombre] = entry


        crear_campo("Nombre", producto.nombre_producto)
        crear_campo("ID Categoría", producto.id_categoria)
        crear_campo("ID Marca", producto.id_marca)
        crear_campo("Presentación", producto.presentacion)
        crear_campo("Unidad de Medida", producto.unidad_medida)
        crear_campo("Contenido", producto.contenido)
        crear_campo("Precio Compra", producto.precio_compra)
        crear_campo("Precio Venta", producto.precio_venta)
        crear_campo("Stock Mínimo", producto.stock_minimo)
        crear_campo("Stock Actual", producto.stock_actual)
        
        #-- Función para guardar cambios ---
        def guardar():
            try:
                nombre = campos["Nombre"].get().strip()
                if not nombre:
                    raise ValueError("El nombre del producto no puede estar vacío.")

                presentacion = campos["Presentación"].get().strip()
                unidad = campos["Unidad de Medida"].get().strip()
                if not presentacion or not unidad:
                    raise ValueError("Presentación y unidad de medida son obligatorios.")

                id_categoria = int(campos["ID Categoría"].get())
                id_marca = int(campos["ID Marca"].get())
                contenido = float(campos["Contenido"].get())
                precio_compra = float(campos["Precio Compra"].get())
                precio_venta = float(campos["Precio Venta"].get())
                stock_minimo = int(campos["Stock Mínimo"].get())
                stock_actual = int(campos["Stock Actual"].get())

                if precio_compra < 0 or precio_venta < 0:
                    raise ValueError("Los precios no pueden ser negativos.")
                if stock_minimo < 0 or stock_actual < 0:
                    raise ValueError("El stock no puede ser negativo.")
                if contenido <= 0:
                    raise ValueError("El contenido debe ser mayor que cero.")

                # Asignar valores al objeto
                producto.nombre_producto = nombre
                producto.id_categoria = id_categoria
                producto.id_marca = id_marca
                producto.presentacion = presentacion
                producto.unidad_medida = unidad
                producto.contenido = contenido
                producto.precio_compra = precio_compra
                producto.precio_venta = precio_venta
                producto.stock_minimo = stock_minimo
                producto.stock_actual = stock_actual

                dao = ProductoDAO()
                if dao.modificar_producto(producto):
                    self.cargar_datos()
                    tk.messagebox.showinfo("Éxito", "El producto fue modificado correctamente.")
                    ventana.destroy()
                else:
                    tk.messagebox.showerror("Error", "No se pudo modificar el producto.")

            except ValueError as ve:
                tk.messagebox.showerror("Error de validación", str(ve))
            except Exception as e:
                tk.messagebox.showerror("Error inesperado", f"Ocurrió un error: {e}")
                

        #Alineado de botones
        frame_botones = ctk.CTkFrame(ventana)
        frame_botones.pack(pady=10)

        # Botón para guardar cambios
        btn_guardar = ctk.CTkButton(frame_botones, text="Guardar Cambios", command=guardar) 
        btn_guardar.pack(side="left", padx=10)

        # Botón para cancelar
        btn_cancelar = ctk.CTkButton(frame_botones, text="Cancelar", command=ventana.destroy) 
        btn_cancelar.pack(side="left", padx=10)

    
        


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
            

            if p.estatus == 1:  # Mostrar solo productos activos
                # Definir la etiqueta si el stock actual es menor al mínimo
                tags = ("alerta",) if p.stock_actual < p.stock_minimo else ()

                self.tree.insert("", "end", values=(
                    p.id_producto,
                    p.nombre_producto,
                    f"${p.precio_venta:,.2f}", # Formato de moneda
                    p.stock_actual,
                    p.stock_minimo,
                ), tags=tags)
                
                
        # Configurar estilo para productos con bajo stock
        self.tree.tag_configure("alerta", foreground="red")
        print(f"Datos cargados: {len(lista_productos)} registros.")