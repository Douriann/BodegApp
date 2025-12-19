from pathlib import Path

class ConfigRutas:
    # 1. Definimos la raíz del proyecto (subiendo un nivel desde 'codigo_fuente')
    _BASE_DIR = Path(__file__).resolve().parent.parent

    # 2. Definimos las carpetas principales
    DIR_DB = _BASE_DIR / "base_de_datos"
    DIR_RECURSOS = _BASE_DIR / "recursos"
    
    # 3. Definimos rutas a archivos específicos (Propiedades para fácil acceso)
    
    @property
    def ruta_base_datos(self):
        return self.DIR_DB / "bodega.db"

    def obtener_ruta_imagen(self, nombre_imagen):
        """Devuelve la ruta completa de una imagen dada su nombre."""
        return self.DIR_RECURSOS / nombre_imagen

# Instanciamos la clase para que otros archivos la usen directamente
rutas = ConfigRutas()