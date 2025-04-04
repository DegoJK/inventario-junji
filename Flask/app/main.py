from app import app
# Se importan las variables blueprint en las vistas correspondientes para que puedan ser iniciadas a traves de main
from proveedor import proveedor
from tipo_adquisicion import tipo_adquisicion
from orden_compra import orden_compra
from provincia import provincias
from comuna import comuna
from tipo_equipo import tipo_equipo
from Unidad import Unidad
from marca_equipo import marca_equipo
from modelo_equipo import modelo_equipo
from estado_equipo import estado_equipo
from funcionario import funcionario
from equipo import equipo
from devolucion import devolucion
from asignacion import asignacion
from traslado import traslado
from incidencia import incidencia
from buscar import buscar
from utils import utils
from cuentas import cuentas

app.register_blueprint(devolucion)
app.register_blueprint(proveedor)
app.register_blueprint(tipo_adquisicion)
app.register_blueprint(provincias)
app.register_blueprint(orden_compra)
app.register_blueprint(comuna)
app.register_blueprint(tipo_equipo)
app.register_blueprint(Unidad)
app.register_blueprint(marca_equipo)
app.register_blueprint(modelo_equipo)
app.register_blueprint(estado_equipo)
app.register_blueprint(funcionario)
app.register_blueprint(equipo)
app.register_blueprint(asignacion)
app.register_blueprint(traslado)
app.register_blueprint(incidencia)
app.register_blueprint(buscar)
app.register_blueprint(utils)
app.register_blueprint(cuentas)

# se inicia la aplicacion, y confirma que __name__ sea la aplicacion main y no un modulo
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)
