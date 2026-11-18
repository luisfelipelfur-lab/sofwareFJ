from excepciones import RUTA_LOG, log, DatoInvalidoError
from modelos import ReservaSala, AlquilerEquipo, Asesoria
from sistema import SoftwareFJ, simulacion

MENU = """
============ SOFTWARE FJ ============
1. Registrar cliente
2. Crear servicio
3. Crear reserva
4. Confirmar reserva
5. Cancelar reserva
6. Procesar reserva (calcular costo)
7. Cambiar disponibilidad de un servicio
8. Ver clientes, servicios y reservas
9. Ejecutar simulación automática
0. Salir
====================================="""


def pedir(texto):
    return input(texto).strip()


def numero(texto, campo):
    try:
        valor = float(texto.replace(",", "."))
    except ValueError as e:
        raise DatoInvalidoError(f"'{campo}' debe ser un número (recibido: '{texto}')") from e
    return int(valor) if valor.is_integer() else valor


def listar(titulo, lista):
    print(f"\n--- {titulo} ---")
    for i, elemento in enumerate(lista, 1):
        print(f"  {i}. {elemento.describir()}")
    if not lista:
        print("  (sin registros)")


def elegir(lista, nombre):
    if not lista:
        raise DatoInvalidoError(f"No hay {nombre} registrados")
    listar(nombre.capitalize(), lista)
    posicion = numero(pedir("Elija el número: "), "opción")
    if not isinstance(posicion, int) or not 1 <= posicion <= len(lista):
        raise DatoInvalidoError("Número fuera de la lista")
    return lista[posicion - 1]


def menu_crear_servicio(s):
    tipo = pedir("Tipo (1=Sala, 2=Equipo, 3=Asesoría): ")
    nombre = pedir("Nombre: ") or None
    if tipo == "1":
        capacidad, tarifa = pedir("Capacidad (personas): "), pedir("Tarifa por hora: ")
        s.ejecutar("Crear sala", lambda: s.agregar_servicio(
            ReservaSala(nombre, numero(capacidad, "capacidad"), numero(tarifa, "tarifa"))))
    elif tipo == "2":
        equipo, tarifa = pedir("Tipo de equipo: "), pedir("Tarifa por hora: ")
        s.ejecutar("Crear equipo", lambda: s.agregar_servicio(
            AlquilerEquipo(nombre, equipo, numero(tarifa, "tarifa"))))
    elif tipo == "3":
        esp, nivel = pedir("Especialidad: "), pedir("Nivel (junior/senior): ").lower()
        tarifa = pedir("Tarifa por hora: ")
        s.ejecutar("Crear asesoría", lambda: s.agregar_servicio(
            Asesoria(nombre, esp, nivel, numero(tarifa, "tarifa"))))
    else:
        print("   Tipo de servicio no válido.")


def menu_crear_reserva(s):
    def crear():
        cliente = elegir(s.clientes, "clientes")
        servicio = elegir(s.servicios, "servicios")
        horas = numero(pedir("Duración en horas: "), "horas")
        return s.crear_reserva(cliente, servicio, horas).describir()
    s.ejecutar("Crear reserva", crear)


def menu_procesar(s):
    def procesar():
        reserva = elegir(s.reservas, "reservas")
        imp, desc = pedir("Impuesto % (Enter = 19): "), pedir("Descuento % (Enter = 0): ")
        impuesto = numero(imp, "impuesto") / 100 if imp else None
        descuento = numero(desc, "descuento") / 100 if desc else 0.0
        return f"Total a pagar: ${reserva.procesar(impuesto, descuento):,.2f}"
    s.ejecutar("Procesar reserva", procesar)


def menu_cambiar_disponibilidad(s):
    def cambiar():
        servicio = elegir(s.servicios, "servicios")
        servicio.disponible = not servicio.disponible
        return f"'{servicio.nombre}' disponible: {'Sí' if servicio.disponible else 'No'}"
    s.ejecutar("Cambiar disponibilidad", cambiar)


def main():
    s = SoftwareFJ()
    log.info("===== SESIÓN INTERACTIVA INICIADA =====")
    while True:
        try:
            print(MENU)
            opcion = pedir("Seleccione una opción: ")
            if opcion == "0":
                break
            elif opcion == "1":
                datos = [pedir("Nombre completo: "), pedir("Documento: "),
                         pedir("Correo: "), pedir("Teléfono: ")]
                s.ejecutar("Registrar cliente", lambda: s.registrar_cliente(*[d or None for d in datos]))
            elif opcion == "2":
                menu_crear_servicio(s)
            elif opcion == "3":
                menu_crear_reserva(s)
            elif opcion == "4":
                s.ejecutar("Confirmar reserva", lambda: elegir(s.reservas, "reservas").confirmar())
            elif opcion == "5":
                s.ejecutar("Cancelar reserva", lambda: elegir(s.reservas, "reservas").cancelar())
            elif opcion == "6":
                menu_procesar(s)
            elif opcion == "7":
                menu_cambiar_disponibilidad(s)
            elif opcion == "8":
                listar("Clientes", s.clientes)
                listar("Servicios", s.servicios)
                listar("Reservas", s.reservas)
            elif opcion == "9":
                simulacion()
            else:
                print("   Opción no válida.")
        except (KeyboardInterrupt, EOFError):
            print("\n   Entrada cancelada.")
            break
    log.info("===== SESIÓN INTERACTIVA FINALIZADA =====")
    print(f"\nHasta pronto. Registro de eventos en: {RUTA_LOG}")


if __name__ == "__main__":
    main()
