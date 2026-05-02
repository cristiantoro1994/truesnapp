# Pantalla para crear un nuevo proyecto.
# El usuario introduce el nombre del proyecto, y al confirmar:
#   - Se crea la carpeta física en datos/imagenes/[nombre]/
#   - Se añade el proyecto a la lista de st.session_state.proyectos
#   - Se redirige a la galería del proyecto recién creado

import streamlit as st
import uuid
import time

# Importamos la función auxiliar que crea la carpeta del proyecto
from utils.helpers import crear_carpeta_proyecto


def mostrar():
    """Muestra la pantalla de creación de un nuevo proyecto."""

    # Botón de volver (arriba a la izquierda)
    
    if st.button("← Volver al dashboard", key="volver_nuevo_proyecto"):
        st.session_state.pagina = "dashboard"
        st.rerun()

    
    # Título de la pantalla
    
    st.markdown("## ➕ Crear nuevo proyecto")

    # Texto explicativo breve
    st.markdown(
        "Dale un nombre a tu propiedad. Por ejemplo: "
        "*Apartamento Centro, Casa de Playa, Loft Madrid.*"
    )

    st.write("")  # Espacio en blanco
    
    # Formulario: nombre del proyecto
    
    nombre = st.text_input(
        label="Nombre del proyecto",
        placeholder="Ej: Apartamento Centro",
        key="input_nombre_proyecto",
    )

    st.write("")  # Espacio antes del botón

   
    # Botón principal: Crear proyecto

    if st.button("Crear proyecto", key="boton_crear_proyecto"):
        crear_proyecto_nuevo(nombre)


def crear_proyecto_nuevo(nombre):
    """
    Lógica para crear un proyecto nuevo:
    valida → crea carpeta → guarda en estado → redirige a galería.
    """

    # ---- VALIDACIÓN 1: el nombre no puede estar vacío ----
    if nombre.strip() == "":
        st.error("Por favor, escribe un nombre para tu proyecto.")
        return

    # ---- VALIDACIÓN 2: no puede haber dos proyectos con el mismo nombre ----
    nombres_existentes = [
        p["nombre"].lower() for p in st.session_state.get("proyectos", [])
    ]
    if nombre.strip().lower() in nombres_existentes:
        st.error(
            f"Ya tienes un proyecto llamado **{nombre}**. "
            "Elige otro nombre."
        )
        return

    # ---- CREAR EL DICCIONARIO DEL PROYECTO ----
    nuevo_proyecto = {
        "id": uuid.uuid4().hex[:8],   # ID único de 8 caracteres
        "nombre": nombre.strip(),
        "fotos_totales": 0,
        "fotos_optimizadas": 0,
        "fotos_certificadas": 0,
        "fecha_creacion": time.strftime("%Y-%m-%d"),
    }

    # ---- CREAR LA CARPETA FÍSICA EN EL DISCO ----
    # La carpeta se nombra con el ID único del proyecto, no con
    # el nombre, para evitar colisiones cuando dos proyectos
    # tengan el mismo nombre.
    crear_carpeta_proyecto(nuevo_proyecto)

    # Si la lista no existe todavía, la inicializamos vacía
    if "proyectos" not in st.session_state:
        st.session_state.proyectos = []

    st.session_state.proyectos.append(nuevo_proyecto)

    # ---- REDIRIGIR A LA GALERÍA DEL NUEVO PROYECTO ----
    st.session_state.proyecto_actual = nuevo_proyecto["id"]
    st.session_state.pagina = "galeria"

    # Mensaje de éxito (se ve un instante antes de redirigir)
    st.success(f"✅ Proyecto **{nombre}** creado correctamente.")
    st.rerun()