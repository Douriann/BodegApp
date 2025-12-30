import customtkinter as ctk
from servicios.Sophia import Agente
from google import genai
import os
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
        self.title(f"Detalles del Agente:")

        label_nombre = ctk.CTkLabel(self, text=f"Nombre: ", font=("Roboto", 18))
        label_nombre.pack(pady=10)

        label_id = ctk.CTkLabel(self, text=f"ID:", font=("Roboto", 14))
        label_id.pack(pady=5)

        label_email = ctk.CTkLabel(self, text=f"Email: ", font=("Roboto", 14))
        label_email.pack(pady=5)

        label_telefono = ctk.CTkLabel(self, text=f"Teléfono: ", font=("Roboto", 14))
        label_telefono.pack(pady=5)

        # Textbox con scrollbar (ambos con customtkinter)
        frame_text = ctk.CTkFrame(self)
        frame_text.pack(fill="both", expand=False, padx=10, pady=(5,10))

        self.textbox = ctk.CTkTextbox(frame_text, width=340, height=100)
        self.textbox.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(frame_text, orientation="vertical", command=self.textbox.yview)
        scrollbar.pack(side="right", fill="y")

        # Vincular el scrollbar al textbox (si el widget lo soporta)
        try:
            self.textbox.configure(yscrollcommand=scrollbar.set)
        except Exception:
            pass

        # Entry debajo del textbox
        self.entry_enviar = ctk.CTkEntry(self, placeholder_text="Escribe aquí...")
        self.entry_enviar.pack(fill="x", padx=10, pady=(0,10))

        # Botón "enviar" con comando
        btn_enviar = ctk.CTkButton(self, text="enviar", command=self.enviar_mensaje)
        btn_enviar.pack(pady=5)

        btn_cerrar = ctk.CTkButton(self, text="Cerrar", command=self.destroy)
        btn_cerrar.pack(pady=10)
    
    def enviar_mensaje(self):
        mensaje = (self.entry_enviar.get() or "").strip()
        if not mensaje:
            return
                    # Mostrar el mensaje del usuario
        self.textbox.insert("end", f"Tú: {mensaje}\n")
        self.entry_enviar.delete(0, "end")
        try:

            # Enviar al agente y mostrar la respuesta
            respuesta = self.sophie.send(mensaje)
            self.textbox.insert("end", f"Sophie: {respuesta}\n")

            # Intentar desplazar al final si el widget lo soporta
            try:
                self.textbox.see("end")
            except Exception:
                pass
        except Exception as e:
            self.textbox.insert("end", f"Error al enviar el mensaje: {e}\n")
            respuesta = f"Error al enviar el mensaje: {e}"
        return respuesta