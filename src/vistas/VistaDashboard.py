import customtkinter as ctk
from servicios.servDashboard import ServDashboard 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator

class VistaDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller # Guardamos el controlador por si se necesita
        self.servicio = ServDashboard()
        
        # --- CONFIGURACIÓN DE COLORES ---
        self.configure(fg_color="transparent")

        # 1. TÍTULO PRINCIPAL
        self.lbl_titulo = ctk.CTkLabel(self, text="Panel de Control BodegApp", font=("Roboto", 24, "bold"))
        self.lbl_titulo.pack(pady=(20, 10))

        # 2. FRAME DE INDICADORES (Ventas, Ingresos, Dólar)
        # Este es el contenedor horizontal solicitado
        self.frame_indicadores = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        self.frame_indicadores.pack(pady=10, padx=20, fill="x")

        # Buscamos los datos reales de los 6 registros
        ventas_totales, ingresos = self.servicio.obtener_resumen_financiero()
        tasa_bcv = self.servicio.obtener_precio_dolar()

        # Indicador: Ventas
        self.lbl_ventas = ctk.CTkLabel(self.frame_indicadores, text=f"📦 Ventas\n{ventas_totales}", font=("Roboto", 16))
        self.lbl_ventas.pack(side="left", expand=True, pady=15)

        # Indicador: Ingresos
        self.lbl_ingresos = ctk.CTkLabel(self.frame_indicadores, text=f"💰 Ingresos\n${ingresos:.2f}", font=("Roboto", 16))
        self.lbl_ingresos.pack(side="left", expand=True, pady=15)

        # Indicador: Tasa BCV
        self.lbl_tasa = ctk.CTkLabel(self.frame_indicadores, text=f"💵 Tasa BCV\n{tasa_bcv:.2f} Bs.", font=("Roboto", 16))
        self.lbl_tasa.pack(side="left", expand=True, pady=15)

        # 3. FRAME DEL GRÁFICO (Top 3 Productos)
        self.frame_grafico = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_grafico.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.crear_grafico()
        
    def crear_grafico(self):
        # 1. Obtener datos (usando el Top 3 que ya tienes)
        datos = self.servicio.obtener_top_vendidos()[:3]
        if not datos: return
        # Limpiar el frame antes de crear el nuevo gráfico
        for widget in self.frame_grafico.winfo_children():
            widget.destroy()

        # 2. Preparar etiquetas y valores
        nombres = [str(d[0]) for d in datos]  
        valores = [d[1] for d in datos]
        cantidades = [d[1] for d in datos]

        # 3. Configurar la figura (Fondo oscuro para que resalte el morado)
        self.fig, self.ax = plt.subplots(figsize=(5, 3.5), dpi=100)
        self.fig.set_facecolor('#1a1a1a') 
        self.ax.set_facecolor('#1a1a1a')
        # Forzar nombres reales y números enteros en Y
        self.ax.set_xticks(range(len(nombres)))
        self.ax.set_xticklabels(nombres)
        self.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        self.ax.set_ylim(bottom=0)
        max_venda = max(cantidades) if cantidades else 1
        self.ax.set_ylim(top=max_venda + 1) 

        # 4. Dibujar las barras (EL SECRETO: width=0.2 para que sean delgadas)
        # Color: #b066ff es el morado brillante...
        barras = self.ax.bar(range(len(nombres)), valores, color='#a674ff', width=0.2, align='center')

        # 5. Estética de los ejes (Letras blancas y limpias)
        self.ax.set_title("TOP 3 MÁS VENDIDOS", color='white', fontsize=18, fontweight='bold', pad=25) 
        self.ax.tick_params(axis='both', colors='white', labelsize=12) 
        self.fig.tight_layout() 
        
        # Quitar los bordes del gráfico para un look moderno
        for side in ['top', 'right', 'left', 'bottom']:
         self.ax.spines[side].set_visible(False)

        # 6. Mostrar el gráfico en el frame
        self.ax.set_xlim(-0.5, 2.5) # Esto obliga al gráfico a dejar espacio para 3 barras siempre
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)