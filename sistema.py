from excepciones import log, ErrorFJ, DatoInvalidoError
from modelos import (
    Entidad,
    Cliente,
    ReservaSala,
    AlquilerEquipo,
    Asesoria,
    Reserva,
)


class SoftwareFJ:
    def __init__(self):
        self.clientes, self.servicios, self.reservas = [], [], []

    def registrar_cliente(self, nombre, documento, email, telefono):
        cliente = Cliente(nombre, documento, email, telefono)
        if any(c.documento == cliente.documento for c in self.clientes):
            raise DatoInvalidoError(f"Ya existe un cliente con documento {cliente.documento}")
        self.clientes.append(cliente)
        log.info(f"Cliente registrado: {cliente.describir()}")
        return cliente

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)
        log.info(f"Servicio creado: {servicio.describir()}")
        return servicio

    def crear_reserva(self, cliente, servicio, horas):
        reserva = Reserva(cliente, servicio, horas)
        self.reservas.append(reserva)
        log.info(f"Reserva {reserva.id} creada")
        return reserva

    def ejecutar(self, descripcion, operacion):
        """Ejecuta una operación sin que el programa se detenga si falla."""
        print(f"\n>> {descripcion}")
        try:
            resultado = operacion()
        except ErrorFJ as e:
            causa = f" | causa: {e.__cause__}" if e.__cause__ else ""
            log.error(f"{descripcion} -> {e}{causa}")
            print(f"   [ERROR CONTROLADO] {e}")
        except Exception as e:
            log.critical(f"{descripcion} -> error inesperado {type(e).__name__}: {e}")
            print(f"   [ERROR INESPERADO] {type(e).__name__}: {e}")
        else:
            texto = resultado.describir() if isinstance(resultado, Entidad) else resultado
            print(f"   [OK] {texto or 'Operación exitosa'}")
            return resultado
        finally:
            log.info(f"Operación finalizada: {descripcion}")


def simulacion():
    s = SoftwareFJ()
    log.info("===== INICIO DE LA SIMULACIÓN =====")
    ana = s.ejecutar("1. Cliente válido (Ana)", lambda: s.registrar_cliente(
        "ana perez", "1020304050", "ana@correo.com", "3001234567"))
    s.ejecutar("2. Cliente con correo inválido", lambda: s.registrar_cliente(
        "Luis Mora", "9988776655", "luis-correo", "3101234567"))
    s.ejecutar("3. Cliente sin nombre (dato faltante)", lambda: s.registrar_cliente(
        None, "1234567", "x@correo.com", "3001112233"))

    sala = s.ejecutar("4. Sala válida", lambda: s.agregar_servicio(ReservaSala("Sala Ejecutiva", 10, 50000)))
    s.ejecutar("5. Sala con capacidad inválida", lambda: s.agregar_servicio(ReservaSala("Sala Rota", -5, 50000)))
    equipo = s.ejecutar("6. Equipo válido", lambda: s.agregar_servicio(AlquilerEquipo("Portátil", "Computador", 8000)))
    asesoria = s.ejecutar("7. Asesoría válida", lambda: s.agregar_servicio(
        Asesoria("Asesoría Python", "Programación", "senior", 90000)))
    s.ejecutar("8. Asesoría con nivel inválido", lambda: s.agregar_servicio(
        Asesoria("Asesoría X", "Redes", "experto", 70000)))

    r1 = s.ejecutar("9. Reserva exitosa (sala 3 h)", lambda: s.crear_reserva(ana, sala, 3))
    s.ejecutar("10. Confirmar y procesar con 10% de descuento",
               lambda: (r1.confirmar(), f"Total ${r1.procesar(descuento=0.10):,.2f}")[1])
    s.ejecutar("11. Reserva con duración excesiva (sala 20 h)", lambda: s.crear_reserva(ana, sala, 20))
    r3 = s.ejecutar("12. Reserva de equipo (24 h)", lambda: s.crear_reserva(ana, equipo, 24))
    equipo.disponible = False
    s.ejecutar("13. Confirmar con el equipo no disponible", lambda: r3.confirmar())
    r4 = s.ejecutar("14. Reserva de asesoría (2 h)", lambda: s.crear_reserva(ana, asesoria, 2))
    s.ejecutar("15. Cancelar y luego confirmar (no permitido)", lambda: (r4.cancelar(), r4.confirmar()))
    s.ejecutar("16. Reserva sin cliente", lambda: s.crear_reserva(None, sala, 2))
    r5 = s.ejecutar("17. Reserva de asesoría (1 h)", lambda: s.crear_reserva(ana, asesoria, 1))
    s.ejecutar("18. Procesar con descuento inconsistente (150%)",
               lambda: (r5.confirmar(), r5.procesar(descuento=1.5)))

    print("\n--- RESUMEN - Reservas ---")
    for i, elemento in enumerate(s.reservas, 1):
        print(f"  {i}. {elemento.describir()}")
    log.info("===== FIN DE LA SIMULACIÓN =====")
