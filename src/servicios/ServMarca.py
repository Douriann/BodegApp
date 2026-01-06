import sqlite3
from servicios.ConexionBD import ConexionBD
from modelos.Marca import Marca

class ServMarca:
    def __init__(self):
        self.db = ConexionBD()
    def crear_marca(self, nombre_marca: str) -> int:
        """Crea una nueva marca en la base de datos y retorna su ID."""
        conexion = self.db.conectar()
        if not conexion:
            return -1  # Indica error de conexión

        try:
            cursor = conexion.cursor()
            query = "INSERT INTO marca (nombre_marca) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM marca WHERE nombre_marca = ?)"
            cursor.execute(query, (nombre_marca, nombre_marca))
            conexion.commit()
            return cursor.lastrowid  # Retorna el ID de la nueva marca
        except sqlite3.Error as e:
            print(f"Error al crear marca: {e}")
            return -1
        finally:
            self.db.desconectar()