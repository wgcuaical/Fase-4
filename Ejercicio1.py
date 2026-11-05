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
