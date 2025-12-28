from servicios.ConexionBD import ConexionBD
from servicios.BCVdatos import BcvScraper 

class ServDashboard:
    def __init__(self):
        self.db = ConexionBD()
        self.scraper = BcvScraper()

    def obtener_precio_dolar(self):
        """Llama a la herramienta del grupo con el nombre correcto"""
        try:
            datos = self.scraper.obtener_tasa() 
            if datos:
                return datos.get('USD', 'N/A') # Extraemos solo el valor del dólar
            return "N/A"
        except:
            return "Error BCV"

    def obtener_top_vendidos(self):
        """Consulta los 3 productos para tu gráfico de barras"""
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