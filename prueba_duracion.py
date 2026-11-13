from Ejercicio1 import (
    Cliente, ReservaSala, Reserva,
    DatosInvalidosError, EstadoReserva, logger
)

# Preparar un cliente y un servicio disponible.
cliente = Cliente("Oscar", "oscar@example.com")
sala = ReservaSala("Sala de prueba", 50000, 10)

# Probar duraciones que deben rechazarse.
casos_invalidos = [
    ("Cero", 0),
    ("Negativa", -1),
    ("Texto", "dos"),
    ("Booleano", True),
    ("Infinito positivo", float("inf")),
    ("Infinito negativo", float("-inf")),
    ("Valor indefinido", float("nan")),
    ("Sin valor", None)
]

for descripcion, duracion in casos_invalidos:
    try:
        Reserva(cliente, sala, duracion)

    except DatosInvalidosError as error:
        logger.info(
            "Prueba de duración rechazada correctamente: %s | %s",
            descripcion, error
        )
        print(f"OK: {descripcion} rechazado.")

    else:
        raise AssertionError(
            f"Se aceptó una duración incorrecta: {descripcion}"
        )

# Probar una duración entera y otra con fracción de hora.
for duracion in [1, 1.5]:
    reserva = Reserva(cliente, sala, duracion)

    assert reserva.duracion_horas == duracion
    assert reserva.estado == EstadoReserva.PENDIENTE
    assert sala.disponible is True

    print(f"OK: duración de {duracion} horas aceptada.")

print("\nLas diez pruebas de duración finalizaron correctamente.")