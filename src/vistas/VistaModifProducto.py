import customtkinter as ctk
from servicios.ProductoDAO import ProductoDAO

class VentanaVerificacion(ctk.CTkToplevel):
    """Ventana de confirmación personalizada con estilo moderno."""
    def __init__(self, parent, titulo, mensaje):
        super().__init__(parent)
        self.title("Confirmación")
        self.geometry("350x200")
        
        # Configuraciones de prioridad
        self.attributes("-topmost", True)
        self.grab_set()  # Bloquea interacción con el padre hasta que se cierre
        self.resizable(False, False)
        
        # Centrado absoluto en la pantalla para evitar errores de coordenadas del padre
        self.update_idletasks()
        ancho_p = self.winfo_screenwidth()
        alto_p = self.winfo_screenheight()
        x = (ancho_p // 2) - 175
        y = (alto_p // 2) - 100
        self.geometry(f"350x200+{x}+{y}")

        self.main_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color="#ab3df4")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.lbl_titulo = ctk.CTkLabel(
            self.main_frame, text=titulo, 
            font=("Segoe UI", 18, "bold"), text_color="#ab3df4"
        )
        self.lbl_titulo.pack(pady=(20, 10))

        self.lbl_msj = ctk.CTkLabel(
            self.main_frame, text=mensaje, 
            font=("Segoe UI", 13), text_color=("#333333", "#D1D1D1"),
            wraplength=280
        )
        self.lbl_msj.pack(pady=10)

        self.btn_ok = ctk.CTkButton(
            self.main_frame, text="Entendido", 
            fg_color="#ab3df4", hover_color="#8f10e5",
            width=120, height=35, font=("Segoe UI", 13, "bold"),
            command=self.destroy
        )
        self.btn_ok.pack(pady=(10, 20))

class VistaModifProducto(ctk.CTkToplevel):
    def __init__(self, parent, producto, callback_actualizar):
        super().__init__(parent)
        
        self.title("Editar Producto")
        self.after(10, lambda: self.state('normal'))
        self.attributes("-topmost", True) 

        anchoVist = 500
        altoVist = 650
        self.update_idletasks()
        anchoPant = self.winfo_screenwidth()
        altoPant = self.winfo_screenheight()
        x = (anchoPant // 2) - (anchoVist // 2)
        y = (altoPant // 2) - (altoVist // 2)
        self.geometry(f"{anchoVist}x{altoVist}+{x}+{y}")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.producto = producto
        self.callback_actualizar = callback_actualizar

        dao = ProductoDAO()
        self.categorias = dao.obtener_categorias()
        self.marcas = dao.obtener_marcas()
        self.campos = {}

        self._construir_ui()

    def _construir_ui(self):
        self.bg_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bg_frame.pack(fill="both", expand=True)

        self.header_frame = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(20, 10), padx=30)
        
        self.lbl_titulo = ctk.CTkLabel(
            self.header_frame, text="DETALLES DEL PRODUCTO", 
            font=("Segoe UI", 20, "bold"), text_color=("#ab3df4", "#ab3df4") 
        )
        self.lbl_titulo.pack(side="left")

        self.scroll_body = ctk.CTkScrollableFrame(
            self.bg_frame, 
            fg_color=("white", "#1a1a1a"), 
            scrollbar_button_color=("#ab3df4", "#ab3df4"),
            corner_radius=15
        )
        self.scroll_body.pack(fill="both", expand=True, padx=20, pady=10)

        self._seccion_titulo("Información Principal")
        self._crear_entrada("Nombre", self.producto.nombre_producto, full_width=True)
        
        fila_datos = self._crear_fila()
        self._crear_entrada("Presentación", self.producto.presentacion, master=fila_datos)
        self._crear_entrada("Unidad de Medida", self.producto.unidad_medida, master=fila_datos)
        self._crear_entrada("Contenido", self.producto.contenido, full_width=True)
        
        self._seccion_titulo("Clasificación")
        cat_actual = next((f"{id_c} - {n}" for id_c, n in self.categorias if id_c == self.producto.id_categoria), "Seleccionar")
        self._crear_combo("Categoría", self.categorias, cat_actual)
        
        mar_actual = next((f"{id_m} - {n}" for id_m, n in self.marcas if id_m == self.producto.id_marca), "Seleccionar")
        self._crear_combo("Marca", self.marcas, mar_actual)

        self._seccion_titulo("Precios e Inventario")
        fila_precios = self._crear_fila()
        self._crear_entrada("Precio Compra", self.producto.precio_compra, master=fila_precios)
        self._crear_entrada("Precio Venta", self.producto.precio_venta, master=fila_precios)
        
        fila_stock = self._crear_fila()
        self._crear_entrada("Stock Actual", self.producto.stock_actual, master=fila_stock)
        self._crear_entrada("Stock Mínimo", self.producto.stock_minimo, master=fila_stock)

        self.footer = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        self.footer.pack(fill="x", side="bottom", padx=30, pady=20)

        self.btn_cancelar = ctk.CTkButton(
            self.footer, text="Cancelar", fg_color=("#E74C3C", "#E74C3C"), 
            hover_color=("#E1311D", "#E1311D"), width=210, height=40,
            font=("Segoe UI", 14, "bold"), command=self.destroy
        )
        self.btn_cancelar.pack(side="left")

        self.btn_guardar = ctk.CTkButton(
            self.footer, text="Guardar Cambios", fg_color=("#2CC985", "#26A46E"), 
            hover_color=("#26A46E", "#1D8356"), width=210, height=40, 
            font=("Segoe UI", 14, "bold"), command=self._guardar
        )
        self.btn_guardar.pack(side="right")

    def _seccion_titulo(self, texto):
        lbl = ctk.CTkLabel(self.scroll_body, text=texto.upper(), font=("Segoe UI", 11, "bold"), text_color=("#555555", "#888888"))
        lbl.pack(pady=(20, 5), padx=10, anchor="w")

    def _crear_fila(self):
        f = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        f.pack(fill="x")
        return f

    def _crear_entrada(self, nombre, valor, full_width=False, master=None):
        target = master if master else self.scroll_body
        container = ctk.CTkFrame(target, fg_color="transparent")
        container.pack(side="left" if not full_width else "top", fill="x", expand=True, padx=5, pady=5)
        lbl = ctk.CTkLabel(container, text=nombre, font=("Segoe UI", 12), text_color=("#333333", "#D1D1D1"))
        lbl.pack(anchor="w", padx=5)
        entry = ctk.CTkEntry(container, height=40)
        entry.insert(0, str(valor))
        entry.pack(fill="x", padx=5, pady=2)
        self.campos[nombre] = entry

    def _crear_combo(self, nombre, opciones, seleccion):
        container = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        container.pack(fill="x", padx=5, pady=5)
        lbl = ctk.CTkLabel(container, text=nombre, font=("Segoe UI", 12), text_color=("#333333", "#D1D1D1"))
        lbl.pack(anchor="w", padx=5)
        combo = ctk.CTkComboBox(
            container, height=40, values=[f"{id_v} - {n}" for id_v, n in opciones],
            state="readonly", button_color="#8f10e5", button_hover_color="#ab3df4",
            border_color="#8f10e5", dropdown_fg_color="#ffffff",
            dropdown_hover_color="#ab3df4", text_color=("#333333", "white"),
            dropdown_text_color="black" 
        )
        combo.set(seleccion)
        combo.pack(fill="x", padx=5, pady=2)
        self.campos[nombre] = combo

    def _guardar(self):
        try:
            self.producto.nombre_producto = self.campos["Nombre"].get().strip()
            self.producto.presentacion = self.campos["Presentación"].get().strip()
            self.producto.unidad_medida = self.campos["Unidad de Medida"].get().strip()

            cat_sel = self.campos["Categoría"].get()
            mar_sel = self.campos["Marca"].get()
            if " - " in cat_sel: self.producto.id_categoria = int(cat_sel.split(" - ")[0])
            if " - " in mar_sel: self.producto.id_marca = int(mar_sel.split(" - ")[0])

            self.producto.contenido = float(self.campos["Contenido"].get() or 0)
            self.producto.precio_compra = float(self.campos["Precio Compra"].get() or 0)
            self.producto.precio_venta = float(self.campos["Precio Venta"].get() or 0)
            self.producto.stock_actual = int(self.campos["Stock Actual"].get() or 0)
            self.producto.stock_minimo = int(self.campos["Stock Mínimo"].get() or 0)

            dao = ProductoDAO()
            if dao.modificar_producto(self.producto):
                # Guardamos referencia de la raíz de la aplicación
                app_root = self.master.winfo_toplevel()
                
                if self.callback_actualizar:
                    self.callback_actualizar()
                
                # CREACIÓN DE LA VENTANA DE ÉXITO
                VentanaVerificacion(app_root, "¡ÉXITO!", "Los cambios se guardaron correctamente.")
                
                # RETRASO DE 100ms para cerrar la ventana de edición. 
                # Esto permite que la ventana de verificación tome el foco antes de que esta desaparezca.
                self.after(100, self.destroy)
                
        except Exception as e:
            print(f"Error al guardar: {e}")