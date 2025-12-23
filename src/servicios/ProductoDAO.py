import sqlite3
from servicios.ConexionBD import ConexionBD
# Asegúrate de importar tu nueva clase Producto. 
# Si están en la misma carpeta: from Producto import Producto
from modelos.Producto import Producto

class ProductoDAO:
    def __init__(self):
        self.db = ConexionBD()

    def consultar_todos(self):
        """
        Retorna una lista de OBJETOS de tipo Producto.
        """
        conexion = self.db.conectar()
        
        if not conexion:
            return []

        lista_objetos_producto = []

        try:
            cursor = conexion.cursor()
            query = "SELECT * FROM PRODUCTO"
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            for fila in resultados:
                # fila es: (1, 'Coca Cola', 2, 5, ...)
                
                # Creamos el objeto Producto pasándole los datos de la fila en orden
                producto_obj = Producto(
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
                    estatus=fila[11]
                )

                # Agregamos el OBJETO a la lista
                lista_objetos_producto.append(producto_obj)

            return lista_objetos_producto

        except sqlite3.Error as e:
            print(f"Error: {e}")
            return []
        finally:
            self.db.desconectar()

    # Función para modificar un producto existente
    def modificar_producto(self, producto):
        conexion = self.db.conectar()
        if not conexion:
            return False

        try:
            cursor = conexion.cursor()
            query = """
                UPDATE PRODUCTO
                SET nombre_producto = ?, id_categoria = ?, id_marca = ?, presentacion = ?, 
                    unidad_medida = ?, contenido = ?, precio_compra = ?, precio_venta = ?, 
                    stock_minimo = ?, stock_actual = ?, estatus = ?
                WHERE id_producto = ?
            """
            cursor.execute(query, (
                producto.nombre_producto,
                producto.id_categoria,
                producto.id_marca,
                producto.presentacion,
                producto.unidad_medida,
                producto.contenido,
                producto.precio_compra,
                producto.precio_venta,
                producto.stock_minimo,
                producto.stock_actual,
                producto.estatus,
                producto.id_producto
            ))
            conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al modificar producto: {e}")
            return False
        finally:
            self.db.desconectar()







# --- EJEMPLO DE CÓMO USARLO AHORA ---
if __name__ == "__main__":
    dao = ProductoDAO()
    mis_productos = dao.consultar_todos()

    print(f"Se recuperaron {len(mis_productos)} productos.\n")

    for prod in mis_productos:
        # ¡Mira qué limpio es acceder a los datos ahora!
        # Ya no usas prod[1], usas prod.nombre_producto
        if prod.stock_actual < 5:
            print(f"ALERTA STOCK BAJO: {prod.nombre_producto}")
        else:
            print(prod) # Esto usa el método __str__ que creamos
            
    
    
    