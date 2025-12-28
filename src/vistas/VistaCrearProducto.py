import customtkinter as ctk
from tkinter import messagebox  # Corregido: Importación necesaria
from servicios.ProductoDAO import ProductoDAO
from modelos.Producto import Producto

class VistaCrearProducto(ctk.CTkToplevel):
    def __init__(self, parent, callback_actualizar):
        super().__init__(parent)
        self.title("Crear Nuevo Producto")
        self.after(10, lambda: self.state('normal'))
        self.attributes("-topmost", True) # La mantiene arriba pero permite minimizar
        
        #Centrado la ventana en la pantalla
        anchoVist = 450
        altoVist = 650
        
        self.update_idletasks()
        
        anchoPant = self.winfo_screenwidth()
        altoPant = self.winfo_screenheight()

        x = (anchoPant // 2) - (anchoVist // 2)
        y = (altoPant // 2) - (altoVist // 2)

        self.geometry(f"{anchoVist}x{altoVist}+{x}+{y}")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.callback_actualizar = callback_actualizar
        
        # Colores consistentes
        self.color_morado = "#ab3df4"
        self.color_morado_hover = "#8e24aa"

        dao = ProductoDAO()
        self.categorias = dao.obtener_categorias()
        self.marcas = dao.obtener_marcas()

        self.campos = {}
        self._crear_formulario()

    def crear_combo(self, parent, nombre, opciones, placeholder):
        label = ctk.CTkLabel(parent, text=nombre, font=("Segoe UI", 13, "bold"))
        label.pack(pady=(10, 0))
        
        # ComboBox
        combo = ctk.CTkComboBox(
            parent, 
            width=350, 
            height=38,
            values=[f"{id_val} - {n}" for id_val, n in opciones], 
            state="readonly",
            button_color=self.color_morado,
            button_hover_color=self.color_morado_hover,
            border_color=self.color_morado,
            text_color=("#333333", "white"),               
            dropdown_text_color="black",      # Texto de la lista en oscuro
            dropdown_fg_color="#ffffff",      # Fondo del desplegable claro
            dropdown_hover_color=self.color_morado
        )
        combo.set(placeholder)
        combo.pack(pady=(0, 10))
        self.campos[nombre] = combo

    def _crear_formulario(self):
        # Frame de desplazamiento
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color="#ab3df4",
            scrollbar_button_hover_color="#c06ef7")
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        def crear_campo(nombre, placeholder=""):
            label = ctk.CTkLabel(scroll_frame, text=nombre, font=("Segoe UI", 13, "bold"))
            label.pack(pady=(10, 0))
            entry = ctk.CTkEntry(scroll_frame, width=350, height=38, placeholder_text=placeholder)
            entry.pack(pady=(0, 10))
            self.campos[nombre] = entry    

        # Campos de texto
        crear_campo("Nombre Producto", "Ej: Refresco Cola")
        crear_campo("Presentación", "Ej: Botella")
        crear_campo("Unidad de Medida", "Ej: Litros")
        crear_campo("Contenido", "Ej: 2.5")
        crear_campo("Precio Compra", "Ej: 100.50")
        crear_campo("Precio Venta", "Ej: 120.00")
        crear_campo("Stock Mínimo", "Ej: 10")
        crear_campo("Stock Actual", "Ej: 50")

        # Combos (Categoría y Marca)
        self.crear_combo(scroll_frame, "Categoría", self.categorias, "Selecciona Categoría")
        self.crear_combo(scroll_frame, "Marca", self.marcas, "Selecciona Marca")

        # Frame de botones (Fuera del scroll para que siempre sean visibles)
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(pady=20, fill="x")

        btn_guardar = ctk.CTkButton(
            frame_botones, 
            text="Guardar", 
            font=("Segoe UI", 14, "bold"),
            fg_color="#2CC985", 
            hover_color="#26A46E",
            height=40,
            command=self._guardar
        )
        btn_guardar.pack(side="right", padx=(10, 40), expand=True, fill="x")

        btn_cancelar = ctk.CTkButton(
            frame_botones, 
            text="Cancelar", 
            font=("Segoe UI", 14, "bold"),
            fg_color="#E74C3C", 
            hover_color="#DB2B18",
            height=40,
            command=self.destroy
        )
        btn_cancelar.pack(side="right", padx=(40, 10), expand=True, fill="x")

    def _guardar(self):
        try:
            # Validación y recolección de datos
            nombre = self.campos["Nombre Producto"].get().strip().title()
            presentacion = self.campos["Presentación"].get().strip()
            unidad = self.campos["Unidad de Medida"].get().strip()
            
            # Conversiones numéricas con validación
            contenido = float(self.campos["Contenido"].get())
            precio_compra = float(self.campos["Precio Compra"].get())
            precio_venta = float(self.campos["Precio Venta"].get())
            stock_minimo = int(self.campos["Stock Mínimo"].get())
            stock_actual = int(self.campos["Stock Actual"].get())

            if not nombre or nombre.isdigit():
                raise ValueError("El nombre no es válido.")
            if contenido <= 0:
                raise ValueError("El contenido debe ser mayor a 0.")

            # Obtener IDs de los ComboBox
            categoria_sel = self.campos["Categoría"].get()
            marca_sel = self.campos["Marca"].get()

            if "Selecciona" in categoria_sel or " - " not in categoria_sel:
                raise ValueError("Selecciona una Categoría de la lista.")
            if "Selecciona" in marca_sel or " - " not in marca_sel:
                raise ValueError("Selecciona una Marca de la lista.")

            id_categoria = int(categoria_sel.split(" - ")[0])
            id_marca = int(marca_sel.split(" - ")[0])

            nuevo_producto = Producto(
                id_producto=None,
                nombre_producto=nombre,
                id_categoria=id_categoria,
                id_marca=id_marca,
                presentacion=presentacion,
                unidad_medida=unidad,
                contenido=contenido,
                precio_compra=precio_compra,
                precio_venta=precio_venta,
                stock_minimo=stock_minimo,
                stock_actual=stock_actual,
                estatus=1
            )

            dao = ProductoDAO()
            if dao.insertar_producto(nuevo_producto):
                messagebox.showinfo("Éxito", "Producto creado correctamente.")
                self.callback_actualizar()
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo guardar en la base de datos.")

        except ValueError as ve:
            messagebox.showerror("Error de entrada", f"Dato inválido: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió algo inesperado: {e}")