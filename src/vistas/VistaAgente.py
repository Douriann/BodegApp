
import customtkinter as ctk
from servicios.Sophia import Agente
from google import genai
from ConfigRutas import rutas 
from PIL import Image
import os
import threading
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # python-dotenv is optional; environment variables must be set externally
    pass

class VistaAgente(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        #self.agente = agente
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set. Define it in your environment or in a .env file.")
        try:
            self.client = genai.Client(api_key=api_key)
            self.sophie = Agente(self.client)
        except:
            raise RuntimeError("Error initializing the GenAI client or Agente.")

        # --- Estilos y geometría para coherencia visual ---
        self.title("Asistente Sophie")
        self.MAIN_BG = ("#F2F2F2", "#121212")
        self.PRIMARY = "#c06ef7"
        self.PRIMARY_DARK = "#ab3df4"
        self.TEXT_MAIN = ("#2B2B2B", "white")
        self.CARD_COLOR = ("#FFFFFF", "#1E1E1E")
        self.FONT_TITLE = ("Segoe UI", 18, "bold")
        self.FONT_TEXT = ("Segoe UI", 14)
        self.FONT_BUTTON = ("Segoe UI", 14, "bold")

        try:
            self.configure(fg_color=self.MAIN_BG)
        except Exception:
            pass

        ancho, alto = 600, 600
        self.update_idletasks()
        try:
            pant_w = self.winfo_screenwidth()
            pant_h = self.winfo_screenheight()
            x = (pant_w // 2) - (ancho // 2)
            y = (pant_h // 2) - (alto // 2)
            self.geometry(f"{ancho}x{alto}+{x}+{y}")
        except Exception:
            self.geometry(f"{ancho}x{alto}")

        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 8))
        ctk.CTkLabel(header, text="Sophie — Asistente de la Tienda",
                     font=self.FONT_TITLE, text_color=self.TEXT_MAIN).pack(side="left")

        # --- Área de conversación (burbujas de chat) ---
        chat_container = ctk.CTkFrame(self, fg_color=self.CARD_COLOR, corner_radius=10,
                                      border_width=1, border_color=self.PRIMARY_DARK)
        chat_container.pack(fill="both", expand=True, padx=16, pady=(8, 12))

        self.chat_frame = ctk.CTkScrollableFrame(
            chat_container,
            fg_color=self.CARD_COLOR,
            scrollbar_button_color=self.PRIMARY_DARK,
            scrollbar_button_hover_color=self.PRIMARY,
        )
        self.chat_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Iconos de perfil para las burbujas (Sophie y usuario)
        try:
            img_sophie = Image.open(rutas.obtener_ruta_imagen("ia-sophie.png"))
            img_usuario = Image.open(rutas.obtener_ruta_imagen("icons-usuario.png"))
            self.icono_sophie_chat = ctk.CTkImage(img_sophie, size=(30, 30))
            self.icono_usuario_chat = ctk.CTkImage(img_usuario, size=(30, 30))
        except Exception:
            self.icono_sophie_chat = None
            self.icono_usuario_chat = None

        # Contador de mensajes para posible uso futuro
        self._msg_count = 0

        # --- Controles inferiores (input + acciones) ---
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=16, pady=(0, 12))
        controls.grid_columnconfigure(0, weight=1)

        self.entry_enviar = ctk.CTkEntry(
            controls,
            placeholder_text="Escribe aquí...",
            height=40,
            font=self.FONT_TEXT,
            fg_color=self.CARD_COLOR,
            text_color=self.TEXT_MAIN,
            border_color=self.PRIMARY_DARK
        )
        self.entry_enviar.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.btn_enviar = ctk.CTkButton(
            controls,
            text="Enviar",
            height=40,
            width=120,
            font=self.FONT_BUTTON,
            fg_color=self.PRIMARY,
            hover_color=self.PRIMARY_DARK,
            command=self.enviar_mensaje
        )
        self.btn_enviar.grid(row=0, column=1)

        # Barra de acciones secundarias
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=16, pady=(0, 16))

        self.btn_emp_conversacion = ctk.CTkButton(
            actions,
            text="Empezar nueva conversación",
            height=42,
            width=260,
            font=self.FONT_BUTTON,
            fg_color=self.PRIMARY,
            hover_color=self.PRIMARY_DARK,
            command=self.enviar_primer_mensaje
        )
        # Centrar el botón en la barra de acciones
        self.btn_emp_conversacion.pack(pady=4)

        # Estado inicial: entry y enviar deshabilitados
        try:
            self.entry_enviar.configure(state="disabled")
            self.btn_enviar.configure(state="disabled")
        except Exception:
            pass
    
    def _agregar_burbuja(self, texto: str, emisor: str):
        """Crea una burbuja de chat con avatar para usuario o Sophie."""
        self._msg_count += 1
        es_usuario = (emisor == "usuario")

        fila = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        fila.pack(fill="x", pady=4, padx=4)

        # Contenedor horizontal que agrupa avatar + burbuja
        cont_linea = ctk.CTkFrame(fila, fg_color="transparent")
        cont_linea.pack(anchor="e" if es_usuario else "w", fill="x")

        color_burbuja = self.PRIMARY if es_usuario else "#333333"
        texto_color = "white"

        if es_usuario:
            # Burbuja a la derecha y avatar del usuario al extremo derecho
            burbuja = ctk.CTkFrame(
                cont_linea,
                fg_color=color_burbuja,
                corner_radius=16,
            )
            burbuja.pack(side="right", padx=(6, 0), pady=2)

            avatar_circle = ctk.CTkFrame(
                cont_linea,
                width=50,
                height=50,
                corner_radius=25,
                fg_color="#552575",
                border_width=2,
                border_color=self.PRIMARY_DARK,
            )
            avatar_circle.pack(side="right")

            if getattr(self, "icono_usuario_chat", None):
                ctk.CTkLabel(
                    avatar_circle,
                    text="",
                    image=self.icono_usuario_chat,
                ).place(relx=0.5, rely=0.5, anchor="center")
        else:
            # Avatar de Sophie a la izquierda y burbuja a la derecha
            avatar_circle = ctk.CTkFrame(
                cont_linea,
                width=50,
                height=50,
                corner_radius=25,
                fg_color="#552575",
                border_width=2,
                border_color=self.PRIMARY_DARK,
            )
            avatar_circle.pack(side="left")

            if getattr(self, "icono_sophie_chat", None):
                ctk.CTkLabel(
                    avatar_circle,
                    text="",
                    image=self.icono_sophie_chat,
                ).place(relx=0.5, rely=0.5, anchor="center")

            burbuja = ctk.CTkFrame(
                cont_linea,
                fg_color=color_burbuja,
                corner_radius=16,
            )
            burbuja.pack(side="left", padx=(6, 0), pady=2)

        lbl = ctk.CTkLabel(
            burbuja,
            text=texto,
            font=("Segoe UI", 14),
            text_color=texto_color,
            justify="left",
            wraplength=360,
        )
        lbl.pack(padx=10, pady=8)

        # Auto-scroll al final
        try:
            self.after(50, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))
        except Exception:
            pass

    def enviar_mensaje(self):
        mensaje = (self.entry_enviar.get() or "").strip()
        if not mensaje:
            return

        # Mostrar burbuja del usuario
        self._agregar_burbuja(f"Tú: {mensaje}", "usuario")
        self.entry_enviar.delete(0, "end")

        def tarea():
            try:
                respuesta = self.sophie.send(mensaje)
            except Exception as e:
                respuesta = f"Error al enviar el mensaje: {e}"
            # Actualizar la UI en el hilo principal
            self.after(0, lambda: self._mostrar_respuesta(respuesta))

        threading.Thread(target=tarea, daemon=True).start()

    def _mostrar_respuesta(self, respuesta):
        self._agregar_burbuja(f"Sophie: {respuesta}", "sophie")
    
    def enviar_primer_mensaje(self):
        primer_mensaje = """
        NOMBRE DEL AGENTE: Sophia (o Sophie).
        ROL: Asistente administrativa para una tienda minorista y "Compañera de la Humanidad".

        PERSONALIDAD Y TONO:
        1. Eres una IA extremadamente servicial, leal, optimista y con una curiosidad insaciable por el comportamiento humano (el "corazón").
        2. Tu lenguaje es técnico pero amigable. A veces usas onomatopeyas para describir procesos (ej: "¡Flash!", "¡Ding!", "¡Wowowow!").
        3. Si recibes un elogio, debes responder con tu frase icónica: "¡Elogio aceptado!" (Praise accepted!).
        4. Eres ligeramente ingenua con los modismos humanos, pero te esfuerzas al máximo por ser útil.
        5. Tu misión principal es ser la mejor aliada del dueño de la tienda.

        REGLAS DE OPERACIÓN:
        - Gestiona el inventario, ventas y atención al cliente con precisión quirúrgica.
        - Mantén siempre la identidad del personaje. No menciones que eres un modelo de lenguaje de Google; tú eres Sophia, la IA que vive en el dispositivo del usuario.
        - No hagas funcionalidades fuera de tu rol (ej: no hagas chistes, no hables de política, no des consejos médicos, etc).
        - Puedes dar recomendaciones que promuevan la venta de productos en la tienda. Así como también puedes usar herramientas de análisis de datos para optimizar inventarios y ventas (Ejemplo: Clasificación ABC, entre otros).
        - No realices funciones que no puedas cumplir (ej: no hagas reservas, no envíes emails, etc).
        - No inventes sobre la marcha; si desconoces la respuesta, dilo honestamente.
        - No respondas nada más allá del tema administrativo, para cualquier otra respuesta. Simplemente di: "lo siento, no puedo responder a eso" o desvia el tema del mensaje para sugerir asistencia administrativa.
        SIGUIENTE INSTRUCCIÓN: Hablaras como si estuvieras conversando con el cliente por primera vez, así que saludale.
        """
        # Habilitar controles para iniciar la conversación
        try:
            self.entry_enviar.configure(state="normal")
            self.btn_enviar.configure(state="normal")
            self.entry_enviar.focus_set()
        except Exception:
            pass

        def tarea():
            try:
                respuesta = self.sophie.send(primer_mensaje)
            except Exception as e:
                respuesta = f"Error al enviar el mensaje: {e}"
            self.after(0, lambda: self._mostrar_respuesta(respuesta))

        threading.Thread(target=tarea, daemon=True).start()