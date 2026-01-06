import sqlite3
from servicios.ConexionBD import ConexionBD
from modelos.Categoria import Categoria

class ServCategoria:
    def __init__(self):
        self.db = ConexionBD()

    def crear_categoria(self, descripcion_categoria: str) -> int:
        """Crea una nueva categoria en la base de datos y retorna su ID."""
        conexion = self.db.conectar()
        if not conexion:
            return -1  # Indica error de conexión

        try:
            cursor = conexion.cursor()
            query = "INSERT INTO categoria (descripcion_categoria) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM categoria WHERE descripcion_categoria = ?)"
            cursor.execute(query, (descripcion_categoria, descripcion_categoria))
            conexion.commit()
            return cursor.lastrowid  # Retorna el ID de la nueva categoria
        except sqlite3.Error as e:
            print(f"Error al crear categoria: {e}")
            return -1
        finally:
            self.db.desconectar()

#creando prueba
"""if __name__ == "__main__":
    servicio_categoria = ServCategoria()
    nueva_categoria_id = servicio_categoria.crear_categoria("Categoria de Prueba")
    if nueva_categoria_id != -1:
        print(f"Categoria creada con ID: {nueva_categoria_id}")
    else:
        print("Error al crear la categoria.")"""