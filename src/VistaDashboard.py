import customtkinter as ctk

class VistaDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ctk.CTkLabel(self, text="Dashboard Principal", font=("Roboto", 24))
        label.pack(pady=20)
        
        # Tarjetas de información (KPIs)
        self.kpi_ventas = ctk.CTkButton(self, text="Total Ventas: $0", state="disabled", fg_color="transparent", border_width=2)
        self.kpi_ventas.pack(pady=10)