import sqlite3
from ConexionBD import ConexionBD

class InicializadorDB:
    def __init__(self):
        # Instanciamos tu clase de conexión
        self.db = ConexionBD()

    def _ejecutar_script(self, script_sql):
        """Método auxiliar para ejecutar scripts SQL crudos."""
        conn = self.db.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                # Activamos llaves foráneas para asegurar integridad referencial
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.executescript(script_sql)
                conn.commit()
                print("--- Estructura de base de datos verificada/creada con éxito ---")
            except sqlite3.Error as e:
                print(f"Error al crear la estructura: {e}")
                conn.rollback()
            finally:
                self.db.desconectar()

    def _ejecutar_insert_muchos(self, sql, datos):
        """Método auxiliar para insertar múltiples registros."""
        conn = self.db.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.executemany(sql, datos)
                conn.commit()
            except sqlite3.Error as e:
                # Si el error es de restricción única (ya existen), lo ignoramos para no duplicar
                if "UNIQUE constraint failed" not in str(e):
                    print(f"Error insertando datos: {e}")
            finally:
                self.db.desconectar()

    def crear_tablas(self):
        """Crea las tablas con las restricciones solicitadas si no existen."""
        
        sql_creation = """
        -- 1. Tabla Categoría
        CREATE TABLE IF NOT EXISTS categoria (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion_categoria TEXT NOT NULL
        );

        -- 2. Tabla Marca
        CREATE TABLE IF NOT EXISTS marca (
            id_marca INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_marca TEXT NOT NULL
        );

        -- 3. Tabla Tipo Transacción
        CREATE TABLE IF NOT EXISTS tipo_transaccion (
            id_tipo INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion_tipo TEXT NOT NULL
        );

        -- 4. Tabla Productos
        CREATE TABLE IF NOT EXISTS producto (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_producto TEXT(20) NOT NULL,
            id_categoria INTEGER NOT NULL,
            id_marca INTEGER NOT NULL,
            presentacion TEXT(20) NOT NULL,
            unidad_medida TEXT(20) NOT NULL,
            contenido REAL NOT NULL, 
            precio_compra REAL NOT NULL,
            precio_venta REAL NOT NULL,
            stock_minimo INTEGER NOT NULL,
            stock_actual INTEGER NOT NULL,
            estatus INTEGER NOT NULL,
            
            FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria),
            FOREIGN KEY (id_marca) REFERENCES marca(id_marca),
            CHECK (stock_actual >= 0),
            CHECK (stock_minimo >= 0),
            CHECK (precio_compra >= 0),
            CHECK (precio_venta >= 0)
        );

        -- 5. Tabla Transacción
        CREATE TABLE IF NOT EXISTS transaccion (
            id_transaccion INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_transaccion DATE NOT NULL,
            id_tipo INTEGER NOT NULL,
            total REAL NOT NULL,
            observaciones TEXT(30) NOT NULL,
            estatus INTEGER NOT NULL,
            
            FOREIGN KEY (id_tipo) REFERENCES tipo_transaccion(id_tipo)
        );

        -- 6. Tabla Detalle Transacción
        CREATE TABLE IF NOT EXISTS detalle_transaccion (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_transaccion INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            cantidad_producto INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            estatus INTEGER NOT NULL,
            
            FOREIGN KEY (id_transaccion) REFERENCES transaccion(id_transaccion),
            FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
        );
        """
        self._ejecutar_script(sql_creation)

    def insertar_datos_semilla(self):
            """Puebla la base de datos con información inicial y ventas históricas."""
            
            # --- 1. DATOS MAESTROS ---
            
            # Categorías
            data_cat = [('Alimentos',), ('Bebidas',), ('Limpieza',), ('Charcutería',)]
            self._ejecutar_insert_muchos(
                "INSERT INTO categoria (descripcion_categoria) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM categoria WHERE descripcion_categoria = ?)",
                [(x[0], x[0]) for x in data_cat]
            )

            # Marcas
            data_marca = [('Polar',), ('P.A.N.',), ('Mavesa',), ('Coca-Cola',), ('Mary',), ('Las Llaves',)]
            self._ejecutar_insert_muchos(
                "INSERT INTO marca (nombre_marca) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM marca WHERE nombre_marca = ?)",
                [(x[0], x[0]) for x in data_marca]
            )

            # Tipos de Transacción (1=Compra, 2=Venta)
            data_tipo = [('Compra',), ('Venta',)]
            self._ejecutar_insert_muchos(
                "INSERT INTO tipo_transaccion (descripcion_tipo) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM tipo_transaccion WHERE descripcion_tipo = ?)",
                [(x[0], x[0]) for x in data_tipo]
            )

            # Productos
            # Nota: Los IDs se generarán en este orden:
            # 1:Harina, 2:Arroz, 3:Margarina, 4:Refresco, 5:Jabón, 6:Cerveza
            productos = [
                ('Harina de Maíz', 1, 2, 'paquete', 'kilogramos', 1.0, 0.90, 1.20, 100, 50, 1),
                ('Arroz Blanco', 1, 5, 'paquete', 'kilogramos', 1.0, 0.85, 1.10, 80, 40, 1),
                ('Margarina', 1, 3, 'paquete', 'kilogramos', 0.5, 1.50, 2.00, 40, 20, 1),
                ('Refresco Cola', 2, 4, 'botella', 'litros', 2.0, 1.80, 2.50, 60, 30, 1),
                ('Jabón en Polvo', 3, 6, 'paquete', 'kilogramos', 1.0, 2.50, 3.20, 30, 15, 1),
                ('Cerveza Pilsen', 2, 1, 'caja', 'unidades', 36.0, 20.00, 25.00, 10, 5, 1) 
            ]

            sql_prod = """
            INSERT INTO producto (
                nombre_producto, id_categoria, id_marca, presentacion, unidad_medida, 
                contenido, precio_compra, precio_venta, stock_minimo, stock_actual, estatus
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Verificamos si hay productos antes de insertar para no duplicar
            conn = self.db.conectar()
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM producto")
            conteo_prod = c.fetchone()[0]
            
            if conteo_prod == 0:
                print("--- Insertando productos semilla ---")
                self._ejecutar_insert_muchos(sql_prod, productos)
                
                # --- 2. TRANSACCIONES (VENTAS) ---
                # Solo insertamos ventas si acabamos de crear los productos (para mantener coherencia de IDs)
                print("--- Insertando histórico de ventas ---")

                # Venta 1: Cliente compró Harina y Margarina
                # Fecha: Ayer. Tipo: 2 (Venta). Total: (2 * 1.20) + (1 * 2.00) = 4.40
                venta_1 = ('2024-03-20', 2, 4.40, 'Cliente frecuente mañana', 1)
                
                # Venta 2: Cliente compró Caja de Cerveza y Refrescos
                # Fecha: Hoy. Tipo: 2 (Venta). Total: (1 * 25.00) + (2 * 2.50) = 30.00
                venta_2 = ('2024-03-21', 2, 30.00, 'Fiesta fin de semana', 1)

                sql_trans = "INSERT INTO transaccion (fecha_transaccion, id_tipo, total, observaciones, estatus) VALUES (?, ?, ?, ?, ?)"
                self._ejecutar_insert_muchos(sql_trans, [venta_1, venta_2])

                # --- 3. DETALLE TRANSACCIONES ---
                # Asumimos que Venta 1 tiene ID=1 y Venta 2 tiene ID=2 (por ser autoincrementales recién creados)
                
                detalles = [
                    # Detalles para la Transacción 1
                    # (id_transaccion, id_producto, cantidad, subtotal, estatus)
                    (1, 1, 2, 2.40, 1), # 2 Harinas (ID 1)
                    (1, 3, 1, 2.00, 1), # 1 Margarina (ID 3)

                    # Detalles para la Transacción 2
                    (2, 6, 1, 25.00, 1), # 1 Caja Cerveza (ID 6)
                    (2, 4, 2, 5.00, 1)   # 2 Refrescos (ID 4)
                ]

                sql_detalles = "INSERT INTO detalle_transaccion (id_transaccion, id_producto, cantidad_producto, subtotal, estatus) VALUES (?, ?, ?, ?, ?)"
                self._ejecutar_insert_muchos(sql_detalles, detalles)

            self.db.desconectar()

# --- Bloque de prueba (Main) ---

if __name__ == "__main__":
    init_db = InicializadorDB()
    
    # 1. Crear Tablas
    print("Iniciando construcción de base de datos...")
    init_db.crear_tablas()
    
    # 2. Llenar datos base
    print("Poblando datos iniciales...")
    init_db.insertar_datos_semilla()
    
    print("Proceso finalizado.")
