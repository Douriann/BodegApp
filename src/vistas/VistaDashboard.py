import customtkinter as ctk
from servicios.servDashboard import ServDashboard 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator

class VistaDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.servicio = ServDashboard()
        
        # Variables para controlar la limpieza de memoria
        self.fig = None
        self.canvas = None

        # --- CONFIGURACIÓN DE COLORES ---
        self.configure(fg_color="transparent")

        # 1. TÍTULO PRINCIPAL
        self.lbl_titulo = ctk.CTkLabel(self, text="Panel de Control BodegApp", font=("Roboto", 24, "bold"))
        self.lbl_titulo.pack(pady=(20, 10))

        # 2. FRAME DE INDICADORES
        self.frame_indicadores = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        self.frame_indicadores.pack(pady=10, padx=20, fill="x")

        # Buscamos los datos reales
        ventas_totales, ingresos = self.servicio.obtener_resumen_financiero()
        tasa_bcv = self.servicio.obtener_precio_dolar()

        # Indicadores
        self.lbl_ventas = ctk.CTkLabel(self.frame_indicadores, text=f"📦 Ventas\n{ventas_totales}", font=("Roboto", 16))
        self.lbl_ventas.pack(side="left", expand=True, pady=15)

        self.lbl_ingresos = ctk.CTkLabel(self.frame_indicadores, text=f"💰 Ingresos\n${ingresos:.2f}", font=("Roboto", 16))
        self.lbl_ingresos.pack(side="left", expand=True, pady=15)

        self.lbl_tasa = ctk.CTkLabel(self.frame_indicadores, text=f"💵 Tasa BCV\n{tasa_bcv:.2f} Bs.", font=("Roboto", 16))
        self.lbl_tasa.pack(side="left", expand=True, pady=15)

        # 3. FRAME DEL GRÁFICO
        self.frame_grafico = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_grafico.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.crear_grafico()
        
    def crear_grafico(self):
        datos = self.servicio.obtener_top_vendidos()[:3]
        if not datos: return

        # Limpieza previa si se recarga el gráfico
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        if self.fig:
            plt.close(self.fig) # Importante: cerrar la figura anterior en Matplotlib

        # Preparar datos
        nombres = [str(d[0]) for d in datos]  
        valores = [d[1] for d in datos]
        cantidades = [d[1] for d in datos]

        # Configurar figura
        self.fig, self.ax = plt.subplots(figsize=(5, 3.5), dpi=100)
        self.fig.set_facecolor('#1a1a1a') 
        self.ax.set_facecolor('#1a1a1a')
        
        # Ejes y límites
        self.ax.set_xticks(range(len(nombres)))
        self.ax.set_xticklabels(nombres)
        self.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        self.ax.set_ylim(bottom=0)
        max_venda = max(cantidades) if cantidades else 1
        self.ax.set_ylim(top=max_venda + 1) 

        # Barras
        self.ax.bar(range(len(nombres)), valores, color='#a674ff', width=0.2, align='center')

        # Estética
        self.ax.set_title("TOP 3 MÁS VENDIDOS", color='white', fontsize=18, fontweight='bold', pad=25) 
        self.ax.tick_params(axis='both', colors='white', labelsize=12) 
        self.fig.tight_layout() 
        
        for side in ['top', 'right', 'left', 'bottom']:
             self.ax.spines[side].set_visible(False)

        self.ax.set_xlim(-0.5, 2.5)
        
        # --- AQUÍ EL CAMBIO IMPORTANTE ---
        # Guardamos la referencia en self.canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def destroy(self):
        """
        Método mágico que se ejecuta cuando este frame (o la app) se cierra.
        Aquí matamos manualmente a Matplotlib.
        """
        if self.fig:
            plt.close(self.fig) # Cierra la figura en la memoria de Matplotlib
        super().destroy()       # Llama a la destrucción normal de CustomTkinter