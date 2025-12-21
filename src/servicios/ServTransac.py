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
                transaccion = Transaccion(fila[0], fila[1], fila[2], fila[3], fila[4])
                lista_objetos_transaccion.append(transaccion)
        except sqlite3.Error as e:
            print(f"Error al consultar transacciones: {e}")
        finally:
            conexion.close()

        return lista_objetos_transaccion