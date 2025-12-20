class DetalleTransaccion:
    def __init__(self, id_detalle, id_transaccion, id_producto, cantidad_producto, subtotal, estatus):
        """
        Constructor de la clase DetalleTransaccion.
        
        Parámetros:
        - id_detalle: El ID único de la línea (None si es nuevo y aún no se guarda).
        - id_transaccion: El ID de la transacción padre a la que pertenece este detalle.
        - id_producto: El ID del producto vendido/comprado.
        - cantidad_producto: La cantidad (entero).
        - subtotal: El monto calculado (precio_unitario * cantidad).
        - estatus: Estado del registro (1 activo, 0 eliminado).
        """
        self.id_detalle = id_detalle
        self.id_transaccion = id_transaccion
        self.id_producto = id_producto
        self.cantidad_producto = cantidad_producto
        self.subtotal = subtotal
        self.estatus = estatus