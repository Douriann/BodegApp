import customtkinter as ctk
import tkinter as tk
from servicios.ProductoDAO import ProductoDAO

class VistaModifProducto(ctk.CTkToplevel):
    def __init__(self, parent, producto, callback_actualizar):
        super().__init__(parent)
        self.title("Editar Producto")
        self.geometry("420x550")
        self.producto = producto
        self.callback_actualizar = callback_actualizar
        dao = ProductoDAO()
        self.categorias = dao.obtener_categorias()
        self.marcas = dao.obtener_marcas()


        self.campos = {}
        self._crear_formulario()
        
    def crear_combo(self, parent, nombre, opciones, seleccion_actual):
        label = ctk.CTkLabel(parent, text=nombre)
        label.pack(pady=(10, 0))
        combo = ctk.CTkComboBox(parent, width=300, values=[f"{id} - {nombre}" for id, nombre in opciones], state="readonly")
        combo.set(seleccion_actual)
        combo.pack(pady=(0, 10))
        self.campos[nombre] = combo


    def _crear_formulario(self):
        scroll_frame = ctk.CTkScrollableFrame(self, width=380, height=400)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        def crear_campo(nombre, valor_inicial):
            label = ctk.CTkLabel(scroll_frame, text=nombre)
            label.pack(pady=(10, 0))
            entry = ctk.CTkEntry(scroll_frame, width=300)
            entry.insert(0, str(valor_inicial))
            entry.pack(pady=(0, 10))
            self.campos[nombre] = entry

        crear_campo("Nombre", self.producto.nombre_producto)
        
        crear_campo("Presentación", self.producto.presentacion)
        crear_campo("Unidad de Medida", self.producto.unidad_medida)
        crear_campo("Contenido", self.producto.contenido)
        
         # Combobox de Categoría
        categoria_actual = next((f"{id} - {nombre}" for id, nombre in self.categorias if id == self.producto.id_categoria), "Selecciona Categoría")
        self.crear_combo(scroll_frame, "Categoría", self.categorias, categoria_actual)

        # Combobox de Marca
        marca_actual = next((f"{id} - {nombre}" for id, nombre in self.marcas if id == self.producto.id_marca), "Selecciona Marca")
        self.crear_combo(scroll_frame, "Marca", self.marcas, marca_actual)
        
        crear_campo("Precio Compra", self.producto.precio_compra)
        crear_campo("Precio Venta", self.producto.precio_venta)
        crear_campo("Stock Mínimo", self.producto.stock_minimo)
        crear_campo("Stock Actual", self.producto.stock_actual) 
         
       

        frame_botones = ctk.CTkFrame(self)
        frame_botones.pack(pady=20)

        btn_guardar = ctk.CTkButton(frame_botones, text="Guardar Cambios", command=self._guardar)
        btn_guardar.pack(side="left", padx=10)

        btn_cancelar = ctk.CTkButton(frame_botones, text="Cancelar", command=self.destroy)
        btn_cancelar.pack(side="left", padx=10)

    def _guardar(self):
        try:
            self.producto.nombre_producto = self.campos["Nombre"].get().strip()
            
            # Obtener valores de los combobox
            categoria_seleccionada = self.campos["Categoría"].get()
            marca_seleccionada = self.campos["Marca"].get()
            
            # Validar selección
            if not categoria_seleccionada or " - " not in categoria_seleccionada: 
                raise ValueError("Debes seleccionar una categoría válida.") 
            if not marca_seleccionada or " - " not in marca_seleccionada: 
                raise ValueError("Debes seleccionar una marca válida.")

            # Extraer IDs desde los combobox
            self.producto.id_categoria = int(categoria_seleccionada.split(" - ")[0])
            self.producto.id_marca = int(marca_seleccionada.split(" - ")[0])

            # Continuar con el resto de campos
            self.producto.presentacion = self.campos["Presentación"].get().strip()
            self.producto.unidad_medida = self.campos["Unidad de Medida"].get().strip()
            self.producto.contenido = float(self.campos["Contenido"].get())
            self.producto.precio_compra = float(self.campos["Precio Compra"].get())
            self.producto.precio_venta = float(self.campos["Precio Venta"].get())
            self.producto.stock_minimo = int(self.campos["Stock Mínimo"].get())
            self.producto.stock_actual = int(self.campos["Stock Actual"].get())

            dao = ProductoDAO()
            if dao.modificar_producto(self.producto):
                tk.messagebox.showinfo("Éxito", "El producto fue modificado correctamente.")
                self.callback_actualizar()
                self.destroy()
            else:
                tk.messagebox.showerror("Error", "No se pudo modificar el producto.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Ocurrió un error: {e}")
