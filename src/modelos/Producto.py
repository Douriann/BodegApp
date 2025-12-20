class Producto:
    def __init__(self, id_producto, nombre_producto, id_categoria, id_marca, 
                 presentacion, unidad_medida, contenido, precio_compra, 
                 precio_venta, stock_minimo, stock_actual, estatus):
        
        self.id_producto = id_producto
        self.nombre_producto = nombre_producto
        self.id_categoria = id_categoria
        self.id_marca = id_marca
        self.presentacion = presentacion
        self.unidad_medida = unidad_medida
        self.contenido = contenido
        self.precio_compra = precio_compra
        self.precio_venta = precio_venta
        self.stock_minimo = stock_minimo
        self.stock_actual = stock_actual
        self.estatus = estatus