from tkinter import messagebox
import customtkinter as ctk
from servicios.ServBusqProduc import ServBusqProduc
from servicios.ServTransac import ServTransac
from modelos.Transaccion import Transaccion
from modelos.DetalleTransaccion import DetalleTransaccion
from datetime import datetime
from servicios.BCVdatos import BcvScraper

class VistaNuevaTransac(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Nueva Transacción")
        self.attributes("-topmost", True)
        self.producto_seleccionado = None  # Para guardar la fila elegida

        #Centrado la ventana en la pantalla
        anchoVist = 1000
        altoVist = 650
        
        self.update_idletasks()
        
        anchoPant = self.winfo_screenwidth()
        altoPant = self.winfo_screenheight()

        x = (anchoPant // 2) - (anchoVist // 2)
        y = (altoPant // 2) - (altoVist // 2)

        self.geometry(f"{anchoVist}x{altoVist}+{x}+{y}")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- CONTENEDOR PRINCIPAL ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # --- LADO IZQUIERDO: BÚSQUEDA Y TABLA ---
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # Buscador
        self.busqueda_frame = ctk.CTkFrame(self.left_container, fg_color="transparent")
        self.busqueda_frame.pack(fill="x", pady=(0, 15))

        self.entry_buscar = ctk.CTkEntry(self.busqueda_frame, placeholder_text="Buscar producto por nombre...", width=460, height=35)
        self.entry_buscar.pack(side="left", padx=(0, 10))

        self.btn_buscar = ctk.CTkButton(self.busqueda_frame, text="Buscar", width=100, height=35, 
                                       fg_color="#ab3df4", hover_color="#c06ef7", command=self.mostrar_producto_busqueda)
        self.btn_buscar.pack(side="left")

        # --- TABLA MODERNA (Encabezado) ---
        self.header_tabla = ctk.CTkFrame(self.left_container, fg_color="transparent", height=30)
        self.header_tabla.pack(fill="x")
        self.header_tabla.pack_propagate(False)

        headers = [("ID", 0.1), ("NOMBRE", 0.6), ("MARCA", 0.4), ("STOCK", 0.2)]
        for text, relx in headers:
            ctk.CTkLabel(self.header_tabla, text=text, font=("Segoe UI", 13, "bold"), text_color="#ab3df4").place(relx=relx, rely=0.5, anchor="w")

        # Contenedor de filas con Scroll
        self.scroll_productos = ctk.CTkScrollableFrame(self.left_container, fg_color="#1e1e1e", corner_radius=10)
        self.scroll_productos.pack(fill="both", expand=True, pady=5)

        # --- LADO DERECHO: FORMULARIO Y DETALLES ---
        self.right_container = ctk.CTkFrame(self, fg_color="#2D2D2D", width=350, corner_radius=15)
        self.right_container.pack(side="right", fill="both", padx=20, pady=20)
        self.right_container.pack_propagate(False)

        self.label_titulo = ctk.CTkLabel(self.right_container, text="Registrar Transacción", font=("Segoe UI", 20, "bold"))
        self.label_titulo.pack(pady=20)

        # Radio Buttons
        self.val_tipo_transac = ctk.IntVar(value=0)
        self.label_tipo = ctk.CTkLabel(self.right_container, text="Tipo de Transacción:", font=("Segoe UI", 14, "bold"))
        self.label_tipo.pack(pady=(10, 5))
        self.radio_frame = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.radio_frame.pack(pady=5)
        self.radiobtn_compra = ctk.CTkRadioButton(self.radio_frame, text="Compra", value=1, border_color="#ab3df4", hover_color="#c06ef7",variable=self.val_tipo_transac, command=self.calcular_totales)
        self.radiobtn_compra.pack(side="left", padx=40)
        self.radiobtn_venta = ctk.CTkRadioButton(self.radio_frame, text="Venta", value=2, border_color="#ab3df4", hover_color="#c06ef7", variable=self.val_tipo_transac, command=self.calcular_totales)
        self.radiobtn_venta.pack(side="left", padx=0)

        self.entry_desc = ctk.CTkEntry(self.right_container, placeholder_text="Descripción", width=290)
        self.entry_desc.pack(pady=15)

        # Control de Cantidad
        self.cant_frame = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.cant_frame.pack(pady=10)
        ctk.CTkButton(self.cant_frame, text="-", width=35, fg_color="#780ac1", hover_color="#ab3df4", command=self.reducir_cantidad).pack(side="left")
        self.label_cantidad = ctk.CTkLabel(self.cant_frame, text="1", font=("Segoe UI", 16, "bold"), width=50)
        self.label_cantidad.pack(side="left")
        ctk.CTkButton(self.cant_frame, text="+", width=35, fg_color="#780ac1", hover_color="#ab3df4", command=self.incrementar_cantidad).pack(side="left")

        self.btn_agregar = ctk.CTkButton(self.right_container, width=120, text="Añadir a Lista", fg_color="#ab3df4", hover_color="#c06ef7", command=self.actualizar_detalles_transaccion)
        self.btn_agregar.pack(pady=10)

        # --- Área de Detalles Estilizada ---
        self.detalles_card = ctk.CTkFrame(self.right_container, fg_color="#1e1e1e", corner_radius=10, border_width=1, border_color="#333333", width=290, height=100)
        self.detalles_card.pack(pady=10, padx=15, fill="both", expand=True)
        self.detalles_card.pack_propagate(False)

        # Título de la sección de detalles
        self.titulo_detalles = ctk.CTkLabel(
            self.detalles_card, 
            text="DETALLES DE LA LISTA", 
            font=("Segoe UI", 16, "bold"),
        )
        self.titulo_detalles.pack(pady=(10, 5), padx=10)

        # Línea divisoria sutil
        self.separador = ctk.CTkFrame(self.detalles_card, fg_color="#333333", height=1)
        self.separador.pack(fill="x", padx=10, pady=5)

        # --- NUEVO: ScrollableFrame interno para el contenido ---
        self.scroll_interno_detalles = ctk.CTkScrollableFrame(self.detalles_card, fg_color="transparent", corner_radius=0)
        self.scroll_interno_detalles.pack(fill="both", expand=True, padx=2, pady=2)

        # El label ahora va dentro de scroll_interno_detalles
        self.label_detalles_info = ctk.CTkLabel(
        self.scroll_interno_detalles, # Cambiado aquí
        text="", 
        font=("Segoe UI", 13), 
        justify="left",
        anchor="nw" 
        )
        self.label_detalles_info.pack(pady=10, padx=15, fill="both", expand=True)

        self.mostrar_productos()

        # --- CONTENEDOR DE BOTONES (Guardar y Cancelar juntos) ---
        self.botones_final_frame = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.botones_final_frame.pack(side="bottom", fill="x", pady=20, padx=20)

        # Botón Guardar (Izquierda dentro del frame)
        self.btn_guardar = ctk.CTkButton(
            self.botones_final_frame, 
            text="Guardar", 
            fg_color="#2CC985", 
            hover_color="#26A46E", 
            font=("Segoe UI", 14, "bold"),
            height=40,
            width=140,
            command=self.obtener_datos_transaccion # Ancho fijo para que sean simétricos,
        )
        self.btn_guardar.pack(side="right", expand=True, padx=(0, 5))

        # Botón Cancelar (Derecha dentro del frame)
        self.btn_cancelar = ctk.CTkButton(
            self.botones_final_frame, 
            text="Cancelar", 
            fg_color="#E74C3C", 
            hover_color="#DB2B18",
            font=("Segoe UI", 14, "bold"),
            height=40,
            width=140,
            command=self.limpiar_formulario
        )
        self.btn_cancelar.pack(side="left", expand=True, padx=(5, 0))
        #  Labels para total en USD y  en bolivares
        self.frame_totales = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.frame_totales.pack(side="bottom", fill="x", pady=(0, 10), padx=20)
        self.label_total_usd = ctk.CTkLabel(self.frame_totales, text="Total (USD): $0.00", font=("Segoe UI", 14, "bold"))
        self.label_total_usd.pack(side="left", padx=5)
        self.label_total_bs = ctk.CTkLabel(self.frame_totales, text="Total (BS): Bs 0.00", font=("Segoe UI", 14, "bold"))
        self.label_total_bs.pack(side="right", padx=5)

        # atributo para almacenar producto seleccionado
        self.lista_productos_seleccionados = []
        self.lista_cantidades = []
        self.lista_subtotales = []
        self.bcv = BcvScraper()

    def crear_fila_producto(self, producto):
        fila = ctk.CTkFrame(self.scroll_productos, fg_color="transparent", height=40, corner_radius=5)
        fila.pack(fill="x", pady=2)
        fila.pack_propagate(False)

        # Eventos de Cursor
        def on_enter(e):
            if self.producto_seleccionado != fila:
                fila.configure(fg_color="#333333")
        
        def on_leave(e):
            if self.producto_seleccionado != fila:
                fila.configure(fg_color="transparent")

        #Seleccion de fila en la tabla despues de buscarlo en la barra
        def on_click(e):
            # 1. Verificamos que exista la variable Y que el widget siga vivo en la interfaz
            if self.producto_seleccionado and self.producto_seleccionado.winfo_exists():
                try:
                    self.producto_seleccionado.configure(fg_color="transparent")
                except Exception:
                    # Si falla por alguna razón de tiempo, simplemente ignoramos
                    pass

            # 2. Actualizamos a la nueva fila seleccionada
            self.producto_seleccionado = fila
            self.fila_data = producto

            # 3. Validamos que la nueva fila también exista antes de mostrarla
            if fila.winfo_exists():
                fila.configure(fg_color="#444444")

        # Datos en la tabla
        cols = [(f"#{producto.id_producto}", 0.1), (producto.nombre_producto, 0.6), 
                (str(producto.id_marca), 0.4), (str(producto.stock_actual), 0.2)]
        
        for txt, rx in cols:
            l = ctk.CTkLabel(fila, text=txt, font=("Segoe UI", 14))
            l.place(relx=rx, rely=0.5, anchor="w")
            l.bind("<Button-1>", on_click) # Permitir clic en el texto también
            # Hacer que el hover funcione también sobre los widgets hijos
            l.bind("<Enter>", on_enter)
            l.bind("<Leave>", on_leave)
            try:
                l.configure(cursor="hand2")
            except Exception:
                pass

        # Bindear también al frame de fila para que los clics/hover en el espacio libre funcionen
        fila.bind("<Enter>", on_enter)
        fila.bind("<Leave>", on_leave)
        fila.bind("<Button-1>", on_click)

    def mostrar_productos(self):
        for child in self.scroll_productos.winfo_children():
            child.destroy()
        servicio = ServBusqProduc()
        lista_productos = servicio.buscar_productos_totales()
        for p in lista_productos:
            self.crear_fila_producto(p)

    def mostrar_producto_busqueda(self):
        for child in self.scroll_productos.winfo_children():
            child.destroy()
        nombre = self.entry_buscar.get()
        servicio = ServBusqProduc()
        lista_productos = servicio.buscar_productos_por_nombre(nombre)
        for p in lista_productos:
            self.crear_fila_producto(p)

    def actualizar_cantidad(self, nueva_cantidad):
        nueva_cantidad = max(1, nueva_cantidad)
        self.label_cantidad.configure(text=str(nueva_cantidad))

    def incrementar_cantidad(self):
        self.actualizar_cantidad(int(self.label_cantidad.cget("text")) + 1)

    def reducir_cantidad(self):
        self.actualizar_cantidad(int(self.label_cantidad.cget("text")) - 1)

    def actualizar_detalles_transaccion(self):
        if self.validar_radio_buttons() is False:
            return
        if hasattr(self, 'fila_data'):
            p = self.fila_data
            self.lista_productos_seleccionados.append(p)
            cantidad = self.label_cantidad.cget("text")
            if int(cantidad) > int(p.stock_actual):
                messagebox.showerror("Error", "Stock insuficiente.", parent=self)
                return
            self.lista_cantidades.append(int(cantidad))
            nuevo_texto = f"• {p.nombre_producto} (x{cantidad})"
            actual = self.label_detalles_info.cget("text")
            self.label_detalles_info.configure(text=f"{actual}\n{nuevo_texto}" if actual else nuevo_texto)
            self.label_cantidad.configure(text="1")
            self.calcular_totales()
        else:
            messagebox.showwarning("Atención", "Seleccione un producto de la lista.", parent=self)

    def validar_radio_buttons(self):
        tipo_seleccionado = self.val_tipo_transac.get()
        if tipo_seleccionado != 1 and tipo_seleccionado != 2:
            messagebox.showwarning("Atención", "Seleccione un tipo de transacción (Compra o Venta).", parent=self)
            return False
        return True
    
    def obtener_datos_transaccion(self):
        tipo_transaccion = self.val_tipo_transac.get()
        descripcion = self.entry_desc.get()
        detalles = []
        if self.lista_productos_seleccionados:
            for producto in self.lista_productos_seleccionados:
                indice = self.lista_productos_seleccionados.index(producto)
                detalle = DetalleTransaccion(
                    id_detalle=None,
                    id_transaccion=None,
                    id_producto=producto.id_producto,
                    cantidad_producto=self.lista_cantidades[indice],
                    subtotal=self.lista_subtotales[indice],
                    estatus=1 
                )
                detalles.append(detalle)
            transaccion = Transaccion(
                id_transaccion=None,
                fecha_transaccion=datetime.now().strftime("%Y-%m-%d"),
                id_tipo=tipo_transaccion,
                total=sum(self.lista_subtotales),
                observaciones=descripcion if descripcion else "Sin observaciones",
                estatus=1
            )
            serv_transac = ServTransac()
            serv_transac.agregar_transaccion(transaccion, detalles)
            self.limpiar_formulario()
            # Intentar refrescar directamente al padre y emitir un evento virtual como respaldo
            try:
                parent = getattr(self, 'master', None)
                if parent is not None:
                    # Llamada directa al método si existe (más confiable)
                    if hasattr(parent, 'cargar_datos'):
                        try:
                            parent.cargar_datos()
                        except Exception:
                            pass
                    # Emitir evento virtual para handlers registrados
                    try:
                        parent.event_generate("<<TransaccionCreada>>")
                    except Exception:
                        pass
            except Exception:
                pass
            # Mostrar mensaje sobre esta ventana antes de cerrarla
            messagebox.showinfo("Éxito", "Transacción guardada correctamente.", parent=self)
            # Cerrar la ventana de nueva transacción
            try:
                self.destroy()
            except Exception:
                pass
            #for det in detalles:
            #    print(f"Detalle - Producto ID: {det.id_producto}, Cantidad: {det.cantidad_producto}, Subtotal: {det.subtotal}")
        else:
            messagebox.showerror("Error", "No se ha realizado la transacción", parent=self)
            return
    #metodo para mostrar el total en USD y en bolivares dependiendo de los productos y el radiobutton seleccionado
    def calcular_totales(self):
        total_usd = 0.0
        if self.lista_productos_seleccionados:
            self.lista_subtotales.clear()
            for producto in self.lista_productos_seleccionados:
                indice = self.lista_productos_seleccionados.index(producto)
                cantidad = self.lista_cantidades[indice]
                precio_select = self.obtener_precio_select(producto)
                total_usd += precio_select * cantidad  # Ajustar según el precio real
                self.lista_subtotales.append(precio_select * cantidad)
            total_bs = total_usd * self.bcv.obtener_tasa_con_respaldo().get('tasa', 0)  # Suponiendo una tasa de cambio fija para el ejemplo
            self.label_total_usd.configure(text=f"Total (USD): ${total_usd:.2f}")
            self.label_total_bs.configure(text=f"Total (BS): Bs {total_bs:.2f}")
            print(self.lista_subtotales)
        else:
            return
        
    def obtener_precio_select(self, producto):
        if self.val_tipo_transac.get() == 1:  # Compra
            return producto.precio_compra
        elif self.val_tipo_transac.get() == 2:  # Venta
            return producto.precio_venta
        else:
            return 0.0
    
    def limpiar_formulario(self):
        self.val_tipo_transac.set(0)
        self.entry_desc.delete(0, 'end')
        self.label_cantidad.configure(text="1")
        self.label_detalles_info.configure(text="")
        self.lista_productos_seleccionados.clear()
        self.lista_cantidades.clear()
        self.lista_subtotales.clear()
        self.label_total_usd.configure(text="Total (USD): $0.00")
        self.label_total_bs.configure(text="Total (BS): Bs 0.00")