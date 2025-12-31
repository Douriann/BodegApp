import customtkinter as ctk
from servicios.ProductoDAO import ProductoDAO
from modelos.Producto import Producto
from vistas.VistaCategoria import VistaCategoria
from vistas.VistaMarca import VistaMarca

class VentanaVerificacion(ctk.CTkToplevel):
    """Ventana de aviso personalizada para Éxito o Error."""
    def __init__(self, parent, titulo, mensaje, es_error=False):
        super().__init__(parent)
        self.title("Aviso")
        self.geometry("350x220")
        self.attributes("-topmost", True)
        self.grab_set() 
        self.resizable(False, False)
        
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
            command=self.destroy
        )
        self.btn_ok.pack(pady=(10, 20))

class VistaCrearProducto(ctk.CTkToplevel):
    def __init__(self, parent, callback_actualizar):
        super().__init__(parent)
        self.title("Crear Nuevo Producto")
        self.after(10, lambda: self.state('normal'))
        self.attributes("-topmost", True) 
        
        anchoVist = 450
        altoVist = 650
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

        dao = ProductoDAO()
        self.categorias = dao.obtener_categorias()
        self.marcas = dao.obtener_marcas()

        self.campos = {}
        self._crear_formulario()

    def crear_combo(self, parent, nombre, opciones, placeholder):
        label = ctk.CTkLabel(parent, text=nombre, font=("Segoe UI", 13, "bold"))
        label.pack(pady=(10, 0))
        
        combo = ctk.CTkComboBox(
            parent, width=350, height=38,
            values=[f"{id_val} - {n}" for id_val, n in opciones], 
            state="readonly",
            button_color=self.color_morado,
            button_hover_color=self.color_morado_hover,
            border_color=self.color_morado,
            text_color=("#333333", "white"),               
            dropdown_text_color="black",      
            dropdown_fg_color="#ffffff",      
            dropdown_hover_color=self.color_morado
        )
        combo.set(placeholder)
        combo.pack(pady=(0, 10))
        self.campos[nombre] = combo

    def _crear_formulario(self):
        scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", 
            scrollbar_button_color="#ab3df4",
            scrollbar_button_hover_color="#c06ef7"
        )
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        def crear_campo(nombre, placeholder=""):
            label = ctk.CTkLabel(scroll_frame, text=nombre, font=("Segoe UI", 13, "bold"))
            label.pack(pady=(10, 0))
            # Guardamos el borde original para poder restaurarlo
            entry = ctk.CTkEntry(scroll_frame, width=350, height=38, placeholder_text=placeholder)
            entry.pack(pady=(0, 10))
            self.campos[nombre] = entry    

        crear_campo("Nombre Producto", "Ej: Refresco Cola")
        crear_campo("Presentación", "Ej: Botella")
        crear_campo("Unidad de Medida", "Ej: Litros")
        crear_campo("Contenido", "Ej: 2.5")
        crear_campo("Precio Compra", "Ej: 100.50")
        crear_campo("Precio Venta", "Ej: 120.00")
        crear_campo("Stock Mínimo", "Ej: 10")
        crear_campo("Stock Actual", "Ej: 50")

        self.crear_combo(scroll_frame, "Categoría", self.categorias, "Selecciona Categoría")
        self.btn_crear_categoria = ctk.CTkButton(
            scroll_frame, text="Crear Nueva Categoría",
            width=200, height=35,
            fg_color=self.color_morado,
            hover_color=self.color_morado_hover,
            command=self.abrir_vista_categoria
        )
        self.btn_crear_categoria.pack(pady=(10, 10))
        self.crear_combo(scroll_frame, "Marca", self.marcas, "Selecciona Marca")
        self.btn_crear_marca = ctk.CTkButton(
            scroll_frame, text="Crear Nueva Marca",
            width=200, height=35,
            fg_color=self.color_morado,
            hover_color=self.color_morado_hover,
            command=self.abrir_vista_marca
        )
        self.btn_crear_marca.pack(pady=(10, 10))
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(pady=20, fill="x")

        btn_guardar = ctk.CTkButton(
            frame_botones, text="Guardar", font=("Segoe UI", 14, "bold"),
            fg_color="#2CC985", hover_color="#26A46E", height=40,
            command=self._guardar
        )
        btn_guardar.pack(side="right", padx=(10, 40), expand=True, fill="x")

        btn_cancelar = ctk.CTkButton(
            frame_botones, text="Cancelar", font=("Segoe UI", 14, "bold"),
            fg_color="#E74C3C", hover_color="#DB2B18", height=40,
            command=self.destroy
        )
        btn_cancelar.pack(side="right", padx=(40, 10), expand=True, fill="x")

    def abrir_vista_marca(self):
        def actualizar_marcas():
            self.marcas = ProductoDAO().obtener_marcas()
            combo_marca = self.campos["Marca"]
            combo_marca.configure(values=[f"{id_val} - {n}" for id_val, n in self.marcas])
            combo_marca.set("Selecciona Marca")

        vista_marca = VistaMarca(self, actualizar_marcas)
        vista_marca.grab_set()

    def abrir_vista_categoria(self):
        def actualizar_categorias():
            self.categorias = ProductoDAO().obtener_categorias()
            combo_categoria = self.campos["Categoría"]
            combo_categoria.configure(values=[f"{id_val} - {n}" for id_val, n in self.categorias])
            combo_categoria.set("Selecciona Categoría")

        vista_categoria = VistaCategoria(self, actualizar_categorias)
        vista_categoria.grab_set()

    def _guardar(self):
        try:
            campos_vacios = []
            
            # Limpiar resaltados previos antes de validar
            for widget in self.campos.values():
                widget.configure(border_color=self.color_morado if isinstance(widget, ctk.CTkComboBox) else ("#979da2", "#565b5e"))

            # 1. Identificar campos vacíos o sin selección
            for nombre, widget in self.campos.items():
                valor = widget.get().strip()
                if not valor or "Selecciona" in valor:
                    campos_vacios.append(nombre)
                    widget.configure(border_color=self.color_error) # Marcar en rojo

            # 2. Lógica de mensajes según cantidad de vacíos
            if len(campos_vacios) > 2:
                VentanaVerificacion(self, "VARIOS CAMPOS INCOMPLETOS", 
                                    f"Faltan {len(campos_vacios)} campos por rellenar. Los hemos marcado en rojo para ti.", 
                                    es_error=True)
                return
            elif len(campos_vacios) > 0:
                nombres_faltantes = ", ".join(campos_vacios)
                VentanaVerificacion(self, "CAMPOS INCOMPLETOS", 
                                    f"Por favor completa: {nombres_faltantes}", 
                                    es_error=True)
                return

            # 3. Recolección de datos
            nombre = self.campos["Nombre Producto"].get().strip().title()
            presentacion = self.campos["Presentación"].get().strip()
            unidad = self.campos["Unidad de Medida"].get().strip()
            
            # 4. Validaciones numéricas
            try:
                contenido = float(self.campos["Contenido"].get())
                precio_compra = float(self.campos["Precio Compra"].get())
                precio_venta = float(self.campos["Precio Venta"].get())
                stock_minimo = int(self.campos["Stock Mínimo"].get())
                stock_actual = int(self.campos["Stock Actual"].get())
            except ValueError:
                VentanaVerificacion(self, "ERROR DE FORMATO", "Los campos numéricos contienen letras o símbolos inválidos.", es_error=True)
                return

            # 5. Obtener IDs
            id_categoria = int(self.campos["Categoría"].get().split(" - ")[0])
            id_marca = int(self.campos["Marca"].get().split(" - ")[0])

            nuevo_producto = Producto(
                id_producto=None, nombre_producto=nombre, id_categoria=id_categoria,
                id_marca=id_marca, presentacion=presentacion, unidad_medida=unidad,
                contenido=contenido, precio_compra=precio_compra, precio_venta=precio_venta,
                stock_minimo=stock_minimo, stock_actual=stock_actual, estatus=1
            )

            dao = ProductoDAO()
            if dao.insertar_producto(nuevo_producto):
                app_root = self.master.winfo_toplevel()
                if self.callback_actualizar:
                    self.callback_actualizar()
                
                VentanaVerificacion(app_root, "¡ÉXITO!", "Producto creado correctamente.")
                self.after(100, self.destroy)
            else:
                VentanaVerificacion(self, "ERROR", "No se pudo guardar en la base de datos.", es_error=True)

        except Exception as e:
            VentanaVerificacion(self, "ERROR INESPERADO", str(e), es_error=True)