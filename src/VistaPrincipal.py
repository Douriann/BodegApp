import customtkinter as ctk
# Importamos las clases desde la carpeta 'vistas'
from VistaDashboard import VistaDashboard
from VistaProductos import VistaProductos
from VistaTransac import VistaTransac

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue") 

class VistaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Sistema de Gestión Modular")
        self.geometry("900x600")

        # Configuración del Grid Layout (1 fila, 2 columnas)
        # Columna 0 = Sidebar (pequeña), Columna 1 = Contenido (grande)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 1. CREACIÓN DEL SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Espacio al final

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Mi Empresa", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botones de navegación
        self.btn_dash = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=lambda: self.show_frame("VistaDashboard"))
        self.btn_dash.grid(row=1, column=0, padx=20, pady=10)

        self.btn_prod = ctk.CTkButton(self.sidebar_frame, text="Productos", command=lambda: self.show_frame("VistaProductos"))
        self.btn_prod.grid(row=2, column=0, padx=20, pady=10)

        self.btn_tran = ctk.CTkButton(self.sidebar_frame, text="Transacciones", command=lambda: self.show_frame("VistaTransac"))
        self.btn_tran.grid(row=3, column=0, padx=20, pady=10)

        # --- 2. ÁREA DE CONTENIDO CENTRAL ---
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        
        # Hacemos que el container permita apilar elementos
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # --- 3. INICIALIZACIÓN DE VISTAS ---
        self.frames = {}
        
        # Lista de clases a instanciar
        for F in (VistaDashboard, VistaProductos, VistaTransac):
            page_name = F.__name__
            # Instanciamos la clase pasando 'self' como controller
            frame = F(parent=self.main_container, controller=self)
            self.frames[page_name] = frame
            
            # Colocamos todas en la misma posición (se apilan una sobre otra)
            frame.grid(row=0, column=0, sticky="nsew")

        # Mostrar la primera ventana por defecto
        self.show_frame("VistaDashboard")

    def show_frame(self, page_name):
        """Trae al frente el frame seleccionado"""
        frame = self.frames[page_name]
        frame.tkraise()
