import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from servicios.ProductoDAO import ProductoDAO
from servicios.BCVdatos import BcvScraper
from servicios.ServTransac import ServTransac 
from servicios.ServProdTransac import ServProdTransac

import matplotlib
matplotlib.use('Agg')

class VistaDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        # Fondo dinámico para el frame principal
        super().__init__(parent, fg_color=("#F2F2F2", "#121212"))
        self.controller = controller
        self.dao = ProductoDAO()
        self.scraper_bcv = BcvScraper()
        self.serv_transac = ServTransac()
        self.serv_detalles = ServProdTransac()
        
        # Paleta Neón (se mantienen vibrantes en ambos modos)
        self.NEON_PURPLE = "#BB86FC"
        self.NEON_CYAN = "#03DAC6"
        self.NEON_ORANGE = "#FFB74D"
        self.NEON_RED = "#FF5252"
        self.NEON_GREEN = "#2ecc71"
        self.NEON_BLUE = "#448AFF"
        
        # Colores de tarjetas adaptables
        self.CARD_COLOR = ("#FFFFFF", "#1E1E1E")
        self.TEXT_MAIN = ("#2B2B2B", "white")
        self.BORDER_CARD = ("#DBDBDB", "#333333")

        # --- HEADER ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=30, pady=(30, 10))
        
        ctk.CTkLabel(self.header, text="Panel de Resumen Financiero", 
                     font=("Segoe UI", 24, "bold"), 
                     text_color=self.TEXT_MAIN).pack(side="left")
        
        self.btn_refresh = ctk.CTkButton(self.header, text="↻", width=40, 
                                         fg_color=self.CARD_COLOR, 
                                         text_color=self.TEXT_MAIN,
                                         hover_color=("#E5E5E5", "#333333"), 
                                         command=self.actualizar_vista)
        self.btn_refresh.pack(side="right", padx=(10, 0))

        self.entry_busqueda = ctk.CTkEntry(self.header, placeholder_text="Filtrar por nombre...", 
                                           width=250, height=35, 
                                           fg_color=self.CARD_COLOR, 
                                           text_color=self.TEXT_MAIN,
                                           border_color=self.NEON_CYAN)
        self.entry_busqueda.pack(side="right", padx=10)
        self.entry_busqueda.bind("<KeyRelease>", self.programar_busqueda)
        self.timer_busqueda = None

        # --- CONTENEDOR CON SCROLL ADAPTABLE ---
        self.main_container = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=self.NEON_PURPLE,      
            scrollbar_button_hover_color=self.NEON_CYAN,  
            label_text="" 
        )
        self.main_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.after(200, self.actualizar_vista)

    def programar_busqueda(self, event):
        if self.timer_busqueda:
            self.after_cancel(self.timer_busqueda)
        self.timer_busqueda = self.after(600, self.actualizar_vista)

    def obtener_tasa_hoy(self):
        try:
            datos = self.scraper_bcv.obtener_tasa_con_respaldo()
            return datos.get('tasa', 0.0)
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

    def actualizar_vista(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
        df = self.obtener_datos_productos()
        texto = self.entry_busqueda.get().lower()
        if not df.empty and texto:
            df = df[df['Nombre'].str.lower().str.contains(texto)]

        tasa_real = self.obtener_tasa_hoy()
        ventas_acumuladas = self.obtener_ventas_totales()
        
        self.crear_kpis_neon(df, tasa_real, ventas_acumuladas)
        
        charts_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        charts_frame.pack(fill="x", pady=20)
        charts_frame.grid_columnconfigure((0, 1), weight=1)

        self.grafico_dona_gordita(df, charts_frame)
        self.grafico_top_vendidos(charts_frame)
        
        self.crear_cuadro_reposicion(df)

    def crear_kpis_neon(self, df, tasa, ventas):
        kpi_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=10)
        kpi_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        val_inv = df['Valor_Total'].sum() if not df.empty else 0
        stk_tot = df['Stock'].sum() if not df.empty else 0
        cant_prod = len(df) if not df.empty else 0

        metrics = [
            ("VALOR INVENTARIO", f"${val_inv:,.2f}", self.NEON_PURPLE),
            ("STOCK TOTAL", f"{int(stk_tot)} Und", self.NEON_CYAN),
            ("VENTAS TOTALES", f"${ventas:,.2f}", self.NEON_GREEN),
            ("VARIEDAD", f"{cant_prod} Prod.", self.NEON_BLUE),
            ("TASA BCV", f"Bs. {tasa:,.2f}", self.NEON_ORANGE)
        ]

        for i, (tit, val, col) in enumerate(metrics):
            card = ctk.CTkFrame(kpi_frame, fg_color=self.CARD_COLOR, corner_radius=15, 
                                border_width=2, border_color=col)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            ctk.CTkLabel(card, text=tit, font=("Segoe UI", 10, "bold"), text_color=col).pack(pady=(12, 0))
            ctk.CTkLabel(card, text=val, font=("Segoe UI", 16, "bold"), text_color=self.TEXT_MAIN).pack(pady=(5, 12))

    def grafico_dona_gordita(self, df, parent):
        card = ctk.CTkFrame(parent, fg_color=self.CARD_COLOR, corner_radius=20)
        card.grid(row=0, column=0, padx=10, sticky="nsew")
        ctk.CTkLabel(card, text="Inversión por Marca", font=("Segoe UI", 16, "bold"), text_color=self.TEXT_MAIN).pack(pady=10)
        
        if df.empty: return

        # Detección de color de fondo para Matplotlib
        bg_color = self.CARD_COLOR[0] if ctk.get_appearance_mode() == "Light" else self.CARD_COLOR[1]
        text_color = "black" if ctk.get_appearance_mode() == "Light" else "white"

        marca_data = df.groupby('Marca')['Valor_Total'].sum().nlargest(4)
        fig, ax = plt.subplots(figsize=(4, 3.5), dpi=90)
        fig.patch.set_facecolor(bg_color)
        
        colors = [self.NEON_PURPLE, self.NEON_CYAN, self.NEON_ORANGE, self.NEON_RED]
        ax.pie(marca_data, labels=marca_data.index, autopct='%1.1f%%', radius=1.4, startangle=140, 
               colors=colors, pctdistance=0.7, 
               textprops={'color': text_color, 'fontsize': 10, 'weight': 'bold'},
               wedgeprops={'width': 0.7, 'edgecolor': bg_color})
        
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10, fill="both")
        plt.close(fig)

    def grafico_top_vendidos(self, parent):
        card = ctk.CTkFrame(parent, fg_color=self.CARD_COLOR, corner_radius=20)
        card.grid(row=0, column=1, padx=10, sticky="nsew")
        ctk.CTkLabel(card, text="🏆 Top 3 Más Vendidos", font=("Segoe UI", 16, "bold"), text_color=self.NEON_GREEN).pack(pady=10)
        
        try:
            bg_color = self.CARD_COLOR[0] if ctk.get_appearance_mode() == "Light" else self.CARD_COLOR[1]
            text_color = "black" if ctk.get_appearance_mode() == "Light" else "white"

            todas = self.serv_transac.consultar_transacciones()
            ventas_ids = [t.id_transaccion for t in todas if int(t.id_tipo) == 2]
            
            lista_detalles = []
            for id_t in ventas_ids:
                detalles = self.serv_detalles.consultar_detalles_por_transaccion(id_t)
                for d in detalles:
                    lista_detalles.append({'Producto': d.nombre_producto, 'Cantidad': d.cantidad_producto})
            
            df_det = pd.DataFrame(lista_detalles)
            top_3 = df_det.groupby('Producto')['Cantidad'].sum().nlargest(3)
            
            fig, ax = plt.subplots(figsize=(4, 3.5), dpi=90)
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)
            
            ax.bar(top_3.index, top_3.values, color=self.NEON_GREEN, width=0.5)
            ax.tick_params(axis='x', colors=text_color, labelsize=8)
            ax.tick_params(axis='y', colors=text_color, labelsize=8)
            for spine in ax.spines.values(): spine.set_visible(False)
            ax.grid(True, axis='y', linestyle='--', alpha=0.2, color=text_color)
            
            canvas = FigureCanvasTkAgg(fig, master=card)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=10, pady=10, fill="both")
            plt.close(fig)
        except:
            ctk.CTkLabel(card, text="Sin datos suficientes", text_color="gray").pack(pady=50)

    def crear_cuadro_reposicion(self, df):
        if df.empty: return
        criticos = df[df['Stock'] <= 10].sort_values(by='Stock')
        if criticos.empty: return

        container = ctk.CTkFrame(self.main_container, fg_color=self.CARD_COLOR, 
                                 corner_radius=20, border_width=1, border_color=self.BORDER_CARD)
        container.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(container, text="🚨 ALERTA DE REPOSICIÓN CRÍTICA", 
                     font=("Segoe UI", 14, "bold"), text_color=self.NEON_RED).pack(pady=15, padx=20, anchor="w")

        for _, row in criticos.iterrows():
            item = ctk.CTkFrame(container, fg_color="transparent")
            item.pack(fill="x", padx=30, pady=5)
            
            ctk.CTkLabel(item, text=row['Nombre'], font=("Segoe UI", 14, "bold"), 
                         width=200, anchor="w", text_color=self.TEXT_MAIN).pack(side="left")
            
            prog_val = max(0, min(row['Stock'] / 10, 1))
            prog = ctk.CTkProgressBar(item, width=250, height=10, 
                                      progress_color=self.NEON_RED, fg_color=("#E0E0E0", "#333333"))
            prog.set(prog_val) 
            prog.pack(side="left", padx=20)
            
            ctk.CTkLabel(item, text=f"{int(row['Stock'])} UNID", 
                         font=("Segoe UI", 11, "bold"), text_color=self.NEON_RED).pack(side="right")

    def destroy(self):
        plt.close('all')
        super().destroy()