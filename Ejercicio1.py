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
    

# Definir las características comunes de los servicios.
class Servicio(Entidad):
    # Validar y guardar los datos iniciales del servicio.
    def __init__(self, nombre, tarifa):
        super().__init__()

        # Exigir un nombre de tipo texto que no esté vacío.
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidosError(
                "El nombre del servicio debe ser texto y no estar vacío."
            )

        # Aceptar números, pero rechazar valores booleanos.
        if isinstance(tarifa, bool) or not isinstance(tarifa, (int, float)):
            raise DatosInvalidosError(
                "La tarifa debe ser un número."
            )

        # Exigir una tarifa positiva y finita.
        if not 0 < tarifa < float("inf"):
            raise DatosInvalidosError(
                "La tarifa debe ser positiva y finita."
            )

        # Guardar los datos después de validarlos.
        self._nombre = nombre.strip()
        self._tarifa = tarifa
        self._disponible = True

    # Permitir consultar el nombre del servicio.
    @property
    def nombre(self):
        return self._nombre

    # Permitir consultar la tarifa del servicio.
    @property
    def tarifa(self):
        return self._tarifa

    # Permitir consultar si el servicio está disponible.
    @property
    def disponible(self):
        return self._disponible

    # Ocupar el servicio solamente si está disponible.
    def ocupar(self):
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible."
            )

        self._disponible = False

    # Dejar el servicio disponible nuevamente.
    def liberar(self):
        self._disponible = True

    # Validar los valores utilizados para calcular el costo.
    def _validar_datos_costo(self, duracion, impuesto, descuento):
        # Comprobar que los tres valores sean números finitos.
        datos = [
            ("La duración", duracion),
            ("El impuesto", impuesto),
            ("El descuento", descuento)
        ]

        for nombre, valor in datos:
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise DatosInvalidosError(
                    f"{nombre} debe ser un número."
                )

            if not float("-inf") < valor < float("inf"):
                raise DatosInvalidosError(
                    f"{nombre} debe ser un número finito."
                )

        # Exigir una duración mayor que cero.
        if duracion <= 0:
            raise DatosInvalidosError(
                "La duración debe ser mayor que cero."
            )

        # Aceptar porcentajes entre cero y cien.
        if not 0 <= impuesto <= 100:
            raise DatosInvalidosError(
                "El impuesto debe estar entre 0 y 100."
            )

        if not 0 <= descuento <= 100:
            raise DatosInvalidosError(
                "El descuento debe estar entre 0 y 100."
            )

    # Calcular el costo aplicando primero el descuento y luego el impuesto.
    def _calcular_costo_base(self, duracion, impuesto=0, descuento=0):
        # Comprobar los datos antes de realizar las operaciones.
        self._validar_datos_costo(duracion, impuesto, descuento)

        try:
            # Multiplicar la tarifa por la duración en horas.
            subtotal = self.tarifa * duracion

            # Aplicar el descuento al subtotal.
            con_descuento = subtotal * (1 - descuento / 100)

            # Aplicar el impuesto al valor con descuento.
            total = con_descuento * (1 + impuesto / 100)

        except OverflowError as error_original:
            # Conservar la causa si los valores exceden el cálculo permitido.
            raise DatosInvalidosError(
                "Los valores son demasiado grandes para calcular el costo."
            ) from error_original

        # Rechazar resultados infinitos, indefinidos o negativos.
        if not 0 <= total < float("inf"):
            raise DatosInvalidosError(
                "El cálculo produjo un costo fuera del rango permitido."
            )

        # Devolver el costo con dos decimales.
        return round(total, 2)

    
    # Exigir que cada servicio valide sus parámetros específicos.
    @abstractmethod
    def validar_parametros(self):
        pass

    # Exigir que cada servicio implemente su cálculo de costos.
    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        pass


# ==========================================
# SERVICIOS ESPECIALIZADOS (HERENCIA Y POLIMORFISMO)
# ==========================================

class ReservaSala(Servicio):
    """Servicio especializado 1: Reserva de salas de conferencias."""

    def __init__(self, nombre: str, tarifa: float, capacidad_personas: int):
        super().__init__(nombre, tarifa)
        self._capacidad_personas = capacidad_personas
        self.validar_parametros()

    @property
    def capacidad_personas(self) -> int:
        return self._capacidad_personas

    def validar_parametros(self):
        if isinstance(self._capacidad_personas, bool) or not isinstance(self._capacidad_personas, int):
            raise DatosInvalidosError("La capacidad de personas debe ser un número entero.")
        if self._capacidad_personas <= 0:
            raise DatosInvalidosError("La capacidad de personas debe ser mayor que cero.")

    def calcular_costo(self, duracion: float, impuesto: float = 0, descuento: float = 0) -> float:

        # Validar los parámetros antes de calcular.
        self._validar_datos_costo(duracion, impuesto, descuento)

        # Aplicar descuento adicional del 5 % cuando
        # la reserva supere las 5 horas.
        descuento_tiempo = 5.0 if duracion > 5 else 0.0

        # Sumar el descuento adicional al descuento solicitado.
        descuento_total = descuento + descuento_tiempo

        # Evitar que los descuentos superen el 100 %.
        if descuento_total > 100:
            raise DatosInvalidosError(
            "El descuento total no puede superar el 100 %."
            )

        return self._calcular_costo_base(
            duracion,
            impuesto,
            descuento_total
        )

    def describir(self) -> str:
        return f"Reserva de Sala '{self.nombre}' | Capacidad: {self.capacidad_personas} personas | Tarifa/h: ${self.tarifa}"


class AlquilerEquipo(Servicio):
    """Servicio especializado 2: Alquiler de equipos tecnológicos."""

    def __init__(self, nombre: str, tarifa: float, incluye_seguro: bool = True):
        super().__init__(nombre, tarifa)
        if not isinstance(incluye_seguro, bool):
            raise DatosInvalidosError("El parámetro 'incluye_seguro' debe ser un valor booleano.")
        self._incluye_seguro = incluye_seguro
        self.validar_parametros()

    @property
    def incluye_seguro(self) -> bool:
        return self._incluye_seguro

    def validar_parametros(self):

    # Verificar que el seguro sea un valor booleano.
     if not isinstance(self._incluye_seguro, bool):
        raise DatosInvalidosError(
            "El seguro debe ser verdadero o falso."
        )

    def calcular_costo(self, duracion: float, impuesto: float = 0, descuento: float = 0) -> float:

        # Calcular el costo del alquiler con sus descuentos e impuestos.
        costo_base = self._calcular_costo_base(
            duracion,
            impuesto,
            descuento
    )

        # Aplicar recargo de seguro cuando corresponda.
        recargo_seguro = 15000.0 if self._incluye_seguro else 0.0

        # Sumar el seguro al costo calculado.
        total = costo_base + recargo_seguro

        return round(total, 2)

    def describir(self) -> str:
        seg_str = "Con seguro contra daños" if self.incluye_seguro else "Sin seguro"
        return f"Alquiler de Equipo '{self.nombre}' ({seg_str}) | Tarifa/h: ${self.tarifa}"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado 3: Asesores técnicos y consultoría."""

    def __init__(self, nombre: str, tarifa: float, especialista: str):
        self._especialista = especialista
        super().__init__(nombre, tarifa)
        self.validar_parametros()

    @property
    def especialista(self) -> str:
        return self._especialista

    def validar_parametros(self):
        if not isinstance(self._especialista, str) or not self._especialista.strip():
            raise DatosInvalidosError("El nombre del especialista debe ser texto y no estar vacío.")

    def calcular_costo(self, duracion: float, impuesto: float = 0, descuento: float = 0) -> float:

        # Validar primero los datos numéricos.
        self._validar_datos_costo(
        duracion,
        impuesto,
        descuento
    )

        # Establecer la duración mínima de contratación.
        if duracion < 1.0:
            raise DatosInvalidosError(
                "Las asesorías especializadas requieren "
                "mínimo 1 hora de contratación."
        )

        # Calcular el costo cuando se cumplen las condiciones.
        return self._calcular_costo_base(
            duracion,
            impuesto,
            descuento
    )

    def describir(self) -> str:
        return f"Asesoría Especializada en '{self.nombre}' por {self.especialista} | Tarifa/h: ${self.tarifa}"


# ==========================================
# CLASE RESERVA
# ==========================================

class EstadoReserva(Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"


class Reserva(Entidad):
    """Integra cliente, servicio, duración y estado con manejo de excepciones."""

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion_horas: float):
        super().__init__()
        
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El cliente asignado debe ser una instancia de la clase Cliente.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El servicio asignado debe ser una instancia de la clase Servicio.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible.")
        
        # Comprobar que la duración sea numérica, sin aceptar booleanos.
        if isinstance(duracion_horas, bool) or not isinstance(
            duracion_horas, (int, float)
        ):
            raise DatosInvalidosError(
                "La duración de la reserva debe ser un número."
            )

        # Rechazar cero, negativos, infinito y valores indefinidos.
        if not 0 < duracion_horas < float("inf"):
            raise DatosInvalidosError(
                "La duración de la reserva debe ser positiva y finita."
            )
        
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._estado = EstadoReserva.PENDIENTE
        self._costo_total = 0.0

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion_horas(self) -> float:
        return self._duracion_horas

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    # Confirmar una reserva pendiente y ocupar su servicio.
    def procesar_confirmacion(self, impuesto=19, descuento=0):
        # Evitar confirmar reservas canceladas o ya confirmadas.
        if self.estado != EstadoReserva.PENDIENTE:
            logger.warning(
                "Confirmación rechazada para reserva %s. Estado: %s",
                self.identificador, self.estado.value
            )
            raise OperacionReservaError(
                "Solo se pueden confirmar reservas pendientes."
            )

        try:
            # Comprobar la disponibilidad al momento de confirmar.
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(
                    f"El servicio '{self.servicio.nombre}' no está disponible."
                )

            # Calcular antes de modificar la reserva o el servicio.
            costo = self.servicio.calcular_costo(
                self.duracion_horas, impuesto, descuento
            )

            # Ocupar el servicio después de calcular correctamente.
            self.servicio.ocupar()

        except Exception as error_origen:
            # Registrar el fallo y conservar su causa original.
            logger.exception(
                "Error al confirmar la reserva %s",
                self.identificador
            )
            raise OperacionReservaError(
                f"No se pudo confirmar la reserva: {error_origen}"
            ) from error_origen

        # Guardar el resultado cuando la operación fue exitosa.
        self._costo_total = costo
        self._estado = EstadoReserva.CONFIRMADA

        logger.info(
            "Reserva %s CONFIRMADA | Servicio: %s | Costo: %s",
            self.identificador, self.servicio.nombre, self.costo_total
        )

        return self.costo_total
    
    # Cancelar la reserva y liberar el servicio si estaba confirmado.
    def cancelar(self, motivo: str):
        # Evitar cancelar dos veces la misma reserva.
        if self.estado == EstadoReserva.CANCELADA:
            logger.warning(
                "Cancelación repetida de la reserva %s",
                self.identificador
            )
            raise OperacionReservaError(
                "La reserva ya se encuentra cancelada."
            )

        # Solo una reserva confirmada había ocupado el servicio.
        if self.estado == EstadoReserva.CONFIRMADA:
            self.servicio.liberar()

        # Registrar la cancelación.
        self._estado = EstadoReserva.CANCELADA
        logger.info(
            "Reserva %s CANCELADA. Motivo: %s",
            self.identificador, motivo
        )


    def describir(self) -> str:
        return (f"Reserva [{self.identificador[:8]}] | Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio.nombre} | Estado: {self.estado.value} | Total: ${self.costo_total:.2f}")


# ==========================================
# SIMULACIÓN DE 10 OPERACIONES COMPLETAS
# ==========================================

def ejecutar_simulacion():
    print("\n==============================================================")
    print("   SOFTWARE FJ - SISTEMA INTEGRAL (SIMULACIÓN FASE 4)        ")
    print("==============================================================\n")
    logger.info("=== INICIO DE LA SIMULACIÓN DE 10 OPERACIONES ===")

    clientes = []
    servicios = []
    reservas = []

    # OP 1: Registro válido de cliente
    print("[OP 1] Registro de Cliente válido...")
    try:
        c1 = Cliente("José Julian Moreno", "jjmorenoi@unadvirtual.edu.co")
        clientes.append(c1)
        logger.info("OP 1 Exitosa: %s", c1.describir())
        print(" -> OK:", c1.describir())
    except ErrorSoftwareFJ as e:
        print(" -> Error:", e)

    # OP 2: Registro inválido de cliente (Correo erróneo)
    print("\n[OP 2] Registro de Cliente inválido (Sin @)...")
    try:
        c2 = Cliente("Pedro Pérez", "pedro_sin_arroba.com")
        clientes.append(c2)
    except ErrorSoftwareFJ as e:
        logger.warning("OP 2 Controlada: %s", e)
        print(" -> Error controlado:", e)

    # OP 3: Creación de Servicio válido (Reserva de Sala)
    print("\n[OP 3] Creación de Servicio de Sala válido...")
    try:
        s1 = ReservaSala("Sala Executive Juntas", tarifa=45000.0, capacidad_personas=12)
        servicios.append(s1)
        logger.info("OP 3 Exitosa: %s", s1.describir())
        print(" -> OK:", s1.describir())
    except ErrorSoftwareFJ as e:
        print(" -> Error:", e)

    # OP 4: Creación de Servicio inválido (Capacidad negativa)
    print("\n[OP 4] Creación de Servicio con capacidad inválida...")
    try:
        s2 = ReservaSala("Sala Pequeña", tarifa=20000.0, capacidad_personas=-5)
        servicios.append(s2)
    except ErrorSoftwareFJ as e:
        logger.warning("OP 4 Controlada: %s", e)
        print(" -> Error controlado:", e)

    # OP 5: Creación de Asesoría Especializada válida
    print("\n[OP 5] Creación de Servicio de Asesoría Técnica...")
    try:
        s3 = AsesoriaEspecializada("Ciberseguridad y Redes", tarifa=80000.0, especialista="Ing. Juan Arango")
        servicios.append(s3)
        logger.info("OP 5 Exitosa: %s", s3.describir())
        print(" -> OK:", s3.describir())
    except ErrorSoftwareFJ as e:
        print(" -> Error:", e)

    # OP 6: Reserva exitosa con confirmación
    print("\n[OP 6] Creación y Confirmación de Reserva Exitosa...")
    try:
        r1 = Reserva(clientes[0], servicios[0], duracion_horas=4.0)
        total = r1.procesar_confirmacion(impuesto=19, descuento=10)
        reservas.append(r1)
        print(" -> OK:", r1.describir())
    except ErrorSoftwareFJ as e:
        print(" -> Error:", e)

    # OP 7: Intento de Reserva con duración 0 (Inválida)
    print("\n[OP 7] Intento de Reserva con duración 0 horas...")
    try:
        r2 = Reserva(clientes[0], servicios[1], duracion_horas=0)
    except ErrorSoftwareFJ as e:
        logger.warning("OP 7 Controlada: %s", e)
        print(" -> Error controlado:", e)

    # OP 8: Alquiler de equipo con seguro y confirmación
    print("\n[OP 8] Alquiler de Equipo de Cómputo...")
    try:
        s4 = AlquilerEquipo("Servidor Portátil Ubuntu", tarifa=35000.0, incluye_seguro=True)
        servicios.append(s4)
        r3 = Reserva(clientes[0], s4, duracion_horas=6.0)
        r3.procesar_confirmacion(impuesto=19, descuento=0)
        reservas.append(r3)
        print(" -> OK:", r3.describir())
    except ErrorSoftwareFJ as e:
        print(" -> Error:", e)

    # OP 9: Cancelación válida de reserva
    print("\n[OP 9] Cancelación de Reserva activa...")
    try:
        reservas[0].cancelar("Reprogramación solicitada por el cliente")
        print(" -> OK:", reservas[0].describir())
    except ErrorSoftwareFJ as e:
        print(" -> Error:", e)

    # OP 10: Intento de cancelar una reserva ya cancelada
    print("\n[OP 10] Intento de cancelar reserva ya cancelada...")
    try:
        reservas[0].cancelar("Intento duplicado de cancelación")
    except ErrorSoftwareFJ as e:
        logger.warning("OP 10 Controlada: %s", e)
        print(" -> Error controlado:", e)

    # ==========================================
    # OP 11: PRUEBAS DE DESCUENTO EN RESERVA DE SALAS
    # ==========================================

    print("\n[OP 11] Pruebas de descuento por tiempo en salas...")

    try:
        sala_prueba = ReservaSala(
            "Sala de Pruebas",
            tarifa=45000.0,
            capacidad_personas=15
        )

        # Prueba 1: Reserva de exactamente 5 horas.
        costo_5_horas = sala_prueba.calcular_costo(
            duracion=5,
            impuesto=0,
            descuento=0
        )

        # Prueba 2: Reserva superior a 5 horas.
        costo_6_horas = sala_prueba.calcular_costo(
            duracion=6,
            impuesto=0,
            descuento=0
        )

        esperado_5 = 225000.00
        esperado_6 = 256500.00

        print(" -> Reserva de 5 horas:")
        print(f"    Costo calculado: ${costo_5_horas:,.2f}")
        print(f"    Costo esperado:  ${esperado_5:,.2f}")

        print(" -> Reserva de 6 horas:")
        print(f"    Costo calculado: ${costo_6_horas:,.2f}")
        print(f"    Costo esperado:  ${esperado_6:,.2f}")

        assert costo_5_horas == esperado_5
        assert costo_6_horas == esperado_6

        print(" -> OK: Descuento por tiempo aplicado correctamente.")

        logger.info(
            "OP 11 Exitosa: Prueba de descuento en salas. "
            "5 horas: %s | 6 horas: %s",
            costo_5_horas,
            costo_6_horas
        )

    except Exception as e:
        logger.exception("OP 11 Error en pruebas de salas")
        print(" -> Error controlado:", e)


    # ==========================================
    # OP 12: PRUEBAS DE ALQUILER CON Y SIN SEGURO
    # ==========================================

    print("\n[OP 12] Pruebas de alquiler de equipos con y sin seguro...")

    try:
        equipo_con_seguro = AlquilerEquipo(
            "Computador Portátil",
            tarifa=35000.0,
            incluye_seguro=True
        )

        equipo_sin_seguro = AlquilerEquipo(
            "Computador Portátil",
            tarifa=35000.0,
            incluye_seguro=False
        )

        # Calcular el alquiler durante 6 horas.
        costo_con_seguro = equipo_con_seguro.calcular_costo(
            duracion=6,
            impuesto=19,
            descuento=0
        )

        costo_sin_seguro = equipo_sin_seguro.calcular_costo(
            duracion=6,
            impuesto=19,
            descuento=0
        )

        esperado_con_seguro = 264900.00
        esperado_sin_seguro = 249900.00

        print(" -> Alquiler con seguro:")
        print(f"    Costo calculado: ${costo_con_seguro:,.2f}")
        print(f"    Costo esperado:  ${esperado_con_seguro:,.2f}")

        print(" -> Alquiler sin seguro:")
        print(f"    Costo calculado: ${costo_sin_seguro:,.2f}")
        print(f"    Costo esperado:  ${esperado_sin_seguro:,.2f}")

        assert costo_con_seguro == esperado_con_seguro
        assert costo_sin_seguro == esperado_sin_seguro

        # Verificar que la diferencia corresponda al seguro.
        diferencia = costo_con_seguro - costo_sin_seguro

        assert diferencia == 15000.00

        print(f" -> Diferencia por seguro: ${diferencia:,.2f}")
        print(" -> OK: Recargo del seguro aplicado correctamente.")

        logger.info(
            "OP 12 Exitosa: Alquiler con seguro: %s | "
            "Sin seguro: %s | Diferencia: %s",
            costo_con_seguro,
            costo_sin_seguro,
            diferencia
        )

    except Exception as e:
        logger.exception("OP 12 Error en pruebas de alquiler")
        print(" -> Error controlado:", e)


    # ==========================================
    # OP 13: PRUEBAS DE DURACIÓN MÍNIMA DE ASESORÍAS
    # ==========================================

    print("\n[OP 13] Pruebas de duración mínima de asesorías...")

    try:
        asesoria_prueba = AsesoriaEspecializada(
            "Consultoría en Seguridad Informática",
            tarifa=80000.0,
            especialista="Ing. Juan Arango"
        )

        # Prueba 1: Duración inferior al mínimo permitido.
        try:
            asesoria_prueba.calcular_costo(
                duracion=0.5,
                impuesto=0,
                descuento=0
            )

            print(" -> ERROR: Se aceptó una asesoría de 0.5 horas.")

        except DatosInvalidosError as e:
            print(" -> OK: Asesoría de 0.5 horas rechazada.")
            print("    Motivo:", e)

            logger.info(
                "OP 13: Prueba de rechazo de asesoría inferior a una hora."
            )

        # Prueba 2: Duración mínima de una hora.
        costo_1_hora = asesoria_prueba.calcular_costo(
            duracion=1,
            impuesto=0,
            descuento=0
        )

        # Prueba 3: Duración de dos horas.
        costo_2_horas = asesoria_prueba.calcular_costo(
            duracion=2,
            impuesto=0,
            descuento=0
        )

        assert costo_1_hora == 80000.00
        assert costo_2_horas == 160000.00

        print(" -> Asesoría de 1 hora aceptada:")
        print(f"    Costo: ${costo_1_hora:,.2f}")

        print(" -> Asesoría de 2 horas aceptada:")
        print(f"    Costo: ${costo_2_horas:,.2f}")

        print(" -> OK: Duración mínima de asesorías validada.")

        logger.info(
            "OP 13 Exitosa: Asesoría de 1 hora: %s | "
            "Asesoría de 2 horas: %s",
            costo_1_hora,
            costo_2_horas
        )

    except Exception as e:
        logger.exception("OP 13 Error en pruebas de asesorías")
        print(" -> Error controlado:", e)

      # Resumen Final  
    print("\n==============================================================")
    print("       SOFTWARE FJ - RESULTADOS DE SIMULACIÓN                  ")
    print("==============================================================")
    print("  Operaciones iniciales: 10")
    print("  Pruebas adicionales:    3")
    print("  Total de operaciones:  13")
    print("--------------------------------------------------------------")
    print("  Pruebas de descuento en salas:       REALIZADAS")
    print("  Pruebas de alquiler con seguro:      REALIZADAS")
    print("  Pruebas de alquiler sin seguro:      REALIZADAS")
    print("  Pruebas de duración de asesorías:    REALIZADAS")
    print("--------------------------------------------------------------")
    print("  Aplicación finalizada.")
    print("  Consulte el archivo software_fj.log")
    print("==============================================================\n")

    logger.info("=== FIN DE LA SIMULACIÓN DE 13 OPERACIONES ===")


if __name__ == "__main__":
    ejecutar_simulacion()
