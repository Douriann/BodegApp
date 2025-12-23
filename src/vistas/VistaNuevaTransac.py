from tkinter import ttk
from tkinter import messagebox
import customtkinter as ctk
from servicios.ServBusqProduc import ServBusqProduc

class VistaNuevaTransac(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # 1. Configuración básica de la ventana emergente
        self.title("Nueva Transacción")
        
        # Hacemos que la ventana aparezca siempre al frente
        self.attributes("-topmost", True)

        # Widgets para la busqueda de productos
        self.producto_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.producto_frame.pack(pady=10, padx=20, fill="y", side="top")

        self.entry_buscar = ctk.CTkEntry(self.producto_frame, placeholder_text="Buscar producto por nombre", width=250)
        self.entry_buscar.pack(side="left", padx=(0,10))

        self.btn_buscar = ctk.CTkButton(self.producto_frame, text="Buscar", width=80, command=self.mostrar_producto_busqueda)
        self.btn_buscar.pack(side="left")

        # Creacion de tabla de productos
        self.tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tree_frame.pack(pady=10, padx=20, fill="y", side="left")
        columnas = ("id", "nombre", "marca", "stock")
        self.tabla_productos = ttk.Treeview(self.tree_frame, columns=columnas, show="headings", selectmode="browse")
        # Encabezados
        self.tabla_productos.heading("id", text="ID")
        self.tabla_productos.heading("nombre", text="Nombre")
        self.tabla_productos.heading("marca", text="Marca")
        self.tabla_productos.heading("stock", text="Stock")
        # Ancho y alineación
        self.tabla_productos.column("id", width=50, anchor="center")
        self.tabla_productos.column("nombre", width=150, anchor="center")
        self.tabla_productos.column("marca", width=100, anchor="center")
        self.tabla_productos.column("stock", width=80, anchor="center")
        self.tabla_productos.pack(side="left", fill="both", expand=True)
        # Scrollbar
        self.scrollbar_productos = ctk.CTkScrollbar(self.tree_frame, orientation="vertical", command=self.tabla_productos.yview)
        self.tabla_productos.configure(yscrollcommand=self.scrollbar_productos.set)
        self.scrollbar_productos.pack(side="right", fill="y")

        # Widgets del Formulario
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.pack(pady=20, padx=20, fill="x", side="right")
        self.label_titulo = ctk.CTkLabel(self.form_frame, text="Registrar Movimiento", font=("Roboto", 20, "bold"))
        self.label_titulo.pack(pady=20)

        # Campo: tipo de  transacción
        self.label_tipo = ctk.CTkLabel(self.form_frame, text="Tipo de Transacción:", font=("Roboto", 14))
        self.label_tipo.pack(pady=(10,0))
        # frame de radio buttons para form frame
        self.radio_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.radio_frame.pack(pady=5)
        self.radiobtn_compra = ctk.CTkRadioButton(self.radio_frame, text="Compra", value=1)
        self.radiobtn_compra.pack(pady=5, side="left")
        self.radiobtn_venta = ctk.CTkRadioButton(self.radio_frame, text="Venta", value=2)
        self.radiobtn_venta.pack(pady=5, side="right")

        # Campo: Descripción
        self.entry_desc = ctk.CTkEntry(self.form_frame, placeholder_text="Descripción (ej. Venta Teclado)", width=300)
        self.entry_desc.pack(pady=10)

        # 3. Botones de Acción
        self.btn_guardar = ctk.CTkButton(self.form_frame, text="Guardar", fg_color="#2CC985", hover_color="#26A46E")
        self.btn_guardar.pack(pady=20)

        self.btn_cancelar = ctk.CTkButton(self.form_frame, text="Cancelar", command=self.destroy, fg_color="transparent", border_width=1)
        self.btn_cancelar.pack(pady=(0, 20))

        # Widgets para confirmar el producto en venta
        self.anadir_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.anadir_frame.pack(pady=10,  side="bottom")

        self.btn_agregar = ctk.CTkButton(self.anadir_frame, text="Agregar Producto", width=150, command=self.actualizar_detalles_transaccion)
        self.btn_agregar.pack(side="left", padx=(0,10))
        # frame dentro del frame añadir para los botones de cantidad
        self.cantidad_frame = ctk.CTkFrame(self.anadir_frame, fg_color="transparent")
        self.cantidad_frame.pack(side="right")

        self.btn_restar = ctk.CTkButton(self.cantidad_frame, text="-", width=30, command=self.reducir_cantidad)
        self.btn_restar.pack(side="left", padx=(0,5))

        self.label_cantidad = ctk.CTkLabel(self.cantidad_frame, text="1", width=30, anchor="center")
        self.label_cantidad.pack(side="left")

        self.btn_sumar = ctk.CTkButton(self.cantidad_frame, text="+", width=30, command=self.incrementar_cantidad)
        self.btn_sumar.pack(side="left", padx=(5,0))
        # frame para manejar los detalles de la transacción
        self.detalles_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.detalles_frame.pack(pady=10, padx=20, fill="y", side="right")
        self.label_detalles = ctk.CTkLabel(self.detalles_frame, text="Detalles de la Transacción", font=("Roboto", 16, "bold"))
        self.label_detalles.pack(pady=10)
        self.label_detalles_info = ctk.CTkLabel(self.detalles_frame, text="", font=("Roboto", 12))
        self.label_detalles_info.pack(pady=10)

        self.mostrar_productos()

    def mostrar_productos(self):
        """
        Llena la tabla de productos con una lista de objetos Producto.
        """
        # Limpiar la tabla antes de llenarla
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)

        # Instanciar el servicio de búsqueda de productos
        servicio = ServBusqProduc()
        lista_productos = servicio.buscar_productos_totales()

        for producto in lista_productos:
            self.tabla_productos.insert("", "end", values=(
                producto.id_producto,
                producto.nombre_producto,
                producto.id_marca,
                producto.stock_actual
            ))

    def mostrar_producto_busqueda(self):
        """
        Llena la tabla de productos con una lista de objetos Producto.
        """
        # Limpiar la tabla antes de llenarla
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)
        # Instanciar el servicio de búsqueda de productos
        nombre_product = self.entry_buscar.get()
        servicio = ServBusqProduc()
        lista_productos = servicio.buscar_productos_por_nombre(nombre_product)
        for producto in lista_productos:
            self.tabla_productos.insert("", "end", values=(
                producto.id_producto,
                producto.nombre_producto,
                producto.id_marca,
                producto.stock_actual
            ))
    # creacion de un metodo para actualizar la cantidad en el label
    def actualizar_cantidad(self, nueva_cantidad):
        # devuelve el valor numerico del label cantidad
        nueva_cantidad = max(1, nueva_cantidad)  # Asegura que la cantidad no sea menor a 1
        self.label_cantidad.configure(text=str(nueva_cantidad))
    def incrementar_cantidad(self):
        cantidad_actual = int(self.label_cantidad.cget("text"))
        self.actualizar_cantidad(cantidad_actual + 1)
    def reducir_cantidad(self):
        cantidad_actual = int(self.label_cantidad.cget("text"))
        self.actualizar_cantidad(cantidad_actual - 1)
    # creacion de metodo para actualizar los detalles de la transaccion
    def actualizar_detalles_transaccion(self):
        if self.tabla_productos.selection():
            selected_item = self.tabla_productos.focus()
            producto_values = self.tabla_productos.item(selected_item, "values")
            id_producto = producto_values[0]
            nombre_producto = producto_values[1]
            cantidad = self.label_cantidad.cget("text")
            detalles_text = f"Producto ID: {id_producto}\nNombre: {nombre_producto}\nCantidad: {cantidad}"
            valor_anterio = self.label_detalles_info.cget("text")
            if int(cantidad) > int(producto_values[3]):
                messagebox.showerror("Error", "Cantidad solicitada excede el stock disponible.")
                self.label_cantidad.configure(text="1")
                return
            if valor_anterio:
                detalles_text += f"\n {valor_anterio}"
            self.label_detalles_info.configure(text=detalles_text)
            self.label_cantidad.configure(text="1")
        else:
            return
