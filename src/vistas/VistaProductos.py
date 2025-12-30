import customtkinter as ctk
import pandas as pd
import os
from tkinter import filedialog, messagebox
from servicios.ProductoDAO import ProductoDAO
from modelos.Producto import Producto
from vistas.VistaModifProducto import VistaModifProducto, VentanaVerificacion
from vistas.VistaCrearProducto import VistaCrearProducto
from PIL import Image
from ConfigRutas import rutas

# --- VENTANA DE CONFIRMACIÓN PARA ELIMINAR ---
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

# --- VENTANA DE ÉXITO PARA EXPORTACIÓN ---
class VentanaExitoExportar(ctk.CTkToplevel):
    def __init__(self, parent, ruta_archivo):
        super().__init__(parent)
        self.title("Exportación Exitosa")
        self.geometry("400x240")
        self.attributes("-topmost", True)
        self.grab_set()
        self.ruta_directorio = os.path.dirname(ruta_archivo)

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 120
        self.geometry(f"400x240+{x}+{y}")

        self.main_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color="#27AE60")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.main_frame, text="✅ ¡Completado!", font=("Segoe UI", 18, "bold"), text_color="#27AE60").pack(pady=(20, 5))
        ctk.CTkLabel(self.main_frame, text="El inventario se ha exportado correctamente a Excel.", font=("Segoe UI", 13), wraplength=340).pack(pady=10, padx=20)

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        self.btn_abrir = ctk.CTkButton(btn_frame, text="Abrir Carpeta", fg_color="#27AE60", hover_color="#1E8449",
                                      width=140, height=35, font=("Segoe UI", 13, "bold"), command=self._abrir_y_cerrar)
        self.btn_abrir.pack(side="left", padx=10)

        self.btn_cerrar = ctk.CTkButton(btn_frame, text="Aceptar", fg_color=("#94a3b8", "#475569"), hover_color="#334155",
                                       width=120, height=35, font=("Segoe UI", 13, "bold"), command=self.destroy)
        self.btn_cerrar.pack(side="left", padx=10)

    def _abrir_y_cerrar(self):
        os.startfile(self.ruta_directorio)
        self.destroy()

# --- VISTA PRINCIPAL DE PRODUCTOS ---
class VistaProductos(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.marcas_dict = self._cargar_diccionario_marcas()
        self.productos_actuales = [] # Para exportación contextual
        
        # --- HEADER ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.titulo = ctk.CTkLabel(header_frame, text="Inventario de Productos", font=("Segoe UI", 24, "bold"))
        self.titulo.pack(side="left", anchor="n")

        #Icono de Excel
        icono_excel = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-ms-excel.png")), size=(20, 20))

        self.btn_exportar = ctk.CTkButton(
            header_frame, text="Exportar Excel", 
            image=icono_excel,
            fg_color="#27AE60", hover_color="#1E8449",
            font=("Segoe UI", 14, "bold"), height=35,
            command=self.exportar_a_excel
        )
        self.btn_exportar.pack(side="right", padx=(10, 0), pady=(35, 10))

        self.btn_nuevo = ctk.CTkButton(
            header_frame, text="+ Nuevo Producto", 
            fg_color="#ab3df4", hover_color="#920cec",
            font=("Segoe UI", 14, "bold"), height=35,
            command=self.crear_producto
        )
        self.btn_nuevo.pack(side="right", pady=(35, 10))

        # --- BÚSQUEDA ---
        icono_buscar = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-busqueda.png")), size=(20, 20))
        self.search_card = ctk.CTkFrame(self, fg_color=("white", "#2b2b2b"), height=70, corner_radius=15)
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

        self.scroll_filas = ctk.CTkScrollableFrame(self.tabla_container, fg_color="transparent", scrollbar_button_color="#ab3df4", scrollbar_button_hover_color="#c06ef7")
        self.scroll_filas.pack(fill="both", expand=True)

        self.cargar_datos()

    def exportar_a_excel(self):
        if not self.productos_actuales:
            messagebox.showwarning("Exportar", "No hay datos para exportar.")
            return

        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Guardar Inventario",
            initialfile="Reporte_Inventario.xlsx"
        )

        if ruta_archivo:
            try:
                datos = []
                for p in self.productos_actuales:
                    estado = "CRÍTICO" if p.stock_actual <= 5 else ("BAJO" if p.stock_actual < p.stock_minimo else "OK")
                    datos.append({
                        "ID": p.id_producto,
                        "Producto": p.nombre_producto,
                        "Marca": self.marcas_dict.get(p.id_marca, "N/A"),
                        "Precio": p.precio_venta,
                        "Stock": p.stock_actual,
                        "Estado": estado
                    })
                
                df = pd.DataFrame(datos)
                df.to_excel(ruta_archivo, index=False)
                
                # Mostrar ventana de éxito personalizada
                VentanaExitoExportar(self.master.winfo_toplevel(), ruta_archivo)

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar: {e}")

    def crear_fila_producto(self, p):
        # Lógica de Stock
        es_critico = p.stock_actual <= 10 or p.stock_actual < p.stock_minimo
        es_muy_critico = p.stock_actual <= 5
        
        # Colores de Fila
        color_fondo = ("white", "#333333")
        color_hover = ("#f2f2f2", "#3d3d3d")

        # Configuración de Badge
        if es_muy_critico:
            bg_b, fg_b, txt_s = ("#FDEDEC", "#5D2929"), "#E74C3C", f"{p.stock_actual} CRÍTICO"
        elif es_critico:
            bg_b, fg_b, txt_s = ("#FEF9E7", "#5D4E29"), "#F39C12", f"{p.stock_actual} BAJO"
        else:
            bg_b, fg_b, txt_s = ("#EAFAF1", "#1D3D2F"), "#27AE60", f"{p.stock_actual} OK"

        # Frame de Fila
        fila = ctk.CTkFrame(self.scroll_filas, fg_color=color_fondo, height=55, corner_radius=12)
        fila.pack(fill="x", pady=4, padx=5)
        fila.pack_propagate(False)

        # Hover manual
        def on_enter(e): fila.configure(fg_color=color_hover)
        def on_leave(e): fila.configure(fg_color=color_fondo)
        fila.bind("<Enter>", on_enter)
        fila.bind("<Leave>", on_leave)

        # Datos
        ctk.CTkLabel(fila, text=f"#{p.id_producto}", font=("Segoe UI", 11, "bold")).place(relx=0.02, rely=0.5, anchor="w")
        ctk.CTkLabel(fila, text=p.nombre_producto[:25], font=("Segoe UI", 12, "bold")).place(relx=0.08, rely=0.5, anchor="w")
        ctk.CTkLabel(fila, text=self.marcas_dict.get(p.id_marca, "N/A"), font=("Segoe UI", 11)).place(relx=0.35, rely=0.5, anchor="w")
        ctk.CTkLabel(fila, text=f"${p.precio_venta:,.2f}", font=("Segoe UI", 12)).place(relx=0.52, rely=0.5, anchor="w")
        
        # El Badge
        badge = ctk.CTkFrame(fila, fg_color=bg_b, corner_radius=20, height=26)
        badge.place(relx=0.65, rely=0.5, anchor="w")
        ctk.CTkLabel(badge, text=txt_s, font=("Segoe UI", 11, "bold"), text_color=fg_b).pack(padx=12, pady=2)

        # Botones
        icono_edit = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-editar.png")), size=(20, 20))
        icono_del = ctk.CTkImage(Image.open(rutas.obtener_ruta_imagen("icons-basura.png")), size=(20, 20))

        ctk.CTkButton(fila, text=None, width=32, height=30, fg_color="#0070b8", image=icono_edit, 
                      command=lambda: self.abrir_formulario_edicion(p)).place(relx=0.82, rely=0.5, anchor="w")

        ctk.CTkButton(fila, text=None, width=32, height=30, fg_color="#E74C3C", hover_color="#C0392B", image=icono_del, 
                      command=lambda: self.confirmar_eliminacion(p)).place(relx=0.90, rely=0.5, anchor="w")

    def cargar_datos(self):
        for child in self.scroll_filas.winfo_children(): child.destroy()
        dao = ProductoDAO()
        self.productos_actuales = [p for p in dao.consultar_todos() if p.estatus == 1]
        for p in self.productos_actuales: self.crear_fila_producto(p)
        self.actualizar_contador(len(self.productos_actuales))

    def buscar_productos(self):
        termino = self.entry_buscar.get().strip()
        if not termino: return
        for child in self.scroll_filas.winfo_children(): child.destroy()
        dao = ProductoDAO()
        self.productos_actuales = [p for p in dao.buscar_por_nombre(termino) if p.estatus == 1]
        if not self.productos_actuales:
            VentanaVerificacion(self.master.winfo_toplevel(), "SIN RESULTADOS", "No hay coincidencias.")
            self.cargar_datos()
            return
        for p in self.productos_actuales: self.crear_fila_producto(p)
        self.actualizar_contador(len(self.productos_actuales))

    def actualizar_contador(self, cantidad):
        self.lbl_contador.configure(text=f"Resultados encontrados: {cantidad} productos")

    def verificar_busqueda_vacia(self, event):
        if not self.entry_buscar.get().strip(): self.cargar_datos()

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