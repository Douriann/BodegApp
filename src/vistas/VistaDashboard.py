import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
from servicios.ProductoDAO import ProductoDAO
from servicios.BCVdatos import BcvScraper
from servicios.ServTransac import ServTransac
from servicios.ServProdTransac import ServProdTransac
from ConfigRutas import rutas 
import math

import matplotlib
matplotlib.use('Agg')

class VistaDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        self.MAIN_BG = ("#F2F2F2", "#121212")
        super().__init__(parent, fg_color=self.MAIN_BG)
        
        self.controller = controller
        self.dao = ProductoDAO()
        self.scraper_bcv = BcvScraper()
        self.serv_transac = ServTransac()
        self.serv_detalles = ServProdTransac()
        
        # Paleta Neón Original
        self.NEON_PURPLE = "#BB86FC"
        self.NEON_CYAN = "#03DAC6"
        self.NEON_ORANGE = "#FFB74D"
        self.NEON_RED = "#FF5252"
        self.NEON_GREEN = "#2ecc71"
        self.NEON_BLUE = "#448AFF"
        
        self.CARD_COLOR = ("#FFFFFF", "#1E1E1E")
        self.TEXT_MAIN = ("#2B2B2B", "white")
        self.BORDER_CARD = ("#DBDBDB", "#333333")

        # --- HEADER ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=30, pady=(30, 10))
        
        ctk.CTkLabel(self.header, text="Panel de Resumen Financiero",
                     font=("Segoe UI", 24, "bold"),
                     text_color=self.TEXT_MAIN).pack(side="left")
        
        # Botón Buscar
        icono_buscar = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-busqueda.png")), size=(18, 18))
        self.btn_buscar = ctk.CTkButton(self.header, text="Buscar", width=100, height=35, image=icono_buscar,
                                         fg_color=self.NEON_PURPLE, text_color="white",
                                         hover_color=self.NEON_BLUE, font=("Segoe UI", 14, "bold"),
                                         command=self.actualizar_vista)
        self.btn_buscar.pack(side="right", padx=(5, 0))

        # Buscador
        self.entry_busqueda = ctk.CTkEntry(
            self.header, 
            placeholder_text="Buscar por nombre o marca...",
            width=300, height=35,
            fg_color=self.CARD_COLOR,
            text_color=self.TEXT_MAIN,
            border_color=self.NEON_PURPLE,
            font=("Segoe UI", 13)
        )
        self.entry_busqueda.pack(side="right", padx=5)
        
        # Eventos del buscador
        self.entry_busqueda.bind("<Return>", lambda e: self.actualizar_vista())
        self.entry_busqueda.bind("<KeyRelease>", self._verificar_vacio)

        # --- CONTENEDOR ---
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color="#ab3df4", 
                                                     scrollbar_button_hover_color="#c06ef7")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Evento global para cerrar a Sophie al hacer clic fuera
        self.bind("<Button-1>", lambda e: self._on_leave_ia(None))
        self.main_container.bind("<Button-1>", lambda e: self._on_leave_ia(None))

        self.setup_ia_ui()
        self.after(200, self.actualizar_vista)

    def _verificar_vacio(self, event):
        if not self.entry_busqueda.get().strip():
            self.actualizar_vista()

    def setup_ia_ui(self):
        try:
            self.icono_sophie = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("ia-sophie.png")), size=(42, 42))
        except: self.icono_sophie = None

        if self.icono_sophie:
            self.btn_ia = ctk.CTkButton(
                self, text="", border_width=2, border_color="#ab3df4",
                image=self.icono_sophie, width=40, height=40,
                fg_color="#552575", hover_color="#b874e5", cursor="hand2"
            )
            self.btn_ia.place(relx=0.90, rely=0.90, anchor="center")

            self.tooltip = ctk.CTkFrame(self, fg_color="#ab3df4", corner_radius=8)
            self.tooltip_label = ctk.CTkLabel(self.tooltip, text="¡Hola! Soy Sophie, Tú Asistente", 
                                              text_color="white", font=("Segoe UI", 13, "bold"))
            self.tooltip_label.pack(padx=8, pady=5)
            
            # Restaurados los eventos de la nube
            self.btn_ia.bind("<Enter>", self._on_enter_ia)
            self.btn_ia.bind("<Leave>", self._on_leave_ia_normal)
            
            self.angulo_animacion = 0
            self.animar_sophie()

    def animar_sophie(self):
        try:
            self.angulo_animacion += 0.1
            nuevo_tam = 50 + (math.sin(self.angulo_animacion) * 4)
            self.icono_sophie.configure(size=(nuevo_tam, nuevo_tam))
            self.after(47, self.animar_sophie)
        except: pass

    def _on_enter_ia(self, event):
        # Solo mostrar si no hay un mensaje de error ya pegado
        self.tooltip.place(relx=0.82, rely=0.81, anchor="center")
        if self.tooltip.cget("fg_color") != self.NEON_RED:
            self.tooltip_label.configure(text="¡Hola! Soy Sophie, Tú Asistente")

    def _on_leave_ia_normal(self, event):
        # Solo ocultar si NO es un mensaje de error
        if self.tooltip.cget("fg_color") != self.NEON_RED:
            self.tooltip.place_forget()

    def _on_leave_ia(self, event):
        # Ocultar todo (usado para clics externos)
        self.tooltip.place_forget()
        self.tooltip.configure(fg_color="#ab3df4")

    def actualizar_vista(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
        df_original = self.obtener_datos_productos()
        texto = self.entry_busqueda.get().lower().strip()
        
        df = df_original.copy()
        if not df.empty and texto:
            df = df[(df['Nombre'].str.lower().str.contains(texto)) | 
                    (df['Marca'].str.lower().str.contains(texto))]

        if df.empty and not df_original.empty:
            # Sophie se queda pegada en ROJO
            self.tooltip_label.configure(text=f"No hay nada resultados para '{texto}' 🔍")
            self.tooltip.configure(fg_color=self.NEON_RED)
            self.tooltip.place(relx=0.78, rely=0.81, anchor="center")
            ctk.CTkLabel(self.main_container, text="No hay coincidencias.", 
                         font=("Segoe UI", 16), text_color="gray").pack(pady=100)
            return
        else:
            # Si hay resultados, limpiar estado de error
            self._on_leave_ia(None)

        tasa = self.obtener_tasa_hoy()
        ventas = self.obtener_ventas_totales()
        self.crear_kpis_neon(df, tasa, ventas)
        
        charts_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        charts_frame.pack(fill="x", pady=20)
        charts_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.grafico_dona_gordita(df, charts_frame)
        self.grafico_top_vendidos(charts_frame)
        self.crear_cuadro_reposicion(df)

    def obtener_tasa_hoy(self):
        try: return self.scraper_bcv.obtener_tasa_con_respaldo().get('tasa', 0.0)
        except: return 0.0

    def obtener_datos_productos(self):
        try:
            productos = [p for p in self.dao.consultar_todos() if p.estatus == 1]
            marcas_dict = {id_m: nombre for id_m, nombre in self.dao.obtener_marcas()}
            data = [{"Nombre": p.nombre_producto, "Marca": marcas_dict.get(p.id_marca, "N/A"),
                     "Stock": p.stock_actual, "Precio": p.precio_venta,
                     "Valor_Total": p.stock_actual * p.precio_venta} for p in productos]
            return pd.DataFrame(data)
        except: return pd.DataFrame()

    def obtener_ventas_totales(self):
        try:
            transacciones = self.serv_transac.consultar_transacciones()
            return sum(float(t.total) for t in transacciones if int(t.id_tipo) == 2)
        except: return 0.0

    def crear_kpis_neon(self, df, tasa, ventas):
        kpi_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=10)
        kpi_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        val_inv = df['Valor_Total'].sum() if not df.empty else 0
        stk_tot = df['Stock'].sum() if not df.empty else 0
        metrics = [("VALOR INVENTARIO", f"${val_inv:,.2f}", self.NEON_PURPLE),
                   ("STOCK TOTAL", f"{int(stk_tot)} Und", self.NEON_CYAN),
                   ("VENTAS TOTALES", f"${ventas:,.2f}", self.NEON_GREEN),
                   ("VARIEDAD", f"{len(df)} Prod.", self.NEON_BLUE),
                   ("TASA BCV", f"Bs. {tasa:,.2f}", self.NEON_ORANGE)]
        for i, (tit, val, col) in enumerate(metrics):
            card = ctk.CTkFrame(kpi_frame, fg_color=self.CARD_COLOR, corner_radius=15, border_width=2, border_color=col)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            ctk.CTkLabel(card, text=tit, font=("Segoe UI", 10, "bold"), text_color=col).pack(pady=(12, 0))
            ctk.CTkLabel(card, text=val, font=("Segoe UI", 16, "bold"), text_color=self.TEXT_MAIN).pack(pady=(5, 12))

    #Grafico de Dona de Inversion por Marca
    def grafico_dona_gordita(self, df, parent):
        card = ctk.CTkFrame(parent, fg_color=self.CARD_COLOR, corner_radius=20)
        card.grid(row=0, column=0, padx=10, sticky="nsew")
        ctk.CTkLabel(card, text="Inversión por Marca", font=("Segoe UI", 16, "bold"), text_color=self.TEXT_MAIN).pack(pady=10)
        if df.empty: return
        bg = self.CARD_COLOR[0] if ctk.get_appearance_mode() == "Light" else self.CARD_COLOR[1]
        text_c = "black" if ctk.get_appearance_mode() == "Light" else "white"
        marca_data = df.groupby('Marca')['Valor_Total'].sum().nlargest(4)
        fig, ax = plt.subplots(figsize=(4, 3.5), dpi=90)
        fig.patch.set_facecolor(bg)
        ax.pie(marca_data, labels=marca_data.index, autopct='%1.1f%%', radius=1.4, startangle=140, pctdistance=0.69,
               colors=[self.NEON_PURPLE, self.NEON_CYAN, self.NEON_ORANGE, self.NEON_RED],
               wedgeprops={'width': 0.7, 'edgecolor': bg},
               textprops={'color': text_c, 'fontsize': 11, 'weight': 'bold'})
        FigureCanvasTkAgg(fig, master=card).get_tk_widget().pack(padx=10, pady=10, fill="both")
        plt.close(fig)

    #Grafico de Top 3 de Productos mas Vendidos
    def grafico_top_vendidos(self, parent):
        card = ctk.CTkFrame(parent, fg_color=self.CARD_COLOR, corner_radius=20)
        card.grid(row=0, column=1, padx=10, sticky="nsew")
        ctk.CTkLabel(card, text="🏆 Top 3 Más Vendidos", font=("Segoe UI", 16, "bold"), text_color=self.NEON_GREEN).pack(pady=10)
        try:
            todas = self.serv_transac.consultar_transacciones()
            v_ids = [t.id_transaccion for t in todas if int(t.id_tipo) == 2]
            detalles = []
            for tid in v_ids:
                for d in self.serv_detalles.consultar_detalles_por_transaccion(tid):
                    detalles.append({'P': d.nombre_producto, 'C': d.cantidad_producto})
            top_3 = pd.DataFrame(detalles).groupby('P')['C'].sum().nlargest(3)
            bg = self.CARD_COLOR[0] if ctk.get_appearance_mode() == "Light" else self.CARD_COLOR[1]
            text_c = "black" if ctk.get_appearance_mode() == "Light" else "white"
            fig, ax = plt.subplots(figsize=(4, 3.5), dpi=90)
            fig.patch.set_facecolor(bg)
            ax.set_facecolor(bg)
            ax.bar(top_3.index, top_3.values, color=self.NEON_GREEN, width=0.5)
            ax.tick_params(colors=text_c, labelsize=8)
            for spine in ax.spines.values(): spine.set_visible(False)
            FigureCanvasTkAgg(fig, master=card).get_tk_widget().pack(padx=10, pady=10, fill="both")
            plt.close(fig)
        except: pass

    #Cuadro de Alerta de Reposicion de Productos
    def crear_cuadro_reposicion(self, df):
        if df.empty: return
        criticos = df[df['Stock'] <= 10].sort_values(by='Stock')
        if criticos.empty: return
        container = ctk.CTkFrame(self.main_container, fg_color=self.CARD_COLOR, corner_radius=20, border_width=1, border_color=self.BORDER_CARD)
        container.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(container, text="🚨 ALERTA DE REPOSICIÓN CRÍTICA", font=("Segoe UI", 14, "bold"), text_color=self.NEON_RED).pack(pady=15, padx=20, anchor="w")
        for _, row in criticos.iterrows():
            item = ctk.CTkFrame(container, fg_color="transparent")
            item.pack(fill="x", padx=30, pady=5)
            ctk.CTkLabel(item, text=row['Nombre'], font=("Segoe UI", 14, "bold"), width=200, anchor="w", text_color=self.TEXT_MAIN).pack(side="left")
            prog = ctk.CTkProgressBar(item, width=250, height=10, progress_color=self.NEON_RED)
            prog.set(max(0, min(row['Stock'] / 10, 1)))
            prog.pack(side="left", padx=20)
            ctk.CTkLabel(item, text=f"{int(row['Stock'])} UNID", font=("Segoe UI", 11, "bold"), text_color=self.NEON_RED).pack(side="right")

    def destroy(self):
        plt.close('all')
        super().destroy()