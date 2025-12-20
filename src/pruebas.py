from servicios.ConexionBD import ConexionBD

def probar_conexion():
    conexion_db = ConexionBD()
    conexion = conexion_db.conectar()
    if conexion:
        print("Conexión exitosa a la base de datos.")
        conexion_db.desconectar()
    else:
        print("Fallo en la conexión a la base de datos.")

probar_conexion()