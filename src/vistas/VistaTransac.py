import customtkinter as ctk
from PIL import Image
from vistas.VistaNuevaTransac import VistaNuevaTransac
from servicios.ServTransac import ServTransac
from servicios.ServProdTransac import ServProdTransac
from ConfigRutas import rutas

class VistaTransac(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.ventana_toplevel = None 
        self.transacciones_full = [] # Caché para filtrado rápido

        # --- HEADER PRINCIPAL ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.titulo = ctk.CTkLabel(header_frame, text="Historial de Transacciones", 
                                   font=("Segoe UI", 24, "bold"))
        self.titulo.pack(side="left", anchor="n")

        self.btn_add = ctk.CTkButton(
            header_frame, 
            text="+ Nueva Transacción", 
            fg_color="#ab3df4", 
            hover_color="#920cec",
            font=("Segoe UI", 14, "bold"), 
            height=35,
            command=self.abrir_ventana_nueva
        )
        self.btn_add.pack(side="right", pady=(10, 0))

        # --- SECCIÓN DE MICRO-KPIs (INTERACTIVOS) ---
        self.kpi_container = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_container.pack(fill="x", padx=20, pady=(10, 15))
        
        # Tarjeta Ingresos (Filtra Ventas)
        self.card_ingresos = self._crear_kpi_card(self.kpi_container, "INGRESOS (VENTAS)", "#27AE60", "VENTA")
        self.card_ingresos.pack(side="left", expand=True, fill="both", padx=(0, 10))
        
        # Tarjeta Egresos (Filtra Compras)
        self.card_egresos = self._crear_kpi_card(self.kpi_container, "EGRESOS (COMPRAS)", "#E74C3C", "COMPRA")
        self.card_egresos.pack(side="left", expand=True, fill="both", padx=10)
        
        # Tarjeta Balance (Muestra Todo)
        self.card_balance = self._crear_kpi_card(self.kpi_container, "BALANCE (VER TODO)", "#ab3df4", "TODOS")
        self.card_balance.pack(side="left", expand=True, fill="both", padx=(10, 0))

        # --- PANEL DE DETALLES ---
        self.detalles_card = ctk.CTkFrame(self, fg_color=("white", "#2b2b2b"), height=80, corner_radius=15, border_width=2, border_color=("#DBDBDB", "#444444"))
        self.detalles_card.pack(fill="x", padx=20, pady=(5, 20))
        
        self.btn_limpiar = ctk.CTkButton(
            self.detalles_card, text="✕", width=25, height=25, 
            fg_color="transparent", text_color="gray", hover_color=("#FF5252"),
            command=self.limpiar_detalles
        )
        self.btn_limpiar.place_forget()

        self.label_detalles = ctk.CTkLabel(
            self.detalles_card, 
            text="Selecciona una transacción para ver los detalles", 
            font=("Segoe UI", 13, "italic"),
            text_color="gray"
        )
        self.label_detalles.pack(pady=20, padx=40)

        # --- CONTENEDOR DE TABLA ---
        self.tabla_container = ctk.CTkFrame(self, fg_color="transparent")
        self.tabla_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.header_tabla = ctk.CTkFrame(self.tabla_container, fg_color="transparent", height=30)
        self.header_tabla.pack(fill="x", pady=(0, 5)) 
        self.header_tabla.pack_propagate(False) 
        
        columnas = [("ID", 0.03), ("FECHA", 0.10), ("TIPO", 0.37), ("TOTAL", 0.57), ("ACCIONES", 0.82)]
        for texto, pos in columnas:
            ctk.CTkLabel(self.header_tabla, text=texto, font=("Segoe UI", 11, "bold"), text_color="#ab3df4").place(relx=pos, rely=0.5, anchor="w")

        self.scroll_filas = ctk.CTkScrollableFrame(self.tabla_container, fg_color="transparent", scrollbar_button_color="#ab3df4")
        self.scroll_filas.pack(fill="both", expand=True)

        self.cargar_datos()
        self.bind("<<TransaccionCreada>>", lambda e: self.cargar_datos())

    def _crear_kpi_card(self, parent, titulo, color, tipo_filtro):
        card = ctk.CTkFrame(parent, fg_color=("white", "#1E1E1E"), corner_radius=12, border_width=1, border_color=color, cursor="hand2")
        card.titulo_lbl = ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 10, "bold"), text_color=color)
        card.titulo_lbl.pack(pady=(10, 0))
        card.valor_lbl = ctk.CTkLabel(card, text="$ 0.00", font=("Segoe UI", 16, "bold"))
        card.valor_lbl.pack(pady=(0, 10))
        for widget in [card, card.titulo_lbl, card.valor_lbl]:
            widget.bind("<Button-1>", lambda e: self.filtrar_tabla(tipo_filtro))
        return card

    def cargar_datos(self):
        servicio = ServTransac()
        self.transacciones_full = servicio.consultar_transacciones()
        total_ingresos = 0.0
        total_egresos = 0.0
        for transac in self.transacciones_full:
            monto = float(transac.total)
            if int(transac.id_tipo) == 1: # COMPRA
                total_egresos += monto
            else: # VENTA
                total_ingresos += monto
        self.card_ingresos.valor_lbl.configure(text=f"$ {total_ingresos:,.2f}")
        self.card_egresos.valor_lbl.configure(text=f"$ {total_egresos:,.2f}")
        balance = total_ingresos - total_egresos
        color_balance = "#27AE60" if balance >= 0 else "#E74C3C"
        self.card_balance.valor_lbl.configure(text=f"$ {balance:,.2f}", text_color=color_balance)
        self.filtrar_tabla("TODOS")

    def filtrar_tabla(self, filtro):
        for child in self.scroll_filas.winfo_children():
            child.destroy()
        for transac in reversed(self.transacciones_full):
            tipo_actual = "COMPRA" if int(transac.id_tipo) == 1 else "VENTA"
            if filtro == "TODOS" or filtro == tipo_actual:
                self.crear_fila_transaccion(transac)

    def crear_fila_transaccion(self, transac):
        color_fondo = ("white", "#333333")
        color_hover = ("#f2f2f2", "#3d3d3d")
        fila = ctk.CTkFrame(self.scroll_filas, fg_color=color_fondo, height=55, corner_radius=12)
        fila.pack(fill="x", pady=4, padx=5)
        fila.pack_propagate(False)
        def on_enter(e): fila.configure(fg_color=color_hover)
        def on_leave(e): fila.configure(fg_color=color_fondo)
        fila.bind("<Enter>", on_enter)
        fila.bind("<Leave>", on_leave)
        if int(transac.id_tipo) == 1:
            val_tipo, icono, bg_b, fg_b = "COMPRA", "▼", ("#FDEDEC", "#5D2929"), "#E74C3C"
        else:
            val_tipo, icono, bg_b, fg_b = "VENTA", "▲", ("#EAFAF1", "#1D3D2F"), "#27AE60"
        ctk.CTkLabel(fila, text=f"#{transac.id_transaccion}", font=("Segoe UI", 11, "bold")).place(relx=0.02, rely=0.5, anchor="w")
        ctk.CTkLabel(fila, text=transac.fecha_transaccion, font=("Segoe UI", 11)).place(relx=0.08, rely=0.5, anchor="w")
        badge = ctk.CTkFrame(fila, fg_color=bg_b, corner_radius=20, height=26)
        badge.place(relx=0.35, rely=0.5, anchor="w")
        ctk.CTkLabel(badge, text=f"{icono} {val_tipo}", font=("Segoe UI", 10, "bold"), text_color=fg_b).pack(padx=12, pady=2)
        ctk.CTkLabel(fila, text=f"$ {float(transac.total):,.2f}", font=("Segoe UI", 13, "bold")).place(relx=0.58, rely=0.5, anchor="w")
        try:
            icono_lupa = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-busqueda.png")), size=(16, 16))
        except:
            icono_lupa = None
        btn_ver = ctk.CTkButton(fila, text="Detalles", width=100, height=32, image=icono_lupa, fg_color="#ab3df4", hover_color="#920cec", font=("Segoe UI", 11, "bold"), command=lambda t=transac: self.seleccionar_transaccion(t))
        btn_ver.place(relx=0.82, rely=0.5, anchor="w")

    def seleccionar_transaccion(self, transac):
        servicio_detalles = ServProdTransac()
        detalles = servicio_detalles.consultar_detalles_por_transaccion(transac.id_transaccion)
        
        # Activar botón de limpiar siempre que se intente seleccionar algo
        self.btn_limpiar.place(relx=0.97, rely=0.15, anchor="center")

        if detalles:
            detalles_text = f"📄 Transacción #{transac.id_transaccion}\n\n"
            items = [f"• {d.nombre_producto} (x{d.cantidad_producto})" for d in detalles]
            if transac.observaciones and transac.observaciones.strip():
                items.append(f"\n💬 Nota: {transac.observaciones.strip()}")
            detalles_text += "\n".join(items)
            self.label_detalles.configure(text=detalles_text, text_color=("#552575", "#D1D1D1"), font=("Segoe UI", 13, "bold"), anchor="w", justify="left")
        else:
            # --- AQUÍ ESTÁ EL TEXTO QUE FALTABA ---
            self.label_detalles.configure(text="Sin detalles disponibles", text_color="#E74C3C", font=("Segoe UI", 13, "italic"))

    def limpiar_detalles(self):
        self.label_detalles.configure(text="Selecciona una transacción para ver los detalles", text_color="gray", font=("Segoe UI", 13, "italic"))
        self.btn_limpiar.place_forget()

    def abrir_ventana_nueva(self):
        if self.ventana_toplevel is None or not self.ventana_toplevel.winfo_exists():
            self.ventana_toplevel = VistaNuevaTransac(self)
            self.ventana_toplevel.after(100, self.ventana_toplevel.lift)
        else:
            self.ventana_toplevel.focus()

    def recibir_datos_nuevos(self, datos):
        self.cargar_datos()