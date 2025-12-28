from servicios.ConexionBD import ConexionBD
from servicios.BCVdatos import BcvScraper 

class ServDashboard:
    def __init__(self):
        self.db = ConexionBD()
        self.scraper = BcvScraper()

    def obtener_precio_dolar(self):
        """Usa el BcvScraper para obtener la tasa oficial del día"""
        try:
            scraper = BcvScraper()
            datos = scraper.obtener_tasa()
            
            # Si el scraper devuelve un diccionario, extraemos el valor de 'USD'
            if datos and isinstance(datos, dict):
                tasa = datos.get('tasa', 0.0)
                return float(tasa)
            
            return 0.0
            
        except Exception as e:
            print(f"Error al conectar con el scraper del BCV: {e}")
            return 0.0

    def obtener_top_vendidos(self):
        """Consulta los 3 productos para el gráfico de barras"""
        conexion = self.db.conectar()
        if conexion:
            cursor = conexion.cursor()
            query = """
                 SELECT p.nombre_producto, SUM(dt.cantidad_producto) as total 
                 FROM detalle_transaccion dt
                 JOIN producto p ON dt.id_producto = p.id_producto
                 GROUP BY p.nombre_producto
                 ORDER BY total DESC
                 LIMIT 3
              """
            cursor.execute(query)
            resultados = cursor.fetchall() # Esto traerá los nombres y cantidades
            self.db.desconectar()
            return resultados
        return []
    
    def obtener_resumen_financiero(self):
        """Consulta totales de ventas e ingresos del mes"""
        conexion = self.db.conectar()
        if conexion:
            cursor = conexion.cursor()
            # Contamos transacciones y sumamos el campo TOTAL
            query = "SELECT COUNT(*), SUM(TOTAL) FROM TRANSACCION"
            cursor.execute(query)
            res = cursor.fetchone()
            self.db.desconectar()
            return res if res[0] else (0, 0.0)
        return (0, 0.0)