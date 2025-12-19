import sqlite3
from ConfigRutas import rutas


class ConexionBD:
    def __init__(self, nombre_bd=rutas.ruta_base_datos):
        self.nombre_bd = nombre_bd
        self.conexion = None

    def conectar(self):
        """Abre la conexión a la base de datos."""
        try:
            # Esto crea el archivo si no existe
            self.conexion = sqlite3.connect(self.nombre_bd)
            return self.conexion
        except sqlite3.Error as e:
            print(f"Error al conectar: {e}")

    def desconectar(self):
        """Cierra la conexión si está abierta."""
        if self.conexion:
            self.conexion.close()