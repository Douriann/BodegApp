import sqlite3
from servicios.ConexionBD import ConexionBD
from modelos.DetalleProductosTransac import DetalleProductosTransac

class ServProdTransac:
    def __init__(self):
        self.db = ConexionBD()

    def consultar_detalles_por_transaccion(self, id_transaccion):
        """
        Retorna una lista de objetos DetalleProductosTransac para una transacción dada.
        """
        conexion = self.db.conectar()
        
        if not conexion:
            return []

        lista_detalles = []

        try:
            cursor = conexion.cursor()
            query = """
                SELECT P.nombre_producto,  M.nombre_marca, DT.cantidad_producto,
                DT.subtotal, DT.id_transaccion

                FROM detalle_transaccion DT
                JOIN producto P ON  DT.id_producto = P.id_producto
                JOIN marca M ON P.id_marca = M.id_marca

                WHERE DT.id_transaccion = ?
                            """
            cursor.execute(query, (id_transaccion,))
            resultados = cursor.fetchall()
            
            for fila in resultados:
                # fila es: (nombre_producto, nombre_marca, cantidad_producto, subtotal, id_transaccion)
                detalle = DetalleProductosTransac(fila[0], fila[1], fila[2], fila[3], fila[4])
                lista_detalles.append(detalle)
        except sqlite3.Error as e:
            print(f"Error al consultar detalles de transacción: {e}")
        finally:
            conexion.close()
        return lista_detalles