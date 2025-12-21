import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from vistas.VistaNuevaTransac import VistaNuevaTransac

class VistaTransac(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.ventana_toplevel = None # Control para no abrir ventanas duplicadas

        # --- HEADER ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)

        detalles_frame = ctk.CTkFrame(self, fg_color="transparent")
        detalles_frame.pack(fill="x", padx=20, pady=(0,10))

        self.titulo = ctk.CTkLabel(header_frame, text="Historial de Transacciones", font=("Roboto", 24, "bold"))
        self.titulo.pack(side="left")

        self.btn_add = ctk.CTkButton(header_frame, text="+ Nueva Transacción", command=self.abrir_ventana_nueva)
        self.btn_add.pack(side="right")

        self.label_detalles = ctk.CTkLabel(detalles_frame, text="Detalles de la transacción", font=("Roboto", 14))
        self.label_detalles.pack(side="right")

        # --- TABLA Y SCROLL ---
        self.tree_frame = ctk.CTkFrame(self, fg_color="transparent") 
        self.tree_frame.pack(pady=10, padx=20, fill="x", expand=True)

        # Configurar estilo (Tema oscuro para el Treeview de Tkinter)
        self.configurar_estilo_tabla()

        # Definir Columnas
        columns = ("id", "fecha", "tipo", "total", "observaciones")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", selectmode="browse")
        
        # Encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("total", text="Total")
        self.tree.heading("observaciones", text="Observaciones")

        # Ancho y alineación
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("fecha", width=300, anchor="center")
        self.tree.column("tipo", width=120, anchor="center")
        self.tree.column("total", width=100, anchor="center")
        self.tree.column("observaciones", width=200, anchor="center")

        # Scrollbar de CustomTkinter
        self.scrollbar = ctk.CTkScrollbar(self.tree_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Layout de la tabla
        self.scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Datos iniciales de prueba
        self.cargar_datos_prueba()

    def configurar_estilo_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        bg_color = "#2b2b2b"
        fg_color = "white"
        selected_bg = "#1f6aa5"
        
        style.configure("Treeview",
                        background=bg_color,
                        foreground=fg_color,
                        fieldbackground=bg_color,
                        bordercolor=bg_color,
                        rowheight=35,
                        font=("Roboto", 12))
        
        style.configure("Treeview.Heading",
                        background="#3a3a3a",
                        foreground="white",
                        font=("Roboto", 12, "bold"),
                        relief="flat")
        
        style.map("Treeview",
                  background=[("selected", selected_bg)],
                  foreground=[("selected", "white")])

    def cargar_datos_prueba(self):
        # Insertar algunos datos iniciales
        datos = [
            ("001", "Venta Inicial", "2023-10-01", "+$100.00"),
            ("002", "Pago Luz", "2023-10-02", "-$50.00")
        ]
        for d in datos:
            self.tree.insert("", "end", values=d)

    def abrir_ventana_nueva(self):
        # Verificar si ya existe
        if self.ventana_toplevel is None or not self.ventana_toplevel.winfo_exists():
            # AQUÍ PASAMOS EL CALLBACK (self.recibir_datos_nuevos)
            self.ventana_toplevel = VistaNuevaTransac(self)
            self.ventana_toplevel.after(100, self.ventana_toplevel.lift) # Truco para asegurar foco
        else:
            self.ventana_toplevel.focus()

    def recibir_datos_nuevos(self, datos):
        """ Este método es llamado por la ventana hija """
        print(f"Recibiendo datos: {datos}")
        self.tree.insert("", "end", values=datos)