import sqlite3
from servicios.ConexionBD import ConexionBD
from modelos.Transaccion import Transaccion

class ServTransac:
    def __init__(self):
        self.db = ConexionBD()

    def consultar_transacciones(self):
        """
        Retorna una lista de objetos Transaccion.
        """
        conexion = self.db.conectar()
        
        if not conexion:
            return []

        lista_objetos_transaccion = []

        try:
            cursor = conexion.cursor()
            query = "SELECT * FROM TRANSACCION"
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            for fila in resultados:
                # fila es: (1, '2023-10-01', 150.0, ...)
                
                # Creamos el objeto Transaccion pasándole los datos de la fila en orden
                transaccion = Transaccion(fila[0], fila[1], fila[2], fila[3], fila[4], fila[5])
                lista_objetos_transaccion.append(transaccion)
        except sqlite3.Error as e:
            print(f"Error al consultar transacciones: {e}")
        finally:
            conexion.close()

        return lista_objetos_transaccion

    def prueba_agregar_transaccion(self,listado_transacciones):
        transacciones = listado_transacciones
        print(transacciones)
    def agregar_transaccion(self, transaccion, detalles):
        """
        Agrega una nueva transacción y sus detalles a la base de datos.
        
        Parámetros:
        - transaccion: Objeto Transaccion a agregar.
        - detalles: Lista de objetos DetalleTransaccion asociados.
        
        Retorna:
        - True si la operación fue exitosa, False en caso contrario.
        """
        conexion = self.db.conectar()
        
        if not conexion:
            return False

        try:
            cursor = conexion.cursor()
            cursor.execute("BEGIN TRANSACTION;")
            query_transaccion = """
                INSERT INTO TRANSACCION (fecha_transaccion, id_tipo, total, observaciones, estatus)
                VALUES (?, ?, ?, ?, ?);
            """
            cursor.execute(query_transaccion, (transaccion.fecha_transaccion, transaccion.id_tipo,
                                              transaccion.total,
                                              transaccion.observaciones,
                                              transaccion.estatus))
            id_transaccion = cursor.lastrowid
            query_detalle = """
                INSERT INTO DETALLE_TRANSACCION (id_transaccion, id_producto, cantidad_producto, subtotal, estatus)
                VALUES (?, ?, ?, ?, ?);
            """
            for det in detalles:
                cursor.execute(query_detalle, (id_transaccion, det.id_producto, det.cantidad_producto, det.subtotal, det.estatus))
                if transaccion.id_tipo == 1:
                    
                    actualizar_stock = """
                        UPDATE PRODUCTO
                        SET stock_actual = stock_actual + ?
                        WHERE id_producto = ?;
                    """
                    cursor.execute(actualizar_stock, (det.cantidad_producto, det.id_producto))
                elif transaccion.id_tipo == 2:
                    actualizar_stock = """
                        UPDATE PRODUCTO
                        SET stock_actual = stock_actual - ?
                        WHERE id_producto = ?;                    
                        """
                    cursor.execute(actualizar_stock, (det.cantidad_producto, det.id_producto))
            cursor.execute("COMMIT;")
        except sqlite3.Error as e:
            print(f"Error al agregar transacción: {e}")
            cursor.execute("ROLLBACK;")
        finally:
            conexion.close()

        return True