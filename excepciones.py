import logging
import os

# Configuración del archivo de logs
RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "software_fj.log")
logging.basicConfig(
    filename=RUTA_LOG,
    level=logging.INFO,
    encoding="utf-8",
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
log = logging.getLogger("software_fj")


class ErrorFJ(Exception):
    """Excepción base de la aplicación."""


class DatoInvalidoError(ErrorFJ):
    """Un dato no cumple las reglas de validación."""


class ParametroFaltanteError(DatoInvalidoError):
    """Falta un dato obligatorio."""


class ServicioNoDisponibleError(ErrorFJ):
    """El servicio no está disponible."""


class OperacionNoPermitidaError(ErrorFJ):
    """La operación no es válida para el estado actual."""


class ReservaInvalidaError(ErrorFJ):
    """Intento de reserva incorrecto."""


class CalculoInconsistenteError(ErrorFJ):
    """Cálculo de costos con valores inconsistentes."""
