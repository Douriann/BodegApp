import requests
from bs4 import BeautifulSoup
import urllib3
import json
import os
from datetime import datetime

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

    def guardar_en_json(self, datos, nombre_archivo="historico_bcv.json"):
        """
        Guarda los datos en un archivo JSON. Si el archivo existe, agrega el registro al final.
        """
        if not datos:
            print("No hay datos para guardar.")
            return

        lista_datos = []

        # 1. Verificamos si el archivo ya existe para leer lo que tiene
        if os.path.exists(nombre_archivo):
            try:
                with open(nombre_archivo, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content: # Si no está vacío
                        lista_datos = json.loads(content)
            except json.JSONDecodeError:
                print("El archivo JSON estaba corrupto, se creará uno nuevo.")

        # 2. Agregamos el nuevo dato a la lista
        lista_datos.append(datos)

        # 3. Escribimos la lista actualizada al archivo
        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                json.dump(lista_datos, f, ensure_ascii=False, indent=4)
            print(f"Datos guardados exitosamente en '{nombre_archivo}'")
        except IOError as e:
            print(f"No se pudo escribir el archivo: {e}")

# --- Bloque de prueba (solo se ejecuta si corres este archivo directamente) ---
if __name__ == "__main__":
    scraper = BcvScraper() # Instanciamos la clase
    datos = scraper.obtener_tasa() # Llamamos al método
    
    if datos:
        print(f"Tasa obtenida: {datos['tasa']} Bs (Fecha: {datos['fecha_vigencia']})")
        scraper.guardar_en_json(datos) # Guardamos