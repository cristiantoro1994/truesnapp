# =====================================================================
# blockchain/registrar_blockchain.py
# =====================================================================
# Registro de hashes SHA-256 en blockchain a través de OpenTimestamps.
#
# Llamamos directamente al servidor público de OpenTimestamps por
# HTTP, en lugar de depender de la librería local "opentimestamps-client"
# (que tiene problemas de compatibilidad con Python 3.14 en Windows).
#
# Es la forma profesional y portable de hacerlo, equivalente a como
# usamos Replicate en la Fase 4: una llamada HTTP a un servicio externo.
# =====================================================================

import hashlib
import requests
from pathlib import Path


# ---------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------

# Servidor público de OpenTimestamps (calendario)
# https://github.com/opentimestamps/opentimestamps-server
SERVIDOR_OTS = "https://a.pool.opentimestamps.org"

# Tiempo máximo de espera (segundos) al llamar al servidor
TIEMPO_MAXIMO_ESPERA = 30


# ---------------------------------------------------------------------
# 1. Función principal: registrar un hash en blockchain
# ---------------------------------------------------------------------

def registrar_hash_en_blockchain(hash_sha256):
    """
    Registra un hash SHA-256 en la blockchain de Bitcoin a través
    del servidor público de OpenTimestamps.

    El servidor agrupa miles de hashes en un solo bloque y lo registra
    en Bitcoin. Devuelve un comprobante criptográfico (.ots) que prueba
    la existencia del hash a partir de ese momento.

    Parámetros:
      hash_sha256: hash SHA-256 de 64 caracteres en formato hexadecimal.

    Devuelve:
      - bytes con el contenido del comprobante .ots si todo salió bien.
      - None si hubo cualquier error.
    """

    # Validamos el formato del hash
    if not _es_hash_valido(hash_sha256):
        return None

    # Convertimos el hash hexadecimal a bytes (32 bytes)
    try:
        bytes_del_hash = bytes.fromhex(hash_sha256)
    except ValueError:
        return None

    # ----- Llamamos al endpoint de "digest" del servidor OTS -----
    # El servidor recibe los 32 bytes del hash en el cuerpo del POST
    url = f"{SERVIDOR_OTS}/digest"

    try:
        respuesta = requests.post(
            url,
            data=bytes_del_hash,
            headers={"Content-Type": "application/octet-stream"},
            timeout=TIEMPO_MAXIMO_ESPERA,
        )

        if respuesta.status_code != 200:
            return None

        # ----- Construimos el comprobante .ots completo -----
        # El servidor devuelve la "rama" del árbol Merkle del calendario.
        # Para construir el archivo .ots completo, necesitamos:
        #   - Cabecera mágica de OTS
        #   - El hash original
        #   - La operación SHA-256 marker
        #   - La rama devuelta por el servidor
        comprobante = _construir_archivo_ots(bytes_del_hash, respuesta.content)

        return comprobante

    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------
# 2. Verificación auxiliar: ¿está disponible el servidor?
# ---------------------------------------------------------------------

def opentimestamps_disponible():
    """
    Comprueba si el servidor público de OpenTimestamps está accesible.

    Hacemos una petición ligera al servidor para ver si responde.
    """
    try:
        respuesta = requests.get(
            f"{SERVIDOR_OTS}/",
            timeout=10,
        )
        # Cualquier respuesta del servidor (incluso 404) significa
        # que el servidor está vivo
        return respuesta.status_code < 500
    except Exception:
        return False


# ---------------------------------------------------------------------
# 3. Construcción del archivo .ots
# ---------------------------------------------------------------------

def _construir_archivo_ots(hash_bytes, rama_calendario):
    """
    Construye el contenido binario del archivo .ots a partir del hash
    y la rama devuelta por el servidor de OpenTimestamps.

    Formato simplificado del archivo .ots:
      - Cabecera mágica (magic header)
      - Versión del formato (0x01)
      - Algoritmo de hash usado: SHA-256 (0x08)
      - Hash original (32 bytes)
      - Rama devuelta por el calendario
    """
    # Cabecera mágica oficial de OpenTimestamps
    # Indica que el archivo es un comprobante .ots versión 1
    cabecera = bytes([
        0x00, 0x4f, 0x70, 0x65, 0x6e, 0x54, 0x69, 0x6d,
        0x65, 0x73, 0x74, 0x61, 0x6d, 0x70, 0x73, 0x00,
        0x00, 0x50, 0x72, 0x6f, 0x6f, 0x66, 0x00, 0xbf,
        0x89, 0xe2, 0xe8, 0x84, 0xe8, 0x92, 0x94,
    ])

    # Versión del formato (1)
    version = bytes([0x01])

    # Algoritmo de hash usado: 0x08 = SHA-256
    algoritmo = bytes([0x08])

    # Construimos el archivo completo
    archivo_ots = (
        cabecera
        + version
        + algoritmo
        + hash_bytes
        + rama_calendario
    )

    return archivo_ots


# ---------------------------------------------------------------------
# 4. Función privada: validar formato del hash
# ---------------------------------------------------------------------

def _es_hash_valido(hash_str):
    """
    Comprueba que un string tenga formato válido de hash SHA-256:
      - Es una cadena de texto.
      - Tiene exactamente 64 caracteres.
      - Solo contiene caracteres hexadecimales (0-9, a-f, A-F).
    """
    if not isinstance(hash_str, str):
        return False

    if len(hash_str) != 64:
        return False

    try:
        int(hash_str, 16)
        return True
    except ValueError:
        return False