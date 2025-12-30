from google import genai
import json
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # python-dotenv is optional; if not installed, environment variables must be set externally
    pass
from servicios.ServBusqProduc import ServBusqProduc
from servicios.ServTransac import ServTransac
from servicios.ProductoDAO import ProductoDAO

servicio_busqueda = ProductoDAO()
servicio_transaccion = ServTransac()

def obtener_productos():
    productos = servicio_busqueda.consultar_todos()
    return productos

def obtener_transacciones():
    transacciones = servicio_transaccion.consultar_transacciones()
    return transacciones

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set. Define it in your environment or in a .env file.")


product_tool = {
    "type": "function",
    "name": "obtener_productos",
    "description": "Obtiene la lista de productos disponibles en la base de datos.",
    "parameters": {
        "type": "object",
        "properties": {
            "productos": {
                "type": "array", "description": "Lista de productos disponibles."
            },
            "producto": {"type": "object", "description": "valores del objeto producto, dado por la clase Producto"}
        },
        "required": []
    },
}

transactions_tool = {
    "type": "function",
    "name": "obtener_transacciones",
    "description": "Obtiene la lista de transacciones registradas en la base de datos.",
    "parameters": {
        "type": "object",
        "properties": {
            "transacciones": {"type": "array", "description": "Lista de transacciones."},
            "transaccion": {"type": "object", "description": "Objeto Transaccion (id, fecha, tipo, total, observaciones, estatus)"}
        },
        "required": []
    },
}


class Agente:
    """Clase que maneja interacciones con el modelo y soporta llamadas a herramientas (tools).

    Uso:
        agent = Agente(client, tools=[product_tool])
        respuesta = agent.send("Hola, mi nombre es Adrian.")
    """

    def __init__(self, client, tools=[product_tool, transactions_tool], model="gemini-2.5-flash-lite"):
        self.client = client
        self.tools = tools or []
        self.model = model
        self.last_interaction_id = None

    def send(self, message: str, tools=None) -> str:
        """Envía un mensaje al modelo y retorna la respuesta textual final.

        Si el modelo hace una llamada a función (tool), la ejecuta localmente y devuelve
        el resultado al modelo, luego retorna la respuesta final.
        """
        use_tools = tools if tools is not None else (self.tools if self.tools else None)

        kwargs = {"model": self.model, "input": message}
        if self.last_interaction_id:
            kwargs["previous_interaction_id"] = self.last_interaction_id
        if use_tools:
            kwargs["tools"] = use_tools

        interaction = self.client.interactions.create(**kwargs)
        self.last_interaction_id = interaction.id

        # Manejar llamadas a funciones si las hay
        for output in interaction.outputs:
            if getattr(output, "type", None) == "function_call":
                # Manejo de funciones soportadas
                if output.name == "obtener_productos":
                    productos_raw = obtener_productos()
                    productos_serial = []
                    for p in productos_raw:
                        productos_serial.append({
                            "id_producto": p.id_producto,
                            "nombre_producto": p.nombre_producto,
                            "id_marca": p.id_marca,
                            "presentacion": p.presentacion,
                            "precio_compra": p.precio_compra,
                            "precio_venta": p.precio_venta,
                            "stock_actual": p.stock_actual,
                            "stock_minimo": p.stock_minimo
                        })

                    result_json = json.dumps(productos_serial, ensure_ascii=False)

                    interaction = self.client.interactions.create(
                        model=self.model,
                        previous_interaction_id=interaction.id,
                        input=[{
                            "type": "function_result",
                            "name": output.name,
                            "call_id": output.id,
                            "result": result_json
                        }]
                    )
                    self.last_interaction_id = interaction.id

                elif output.name == "obtener_transacciones":
                    trans_raw = obtener_transacciones()
                    trans_serial = []
                    for t in trans_raw:
                        trans_serial.append({
                            "id_transaccion": t.id_transaccion,
                            "fecha_transaccion": t.fecha_transaccion,
                            "id_tipo": t.id_tipo,
                            "total": t.total,
                            "observaciones": t.observaciones,
                            "estatus": t.estatus
                        })

                    result_json = json.dumps(trans_serial, ensure_ascii=False)

                    interaction = self.client.interactions.create(
                        model=self.model,
                        previous_interaction_id=interaction.id,
                        input=[{
                            "type": "function_result",
                            "name": output.name,
                            "call_id": output.id,
                            "result": result_json
                        }]
                    )
                    self.last_interaction_id = interaction.id

                else:
                    # Función desconocida
                    interaction = self.client.interactions.create(
                        model=self.model,
                        previous_interaction_id=interaction.id,
                        input=[{
                            "type": "function_result",
                            "name": output.name,
                            "call_id": output.id,
                            "result": f"Función desconocida: {output.name}"
                        }]
                    )
                    self.last_interaction_id = interaction.id

        # Retornar la última salida textual disponible
        if getattr(interaction, "outputs", None):
            last = interaction.outputs[-1]
            if getattr(last, "text", None) is not None:
                return last.text
            elif getattr(last, "type", None) == "function_call":
                return f"Tool call executed: {last.name}"
            else:
                return str(getattr(last, "arguments", None))

        return ""


# Ejemplo de uso: crear el agente e interactuar
"""if __name__ == "__main__":
    agent = Agente(client, tools=[product_tool, transactions_tool])

    # Interacción 1: decirle al agente tu nombre
    respuesta1 = agent.send("Hola, mi nombre es Adrian.")
    print("Agente:", respuesta1)

    # Interacción 2: pedir que diga el nombre que recuerda y luego muestre productos
    respuesta2 = agent.send(
        "Antes de mostrar los productos, por favor di el nombre del usuario que conoces, y luego muéstrame los productos disponibles."
    )
    print("Agente:", respuesta2)

    # Interacción 3: pedir que diga el nombre que recuerda y luego muestre transacciones
    respuesta3 = agent.send(
        "Cuales productos están bajos de stock? compara el stock actual con el stock mínimo."
    )
    print("Agente:", respuesta3)"""