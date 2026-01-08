from vistas.VistaPrincipal import VistaPrincipal
from servicios.InicializadorBD import InicializadorDB

if __name__ == "__main__":
    # Inicializar/verificar base de datos antes de crear la ventana principal
    init_bd = InicializadorDB()
    init_bd.crear_tablas()
    # Crear y mostrar la ventana principal de la aplicación
    app = VistaPrincipal()
    app.mainloop()