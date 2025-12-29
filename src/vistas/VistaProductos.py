import customtkinter as ctk
from servicios.ProductoDAO import ProductoDAO
from modelos.Producto import Producto
from vistas.VistaModifProducto import VistaModifProducto, VentanaVerificacion
from vistas.VistaCrearProducto import VistaCrearProducto
from PIL import Image
from ConfigRutas import rutas

class VentanaConfirmacion(ctk.CTkToplevel):
    def __init__(self, parent, titulo, mensaje, comando_si):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("400x220")
        self.attributes("-topmost", True)
        self.grab_set()
        self.resizable(False, False)
        self.comando_si = comando_si

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 110
        self.geometry(f"400x220+{x}+{y}")

        self.main_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color="#E74C3C")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.main_frame, text="⚠️ " + titulo, font=("Segoe UI", 18, "bold"), text_color="#E74C3C").pack(pady=(20, 5))
        ctk.CTkLabel(self.main_frame, text=mensaje, font=("Segoe UI", 13), wraplength=340).pack(pady=10, padx=20)

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        self.btn_si = ctk.CTkButton(btn_frame, text="Sí, Eliminar", fg_color="#E74C3C", hover_color="#C0392B",
                                   width=120, height=35, font=("Segoe UI", 13, "bold"), command=self._ejecutar_si)
        self.btn_si.pack(side="right", padx=10)

        self.btn_no = ctk.CTkButton(btn_frame, text="Cancelar", fg_color=("#94a3b8", "#475569"), hover_color="#334155",
                                   width=120, height=35, font=("Segoe UI", 13, "bold"), command=self.destroy)
        self.btn_no.pack(side="right", padx=10)

    def _ejecutar_si(self):
        self.comando_si()
        self.destroy()

class VistaProductos(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.marcas_dict = self._cargar_diccionario_marcas()
        
        # --- HEADER ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.titulo = ctk.CTkLabel(header_frame, text="Inventario de Productos", font=("Segoe UI", 24, "bold"))
        self.titulo.pack(side="left", anchor="n")

        self.btn_nuevo = ctk.CTkButton(
            header_frame, text="+ Nuevo Producto", 
            fg_color="#ab3df4", hover_color="#920cec",
            font=("Segoe UI", 14, "bold"), height=35,
            command=self.crear_producto
        )
        self.btn_nuevo.pack(side="right", pady=(35, 10))

        # --- BÚSQUEDA ---
        icono_buscar = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-busqueda.png")), size=(20, 20))
        self.search_card = ctk.CTkFrame(self, fg_color=("white", "#2b2b2b"), height=70)
        self.search_card.pack(fill="x", padx=20, pady=(10, 5)) 
        self.search_card.grid_columnconfigure(0, weight=1) 

        self.entry_buscar = ctk.CTkEntry(self.search_card, height=35, placeholder_text="Buscar producto...", border_color="#ab3df4")
        self.entry_buscar.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="ew")
        self.entry_buscar.bind("<KeyRelease>", self.verificar_busqueda_vacia)

        btn_buscar = ctk.CTkButton(self.search_card, text="Buscar", width=110, height=35, fg_color="#ab3df4", hover_color="#920cec",
                                  command=self.buscar_productos, image=icono_buscar)
        btn_buscar.grid(row=0, column=1, padx=(0, 20), pady=15)

        # --- CONTADOR ---
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(fill="x", padx=25, pady=(0, 10))
        self.lbl_contador = ctk.CTkLabel(self.info_frame, text="Mostrando 0 productos", font=("Segoe UI", 12, "italic"), text_color=("#555555", "#aaaaaa"))
        self.lbl_contador.pack(side="left")

        # --- TABLA ---
        self.tabla_container = ctk.CTkFrame(self, fg_color="transparent")
        self.tabla_container.pack(fill="both", expand=True, padx=20, pady=(10, 10))

        self.header_tabla = ctk.CTkFrame(self.tabla_container, fg_color="transparent", height=30)
        self.header_tabla.pack(fill="x", pady=(0, 5))

        columnas = [("ID", 0.04), ("PRODUCTO", 0.09), ("MARCA", 0.35), ("PRECIO", 0.50), ("STOCK", 0.65), ("ACCIONES", 0.82)]
        for texto, pos in columnas:
            ctk.CTkLabel(self.header_tabla, text=texto, font=("Segoe UI", 11, "bold"), text_color="#ab3df4").place(relx=pos, rely=0.5, anchor="w")

        self.scroll_filas = ctk.CTkScrollableFrame(self.tabla_container, fg_color="transparent", scrollbar_button_color="#ab3df4")
        self.scroll_filas.pack(fill="both", expand=True)

        self.cargar_datos()

    def actualizar_contador(self, cantidad):
        self.lbl_contador.configure(text=f"Resultados encontrados: {cantidad} productos")

    def verificar_busqueda_vacia(self, event):
        if not self.entry_buscar.get().strip():
            self.cargar_datos()

    def crear_fila_producto(self, p):
        es_critico = p.stock_actual <= 10 or p.stock_actual < p.stock_minimo
        es_muy_critico = p.stock_actual <= 5
        
        # Colores
        color_fondo = ("#FDEDEC", "#422020") if es_muy_critico else ("white", "#333333")
        color_hover = ("#FADBD8", "#5D2929") if es_muy_critico else ("#f2f2f2", "#3d3d3d")
        color_texto_stock = "#E74C3C" if es_muy_critico else ("#F39C12" if es_critico else ("#333333", "white"))

        # Frame de la fila (SIN hover_color para evitar el error)
        fila = ctk.CTkFrame(
            self.scroll_filas, 
            fg_color=color_fondo, 
            height=55, 
            corner_radius=8,
            border_width=2 if es_muy_critico else 0, 
            border_color="#E74C3C" if es_muy_critico else None
        )
        fila.pack(fill="x", pady=4, padx=5)
        fila.pack_propagate(False)

        # Funciones para simular el hover manualmente
        def on_enter(e): fila.configure(fg_color=color_hover)
        def on_leave(e): fila.configure(fg_color=color_fondo)

        # Vincular eventos a la fila y a sus hijos (labels)
        fila.bind("<Enter>", on_enter)
        fila.bind("<Leave>", on_leave)

        # Labels
        lbl_id = ctk.CTkLabel(fila, text=f"#{p.id_producto}", font=("Segoe UI", 11, "bold"))
        lbl_id.place(relx=0.02, rely=0.5, anchor="w")
        
        lbl_nom = ctk.CTkLabel(fila, text=p.nombre_producto[:25], font=("Segoe UI", 12, "bold"))
        lbl_nom.place(relx=0.08, rely=0.5, anchor="w")
        
        ctk.CTkLabel(fila, text=self.marcas_dict.get(p.id_marca, "N/A"), font=("Segoe UI", 11)).place(relx=0.35, rely=0.5, anchor="w")
        ctk.CTkLabel(fila, text=f"${p.precio_venta:,.2f}", font=("Segoe UI", 12)).place(relx=0.52, rely=0.5, anchor="w")
        
        label_stock_text = f"{p.stock_actual} ¡BAJO!" if es_critico else str(p.stock_actual)
        ctk.CTkLabel(fila, text=label_stock_text, font=("Segoe UI", 13, "bold"), text_color=color_texto_stock).place(relx=0.65, rely=0.5, anchor="w")

        # Botones
        icono_editar = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-editar.png")), size=(20, 20))
        icono_basura = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-basura.png")), size=(20, 20))

        btn_edit = ctk.CTkButton(fila, text=None, width=32, height=30, fg_color="#0070b8", image=icono_editar, command=lambda: self.abrir_formulario_edicion(p))
        btn_edit.place(relx=0.82, rely=0.5, anchor="w")

        btn_del = ctk.CTkButton(fila, text=None, width=32, height=30, fg_color="#E74C3C", hover_color="#C0392B", image=icono_basura, command=lambda: self.confirmar_eliminacion(p))
        btn_del.place(relx=0.90, rely=0.5, anchor="w")

    def cargar_datos(self):
        for child in self.scroll_filas.winfo_children(): child.destroy()
        dao = ProductoDAO()
        productos = [p for p in dao.consultar_todos() if p.estatus == 1]
        for p in productos: self.crear_fila_producto(p)
        self.actualizar_contador(len(productos))

    def buscar_productos(self):
        termino = self.entry_buscar.get().strip()
        if not termino: return
        for child in self.scroll_filas.winfo_children(): child.destroy()
        dao = ProductoDAO()
        resultados = [p for p in dao.buscar_por_nombre(termino) if p.estatus == 1]
        if not resultados:
            VentanaVerificacion(self.master.winfo_toplevel(), "SIN RESULTADOS", "No hay coincidencias.", es_error=True)
            self.cargar_datos()
            return
        for p in resultados: self.crear_fila_producto(p)
        self.actualizar_contador(len(resultados))

    def confirmar_eliminacion(self, producto):
        def proceder():
            dao = ProductoDAO()
            producto.estatus = 0
            if dao.modificar_producto(producto):
                VentanaVerificacion(self.master.winfo_toplevel(), "ELIMINADO", f"'{producto.nombre_producto}' ha sido borrado.")
                self.cargar_datos()
        VentanaConfirmacion(self.master.winfo_toplevel(), "CONFIRMAR ELIMINACIÓN", f"¿Deseas eliminar {producto.nombre_producto}?", comando_si=proceder)

    def abrir_formulario_edicion(self, producto):
        VistaModifProducto(self.master.winfo_toplevel(), producto, self.cargar_datos)

    def crear_producto(self):
        VistaCrearProducto(self.master.winfo_toplevel(), self.cargar_datos)

    def _cargar_diccionario_marcas(self):
        dao = ProductoDAO()
        return {id_m: nombre for id_m, nombre in dao.obtener_marcas()}