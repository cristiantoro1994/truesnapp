# procesamiento/optimizar_ia.py
# Mejora AVANZADA de imágenes con inteligencia artificial real.
# Esta es la CAPA 2 del sistema híbrido de optimización de TrueSnapp.
# Usa el modelo Real-ESRGAN alojado en Replicate (servidores externos
# con GPU profesional) para hacer super-resolución de las imágenes.
#
# IMPORTANTE: si la API falla o no hay créditos, la función devuelve
# None y la app sigue funcionando con el resultado de OpenCV (Capa 1).


import base64
import io
import streamlit as st
import requests
import cv2
import numpy as np
from pathlib import Path

# Librería oficial de Replicate
import replicate


# Configuración del modelo

# Modelo de Replicate que vamos a usar.
# nightmareai/real-esrgan es el modelo estándar y más probado.
MODELO_REPLICATE = (
    "nightmareai/real-esrgan:"
    "f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa"
)

# Tiempo máximo de espera (segundos) antes de cancelar
TIEMPO_MAXIMO_ESPERA = 60

# Factor de escala (cuánto agranda la imagen)
# Real-ESRGAN soporta 2, 3 o 4. Usamos 2 para mantener tamaño razonable.
FACTOR_ESCALA = 2


# 1. Comprobar si la clave API está configurada

def hay_clave_replicate():
    """
    Comprueba si el token de Replicate está configurado correctamente.

    Devuelve True si hay token válido, False si no.
    Si no hay token, la app debe usar solo OpenCV (capa 1).
    """
    try:
        # Intentamos leer el token desde st.secrets
        token = st.secrets.get("REPLICATE_API_TOKEN", "")

        # Comprobamos que no esté vacío y que tenga el formato correcto
        if not token or not token.startswith("r8_"):
            return False

        return True

    except Exception:
        # Si hay cualquier error leyendo los secrets, asumimos que no hay token
        return False


# 2. Función principal: optimizar una imagen con IA

def optimizar_con_ia(ruta_imagen):
    """
    Envía una imagen a Replicate (Real-ESRGAN) y devuelve la versión
    mejorada por IA.

    Parámetros:
      ruta_imagen: ruta de la imagen original (Path o string).

    Devuelve:
      - matriz NumPy con la imagen mejorada (formato BGR de OpenCV)
        si todo salió bien.
      - None si hubo cualquier error (sin internet, sin créditos,
        error del servidor, timeout, etc.).
    """

    # Comprobamos que tenemos token configurado
    if not hay_clave_replicate():
        return None

    try:
        # Configuramos el cliente de Replicate
        import os
        os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

        # Convertimos la imagen a base64 (data URI)
        ruta = Path(ruta_imagen)
        with open(ruta, "rb") as f:
            datos_imagen = f.read()

        # Detectamos el tipo MIME según la extensión
        extension = ruta.suffix.lower().lstrip(".")
        if extension in ("jpg", "jpeg"):
            tipo_mime = "image/jpeg"
        elif extension == "png":
            tipo_mime = "image/png"
        else:
            return None

        imagen_base64 = base64.b64encode(datos_imagen).decode("utf-8")
        data_uri = f"data:{tipo_mime};base64,{imagen_base64}"

        # Llamamos al modelo de Replicate
        url_resultado = replicate.run(
            MODELO_REPLICATE,
            input={
                "image": data_uri,
                "scale": FACTOR_ESCALA,
                "face_enhance": False,
            },
        )

        # Descargamos la imagen mejorada
        if hasattr(url_resultado, "read"):
            datos_imagen_mejorada = url_resultado.read()
        else:
            url = str(url_resultado)
            respuesta = requests.get(url, timeout=30)
            if respuesta.status_code != 200:
                return None
            datos_imagen_mejorada = respuesta.content

        # Convertimos los bytes a matriz OpenCV
        array_bytes = np.frombuffer(datos_imagen_mejorada, dtype=np.uint8)
        imagen_mejorada = cv2.imdecode(array_bytes, cv2.IMREAD_COLOR)

        if imagen_mejorada is None:
            return None

        return imagen_mejorada

    except Exception:
        # Cualquier fallo (red, créditos, formato, timeout, etc.)
        # se traga aquí. La función devuelve None y la app sigue
        # funcionando con el resultado de OpenCV.
        return None

    except Exception as error:
        # MODO DEPURACIÓN ACTIVO
        # Mostramos el error en pantalla para diagnosticar
        st.error(f"🐛 ERROR EN IA: {type(error).__name__}: {error}")
        import traceback
        st.code(traceback.format_exc(), language="python")
        return None