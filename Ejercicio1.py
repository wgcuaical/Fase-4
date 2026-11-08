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


# Definir una base común para las entidades del sistema.
class Entidad(ABC):
    # Asignar un identificador único al crear cada entidad.
    def __init__(self):
        self._identificador = str(uuid.uuid4())

    # Permitir consultar el identificador mediante una propiedad.
    @property
    def identificador(self):
        return self._identificador

    # Exigir que las clases hijas definan cómo describirse.
    @abstractmethod
    def describir(self):
        pass

# Representar a un cliente del sistema.
class Cliente(Entidad):
    # Validar y guardar los datos iniciales del cliente.
    def __init__(self, nombre, correo):
        super().__init__()

        # Comprobar que el nombre sea texto y tenga contenido.
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidosError(
                "El nombre del cliente no puede estar vacío y debe ser texto."
            )

        # Comprobar que el correo sea texto.
        if not isinstance(correo, str):
            raise DatosInvalidosError(
                "El correo del cliente debe ser texto."
            )

        # Quitar espacios al principio y al final del correo.
        correo = correo.strip()

        # Comprobar una estructura básica de correo electrónico.
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
            raise DatosInvalidosError(
                "El correo electrónico no tiene un formato válido."
            )

        # Guardar los datos como atributos de uso interno.
        self._nombre = nombre.strip()
        self._correo = correo

    # Permitir consultar el nombre.
    @property
    def nombre(self):
        return self._nombre

    # Permitir consultar el correo.
    @property
    def correo(self):
        return self._correo

    # Implementar la descripción exigida por Entidad.
    def describir(self):
        return f"Cliente: {self.nombre} | Correo: {self.correo}"
    

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
