class Transaccion:
    def __init__(self, id_transaccion, fecha_transaccion, id_tipo, total, observaciones, estatus):
        self.id_transaccion = id_transaccion
        self.fecha_transaccion = fecha_transaccion  # Se recibe como string (YYYY-MM-DD) o datetime
        self.id_tipo = id_tipo                      # FK hacia tipo_transaccion
        self.total = total
        self.observaciones = observaciones
        self.estatus = estatus