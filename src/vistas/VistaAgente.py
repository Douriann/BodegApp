
import customtkinter as ctk
from servicios.Sophia import Agente
from google import genai
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

        ancho, alto = 720, 520
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

        # --- Área de conversación ---
        frame_text = ctk.CTkFrame(self, fg_color=self.CARD_COLOR, corner_radius=10,
                                  border_width=1, border_color=self.PRIMARY_DARK)
        frame_text.pack(fill="both", expand=True, padx=16, pady=(8, 12))

        self.textbox = ctk.CTkTextbox(frame_text, width=560, height=320,
                                       font=("Segoe UI", 15),
                                       text_color=self.TEXT_MAIN)
        self.textbox.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)

        scrollbar = ctk.CTkScrollbar(frame_text, orientation="vertical", command=self.textbox.yview,
                                     button_color=self.PRIMARY_DARK, button_hover_color=self.PRIMARY)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)

        try:
            self.textbox.configure(yscrollcommand=scrollbar.set)
        except Exception:
            pass

        # Hacer el textbox de solo lectura inicialmente
        try:
            self.textbox.configure(state="disabled")
        except Exception:
            pass

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
            width=220,
            font=self.FONT_BUTTON,
            fg_color=self.PRIMARY,
            hover_color=self.PRIMARY_DARK,
            command=self.enviar_primer_mensaje
        )
        self.btn_emp_conversacion.pack(side="left")

        btn_cerrar = ctk.CTkButton(
            actions,
            text="Cerrar",
            height=42,
            width=120,
            font=self.FONT_BUTTON,
            fg_color="#552575",
            hover_color="#b874e5",
            command=self.destroy
        )
        btn_cerrar.pack(side="right")

        # Estado inicial: entry y enviar deshabilitados
        try:
            self.entry_enviar.configure(state="disabled")
            self.btn_enviar.configure(state="disabled")
        except Exception:
            pass
    
    def enviar_mensaje(self):
        mensaje = (self.entry_enviar.get() or "").strip()
        if not mensaje:
            return
        # Mostrar el mensaje del usuario en textbox (temporalmente habilitar para insertar)
        try:
            self.textbox.configure(state="normal")
        except Exception:
            pass
        self.textbox.insert("end", f"Tú: {mensaje}\n")
        try:
            self.textbox.configure(state="disabled")
        except Exception:
            pass
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
        try:
            self.textbox.configure(state="normal")
        except Exception:
            pass
        self.textbox.insert("end", f"Sophie: {respuesta}\n")
        try:
            self.textbox.see("end")
        except Exception:
            pass
        try:
            self.textbox.configure(state="disabled")
        except Exception:
            pass
    
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
        - No realices funciones que no puedas cumplir (ej: no hagas reservas, no envíes emails, etc).
        SIGUIENTE INSTRUCCIÓN: Hablaras como si estuvieras hablando con el cliente por primera vez, así que saludale.
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