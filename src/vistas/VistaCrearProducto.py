import customtkinter as ctk
import tkinter as tk
from servicios.ProductoDAO import ProductoDAO
from modelos.Producto import Producto

class VistaCrearProducto(ctk.CTkToplevel):
	def __init__(self, parent, callback_actualizar):
		super().__init__(parent)
		self.title("Crear Nuevo Producto")
		self.geometry("420x600")
		self.callback_actualizar = callback_actualizar

		dao = ProductoDAO()
		self.categorias = dao.obtener_categorias()
		self.marcas = dao.obtener_marcas()

		self.campos = {}
		self._crear_formulario()

	def crear_combo(self, parent, nombre, opciones, placeholder):
		label = ctk.CTkLabel(parent, text=nombre)
        label.pack(pady=(10, 0))
        combo = ctk.CTkComboBox(parent, width=300, values=[f"{id} - {nombre}" for id, nombre in opciones], state="readonly")
        combo.set(placeholder)
        combo.pack(pady=(0, 10))
        self.campos[nombre] = combo

    def _crear_formulario(self):
    	scroll_frame = ctk.CTkScrollableFrame(ventana, width=380, height=500)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        def crear_campo(nombre, placeholder=""):
	        label = ctk.CTkLabel(scroll_frame, text=nombre)
	        label.pack(pady=(10, 0))
	        entry = ctk.CTkEntry(scroll_frame, width=300, placeholder_text=placeholder)
	        entry.pack(pady=(0, 10))
	        self.campos[nombre] = entry

	    crear_campo("Nombre Producto",  "Ej: Refresco Cola")
	    crear_campo("Presentación", "Ej: Botella")
	    crear_campo("Unidad de Medida", "Ej: Litros")
	    crear_campo("Contenido", "Ej: 2.5")
	    crear_campo("Precio Compra", "Ej: 100.50")
	    crear_campo("Precio Venta", "Ej: 120.00")
	    crear_campo("Stock Mínimo", "Ej: 10")
	    crear_campo("Stock Actual", "Ej: 50")

	    self.crear_combo(scroll_frame, "Categoría", self.categorias, "Selecciona una categoría")
	    self.crear_combo(scroll_frame, "Marca", self.categorias, "Selecciona una marca")

	    frame_botones = ctk.CTkFrame(self)
        frame_botones.pack(pady=20)

        btn_guardar = ctk.CTkButton(frame_botones, text="Guardar", command=self._guardar)
        btn_guardar.pack(side="left", padx=10)

        btn_cancelar = ctk.CTkButton(frame_botones, text="Cancelar", command=self.destroy)
        btn_cancelar.pack(side="left", padx=10)

    def _guardar(self):
        try:
            nombre = self.campos["Nombre Producto"].get().strip().title()
            presentacion = self.campos["Presentación"].get().strip()
            unidad_medida = self.campos["Unidad de Medida"].get().strip()
            contenido = float(self.campos["Contenido"].get())
            precio_compra = float(self.campos["Precio Compra"].get())
            precio_venta = float(self.campos["Precio Venta"].get())
            stock_minimo = int(self.campos["Stock Mínimo"].get())
            stock_actual = int(self.campos["Stock Actual"].get())

            categoria = self.campos["Categoría"].get()
            marca = self.campos["Marca"].get()

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

	        
	        if categoria == "Selecciona Categoría":
	            raise ValueError("Debes seleccionar una categoría.")
	        id_categoria = int(categoria_seleccionada.split(" - ")[0])

	        
	        if marca == "Selecciona Marca":
	            raise ValueError("Debes seleccionar una marca.")
	        id_marca = int(marca_seleccionada.split(" - ")[0])

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
                tk.messagebox.showinfo("Éxito", "Producto creado correctamente.")
                self.callback_actualizar()
                self.destroy()
            else:
                tk.messagebox.showerror("Error", "No se pudo crear el producto.")
        except ValueError as ve:
            tk.messagebox.showerror("Error de validación", str(ve))
        except Exception as e:
            tk.messagebox.showerror("Error inesperado", f"Ocurrió un error: {e}")