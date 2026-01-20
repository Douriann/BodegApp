import sqlite3
from servicios.ConexionBD import ConexionBD
from modelos.DetalleProductosTransac import DetalleProductosTransac
from modelos.Producto import Producto


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

	def consult_productos_ultima_venta(self):
		"""Retorna los productos vendidos en la última venta (id_tipo = 2).

		Devuelve una lista de objetos DetalleProductosTransac. Si no hay ventas,
		retorna una lista vacía.
		"""
		conexion = self.db.conectar()

		if not conexion:
			return []

		lista_detalles = []

		try:
			cursor = conexion.cursor()

			# 1) Obtener el id de la última transacción de tipo VENTA (id_tipo = 2)
			query_ultima_venta = """
				SELECT id_transaccion
				FROM transaccion
				WHERE id_tipo = 2 AND estatus = 1
				ORDER BY id_transaccion DESC
				LIMIT 1
			"""
			cursor.execute(query_ultima_venta)
			fila = cursor.fetchone()
			if not fila:
				return []

			id_ultima_venta = fila[0]

			# 2) Obtener los productos vendidos en esa transacción
			query_detalles = """
				SELECT P.nombre_producto, M.nombre_marca, DT.cantidad_producto,
				       DT.subtotal, DT.id_transaccion
				FROM detalle_transaccion DT
				JOIN producto P ON DT.id_producto = P.id_producto
				JOIN marca M ON P.id_marca = M.id_marca
				WHERE DT.id_transaccion = ?
			"""
			cursor.execute(query_detalles, (id_ultima_venta,))
			resultados = cursor.fetchall()

			for fila in resultados:
				# (nombre_producto, nombre_marca, cantidad_producto, subtotal, id_transaccion)
				detalle = DetalleProductosTransac(
					nombre_producto=fila[0],
					nombre_marca=fila[1],
					cantidad_producto=fila[2],
					subtotal=fila[3],
					id_transaccion=fila[4],
				)
				lista_detalles.append(detalle)

			return lista_detalles

		except sqlite3.Error as e:
			print(f"Error al consultar productos de la última venta: {e}")
			return []
		finally:
			self.db.desconectar()

	def consult_ultimo_producto(self):
		"""Retorna el último producto registrado (por id_producto DESC) como objeto Producto.

		Si no hay productos, retorna None.
		"""
		conexion = self.db.conectar()

		if not conexion:
			return None

		try:
			cursor = conexion.cursor()
			query = """
				SELECT id_producto, nombre_producto, id_categoria, id_marca,
				       presentacion, unidad_medida, contenido, precio_compra,
				       precio_venta, stock_minimo, stock_actual, estatus
				FROM producto P
				ORDER BY P.id_producto DESC
				LIMIT 1
			"""
			cursor.execute(query)
			fila = cursor.fetchone()
			if not fila:
				return None

			producto = Producto(
				id_producto=fila[0],
				nombre_producto=fila[1],
				id_categoria=fila[2],
				id_marca=fila[3],
				presentacion=fila[4],
				unidad_medida=fila[5],
				contenido=fila[6],
				precio_compra=fila[7],
				precio_venta=fila[8],
				stock_minimo=fila[9],
				stock_actual=fila[10],
				estatus=fila[11],
			)
			return producto

		except sqlite3.Error as e:
			print(f"Error al consultar el último producto: {e}")
			return None
		finally:
			self.db.desconectar()

