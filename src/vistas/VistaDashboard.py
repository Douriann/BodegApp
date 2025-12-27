import customtkinter as ctk
from servicios.servDashboard import ServDashboard # Tu "cerebro" de datos
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class VistaDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller # Guardamos el controlador por si lo necesitas
        self.servicio = ServDashboard()
        
        # --- CONFIGURACIÓN DE COLORES ---
        self.configure(fg_color="transparent")

        # 1. TÍTULO PRINCIPAL
        self.lbl_titulo = ctk.CTkLabel(self, text="Panel de Control BodegApp", font=("Roboto", 24, "bold"))
        self.lbl_titulo.pack(pady=(20, 10))

        # 2. FRAME DE INDICADORES (Ventas, Ingresos, Dólar)
        # Este es el contenedor horizontal que te pidió el grupo
        self.frame_indicadores = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        self.frame_indicadores.pack(pady=10, padx=20, fill="x")

        # Buscamos los datos reales de tus 6 registros
        ventas_totales, ingresos = self.servicio.obtener_resumen_financiero()
        tasa_bcv = self.servicio.obtener_precio_dolar()

        # Indicador: Ventas
        self.lbl_ventas = ctk.CTkLabel(self.frame_indicadores, text=f"📦 Ventas\n{ventas_totales}", font=("Roboto", 16))
        self.lbl_ventas.pack(side="left", expand=True, pady=15)

        # Indicador: Ingresos
        self.lbl_ingresos = ctk.CTkLabel(self.frame_indicadores, text=f"💰 Ingresos\n${ingresos:.2f}", font=("Roboto", 16))
        self.lbl_ingresos.pack(side="left", expand=True, pady=15)

        # Indicador: Tasa BCV
        self.lbl_tasa = ctk.CTkLabel(self.frame_indicadores, text=f"💵 Tasa BCV\n{tasa_bcv} Bs.", font=("Roboto", 16))
        self.lbl_tasa.pack(side="left", expand=True, pady=15)

        # 3. FRAME DEL GRÁFICO (Top 3 Productos)
        self.frame_grafico = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_grafico.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.crear_grafico()

    def crear_grafico(self):
        # Obtenemos los 3 productos más vendidos desde el servicio
        datos = self.servicio.obtener_top_vendidos()
        
        if not datos:
            # Si no hay ventas, mostramos un mensaje en lugar del gráfico
            ctk.CTkLabel(self.frame_grafico, text="No hay datos suficientes para el gráfico").pack()
            return

        # Preparamos los nombres y las cantidades
        nombres = [d[0] for d in datos]
        cantidades = [d[1] for d in datos]

        # Configuramos el estilo del gráfico con Matplotlib
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor('#242424') # Color de fondo oscuro para que combine
        ax.set_facecolor('#242424')
        
        # Dibujamos las barras
        barras = ax.bar(nombres, cantidades, color='#9b59b6') # Color morado
        ax.set_title("Top 3 Productos Más Vendidos", color="white", pad=20)
        
        # Estética de los ejes
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Insertamos el gráfico en la interfaz de CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)