from google import genai
import json
import os
import unicodedata
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # python-dotenv is optional; if not installed, environment variables must be set externally
    pass
from servicios.ServBusqProduc import ServBusqProduc
from servicios.ServTransac import ServTransac
from servicios.ProductoDAO import ProductoDAO
from servicios.ServProdStockBajo import ServProdStockBajo
from servicios.ServConsultSophia import ServConsultSophia

servicio_stock_bajo = ServProdStockBajo()

servicio_busqueda = ProductoDAO()
servicio_transaccion = ServTransac()
servicio_consultas = ServConsultSophia()

def obtener_productos():
    productos = servicio_busqueda.consultar_todos()
    return productos

def obtener_transacciones():
    transacciones = servicio_transaccion.consultar_transacciones()
    return transacciones

def normalizar(texto: str) -> str:
    # Quitar tildes y normalizar a minúsculas
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto.strip().lower()

def existe_categoria(nombre_categoria: str) -> bool:
    categorias = servicio_busqueda.obtener_categorias()
    for _, descripcion in categorias:
        if normalizar(descripcion) in normalizar(nombre_categoria):
            return True
    return False

def existe_marca(nombre_marca: str) -> bool:
    marcas = servicio_busqueda.obtener_marcas()
    for _, nombre in marcas:
        if normalizar(nombre) in normalizar(nombre_marca):
            return True
    return False

def productos_bajo_stock():
    productos = servicio_stock_bajo.obtener_productos_bajo_stock()
    resultado = []
    for p in productos:
        resultado.append({
            "id_producto": p.id_producto,
            "nombre_producto": p.nombre_producto,
            "stock_actual": p.stock_actual,
            "stock_minimo": p.stock_minimo
        })
    return resultado


def top_productos(limite: int | None = None):
    """Obtiene el top de productos vendidos (histórico), opcionalmente limitado.

    Retorna una lista de diccionarios con nombre_producto y cantidad.
    """
    detalles = servicio_consultas.consult_top_productos(limite=limite)
    resultado = []
    for d in detalles:
        resultado.append({
            "nombre_producto": d.nombre_producto,
            "cantidad": d.cantidad_producto,
        })
    return resultado


def top_productos_mes_actual(limite: int | None = None):
    """Obtiene el top de productos vendidos en el mes actual, opcionalmente limitado.

    Retorna una lista de diccionarios con nombre_producto y cantidad.
    """
    detalles = servicio_consultas.consult_top_productos_mes_actual(limite=limite)
    resultado = []
    for d in detalles:
        resultado.append({
            "nombre_producto": d.nombre_producto,
            "cantidad": d.cantidad_producto,
        })
    return resultado


def total_ventas():
    """Obtiene el monto total de ventas históricas (solo ventas)."""
    total = servicio_consultas.consult_total_ventas()
    return {"total_ventas": total}


def total_ventas_dia_actual():
    """Obtiene el monto total de ventas del día actual (solo ventas)."""
    total = servicio_consultas.consult_total_ventas_dia_actual()
    return {"total_ventas_dia": total}


def ultimo_producto():
    """Obtiene el último producto registrado en la base de datos.

    Retorna un diccionario con todos los campos del producto o None si no existe.
    """
    p = servicio_consultas.consult_ultimo_producto()
    if not p:
        return None
    return {
        "id_producto": p.id_producto,
        "nombre_producto": p.nombre_producto,
        "id_categoria": p.id_categoria,
        "id_marca": p.id_marca,
        "presentacion": p.presentacion,
        "unidad_medida": p.unidad_medida,
        "contenido": p.contenido,
        "precio_compra": p.precio_compra,
        "precio_venta": p.precio_venta,
        "stock_minimo": p.stock_minimo,
        "stock_actual": p.stock_actual,
        "estatus": p.estatus,
    }


def productos_ultima_venta():
    """Obtiene los productos vendidos en la última venta registrada.

    Retorna una lista de diccionarios con nombre_producto, nombre_marca,
    cantidad, subtotal e id_transaccion. Si no hay ventas, retorna lista vacía.
    """
    detalles = servicio_consultas.consult_productos_ultima_venta()
    resultado = []
    for d in detalles:
        resultado.append({
            "nombre_producto": d.nombre_producto,
            "nombre_marca": d.nombre_marca,
            "cantidad": d.cantidad_producto,
            "subtotal": d.subtotal,
            "id_transaccion": d.id_transaccion,
        })
    return resultado


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

category_tool = {
    "type": "function",
    "name": "existe_categoria",
    "description": "Verifica si existe una categoría de productos en la base de datos.",
    "parameters": {
        "type": "object",
        "properties": {
            "nombre_categoria": {
                "type": "string",
                "description": "Nombre de la categoría a verificar"
            }
        },
        "required": ["nombre_categoria"]
    },
}

brand_tool = {
    "type": "function",
    "name": "existe_marca",
    "description": "Verifica si existe una marca de producto en la base de datos.",
    "parameters": {
        "type": "object",
        "properties": {
            "nombre_marca": {
                "type": "string",
                "description": "Nombre de la marca a verificar"
            }
        },
        "required": ["nombre_marca"]
    },
}

low_stock_tool = {
    "type": "function",
    "name": "productos_bajo_stock",
    "description": "Devuelve productos cuyo stock actual es menor al stock mínimo.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    },
}


top_products_tool = {
    "type": "function",
    "name": "top_productos",
    "description": "Devuelve el top de productos más vendidos (histórico), con límite opcional.",
    "parameters": {
        "type": "object",
        "properties": {
            "limite": {
                "type": "integer",
                "description": "Cantidad máxima de productos a devolver. Si se omite, no se aplica límite."
            }
        },
        "required": []
    },
}


top_products_mes_actual_tool = {
    "type": "function",
    "name": "top_productos_mes_actual",
    "description": "Devuelve el top de productos más vendidos en el mes actual, con límite opcional.",
    "parameters": {
        "type": "object",
        "properties": {
            "limite": {
                "type": "integer",
                "description": "Cantidad máxima de productos a devolver. Si se omite, no se aplica límite."
            }
        },
        "required": []
    },
}


total_ventas_tool = {
    "type": "function",
    "name": "total_ventas",
    "description": "Devuelve el monto total histórico de ventas (id_tipo = 2).",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    },
}


total_ventas_dia_actual_tool = {
    "type": "function",
    "name": "total_ventas_dia_actual",
    "description": "Devuelve el monto total de ventas del día actual (id_tipo = 2).",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    },
}


ultimo_producto_tool = {
    "type": "function",
    "name": "ultimo_producto",
    "description": "Devuelve el último producto registrado en la base de datos.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    },
}


productos_ultima_venta_tool = {
    "type": "function",
    "name": "productos_ultima_venta",
    "description": "Devuelve los productos vendidos en la última venta registrada.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    },
}


class Agente:
    """Clase que maneja interacciones con el modelo y soporta llamadas a herramientas (tools).

    Uso:
        agent = Agente(client, tools=[product_tool])
        respuesta = agent.send("Hola, mi nombre es Adrian.")
    """

    def __init__(self, client, tools=[product_tool, transactions_tool, category_tool, brand_tool, low_stock_tool, top_products_tool, top_products_mes_actual_tool, total_ventas_tool, total_ventas_dia_actual_tool, ultimo_producto_tool, productos_ultima_venta_tool], model="gemini-2.5-flash-lite"):
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

                elif output.name == "existe_categoria":
                    nombre = output.arguments.get("nombre_categoria")
                    resultado = existe_categoria(nombre)
                    result_json = json.dumps({"existe": resultado}, ensure_ascii=False)

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

                elif output.name == "existe_marca":
                    nombre = output.arguments.get("nombre_marca")
                    resultado = existe_marca(nombre)
                    result_json = json.dumps({"existe": resultado}, ensure_ascii=False)

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
                    
                elif output.name == "productos_bajo_stock":
                    productos = productos_bajo_stock()
                    result_json = json.dumps(productos, ensure_ascii=False)

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

                elif output.name == "top_productos":
                    limite = output.arguments.get("limite")
                    productos = top_productos(limite=limite)
                    result_json = json.dumps(productos, ensure_ascii=False)

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

                elif output.name == "top_productos_mes_actual":
                    limite = output.arguments.get("limite")
                    productos = top_productos_mes_actual(limite=limite)
                    result_json = json.dumps(productos, ensure_ascii=False)

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

                elif output.name == "total_ventas":
                    resultado = total_ventas()
                    result_json = json.dumps(resultado, ensure_ascii=False)

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

                elif output.name == "total_ventas_dia_actual":
                    resultado = total_ventas_dia_actual()
                    result_json = json.dumps(resultado, ensure_ascii=False)

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

                elif output.name == "ultimo_producto":
                    resultado = ultimo_producto()
                    result_json = json.dumps(resultado, ensure_ascii=False)

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

                elif output.name == "productos_ultima_venta":
                    resultado = productos_ultima_venta()
                    result_json = json.dumps(resultado, ensure_ascii=False)

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