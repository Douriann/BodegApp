import customtkinter as ctk
from vistas.VistaNuevaTransac import VistaNuevaTransac
from servicios.ServTransac import ServTransac
from servicios.ServProdTransac import ServProdTransac

class VistaTransac(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.ventana_toplevel = None 

        # --- HEADER PRINCIPAL ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # 1. El título se mantiene a la izquierda y arriba
        self.titulo = ctk.CTkLabel(header_frame, text="Historial de Transacciones", font=("Segoe UI", 24, "bold"))
        self.titulo.pack(side="left", anchor="n") # "n" de norte lo mantiene arriba

        # 2. Creamos un frame pequeño a la derecha para el botón (actúa como "ancla")
        boton_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        boton_container.pack(side="right", fill="y")

        # 3. Colocamos el botón dentro de ese frame con el margen superior
        self.btn_add = ctk.CTkButton(
            boton_container, 
            text="+ Nueva Transacción", 
            fg_color="#ab3df4", 
            hover_color="#c06ef7",
            font=("Segoe UI", 14, "bold"), 
            height=35,
            command=self.abrir_ventana_nueva
        )
        self.btn_add.pack(pady=(35, 0))

        # --- PANEL DE DETALLES ---
        self.detalles_card = ctk.CTkFrame(self, fg_color=("white", "#2b2b2b"), height=60) # Altura reducida
        self.detalles_card.pack(fill="x", padx=20, pady=(10, 25))
        
        self.label_detalles = ctk.CTkLabel(
            self.detalles_card, 
            text="Selecciona una transacción para ver los detalles", 
            font=("Segoe UI", 13, "italic"),
            text_color="gray"
        )
        self.label_detalles.pack(pady=15, padx=20)

        # --- CONTENEDOR DE TABLA ---
        self.tabla_container = ctk.CTkFrame(self, fg_color="transparent")
        self.tabla_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # --- ENCABEZADO DE TABLA COMPACTO ---
        # height=30 y pack_propagate(False) eliminan el espacio sobrante
        self.header_tabla = ctk.CTkFrame(self.tabla_container, fg_color="transparent", height=30)
        self.header_tabla.pack(fill="x", pady=(0, 5)) 
        self.header_tabla.pack_propagate(False) 
        
        # Definición de anchos proporcionales (suman 1.0)
        columnas = [("ID", 0.05), ("FECHA", 0.25), ("TIPO", 0.25), ("TOTAL", 0.20), ("ACCIONES", 0.25)]
        
        pos_x = 0.02 # Margen inicial
        for texto, ancho in columnas:
            lbl = ctk.CTkLabel(
                self.header_tabla, 
                text=texto, 
                font=("Segoe UI", 11, "bold"), 
                text_color="#ab3df4"
            )
            lbl.place(relx=pos_x, rely=0.5, anchor="w")
            pos_x += ancho

        # --- CONTENEDOR DE FILAS (SCROLLABLE) ---
        self.scroll_filas = ctk.CTkScrollableFrame(
            self.tabla_container, 
            fg_color="transparent",
            label_text=""
        )
        self.scroll_filas.pack(fill="both", expand=True)

        self.cargar_datos()

        # Escuchar eventos de nuevas transacciones para refrescar la tabla
        self.bind("<<TransaccionCreada>>", lambda e: self.cargar_datos())

    def crear_fila_transaccion(self, transac):
        # Cada fila es una "tarjeta" compacta (height=45)
        fila = ctk.CTkFrame(self.scroll_filas, fg_color=("white", "#333333"), height=45, corner_radius=6)
        fila.pack(fill="x", pady=3, padx=2)
        fila.pack_propagate(False)

        val_tipo = "COMPRA" if transac.id_tipo == 1 else "VENTA"
        color_badge = "#e74c3c" if val_tipo == "COMPRA" else "#2ecc71"

        # Colocación de datos alineados con el encabezado
        ctk.CTkLabel(fila, text=f"#{transac.id_transaccion}", font=("Segoe UI", 11, "bold")).place(relx=0.02, rely=0.5, anchor="w")
        ctk.CTkLabel(fila, text=transac.fecha_transaccion, font=("Segoe UI", 11)).place(relx=0.07, rely=0.5, anchor="w")
        
        # Badge de Tipo
        badge = ctk.CTkFrame(fila, fg_color=color_badge, corner_radius=4, height=20)
        badge.place(relx=0.32, rely=0.5, anchor="center")
        ctk.CTkLabel(badge, text=val_tipo, text_color="white", font=("Segoe UI", 9, "bold"), height=30).pack(padx=10)

        # Total
        ctk.CTkLabel(fila, text=f"$ {float(transac.total):,.2f}", font=("Segoe UI", 12, "bold")).place(relx=0.52, rely=0.5, anchor="w")

        # Botón Acciones
        btn_ver = ctk.CTkButton(
            fila, text="Ver Detalles", width=90, height=24, 
            fg_color="transparent", border_width=1, border_color="#ab3df4",
            text_color=("black", "white"), hover_color="#ab3df4",
            font=("Segoe UI", 11),
            command=lambda t=transac: self.seleccionar_transaccion(t)
        )
        btn_ver.place(relx=0.77, rely=0.5, anchor="w")

    def cargar_datos(self):
        for child in self.scroll_filas.winfo_children():
            child.destroy()

        servicio = ServTransac()
        transacciones = servicio.consultar_transacciones()
        for transac in transacciones:
            self.crear_fila_transaccion(transac)

    def seleccionar_transaccion(self, transac):
        servicio_detalles = ServProdTransac()
        detalles = servicio_detalles.consultar_detalles_por_transaccion(transac.id_transaccion)
        
        if detalles:
            # Iniciamos el encabezado con un salto de línea doble para separar del primer producto
            detalles_text = f"Transacción #{transac.id_transaccion}:\n\n"
            
            # Creamos la lista de productos (sin el \n interno para que el join lo controle mejor)
            items = [f"• {d.nombre_producto} (x{d.cantidad_producto})" for d in detalles]
            
            # UNIMOS CON SALTO DE LÍNEA: Esto reemplaza al "|" y los pone uno abajo del otro
            detalles_text += "\n".join(items)
            
            # Configuramos el label
            self.label_detalles.configure(text=detalles_text, text_color=("#ab3df4", "#D1D1D1"), font=("Segoe UI", 14, "bold"), anchor="w")
        else:
            self.label_detalles.configure(text="Sin detalles disponibles.", text_color="gray")

    def abrir_ventana_nueva(self):
        if self.ventana_toplevel is None or not self.ventana_toplevel.winfo_exists():
            self.ventana_toplevel = VistaNuevaTransac(self)
            self.ventana_toplevel.after(100, self.ventana_toplevel.lift)
        else:
            self.ventana_toplevel.focus()

    def recibir_datos_nuevos(self, datos):
        self.cargar_datos()