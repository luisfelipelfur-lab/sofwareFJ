from abc import ABC, abstractmethod
from excepciones import (
    log,
    ErrorFJ,
    DatoInvalidoError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    CalculoInconsistenteError,
)


# ===== ENTIDAD ABSTRACTA Y CLIENTE =====
class Entidad(ABC):
    """Entidad general del sistema: todas tienen un id y se pueden describir."""
    _contadores = {}
    _tipo = "entidad"

    def __init__(self):
        Entidad._contadores[self._tipo] = Entidad._contadores.get(self._tipo, 0) + 1
        self._id = Entidad._contadores[self._tipo]

    @property
    def id(self):
        return self._id

    @abstractmethod
    def describir(self):
        """Devuelve un texto que describe la entidad."""


class Cliente(Entidad):
    """Cliente con datos personales encapsulados (atributos privados + validación)."""
    _tipo = "cliente"

    def __init__(self, nombre, documento, email, telefono):
        try:
            nombre = self._texto(nombre, "nombre")
            documento = self._texto(documento, "documento")
            email = self._texto(email, "correo")
            telefono = self._texto(telefono, "teléfono")
            if len(nombre) < 3 or any(c.isdigit() for c in nombre):
                raise DatoInvalidoError("El nombre debe tener mínimo 3 letras y no llevar números")
            if not documento.isdigit() or not 6 <= len(documento) <= 12:
                raise DatoInvalidoError("El documento debe ser numérico (6 a 12 dígitos)")
            if "@" not in email or "." not in email.split("@")[-1]:
                raise DatoInvalidoError(f"Correo inválido: {email}")
            if not telefono.isdigit() or not 7 <= len(telefono) <= 10:
                raise DatoInvalidoError("El teléfono debe ser numérico (7 a 10 dígitos)")
        except DatoInvalidoError as e:
            raise DatoInvalidoError(f"No se pudo crear el cliente: {e}") from e

        super().__init__()
        self.__nombre = nombre.title()
        self.__documento = documento
        self.__email = email.lower()
        self.__telefono = telefono

    @staticmethod
    def _texto(valor, campo):
        if valor is None or not str(valor).strip():
            raise ParametroFaltanteError(f"Falta el dato obligatorio: {campo}")
        return str(valor).strip()

    @property
    def nombre(self):
        return self.__nombre

    @property
    def documento(self):
        return self.__documento

    @property
    def email(self):
        return self.__email

    @property
    def telefono(self):
        return self.__telefono

    def describir(self):
        return f"Cliente {self.__nombre} (doc. {self.__documento}, {self.__email}, tel. {self.__telefono})"


# ===== SERVICIO (ABSTRACTA) Y SERVICIOS ESPECIALIZADOS =====
class Servicio(Entidad, ABC):
    """Servicio abstracto. Los hijos sobrescriben costo, descripción y validación."""
    _tipo = "servicio"
    IVA = 0.19
    MAX_HORAS = 8

    def __init__(self, nombre, tarifa_hora):
        self._nombre = nombre
        self._tarifa = tarifa_hora
        self.disponible = True
        self.validar_parametros()
        super().__init__()

    @property
    def nombre(self):
        return self._nombre

    def validar_parametros(self):
        if self._nombre is None or not str(self._nombre).strip():
            raise ParametroFaltanteError("Falta el nombre del servicio")
        if not isinstance(self._tarifa, (int, float)) or self._tarifa <= 0:
            raise DatoInvalidoError("La tarifa por hora debe ser un número mayor a 0")

    def validar_duracion(self, horas):
        if not isinstance(horas, (int, float)) or horas <= 0:
            raise DatoInvalidoError("La duración debe ser un número mayor a 0")
        if horas > self.MAX_HORAS:
            raise DatoInvalidoError(f"'{self._nombre}' permite máximo {self.MAX_HORAS} horas")

    @abstractmethod
    def calcular_costo(self, horas):
        """Costo base sin impuestos ni descuentos."""

    @abstractmethod
    def describir(self):
        """Descripción del servicio."""

    def costo_total(self, horas, impuesto=None, descuento=0.0):
        """Método sobrecargado mediante parámetros opcionales."""
        self.validar_duracion(horas)
        impuesto = self.IVA if impuesto is None else impuesto
        if not 0 <= impuesto <= 1:
            raise CalculoInconsistenteError(f"Impuesto fuera de rango (0 a 1): {impuesto}")
        if not 0 <= descuento < 1:
            raise CalculoInconsistenteError(f"Descuento fuera de rango (0 a menos de 1): {descuento}")
        return round(self.calcular_costo(horas) * (1 - descuento) * (1 + impuesto), 2)


class ReservaSala(Servicio):
    MAX_HORAS = 8

    def __init__(self, nombre, capacidad, tarifa_hora):
        self._capacidad = capacidad
        super().__init__(nombre, tarifa_hora)

    def validar_parametros(self):
        super().validar_parametros()
        if not isinstance(self._capacidad, int) or self._capacidad <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser un entero mayor a 0")

    def calcular_costo(self, horas):
        recargo = 1.10 if self._capacidad >= 20 else 1
        return self._tarifa * horas * recargo

    def describir(self):
        return f"Sala '{self._nombre}' ({self._capacidad} personas) ${self._tarifa:,.0f}/h"


class AlquilerEquipo(Servicio):
    MAX_HORAS = 72

    def __init__(self, nombre, tipo_equipo, tarifa_hora):
        self._tipo = tipo_equipo
        super().__init__(nombre, tarifa_hora)

    def validar_parametros(self):
        super().validar_parametros()
        if not self._tipo or not str(self._tipo).strip():
            raise ParametroFaltanteError("Falta el tipo de equipo")

    def calcular_costo(self, horas):
        return self._tarifa * horas * 1.05

    def describir(self):
        return f"Equipo '{self._nombre}' ({self._tipo}) ${self._tarifa:,.0f}/h + seguro 5%"


class Asesoria(Servicio):
    MAX_HORAS = 4

    def __init__(self, nombre, especialidad, nivel, tarifa_hora):
        self._especialidad = especialidad
        self._nivel = nivel
        super().__init__(nombre, tarifa_hora)

    def validar_parametros(self):
        super().validar_parametros()
        if not self._especialidad or not str(self._especialidad).strip():
            raise ParametroFaltanteError("Falta la especialidad de la asesoría")
        if self._nivel not in ("junior", "senior"):
            raise DatoInvalidoError(f"Nivel inválido '{self._nivel}' (use junior o senior)")

    def calcular_costo(self, horas):
        return self._tarifa * horas * (1.5 if self._nivel == "senior" else 1)

    def describir(self):
        return f"Asesoría '{self._nombre}' en {self._especialidad} ({self._nivel}) ${self._tarifa:,.0f}/h"


# ===== RESERVA (COMPOSICIÓN) =====
class Reserva(Entidad):
    """Integra cliente, servicio, duración y estado."""
    _tipo = "reserva"

    def __init__(self, cliente, servicio, horas):
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva necesita un cliente válido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva necesita un servicio válido")
        try:
            servicio.validar_duracion(horas)
        except DatoInvalidoError as e:
            raise ReservaInvalidaError(f"Reserva rechazada: {e}") from e
        super().__init__()
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self.estado = "Pendiente"
        self.total = None

    def confirmar(self):
        if self.estado != "Pendiente":
            raise OperacionNoPermitidaError(f"No se puede confirmar una reserva {self.estado}")
        try:
            if not self._servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio '{self._servicio.nombre}' no está disponible")
        except ServicioNoDisponibleError:
            log.warning(f"Reserva {self.id}: confirmación rechazada (servicio no disponible)")
            raise
        else:
            self.estado = "Confirmada"
            self._servicio.disponible = False
            log.info(f"Reserva {self.id} confirmada")
        finally:
            log.info(f"Reserva {self.id}: fin del intento de confirmación")

    def cancelar(self):
        if self.estado in ("Cancelada", "Procesada"):
            raise OperacionNoPermitidaError(f"No se puede cancelar una reserva {self.estado}")
        if self.estado == "Confirmada":
            self._servicio.disponible = True
        self.estado = "Cancelada"
        log.info(f"Reserva {self.id} cancelada")

    def procesar(self, impuesto=None, descuento=0.0):
        if self.estado != "Confirmada":
            raise OperacionNoPermitidaError(f"Solo se procesan reservas confirmadas (estado: {self.estado})")
        try:
            total = self._servicio.costo_total(self._horas, impuesto, descuento)
        except ErrorFJ as e:
            self.estado = "Fallida"
            raise ReservaInvalidaError(f"No se pudo procesar la reserva {self.id}: {e}") from e
        else:
            self.total = total
            self.estado = "Procesada"
            self._servicio.disponible = True
            log.info(f"Reserva {self.id} procesada. Total ${total:,.2f}")
            return total
        finally:
            log.info(f"Reserva {self.id}: fin del procesamiento")

    def describir(self):
        total = f" | total ${self.total:,.2f}" if self.total else ""
        return (f"Reserva {self.id} [{self.estado}] {self._cliente.nombre} -> "
                f"{self._servicio.nombre} ({self._horas} h){total}")
