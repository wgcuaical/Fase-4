"""
SOFTWARE FJ
Sistema integral de gestión de clientes, servicios y reservas.
Sin bases de datos: utiliza objetos y listas en memoria.
El archivo software_fj.log registra eventos y errores.
"""

# Importacion de librerias
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
import logging
import re
import uuid


# Definir la excepción base para los errores del sistema.
class ErrorSoftwareFJ(Exception):
    pass


# Representar errores en los datos ingresados.
class DatosInvalidosError(ErrorSoftwareFJ):
    pass


# Indicar que un servicio no está disponible para reservar.
class ServicioNoDisponibleError(ErrorSoftwareFJ):
    pass


# Representar operaciones no permitidas sobre una reserva.
class OperacionReservaError(ErrorSoftwareFJ):
    pass


# Guardar el archivo de registros junto al programa.
ruta_log = Path(__file__).resolve().parent / "software_fj.log"

# Crear el registrador del sistema.
logger = logging.getLogger("software_fj")
logger.setLevel(logging.INFO)
logger.propagate = False

# Evitar manejadores duplicados.
if not logger.handlers:
    # Conservar los registros anteriores y admitir tildes.
    manejador = logging.FileHandler(
        ruta_log,
        mode="a",
        encoding="utf-8"
    )

    # Registrar fecha, hora, nivel y mensaje.
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    manejador.setFormatter(formato)
    logger.addHandler(manejador)

# Ejecutar esta prueba solo cuando se inicia este archivo directamente.
if __name__ == "__main__":
    logger.info("Inicio de la prueba de integración.")

    try:
        # Simular un nombre vacío.
        nombre = ""

        if not nombre.strip():
            raise DatosInvalidosError(
                "El nombre no puede estar vacío."
            )

    except DatosInvalidosError as error:
        logger.error("Error de validación: %s", error)
        print("Error controlado:", error)

    else:
        logger.info("Nombre validado correctamente.")
        print("Nombre válido:", nombre)

    finally:
        logger.info("Fin de la prueba de integración.")

    print("El sistema sigue funcionando.")
