import sqlite3
from servicios.ConexionBD import ConexionBD
from modelos.DetalleProductosTransac import DetalleProductosTransac


class ServConsultSophia:
	def __init__(self):
		self.db = ConexionBD()

	def consult_top_productos(self, limite=None):
		"""Retorna una lista de objetos DetalleProductosTransac con el top de productos vendidos.

		Parámetros
		----------
		limite: int | None
			Cantidad máxima de productos a retornar. Si es None, no se aplica límite.

		Se utiliza nombre_producto y cantidad_producto (contador). Los demás atributos
		de DetalleProductosTransac se dejan en None.
		"""
		conexion = self.db.conectar()

		if not conexion:
			return []

		lista_top_productos = []

		try:
			cursor = conexion.cursor()
			query = """
				SELECT P.nombre_producto, COUNT(DT.id_producto) AS contador
				FROM producto P
				INNER JOIN detalle_transaccion DT ON P.id_producto = DT.id_producto
				GROUP BY P.nombre_producto
				ORDER BY contador DESC
			"""
			params = []
			if limite is not None:
				query += " LIMIT ?"
				params.append(limite)

			cursor.execute(query, params)
			resultados = cursor.fetchall()

			for fila in resultados:
				# fila: (nombre_producto, contador)
				detalle = DetalleProductosTransac(
					nombre_producto=fila[0],
					nombre_marca=None,
					cantidad_producto=fila[1],
					subtotal=None,
					id_transaccion=None,
				)
				lista_top_productos.append(detalle)

			return lista_top_productos

		except sqlite3.Error as e:
			print(f"Error al consultar top de productos: {e}")
			return []
		finally:
			self.db.desconectar()

	def consult_top_productos_mes_actual(self, limite=None):
		"""Retorna el top de productos vendidos en el mes actual.

		Parámetros
		----------
		limite: int | None
			Cantidad máxima de productos a retornar. Si es None, no se aplica límite.

		Filtra las transacciones para el mes y año actuales usando la fecha
		registrada en la tabla TRANSACCION.
		"""
		conexion = self.db.conectar()

		if not conexion:
			return []

		lista_top_productos = []

		try:
			cursor = conexion.cursor()
			query = """
				SELECT P.nombre_producto, COUNT(DT.id_producto) AS contador
				FROM producto P
				INNER JOIN detalle_transaccion DT ON P.id_producto = DT.id_producto
				INNER JOIN transaccion T ON DT.id_transaccion = T.id_transaccion
				WHERE strftime('%Y-%m', T.fecha_transaccion) = strftime('%Y-%m', 'now')
				GROUP BY P.nombre_producto
				ORDER BY contador DESC
			"""
			params = []
			if limite is not None:
				query += " LIMIT ?"
				params.append(limite)

			cursor.execute(query, params)
			resultados = cursor.fetchall()

			for fila in resultados:
				# fila: (nombre_producto, contador)
				detalle = DetalleProductosTransac(
					nombre_producto=fila[0],
					nombre_marca=None,
					cantidad_producto=fila[1],
					subtotal=None,
					id_transaccion=None,
				)
				lista_top_productos.append(detalle)

			return lista_top_productos

		except sqlite3.Error as e:
			print(f"Error al consultar top de productos del mes actual: {e}")
			return []
		finally:
			self.db.desconectar()

	def consult_total_ventas(self):
		"""Retorna el monto total de ventas históricas (id_tipo = 2)."""
		conexion = self.db.conectar()

		if not conexion:
			return 0.0

		try:
			cursor = conexion.cursor()
			query = """
				SELECT COALESCE(SUM(total), 0)
				FROM transaccion
				WHERE id_tipo = 2
			"""
			cursor.execute(query)
			resultado = cursor.fetchone()
			return float(resultado[0]) if resultado and resultado[0] is not None else 0.0

		except sqlite3.Error as e:
			print(f"Error al consultar total de ventas: {e}")
			return 0.0
		finally:
			self.db.desconectar()

	def consult_total_ventas_dia_actual(self):
		"""Retorna el monto total de ventas del día actual (id_tipo = 2)."""
		conexion = self.db.conectar()

		if not conexion:
			return 0.0

		try:
			cursor = conexion.cursor()
			query = """
				SELECT COALESCE(SUM(total), 0)
				FROM transaccion
				WHERE id_tipo = 2
				  AND DATE(fecha_transaccion) = DATE('now')
			"""
			cursor.execute(query)
			resultado = cursor.fetchone()
			return float(resultado[0]) if resultado and resultado[0] is not None else 0.0

		except sqlite3.Error as e:
			print(f"Error al consultar total de ventas del día actual: {e}")
			return 0.0
		finally:
			self.db.desconectar()

