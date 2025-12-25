import sqlite3
from servicios.ConexionBD import ConexionBD
from modelos.Producto import Producto

class ServBusqProduc:
    def __init__(self):
        self.db = ConexionBD()

    def buscar_productos_totales(self):
        """
        Retorna una lista de OBJETOS de tipo Producto con todos los productos en la base de datos.
        """
        conexion = self.db.conectar()
        
        if not conexion:
            return []

        lista_objetos_producto = []

        try:
            cursor = conexion.cursor()
            query = """SELECT P.id_producto, P.nombre_producto, M.nombre_marca, P.precio_compra, P.precio_venta, P.stock_actual
            FROM PRODUCTO P
            JOIN MARCA M ON P.id_marca = M.id_marca"""
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            for fila in resultados:
                producto_obj = Producto(
                    id_producto=fila[0],
                    nombre_producto=fila[1],
                    id_categoria=None,
                    id_marca=fila[2],
                    presentacion=None,
                    unidad_medida=None,
                    contenido=None,
                    precio_compra=fila[3],
                    precio_venta=fila[4],
                    stock_minimo=None,
                    stock_actual=fila[5],
                    estatus=None
                )

                lista_objetos_producto.append(producto_obj)

            return lista_objetos_producto

        except sqlite3.Error as e:
            print(f"Error: {e}")
            return []
        finally:
            self.db.desconectar()

    def buscar_productos_por_nombre(self, nombre_producto):
        """
        Retorna una lista de OBJETOS de tipo Producto que coinciden con el nombre dado.
        """
        conexion = self.db.conectar()
        
        if not conexion:
            return []

        lista_objetos_producto = []

        try:
            cursor = conexion.cursor()
            query = """SELECT P.id_producto, P.nombre_producto, M.nombre_marca, P.precio_compra, P.precio_venta, P.stock_actual
            FROM PRODUCTO P
            JOIN MARCA M ON P.id_marca = M.id_marca
            WHERE P.nombre_producto LIKE ?"""
            cursor.execute(query, ('%' + nombre_producto + '%',))
            resultados = cursor.fetchall()
            
            for fila in resultados:
                producto_obj = Producto(
                    id_producto=fila[0],
                    nombre_producto=fila[1],
                    id_categoria=None,
                    id_marca=fila[2],
                    presentacion=None,
                    unidad_medida=None,
                    contenido=None,
                    precio_compra=fila[3],
                    precio_venta=fila[4],
                    stock_minimo=None,
                    stock_actual=fila[5],
                    estatus=None
                )

                lista_objetos_producto.append(producto_obj)

            return lista_objetos_producto

        except sqlite3.Error as e:
            print(f"Error: {e}")
            return []
        finally:
            self.db.desconectar()
