import customtkinter as ctk
from vistas.VistaDashboard import VistaDashboard
from vistas.VistaProductos import VistaProductos
from vistas.VistaTransac import VistaTransac
from PIL import Image

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue") 

class VistaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        #Titulo de la ventana
        self.title("Sistema de Gestión de Inventario")

        #Configurar tamaño fijo y centrar
        anchoVist = 1000
        altoVist = 600
        
        # Forzamos la actualización para obtener datos reales del monitor
        self.update_idletasks()
        
        anchoPant = self.winfo_screenwidth()
        altoPant = self.winfo_screenheight()

        x = (anchoPant // 2) - (anchoVist // 2)
        y = (altoPant // 2) - (altoVist // 2)

        # Aplicamos la posición
        self.geometry(f"{anchoVist}x{altoVist}+{x}+{y}")
        
        # Configuración del Grid Layout (1 fila, 2 columnas)
        # Columna 0 = Sidebar (pequeña), Columna 1 = Contenido (grande)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        
        # --- 1. CREACIÓN DEL SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, fg_color="#9B3D95")
        self.sidebar_frame.grid(row=0, column=0, sticky="nse" )
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Espacio al final

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BodegApp", font=ctk.CTkFont(size=35, weight="bold"))
        self.logo_label.grid(row=0, column=0, pady=(30, 40))

        # Botones de navegación
        # Ahora que 'recursos' está al lado de 'main.py', esta ruta funcionará:
        icono_dash = ctk.CTkImage(Image.open("recursos/icons-panel-de-control.png"), size=(26, 26))
        icono_prod = ctk.CTkImage(Image.open("recursos/icons-productos.png"), size=(26, 26))
        icono_tran = ctk.CTkImage(Image.open("recursos/icons-transaccion.png"), size=(26, 26))

        self.btn_dash = ctk.CTkButton(
            self.sidebar_frame, 
            text="Dashboard",
            image=icono_dash,
            width=200,   # Ancho en píxeles
            height=50,   # Alto en píxeles
            corner_radius=0,
            font=ctk.CTkFont(family="Verdana", size=16, weight="bold"),
            fg_color="#9B3D95",       # Morado claro
            hover_color="#7f2376",    # Morado oscuro 
            anchor="w",      # Alinea el contenido a la izquierda
            border_spacing=10,
            command=lambda: self.show_frame("VistaDashboard")
          )
        self.btn_dash.grid(row=1, column=0, padx=0, pady=0, sticky="ew")

        self.btn_prod = ctk.CTkButton(
            self.sidebar_frame, 
            text="Productos",
            image=icono_prod,
            width=200,   # Ancho en píxeles
            height=50,   # Alto en píxeles
            corner_radius=0,
            font=ctk.CTkFont(family="Verdana", size=16, weight="bold"),
            fg_color="#9B3D95",       # Morado claro
            hover_color="#7f2376",    # Morado oscuro 
            anchor="w",      #Alinea el contenido a la izquierda
            border_spacing=10,
            command=lambda: self.show_frame("VistaProductos")
        )
        self.btn_prod.grid(row=2, column=0, padx=0, pady=0, sticky="ew")

        self.btn_tran = ctk.CTkButton(
            self.sidebar_frame, 
            text="Transaccion",
            image=icono_tran,
            width=200,   # Ancho en píxeles
            height=50,   # Alto en píxeles
            corner_radius=0,
            font=ctk.CTkFont(family="Verdana", size=16, weight="bold"),
            fg_color="#9B3D95",       # Morado claro
            hover_color="#7f2376",    # Morado oscuro
            anchor="w",      #Alinea el contenido a la izquierda
            border_spacing=10,
            command=lambda: self.show_frame("VistaTransac")
        )
        self.btn_tran.grid(row=3, column=0, padx=0, pady=0, sticky="ew")

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

    
