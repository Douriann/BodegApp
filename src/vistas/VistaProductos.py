import customtkinter as ctk
from tkinter import ttk # Necesario para el Treeview
import tkinter as tk

# Importar el DAO y el modelo Producto
from servicios.ProductoDAO import ProductoDAO
from modelos.Producto import Producto

# Importar la vista de modificación de producto
from vistas.VistaModifProducto import VistaModifProducto



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
        
    # Método auxiliar para abrir una ventana emergente genérica con formulario
    def abrir_ventana_formulario(self, titulo, campos_config, combos_config, accion_guardar, ancho=420, alto=600):
        """
        Abre una ventana emergente con formulario reutilizable.
        - titulo: Título de la ventana.
        - campos_config: Lista de tuplas para campos de texto (ej. [("Nombre Producto", "Ej: Coca Cola")]).
        - combos_config: Lista de tuplas para combos (ej. [("Categoría", categorias, "Selecciona Categoría")]).
        - accion_guardar: Función callback para guardar (recibe campos y combos).
        - ancho/alto: Dimensiones de la ventana.
        """

        # 1- Creacion de ventana y frame con sroll para formulario emergente
        ventana = ctk.CTkToplevel(self)
        ventana.title(titulo)
        ventana.geometry(f"{ancho}x{alto}")

        scroll_frame = ctk.CTkScrollableFrame(ventana, width=380, height=500)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # 2- Diccionarios para guardar entradas de usuario

        campos = {}
        combos = {}
        
        # 3- Crear campos de texto
        for nombre, placeholder in campos_config:
            self.crear_campo_texto(scroll_frame, nombre, placeholder, campos)

        # 4- Crear combos
        for nombre, opciones, placeholder in combos_config:
            self.crear_combo(scroll_frame, nombre, opciones, placeholder, combos)

        # 5- Frame para botones guardar y cancelar
        frame_botones = ctk.CTkFrame(ventana)
        frame_botones.pack(pady=10)

        btn_guardar = ctk.CTkButton(frame_botones, text="Guardar", command=lambda: self.manejar_guardar(ventana, campos, combos, accion_guardar)) 
        btn_guardar.pack(side="left", padx=10)

        btn_cancelar= ctk.CTkButton(frame_botones, text="Cancelar", command=ventana.destroy)
        btn_cancelar.pack(side="left", padx=10)

    # Metodo auxiliar para crear un campo de texto
    def crear_campo_texto(self, parent, nombre, placeholder, campos_dict):
        label = ctk.CTkLabel(parent, text=nombre)
        label.pack(pady=(10, 0))
        entry = ctk.CTkEntry(parent, width=300, placeholder_text=placeholder)
        entry.pack(pady=(0, 10))
        campos_dict[nombre] = entry

     # Método auxiliar para crear un combo
    def crear_combo(self, parent, nombre, opciones, placeholder, combos_dict):
        label = ctk.CTkLabel(parent, text=nombre)
        label.pack(pady=(10, 0))
        combo = ctk.CTkComboBox(parent, width=300, values=[f"{id} - {nombre}" for id, nombre in opciones], state="readonly")
        combo.set(placeholder)
        combo.pack(pady=(0, 10))
        combos_dict[nombre] = combo

    # Método auxiliar para validar y obtener valores de campos
    def validar_y_obtener_valores(self, campos, combos):
        """
        Valida campos comunes y retorna un diccionario con valores.
        Lanza ValueError si hay errores.
        """
        # 1- Desempaquetar diccionario en variables
        # Campos de texto
        nombre = campos["Nombre Producto"].get().strip().title()
        presentacion = campos["Presentación"].get().strip()
        unidad_medida = campos["Unidad de Medida"].get().strip()
        contenido = float(campos["Contenido"].get())
        precio_compra = float(campos["Precio Compra"].get())
        precio_venta = float(campos["Precio Venta"].get())
        stock_minimo = int(campos["Stock Mínimo"].get())
        stock_actual = int(campos["Stock Actual"].get())
        # Combos
        categoria_seleccionada = combos["Categoría"].get()
        marca_seleccionada = combos["Marca"].get()

        # 2- Validar entradas
        if not nombre or nombre.isdigit():
            raise ValueError("El nombre del producto no puede estar vacío ni ser solo números.")

        
        if not presentacion or presentacion.isdigit():
            raise ValueError("La presentación no puede estar vacía ni ser solo números.")

        
        if not unidad_medida or unidad_medida.isdigit():
            raise ValueError("La unidad de medida no puede estar vacía ni ser solo números.")

        
        if contenido <= 0:
            raise ValueError("El contenido debe ser un número mayor que cero.")

        
        if precio_compra < 0 or precio_venta < 0:
            raise ValueError("Los precios no pueden ser negativo.")

        
        if stock_minimo < 0 or stock_actual < 0 :
            raise ValueError("El stock no puede ser negativo.")

        
        if categoria_seleccionada == "Selecciona Categoría":
            raise ValueError("Debes seleccionar una categoría.")
        id_categoria = int(categoria_seleccionada.split(" - ")[0])

        
        if marca_seleccionada == "Selecciona Marca":
            raise ValueError("Debes seleccionar una marca.")
        id_marca = int(marca_seleccionada.split(" - ")[0])

        return {
            "nombre": nombre,
            "id_categoria": id_categoria,
            "id_marca": id_marca,
            "presentacion": presentacion,
            "unidad_medida": unidad_medida,
            "contenido": contenido,
            "precio_compra": precio_compra,
            "precio_venta": precio_venta,
            "stock_minimo": stock_minimo,
            "stock_actual": stock_actual
        }

        # Método auxiliar para manejar el guardado
    def manejar_guardar(self, ventana, campos, combos, accion_guardar):
        try:
            valores = self.validar_y_obtener_valores(campos, combos)
            if accion_guardar(valores):  # Llama al callback (crear o editar)
                self.cargar_datos()
                tk.messagebox.showinfo("Éxito", "Operación realizada correctamente.")
                ventana.destroy()
            else:
                tk.messagebox.showerror("Error", "No se pudo realizar la operación.")
        except ValueError as ve:
            tk.messagebox.showerror("Error de validación", str(ve))
        except Exception as e:
            tk.messagebox.showerror("Error inesperado", f"Ocurrió un error: {e}")

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
        """
        Abre el formulario para crear un nuevo producto usando auxiliares reutilizables.
        """
        dao = ProductoDAO()
        categorias = dao.obtener_categorias()
        marcas = dao.obtener_marcas()

        # Configuración de campos y combos
        campos_config = [
            ("Nombre Producto", "Ej: Refresco Cola"),
            ("Presentación", "Ej: Botella"),
            ("Unidad de Medida", "Ej: Litros"),
            ("Contenido", "Ej: 2.5"),
            ("Precio Compra", "Ej: 100.50"),
            ("Precio Venta", "Ej: 120.00"),
            ("Stock Mínimo", "Ej: 10"),
            ("Stock Actual", "Ej: 50")
            ]
        combos_config = [
            ("Categoría", categorias, "Selecciona Categoría"),
            ("Marca", marcas, "Selecciona Marca")
            ]

        # Callback para guardar (crear producto)
        def accion_guardar_crear(valores):
            nuevo_producto = Producto(
                id_producto=None,
                nombre_producto=valores["nombre"],
                id_categoria=valores["id_categoria"],
                id_marca=valores["id_marca"],
                presentacion=valores["presentacion"],
                unidad_medida=valores["unidad_medida"],
                contenido=valores["contenido"],
                precio_compra=valores["precio_compra"],
                precio_venta=valores["precio_venta"],
                stock_minimo=valores["stock_minimo"],
                stock_actual=valores["stock_actual"],
                estatus=1
                )
            return dao.insertar_producto(nuevo_producto)

        # Abrir ventana
        self.abrir_ventana_formulario("Crear Nuevo Producto", campos_config, combos_config, accion_guardar_crear)

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