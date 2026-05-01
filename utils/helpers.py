# =====================================================================
# utils/helpers.py
# =====================================================================
# Funciones auxiliares reutilizables en toda la app.
#
# Contiene:
#   1. Inicialización del estado de sesión
#   2. Cambiar de pantalla
#   3. Router (decide qué pantalla mostrar)
#   4. Funciones para gestión de archivos de imágenes
# =====================================================================

import streamlit as st
from pathlib import Path  # Para trabajar con rutas de archivos
import uuid               # Para generar identificadores únicos


# ---------------------------------------------------------------------
# 1. Inicialización del estado de sesión
# ---------------------------------------------------------------------
def inicializar_estado():
    """
    Crea las variables básicas de st.session_state si no existen.
    Se llama UNA sola vez al inicio de app.py.

    Variables que prepara:
      - pagina: nombre de la pantalla actual
      - usuario_logueado: True/False según si el usuario entró
      - email_usuario: email del usuario logueado
      - proyecto_actual: ID del proyecto que el usuario está viendo
      - foto_a_borrar: foto que está esperando confirmación de borrado
      - proyecto_a_borrar: proyecto que está esperando confirmación
    """

    # Pantalla actual. Empezamos en "login".
    if "pagina" not in st.session_state:
        st.session_state.pagina = "login"

    # Estado del usuario
    if "usuario_logueado" not in st.session_state:
        st.session_state.usuario_logueado = False

    if "email_usuario" not in st.session_state:
        st.session_state.email_usuario = ""

    # Proyecto que el usuario está viendo (None = ninguno)
    if "proyecto_actual" not in st.session_state:
        st.session_state.proyecto_actual = None

    # Confirmaciones pendientes (Fase 3)
    if "foto_a_borrar" not in st.session_state:
        st.session_state.foto_a_borrar = None

    if "proyecto_a_borrar" not in st.session_state:
        st.session_state.proyecto_a_borrar = None


# ---------------------------------------------------------------------
# 2. Cambiar de pantalla
# ---------------------------------------------------------------------
def cambiar_pagina(nombre_pagina):
    """
    Cambia la pantalla activa de la app.

    Parámetros:
      nombre_pagina: texto con el nombre de la pantalla a mostrar.
                     Valores válidos: "login", "dashboard", "galeria",
                     "certificado", "descargas", "nuevo_proyecto".

    Uso desde otro archivo:
      from utils.helpers import cambiar_pagina
      cambiar_pagina("dashboard")
    """
    st.session_state.pagina = nombre_pagina
    st.rerun()


# ---------------------------------------------------------------------
# 3. Router: decide qué pantalla mostrar
# ---------------------------------------------------------------------
def mostrar_pagina_actual():
    """
    Lee st.session_state.pagina y muestra la pantalla correspondiente.
    Esta función se llama desde app.py.

    Funciona como un "portero": recibe el nombre de la pantalla y
    llama a la función mostrar() del archivo correcto.
    """

    # Importamos las pantallas aquí dentro (no arriba) para evitar
    # importaciones circulares.
    from paginas import (
        login,
        dashboard,
        galeria,
        certificado,
        descargas,
        nuevo_proyecto,
    )

    # Protección de acceso: si el usuario NO está logueado,
    # solo puede ver la pantalla de login.
    if not st.session_state.usuario_logueado:
        login.mostrar()
        return

    # Si está logueado, mostramos la pantalla seleccionada
    pagina = st.session_state.pagina

    if pagina == "login":
        login.mostrar()
    elif pagina == "dashboard":
        dashboard.mostrar()
    elif pagina == "galeria":
        galeria.mostrar()
    elif pagina == "certificado":
        certificado.mostrar()
    elif pagina == "descargas":
        descargas.mostrar()
    elif pagina == "nuevo_proyecto":
        nuevo_proyecto.mostrar()
    else:
        # Si llega un nombre desconocido, volvemos al dashboard
        st.warning(f"Pantalla desconocida: '{pagina}'. Volviendo al dashboard.")
        st.session_state.pagina = "dashboard"
        dashboard.mostrar()


# =====================================================================
# 4. FUNCIONES PARA GESTIÓN DE ARCHIVOS DE IMÁGENES
# =====================================================================
# Estas funciones manejan la lectura, escritura y borrado de fotos
# en el disco. Las fotos se guardan en: datos/imagenes/[proyecto]/
# =====================================================================


# Carpeta raíz donde se guardan TODAS las imágenes de la app
CARPETA_RAIZ_IMAGENES = Path("datos/imagenes")

# Extensiones de imagen permitidas en TrueSnapp
EXTENSIONES_PERMITIDAS = ["jpg", "jpeg", "png"]


def carpeta_proyecto(nombre_proyecto):
    """
    Devuelve la ruta de la carpeta de un proyecto.
    No crea la carpeta, solo calcula su ruta.

    Ejemplo:
      carpeta_proyecto("Casa Playa") → datos/imagenes/Casa_Playa
    """
    # Reemplazamos espacios por guiones bajos para evitar problemas
    nombre_limpio = nombre_proyecto.strip().replace(" ", "_")
    return CARPETA_RAIZ_IMAGENES / nombre_limpio


def crear_carpeta_proyecto(nombre_proyecto):
    """
    Crea físicamente la carpeta de un proyecto en el disco.
    Si ya existe, no hace nada (no lanza error).
    """
    ruta = carpeta_proyecto(nombre_proyecto)
    # parents=True: crea las carpetas padre si no existen
    # exist_ok=True: no protesta si ya existe
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta


def guardar_imagen(archivo_subido, nombre_proyecto):
    """
    Guarda una imagen subida por el usuario en la carpeta del proyecto.

    Parámetros:
      archivo_subido: el archivo que devuelve st.file_uploader
      nombre_proyecto: nombre del proyecto al que pertenece la foto

    Devuelve la ruta donde se guardó la imagen.
    """
    # Aseguramos que la carpeta del proyecto existe
    carpeta = crear_carpeta_proyecto(nombre_proyecto)

    # Generamos un nombre único para evitar sobreescribir fotos
    # Ejemplo: "a1b2c3d4_foto.jpg"
    id_unico = uuid.uuid4().hex[:8]  # 8 caracteres aleatorios
    nombre_archivo = f"{id_unico}_{archivo_subido.name}"

    # Ruta completa donde guardaremos la imagen
    ruta_completa = carpeta / nombre_archivo

    # Escribimos el contenido del archivo subido al disco
    with open(ruta_completa, "wb") as f:
        f.write(archivo_subido.getbuffer())

    return ruta_completa


def listar_imagenes(nombre_proyecto):
    """
    Devuelve una lista con las rutas de todas las imágenes
    de un proyecto, ordenadas por fecha (más recientes primero).
    """
    carpeta = carpeta_proyecto(nombre_proyecto)

    # Si la carpeta no existe, devolvemos lista vacía
    if not carpeta.exists():
        return []

    # Buscamos archivos con las extensiones permitidas
    imagenes = []
    for extension in EXTENSIONES_PERMITIDAS:
        # glob busca archivos que coincidan con un patrón
        imagenes.extend(carpeta.glob(f"*.{extension}"))
        imagenes.extend(carpeta.glob(f"*.{extension.upper()}"))

    # Ordenamos por fecha de modificación (las más recientes primero)
    imagenes.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    return imagenes


def eliminar_imagen(ruta_imagen):
    """
    Elimina una imagen del disco.
    Recibe la ruta completa de la imagen a borrar.
    """
    ruta = Path(ruta_imagen)
    if ruta.exists():
        ruta.unlink()  # unlink() es como "borrar archivo"
        return True
    return False