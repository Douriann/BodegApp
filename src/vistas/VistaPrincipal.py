import customtkinter as ctk
from vistas.VistaDashboard import VistaDashboard
from vistas.VistaProductos import VistaProductos
from vistas.VistaTransac import VistaTransac
from PIL import Image
from ConfigRutas import rutas


class VistaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Sistema de Gestión de Inventario")

        anchoVist = 1100
        altoVist = 650
        
        self.update_idletasks()
        
        anchoPant = self.winfo_screenwidth()
        altoPant = self.winfo_screenheight()

        x = (anchoPant // 2) - (anchoVist // 2)
        y = (altoPant // 2) - (altoVist // 2)

        self.geometry(f"{anchoVist}x{altoVist}+{x}+{y}")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- CREACIÓN DEL SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=240, fg_color="#c06ef7")
        self.sidebar_frame.grid(row=0, column=0, sticky="nse")
        
        # El weight=1 en la fila 4 empuja todo lo que sigue hacia abajo
        self.sidebar_frame.grid_rowconfigure(4, weight=1) 

        # --- SECCIÓN DEL LOGO (Imagen + Texto) ---
        # Definir la imagen
        logo_img = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("logo-bodegApp-blanco.png")), size=(170, 70))

        # Contenedor de la IMAGEN (Fila 0)
        self.logo_container = ctk.CTkLabel(
            self.sidebar_frame, 
            text="", 
            image=logo_img
        )
        self.logo_container.grid(row=0, column=0, pady=(20, 25), padx=10)

        # Iconos
        icono_dash = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-panel-de-control.png")), size=(26, 26))
        icono_prod = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-productos.png")), size=(26, 26))
        icono_tran = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-transaccion.png")), size=(26, 26))

        # Botones de navegación
        self.btn_dash = ctk.CTkButton(
            self.sidebar_frame, 
            text="Dashboard", 
            image=icono_dash,
            width=238, 
            height=50, 
            corner_radius=0,
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            fg_color="#c06ef7", 
            hover_color="#ab3df4", 
            anchor="w", 
            border_spacing=10,
            command=lambda: self.show_frame("VistaDashboard")
        )
        self.btn_dash.grid(row=1, column=0, padx=0, pady=0, sticky="ew")

        self.btn_prod = ctk.CTkButton(
            self.sidebar_frame, 
            text="Productos", 
            image=icono_prod,
            width=230, 
            height=50, 
            corner_radius=0,
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            fg_color="#c06ef7", 
            hover_color="#ab3df4", 
            anchor="w", 
            border_spacing=10,
            command=lambda: self.show_frame("VistaProductos")
        )
        self.btn_prod.grid(row=2, column=0, padx=0, pady=0, sticky="ew")

        self.btn_tran = ctk.CTkButton(
            self.sidebar_frame, 
            text="Transaccion", 
            image=icono_tran,
            width=230, 
            height=50, 
            corner_radius=0,
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            fg_color="#c06ef7", 
            hover_color="#ab3df4", 
            anchor="w", 
            border_spacing=10,
            command=lambda: self.show_frame("VistaTransac")
        )
        self.btn_tran.grid(row=3, column=0, padx=0, pady=0, sticky="ew")

        # --- SECCIÓN DE APARIENCIA PERSONALIZADA ---

        icono_tema= ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-paleta-de-color.png")), size=(20, 20))

        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="  Tema", 
            image=icono_tema,
            compound="left",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            anchor="w"
        )
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["Claro", "Oscuro", "Sistema"],
            command=self.change_appearance_mode_event,
            height=35,
            fg_color="#ab3df4",          # Color del fondo (morado oscuro)
            button_color="#ab3df4",      # Color del botón/flecha
            button_hover_color="#780ac1", # Color al pasar el mouse
            dropdown_fg_color="#ab3df4",  # Color de la lista desplegable
            dropdown_hover_color="#780ac1"
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=15, pady=(10, 20), sticky="ew")
        self.appearance_mode_optionemenu.set("Sistema")

        # --- ÁREA DE CONTENIDO CENTRAL ---
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # --- INICIALIZACIÓN DE VISTAS ---
        self.frames = {}
        for F in (VistaDashboard, VistaProductos, VistaTransac):
            page_name = F.__name__
            frame = F(parent=self.main_container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("VistaDashboard")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def change_appearance_mode_event(self, seleccion_usuario: str):
        # Mapeamos la selección en español a la instrucción en inglés
        if seleccion_usuario == "Claro":
            ctk.set_appearance_mode("Light")
        elif seleccion_usuario == "Oscuro":
            ctk.set_appearance_mode("Dark")
        elif seleccion_usuario == "Sistema":
            ctk.set_appearance_mode("System")