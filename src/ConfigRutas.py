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

    def obtener_ruta_json(self, nombre_json: str, must_exist: bool = False) -> Path:
        """Devuelve la Path de un JSON en `base_de_datos`. Añade .json si hace falta.
        Si `must_exist` es True y el archivo no existe, lanza FileNotFoundError."""
        ruta = self.DIR_DB / nombre_json
        if not ruta.suffix:
            ruta = ruta.with_suffix(".json")
        if must_exist and not ruta.is_file():
            raise FileNotFoundError(f"No existe el archivo JSON: {ruta}")
        return ruta

    def existe_ruta_json(self, nombre_json: str) -> bool:
        """Devuelve True si el JSON existe en `base_de_datos`."""
        ruta = self.DIR_DB / nombre_json
        if not ruta.suffix:
            ruta = ruta.with_suffix(".json")
        return ruta.is_file()

# Instanciamos la clase para que otros archivos la usen directamente
rutas = ConfigRutas()