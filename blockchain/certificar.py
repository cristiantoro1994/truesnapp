
# Esta es la base de la Fase 5 de TrueSnapp.
# Se compone de tres etapas:
#   1. Generar el hash SHA-256 de la imagen optimizada (este archivo).
#   2. Registrar el hash en blockchain (vía OpenTimestamps).
#   3. Verificar el certificado.
# IMPORTANTE: el hash NUNCA se calcula sobre la imagen original.
# Se calcula sobre la versión OPTIMIZADA, que es la que el usuario
# va a publicar en sus anuncios. Así certificamos la versión final
# con todas las mejoras aplicadas.


import hashlib
from pathlib import Path

# Constantes


# Tamaño del bloque para leer archivos grandes sin saturar la memoria
# 64 KB es un buen equilibrio: rápido y sin consumir mucha RAM
TAMANO_BLOQUE = 64 * 1024  # 65536 bytes

# 1. Calcular el hash SHA-256 de un archivo


def calcular_hash(ruta_archivo):
    """
    Calcula el hash SHA-256 de un archivo del disco.

    El hash es una "huella digital" única e irreversible:
      - Si cambia 1 solo byte del archivo, el hash cambia por completo.
      - Dos archivos idénticos siempre tienen el mismo hash.
      - Dos archivos distintos siempre tienen hashes distintos.

    Lectura por bloques: leemos el archivo en trozos de 64 KB para
    poder procesar imágenes grandes (10+ MB) sin saturar la memoria.

    Parámetros:
      ruta_archivo: ruta del archivo a procesar (Path o string).

    Devuelve:
      - String de 64 caracteres hexadecimales con el hash.
      - None si el archivo no existe o no se puede leer.

    Ejemplo:
      hash = calcular_hash("foto.jpg")
      → "a3f1c8d2e9b4567890abcdef1234567890abcdef1234567890abcdef12345678"
    """
    ruta = Path(ruta_archivo)

    # Si el archivo no existe, abandonamos
    if not ruta.exists():
        return None

    if not ruta.is_file():
        return None

    try:
        # Creamos un objeto hash SHA-256 vacío
        hasher = hashlib.sha256()

        # Abrimos el archivo en modo binario ("rb")
        # Lo leemos por bloques para soportar archivos grandes
        with open(ruta, "rb") as f:
            while True:
                bloque = f.read(TAMANO_BLOQUE)
                # Cuando read() devuelve bytes vacíos, hemos llegado al final
                if not bloque:
                    break
                # Vamos "alimentando" el hasher con cada bloque
                hasher.update(bloque)

        # Devolvemos el hash en formato hexadecimal (64 caracteres)
        return hasher.hexdigest()

    except OSError:
        # Cualquier error de lectura (permisos, archivo bloqueado, etc.)
        return None


# 2. Verificar que dos archivos tienen el mismo hash


def hashes_coinciden(ruta_archivo, hash_esperado):
    """
    Comprueba si un archivo tiene un hash determinado.

    Útil para verificar que una foto NO ha sido modificada desde
    su certificación: se calcula el hash actual y se compara con
    el hash que se registró en blockchain.

    Parámetros:
      ruta_archivo: ruta del archivo a verificar.
      hash_esperado: hash de 64 caracteres a comparar.

    Devuelve:
      True si los hashes coinciden, False si no (o si hay error).
    """
    hash_actual = calcular_hash(ruta_archivo)

    if hash_actual is None:
        return False

    # Comparación insensible a mayúsculas (los hashes pueden venir
    # en cualquier formato)
    return hash_actual.lower() == hash_esperado.lower()


# 3. Hash corto para mostrar (versión humana)


def hash_corto(hash_completo, caracteres=12):
    """
    Devuelve una versión corta del hash para mostrar en pantalla.

    Un hash de 64 caracteres es difícil de leer.
    Mostramos los primeros 6 + "..." + últimos 6, como se hace en
    los exploradores de blockchain (estilo Etherscan, blockchain.com).

    Parámetros:
      hash_completo: hash de 64 caracteres.
      caracteres: cuántos caracteres mostrar al inicio y al final
                  (por defecto 6 al inicio + 6 al final = 12 visibles).

    Devuelve:
      String con el hash abreviado.

    Ejemplo:
      hash_corto("a3f1c8d2e9b4...12345678")
      → "a3f1c8...345678"
    """
    if hash_completo is None or len(hash_completo) < caracteres * 2:
        return hash_completo

    mitad = caracteres // 2
    return f"{hash_completo[:mitad]}...{hash_completo[-mitad:]}"