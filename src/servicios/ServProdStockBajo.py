import sqlite3
from servicios.ConexionBD import ConexionBD
from modelos.Producto import Producto

class ServProdStockBajo:
    def __init__(self):
        self.db = ConexionBD()

    def obtener_productos_bajo_stock(self):
        conexion = self.db.conectar()
        if not conexion:
            return []

        productos_bajos = []

        try:
            cursor = conexion.cursor()
            query = """
                SELECT id_producto, nombre_producto, stock_actual, stock_minimo
                FROM producto
                WHERE stock_actual < stock_minimo
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            for fila in resultados:
                producto = Producto(
                    id_producto=fila[0],
                    nombre_producto=fila[1],
                    id_categoria=None,
                    id_marca=None,
                    presentacion=None,
                    unidad_medida=None,
                    contenido=None,
                    precio_compra=None,
                    precio_venta=None,
                    stock_minimo=fila[3],
                    stock_actual=fila[2],
                    estatus=None
                )
                productos_bajos.append(producto)

        except Exception as e:
            print(f"Error al consultar productos con bajo stock: {e}")
        finally:
            self.db.desconectar()

        return productos_bajos
