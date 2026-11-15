from Ejercicio1 import (
    Cliente, ReservaSala, Reserva, EstadoReserva,
    OperacionReservaError, ServicioNoDisponibleError
)

cliente = Cliente("Oscar", "oscar@example.com")
sala = ReservaSala("Sala de prueba", 50000, 10)

# Crear dos reservas pendientes para el mismo servicio.
reserva1 = Reserva(cliente, sala, 2)
reserva2 = Reserva(cliente, sala, 1)

# Confirmar la primera debe ocupar el servicio.
reserva1.procesar_confirmacion()
assert reserva1.estado == EstadoReserva.CONFIRMADA
assert sala.disponible is False
print("OK 1: confirmar ocupa el servicio.")

# La segunda no puede confirmarse mientras esté ocupado.
try:
    reserva2.procesar_confirmacion()
except OperacionReservaError as error:
    assert isinstance(error.__cause__, ServicioNoDisponibleError)
    assert reserva2.estado == EstadoReserva.PENDIENTE
    print("OK 2: se rechaza confirmar un servicio ocupado.")
else:
    raise AssertionError("Se confirmó un servicio ocupado.")

# Cancelar la pendiente no debe liberar el servicio de la primera.
reserva2.cancelar("Cancelar solicitud pendiente")
assert sala.disponible is False
print("OK 3: cancelar una pendiente no libera el servicio.")

# Cancelar la confirmada sí debe liberarlo.
reserva1.cancelar("Cancelación del cliente")
assert sala.disponible is True
assert reserva1.estado == EstadoReserva.CANCELADA
print("OK 4: cancelar la confirmada libera el servicio.")

# Una reserva cancelada no puede volver a confirmarse.
try:
    reserva1.procesar_confirmacion()
except OperacionReservaError:
    assert reserva1.estado == EstadoReserva.CANCELADA
    assert sala.disponible is True
    print("OK 5: una reserva cancelada no puede confirmarse.")
else:
    raise AssertionError("Se confirmó una reserva cancelada.")

# Otra reserva puede utilizar el servicio liberado.
reserva3 = Reserva(cliente, sala, 1)
reserva3.procesar_confirmacion()
assert reserva3.estado == EstadoReserva.CONFIRMADA
assert sala.disponible is False
print("OK 6: el servicio liberado puede reservarse nuevamente.")

print("\nTodas las pruebas de estados finalizaron correctamente.")