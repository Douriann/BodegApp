import os
import customtkinter as ctk
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# Servicios y Modelos
from servicios.ServBusqProduc import ServBusqProduc
from servicios.ServTransac import ServTransac
from modelos.Transaccion import Transaccion
from modelos.DetalleTransaccion import DetalleTransaccion
from servicios.BCVdatos import BcvScraper

# --- VENTANA DE AVISO PERSONALIZADA ---
class VentanaAviso(ctk.CTkToplevel):
    def __init__(self, parent, titulo, mensaje, color_estilo="#ab3df4", emoji="⚠️"):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("400x220")
        self.attributes("-topmost", True)
        self.grab_set()
        self.resizable(False, False)

        # Centrado
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 110
        self.geometry(f"+{x}+{y}")

        self.main_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color=color_estilo)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.main_frame, text=f"{emoji} {titulo}", 
                     font=("Segoe UI", 18, "bold"), text_color=color_estilo).pack(pady=(20, 5))
        
        ctk.CTkLabel(self.main_frame, text=mensaje, 
                     font=("Segoe UI", 13), wraplength=340).pack(pady=10, padx=20)

        ctk.CTkButton(self.main_frame, text="Entendido", 
                      fg_color=color_estilo, hover_color=("#8E44AD", "#780ac1"), 
                      width=150, height=35, font=("Segoe UI", 13, "bold"), 
                      command=self.destroy).pack(pady=20)

# --- VENTANA DE CONFIRMACIÓN PERSONALIZADA ---
class VentanaConfirmacion(ctk.CTkToplevel):
    def __init__(self, parent, titulo, mensaje, colores, comando_confirmar):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("400x230")
        self.attributes("-topmost", True)
        self.grab_set()
        self.resizable(False, False)
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 115
        self.geometry(f"+{x}+{y}")

        color_morado = colores["morado"][0] if isinstance(colores["morado"], tuple) else colores["morado"]
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color=color_morado)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.main_frame, text="❓ Confirmación", 
                     font=("Segoe UI", 18, "bold"), text_color=color_morado).pack(pady=(20, 5))

        ctk.CTkLabel(self.main_frame, text=mensaje, font=("Segoe UI", 14), wraplength=340).pack(pady=10, padx=20)
        
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=20)

        ctk.CTkButton(btn_frame, text="Confirmar", fg_color=colores["morado"], 
                      hover_color=colores["morado_hover"], width=120, height=35, font=("Segoe UI", 13, "bold"),
                      command=lambda: [comando_confirmar(), self.destroy()]).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color=("#94a3b8", "#475569"), 
                      hover_color=("#64748b", "#334155"), width=120, height=35, font=("Segoe UI", 13, "bold"),
                      command=self.destroy).pack(side="left", padx=10)

class VistaNuevaTransac(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Nueva Transacción")
        self.attributes("-topmost", True)
        self.producto_seleccionado = None  

        # --- CONFIGURACIÓN DE COLORES DINÁMICOS ---
        self.colores = {
            "morado": ("#ab3df4", "#ab3df4"),
            "morado_hover": ("#c06ef7", "#c06ef7"),
            "bg_tarjetas": ("#FFFEFE", "#1e1e1e"),
            "bg_panel_derecho": ("#D0D0D0", "#2D2D2D"),
            "texto_principal": ("#333333", "#FFFFFF"),
            "borde": ("#CCCCCC", "#333333")
        }

        # Centrado de ventana
        anchoVist = 1220
        altoVist = 720
        self.update_idletasks()
        anchoPant = self.winfo_screenwidth()
        altoPant = self.winfo_screenheight()
        x = (anchoPant // 2) - (anchoVist // 2)
        y = (altoPant // 2) - (altoVist // 2)
        self.geometry(f"{anchoVist}x{altoVist}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # --- LADO IZQUIERDO: BÚSQUEDA Y TABLA ---
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # Buscador
        self.busqueda_frame = ctk.CTkFrame(self.left_container, fg_color="transparent")
        self.busqueda_frame.pack(fill="x", pady=(0, 15))

        self.entry_buscar = ctk.CTkEntry(self.busqueda_frame, placeholder_text="Buscar producto por nombre...", width=680, height=35)
        self.entry_buscar.pack(side="left", padx=(0, 10))

        self.btn_buscar = ctk.CTkButton(self.busqueda_frame, text="Buscar", width=100, height=35, 
                                       fg_color=self.colores["morado"], hover_color=self.colores["morado_hover"], command=self.mostrar_producto_busqueda)
        self.btn_buscar.pack(side="left")

        # --- TABLA (Encabezado) ---
        self.header_tabla = ctk.CTkFrame(self.left_container, fg_color="transparent", height=30)
        self.header_tabla.pack(fill="x")
        self.header_tabla.pack_propagate(False)

        headers = [("ID", 0.04), ("NOMBRE", 0.13), ("MARCA", 0.28), ("PRESENTACION", 0.37), ("PRECIO VENTA", 0.53), ("PRECIO COMPRA", 0.73), ("STOCK", 0.91)]
        for text, relx in headers:
            ctk.CTkLabel(self.header_tabla, text=text, font=("Segoe UI", 13, "bold"), 
                         text_color=self.colores["morado"]).place(relx=relx, rely=0.5, anchor="w")

        self.scroll_productos = ctk.CTkScrollableFrame(self.left_container, fg_color=self.colores["bg_tarjetas"], corner_radius=10)
        self.scroll_productos.pack(fill="both", expand=True, pady=5)

        # --- LADO DERECHO: FORMULARIO ---
        self.right_container = ctk.CTkFrame(self, fg_color=self.colores["bg_panel_derecho"], width=350, corner_radius=15)
        self.right_container.pack(side="right", fill="both", padx=20, pady=20)
        self.right_container.pack_propagate(False)

        self.label_titulo = ctk.CTkLabel(self.right_container, text="Registrar Transacción", font=("Segoe UI", 20, "bold"), text_color=self.colores["texto_principal"])
        self.label_titulo.pack(pady=20)

        # Tipo de Transacción
        self.val_tipo_transac = ctk.IntVar(value=0)
        self.label_tipo = ctk.CTkLabel(self.right_container, text="Tipo de Transacción:", font=("Segoe UI", 14, "bold"))
        self.label_tipo.pack(pady=(10, 5))
        
        self.radio_frame = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.radio_frame.pack(pady=5)
        self.radiobtn_compra = ctk.CTkRadioButton(self.radio_frame, text="Compra", value=1, border_color=self.colores["morado"], hover_color=self.colores["morado_hover"], variable=self.val_tipo_transac, command=self.calcular_totales)
        self.radiobtn_compra.pack(side="left", padx=40)
        self.radiobtn_venta = ctk.CTkRadioButton(self.radio_frame, text="Venta", value=2, border_color=self.colores["morado"], hover_color=self.colores["morado_hover"], variable=self.val_tipo_transac, command=self.calcular_totales)
        self.radiobtn_venta.pack(side="left", padx=0)

        self.entry_desc = ctk.CTkEntry(self.right_container, placeholder_text="Descripción", width=290)
        self.entry_desc.pack(pady=15)

        # Control de Cantidad
        self.cant_frame = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.cant_frame.pack(pady=10)
        ctk.CTkButton(self.cant_frame, text="-", width=35, fg_color=("#8E44AD", "#780ac1"), hover_color=self.colores["morado"], command=self.reducir_cantidad).pack(side="left")
        self.label_cantidad = ctk.CTkLabel(self.cant_frame, text="1", font=("Segoe UI", 16, "bold"), width=50)
        self.label_cantidad.pack(side="left")
        ctk.CTkButton(self.cant_frame, text="+", width=35, fg_color=("#8E44AD", "#780ac1"), hover_color=self.colores["morado"], command=self.incrementar_cantidad).pack(side="left")

        self.btn_agregar = ctk.CTkButton(self.right_container, width=120, text="Añadir a Lista", fg_color=self.colores["morado"], hover_color=self.colores["morado_hover"], command=self.actualizar_detalles_transaccion)
        self.btn_agregar.pack(pady=10)

        # --- Área de Detalles ---
        self.detalles_card = ctk.CTkFrame(self.right_container, fg_color=self.colores["bg_tarjetas"], corner_radius=10, border_width=1, border_color=self.colores["borde"], width=290, height=100)
        self.detalles_card.pack(pady=10, padx=15, fill="both", expand=True)
        self.detalles_card.pack_propagate(False)

        self.titulo_detalles = ctk.CTkLabel(self.detalles_card, text="DETALLES DE LA LISTA", font=("Segoe UI", 16, "bold"), text_color=self.colores["morado"])
        self.titulo_detalles.pack(pady=(10, 5), padx=10)

        self.separador = ctk.CTkFrame(self.detalles_card, fg_color=self.colores["borde"], height=1)
        self.separador.pack(fill="x", padx=10, pady=5)

        self.scroll_interno_detalles = ctk.CTkScrollableFrame(self.detalles_card, fg_color="transparent")
        self.scroll_interno_detalles.pack(fill="both", expand=True, padx=2, pady=2)

        self.label_detalles_info = ctk.CTkLabel(self.scroll_interno_detalles, text="", font=("Segoe UI", 13), justify="left", anchor="nw")
        self.label_detalles_info.pack(pady=10, padx=15, fill="both", expand=True)

        # --- Tasas e inicialización ---
        self.bcv = BcvScraper()
        self.lista_productos_seleccionados = []
        self.lista_cantidades = []
        self.lista_subtotales = []
        
        self.mostrar_productos()

        # --- Botones Finales ---
        self.botones_final_frame = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.botones_final_frame.pack(side="bottom", fill="x", pady=20, padx=20)

        self.btn_guardar = ctk.CTkButton(self.botones_final_frame, text="Guardar", fg_color=("#2CC985", "#2CC985"), 
                                        hover_color=("#26A46E", "#26A46E"), font=("Segoe UI", 14, "bold"), height=40, width=140, command=self.confirmar_guardado)
        self.btn_guardar.pack(side="right", expand=True, padx=(0, 5))

        self.btn_cancelar = ctk.CTkButton(self.botones_final_frame, text="Cancelar", fg_color=("#E74C3C", "#E74C3C"), 
                                         hover_color=("#DB2B18", "#DB2B18"), font=("Segoe UI", 14, "bold"), height=40, width=140, command=self.confirmar_cancelar)
        self.btn_cancelar.pack(side="left", expand=True, padx=(5, 0))

        # --- Totales ---
        self.frame_totales = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.frame_totales.pack(side="bottom", fill="x", pady=(0, 10), padx=20)
        self.label_total_usd = ctk.CTkLabel(self.frame_totales, text="Total (USD): $0.00", font=("Segoe UI", 14, "bold"))
        self.label_total_usd.pack(side="left", padx=5)
        self.label_total_bs = ctk.CTkLabel(self.frame_totales, text="Total (BS): Bs 0.00", font=("Segoe UI", 14, "bold"))
        self.label_total_bs.pack(side="right", padx=5)

    # --- LÓGICA DE FUNCIONAMIENTO ---
    def actualizar_detalles_transaccion(self):
        if self.val_tipo_transac.get() == 0:
            VentanaAviso(self, "Atención", "Seleccione tipo de transacción.", self.colores["morado"][0])
            return
        if hasattr(self, 'fila_data'):
            p = self.fila_data
            cant = int(self.label_cantidad.cget("text"))
            if self.val_tipo_transac.get() == 2 and cant > int(p.stock_actual):
                VentanaAviso(self, "Stock Insuficiente", f"No puedes vender {cant} unidades, solo hay {p.stock_actual}.", "#E74C3C", "❌")
                return
            self.lista_productos_seleccionados.append(p)
            self.lista_cantidades.append(cant)
            actual = self.label_detalles_info.cget("text")
            self.label_detalles_info.configure(text=f"{actual}\n• {p.nombre_producto} (x{cant})" if actual else f"• {p.nombre_producto} (x{cant})")
            self.calcular_totales()
            self.label_cantidad.configure(text="1")
        else:
            VentanaAviso(self, "Selección Vacía", "Por favor, seleccione un producto de la tabla.", self.colores["morado"][0], "🔍")

    def confirmar_guardado(self):
        if not self.lista_productos_seleccionados:
            VentanaAviso(self, "Lista Vacía", "No hay productos en la lista para procesar.", "#E74C3C")
            return
        VentanaConfirmacion(self, "Confirmar Registro", "¿Desea guardar la transacción y generar el ticket?", 
                            self.colores, self.obtener_datos_transaccion)

    def confirmar_cancelar(self):
        if self.lista_productos_seleccionados or self.entry_desc.get():
            VentanaConfirmacion(self, "Confirmar Cancelación", "¿Desea limpiar el formulario? Se perderán los cambios.", 
                                self.colores, self.limpiar_formulario)
        else:
            self.limpiar_formulario()

    def obtener_datos_transaccion(self):
        detalles = []
        for i, p in enumerate(self.lista_productos_seleccionados):
            detalles.append(DetalleTransaccion(None, None, p.id_producto, self.lista_cantidades[i], self.lista_subtotales[i], 1))
        
        trans = Transaccion(None, datetime.now().strftime("%Y-%m-%d"), self.val_tipo_transac.get(), sum(self.lista_subtotales), self.entry_desc.get() or "Sin observaciones", 1)
        
        ServTransac().agregar_transaccion(trans, detalles)
        self.generar_ticket_pdf(trans, detalles)
        VentanaAviso(self, "Éxito", "Transacción guardada y ticket generado.", "#2CC985", "✅")
        self.destroy()

    def calcular_totales(self):
        total_usd = 0.0
        self.lista_subtotales.clear()
        for i, p in enumerate(self.lista_productos_seleccionados):
            precio = p.precio_compra if self.val_tipo_transac.get() == 1 else p.precio_venta
            sub = precio * self.lista_cantidades[i]
            total_usd += sub
            self.lista_subtotales.append(sub)
        tasa = self.bcv.obtener_tasa_con_respaldo().get('tasa', 0)
        self.label_total_usd.configure(text=f"Total (USD): ${total_usd:.2f}")
        self.label_total_bs.configure(text=f"Total (BS): Bs {total_usd * tasa:.2f}")

    # (El resto de métodos: crear_fila_producto, mostrar_productos, etc., se mantienen intactos según tu código original)
    def crear_fila_producto(self, producto):
        fila = ctk.CTkFrame(self.scroll_productos, fg_color="transparent", height=40, corner_radius=5)
        fila.pack(fill="x", pady=2)
        fila.pack_propagate(False)

        def on_click(e):
            if self.producto_seleccionado and self.producto_seleccionado.winfo_exists():
                self.producto_seleccionado.configure(fg_color="transparent")
            self.producto_seleccionado = fila
            self.fila_data = producto
            fila.configure(fg_color=("#D1D1D1", "#444444"))

        cols = [(f"#{producto.id_producto}", 0.025), (producto.nombre_producto, 0.10), 
                (str(producto.id_marca), 0.28), (str(getattr(producto, 'contenido', '')), 0.39), 
                (f"${producto.precio_venta:.2f}", 0.52), (f"${producto.precio_compra:.2f}", 0.73), (str(producto.stock_actual), 0.94)]
        
        for txt, rx in cols:
            l = ctk.CTkLabel(fila, text=txt, font=("Segoe UI", 13))
            l.place(relx=rx, rely=0.5, anchor="w")
            l.bind("<Button-1>", on_click)
        fila.bind("<Button-1>", on_click)

    def mostrar_productos(self):
        for child in self.scroll_productos.winfo_children(): child.destroy()
        lista = ServBusqProduc().buscar_productos_totales()
        for p in lista: self.crear_fila_producto(p)

    def mostrar_producto_busqueda(self):
        for child in self.scroll_productos.winfo_children(): child.destroy()
        lista = ServBusqProduc().buscar_productos_por_nombre(self.entry_buscar.get())
        for p in lista: self.crear_fila_producto(p)

    def incrementar_cantidad(self):
        self.label_cantidad.configure(text=str(int(self.label_cantidad.cget("text")) + 1))
    
    def reducir_cantidad(self):
        curr = int(self.label_cantidad.cget("text"))
        self.label_cantidad.configure(text=str(max(1, curr - 1)))

    def limpiar_formulario(self):
        self.val_tipo_transac.set(0)
        self.entry_desc.delete(0, 'end')
        self.label_detalles_info.configure(text="")
        self.lista_productos_seleccionados.clear()
        self.lista_cantidades.clear()
        self.label_total_usd.configure(text="Total (USD): $0.00")
        self.label_total_bs.configure(text="Total (BS): Bs 0.00")

    def generar_ticket_pdf(self, trans, detalles):
        try:
            if not os.path.exists("tickets"): os.makedirs("tickets")
            nombre_archivo = f"tickets/Ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            c = canvas.Canvas(nombre_archivo, pagesize=(58 * mm, 150 * mm))
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(29 * mm, 142 * mm, "MI BODEGAPP")
            c.save()
            os.startfile(os.path.abspath(nombre_archivo))
        except Exception as e: print(f"Error ticket: {e}")