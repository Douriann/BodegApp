import requests
from bs4 import BeautifulSoup
import urllib3
import json
import re
from datetime import datetime
from pathlib import Path

# Intento de importar `rutas` desde `ConfigRutas` (soporta ejecución como paquete o script)
try:
    from ConfigRutas import rutas
except Exception:
    try:
        from ..ConfigRutas import rutas
    except Exception:
        rutas = None

# Desactivamos advertencias SSL globalmente para esta clase
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BcvScraper:
    def __init__(self):
        """Constructor: Configura la URL y los headers base."""
        self.url = "https://www.bcv.org.ve"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def obtener_tasa(self):
        """
        Realiza el scraping a la página del BCV.
        Retorna: Un diccionario con los datos o None si falla.
        """
        try:
            # Petición con verify=False para saltar el error de certificado del BCV
            response = requests.get(self.url, headers=self.headers, verify=False, timeout=15)
            
            if response.status_code != 200:
                print(f"Error HTTP: {response.status_code}")
                return None

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # --- Extracción del Dólar ---
            dolar_div = soup.find('div', {'id': 'dolar'})
            if not dolar_div:
                return None

            tasa_texto = dolar_div.find('strong').text.strip()
            tasa_float = float(tasa_texto.replace(',', '.'))

            # --- Extracción de la Fecha del BCV ---
            fecha_seccion = soup.find('div', {'class': 'pull-right dinpro center'})
            fecha_valor = fecha_seccion.find('span').text.strip() if fecha_seccion else "Desconocida"

            # Retornamos el diccionario limpio
            return {
                'moneda': 'USD',
                'tasa': tasa_float,
                'fecha_vigencia': fecha_valor,
                'fecha_scraping': datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Agregamos cuándo hicimos la consulta
            }

        except Exception as e:
            print(f"Ocurrió un error en el scraping: {e}")
            return None

    def _ruta_archivo(self, nombre_archivo):
        """Devuelve un Path al archivo en `base_de_datos` si `rutas` está disponible, o Path local."""
        if rutas:
            try:
                return rutas.obtener_ruta_json(nombre_archivo)
            except Exception:
                return Path(nombre_archivo)
        return Path(nombre_archivo)

    def guardar_en_json(self, datos, nombre_archivo="historico_bcv.json"):
        """
        Guarda los datos en un archivo JSON. Si el archivo existe, agrega el registro al final.
        (Comportamiento conservado para compatibilidad; usar `guardar_json_reemplazando` para reemplazar)
        """
        if not datos:
            print("No hay datos para guardar.")
            return False

        ruta = self._ruta_archivo(nombre_archivo)
        lista_datos = []

        # 1. Verificamos si el archivo ya existe para leer lo que tiene
        if ruta.is_file():
            try:
                with ruta.open('r', encoding='utf-8') as f:
                    content = f.read()
                    if content: # Si no está vacío
                        lista_datos = json.loads(content)
            except json.JSONDecodeError:
                print("El archivo JSON estaba corrupto, se creará uno nuevo.")
            except Exception as e:
                print(f"Error leyendo el archivo existente: {e}")

        # 2. Agregamos el nuevo dato a la lista
        lista_datos.append(datos)

        # 3. Escribimos la lista actualizada al archivo
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with ruta.open('w', encoding='utf-8') as f:
                json.dump(lista_datos, f, ensure_ascii=False, indent=4)
            #print(f"Datos guardados exitosamente en '{ruta}'")
            return True
        except IOError as e:
            print(f"No se pudo escribir el archivo: {e}")
            return False

    def guardar_json_reemplazando(self, datos, nombre_archivo="historico_bcv.json"):
        """Escribe/reescribe el JSON con 'datos' (no acumula)."""
        if not datos:
            print("No hay datos para guardar.")
            return False
        try:
            ruta = self._ruta_archivo(nombre_archivo)
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with ruta.open('w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
            print(f"Datos guardados exitosamente en '{ruta}' (reemplazados)")
            return True
        except Exception as e:
            print(f"No se pudo guardar JSON: {e}")
            return False

    def leer_json_local(self, nombre_archivo="historico_bcv.json"):
        """Intenta leer el JSON local; devuelve dict o None."""
        try:
            ruta = self._ruta_archivo(nombre_archivo)
            if not ruta.is_file():
                return None
            with ruta.open('r', encoding='utf-8') as f:
                content = f.read()
                if not content:
                    return None
                return json.loads(content)
        except Exception as e:
            print(f"Error leyendo archivo local JSON: {e}")
            return None

    def _vigencia_es_hoy(self, datos: dict) -> bool:
        """Devuelve True si la 'fecha_vigencia' o la 'fecha_scraping' del dict es la fecha de hoy."""
        if not isinstance(datos, dict):
            return False
        hoy = datetime.now().date()

        fv = datos.get("fecha_vigencia")
        if fv:
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y"):
                try:
                    if datetime.strptime(fv, fmt).date() == hoy:
                        return True
                except Exception:
                    pass
            try:
                nums = re.findall(r"\d+", fv)
                if len(nums) >= 2:
                    day = int(nums[0]); month = int(nums[1])
                    year = int(nums[2]) if len(nums) >= 3 else hoy.year
                    if year < 100:
                        year += 2000
                    if datetime(year, month, day).date() == hoy:
                        return True
            except Exception:
                pass

        fs = datos.get("fecha_scraping")
        if fs:
            try:
                if datetime.strptime(fs, "%Y-%m-%d %H:%M:%S").date() == hoy:
                    return True
            except Exception:
                pass

        return False

    def obtener_tasa_con_respaldo(self, nombre_archivo="historico_bcv.json"):
        """Primero intenta usar el respaldo local si su fecha de vigencia es hoy; si no, hace scraping (y guarda reemplazando)."""
        # 0) Intento rápido: leer local y si su vigencia es hoy, devolverlo sin hacer scraping
        respaldo = self.leer_json_local(nombre_archivo)
        ultimo = None
        if respaldo:
            if isinstance(respaldo, list) and respaldo:
                ultimo = respaldo[-1]
            elif isinstance(respaldo, dict):
                ultimo = respaldo
            if ultimo and self._vigencia_es_hoy(ultimo):
                return ultimo

        # 1) Si no hay respaldo válido de hoy, intentar scraping
        datos = self.obtener_tasa()
        if datos:
            ok = self.guardar_json_reemplazando(datos, nombre_archivo)
            if ok:
                return datos
        # 2) Si scraping falla o no pudo guardarse, devolver último respaldo si existe
        if ultimo:
            return ultimo
        if respaldo:
            if isinstance(respaldo, list) and respaldo:
                return respaldo[-1]
            return respaldo
        return 0

# --- Bloque de prueba (solo se ejecuta si corres este archivo directamente) ---
if __name__ == "__main__":
    scraper = BcvScraper() # Instanciamos la clase
    resultado = scraper.obtener_tasa_con_respaldo()
    
    if resultado and resultado != 0:
        tasa = resultado.get('tasa') if isinstance(resultado, dict) else resultado
        fecha = resultado.get('fecha_vigencia') if isinstance(resultado, dict) else None
        print(f"Tasa resultante: {tasa} Bs (Fecha: {fecha})")
    else:
        print("No fue posible obtener la tasa ni un respaldo local. Retornando 0.")