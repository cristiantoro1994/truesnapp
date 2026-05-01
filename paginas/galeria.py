# Galería de imágenes de un proyecto.
# El usuario puede:
#   - Ver todas las fotos del proyecto en una rejilla
#   - Subir nuevas fotos (desde móvil o escritorio)
#   - Eliminar fotos con doble confirmación

# Las fotos se guardan en: datos/imagenes/[nombre_proyecto]/


import streamlit as st

# Funciones auxiliares que creamos en el Paso 1
from utils.helpers import guardar_imagen, listar_imagenes, eliminar_imagen


def mostrar():
    """Muestra la galería de imágenes del proyecto seleccionado."""

    
    # Botón de volver (siempre arriba)
   
    if st.button("← Volver al dashboard", key="volver_galeria"):
        # Limpiamos cualquier confirmación pendiente al salir
        st.session_state.foto_a_borrar = None
        st.session_state.pagina = "dashboard"
        st.rerun()

    
    # Buscar el proyecto actual en la lista
   
    proyecto = obtener_proyecto_actual()

    if proyecto is None:
        st.warning("No se encontró el proyecto. Volviendo al dashboard...")
        st.session_state.pagina = "dashboard"
        st.rerun()
        return

   
    # Cabecera: nombre del proyecto
  
    st.markdown(f"## 🏠 {proyecto['nombre']}")

   
    # Zona de subida de fotos
   
    st.markdown("### 📤 Subir fotos")

    archivos_subidos = st.file_uploader(
        label="Arrastra tus fotos aquí o pulsa para seleccionarlas",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=f"uploader_{proyecto['id']}",
    )

    if archivos_subidos:
        guardar_archivos_subidos(archivos_subidos, proyecto["nombre"])

    st.markdown("---")

   
    # Galería: mostrar las fotos del proyecto
    
    imagenes = listar_imagenes(proyecto["nombre"])
    total = len(imagenes)

    st.markdown(f"### 📷 Galería ({total} fotos)")

    if total == 0:
        st.info(
            "Aún no has subido ninguna foto a este proyecto. "
            "Usa el botón de arriba para añadir las primeras."
        )
    else:
        mostrar_rejilla_imagenes(imagenes)


def obtener_proyecto_actual():
    """Busca en la lista el proyecto seleccionado."""
    proyecto_id = st.session_state.get("proyecto_actual", None)

    if proyecto_id is None:
        return None

    for p in st.session_state.get("proyectos", []):
        if p["id"] == proyecto_id:
            return p

    return None


def guardar_archivos_subidos(archivos_subidos, nombre_proyecto):
    """Guarda en el disco las fotos subidas por el usuario."""
    cantidad = 0
    for archivo in archivos_subidos:
        try:
            guardar_imagen(archivo, nombre_proyecto)
            cantidad += 1
        except Exception as error:
            st.error(f"Error al guardar **{archivo.name}**: {error}")

    if cantidad > 0:
        st.success(f"✅ {cantidad} foto(s) guardada(s) correctamente.")
        # Limpiamos cualquier confirmación pendiente al subir nuevas fotos
        st.session_state.foto_a_borrar = None
        st.rerun()


def mostrar_rejilla_imagenes(imagenes):
    """Muestra las imágenes en una rejilla de 3 columnas, con botón borrar."""
    columnas_por_fila = 3

    for i in range(0, len(imagenes), columnas_por_fila):
        cols = st.columns(columnas_por_fila)

        for j in range(columnas_por_fila):
            indice = i + j
            if indice < len(imagenes):
                ruta_imagen = imagenes[indice]
                with cols[j]:
                    mostrar_miniatura_con_borrar(ruta_imagen)


def mostrar_miniatura_con_borrar(ruta_imagen):
    """
    Muestra una miniatura de la imagen + botón para borrar.
    Implementa doble confirmación para evitar borrados accidentales.
    """
    # Mostramos la imagen
    st.image(str(ruta_imagen), use_container_width=True)

    # Nombre limpio (sin el ID único del inicio)
    nombre_limpio = quitar_id_del_nombre(ruta_imagen.name)
    st.markdown(
        f"<p style='font-size: 0.75rem; color: #A0A6AC; "
        f"text-align: center; margin-top: -0.5rem; margin-bottom: 0.3rem;'>"
        f"{nombre_limpio}</p>",
        unsafe_allow_html=True,
    )

    # Identificador único de esta foto (para los botones)
    id_foto = str(ruta_imagen)

    # Variable de estado: ¿qué foto está esperando confirmación?
    foto_pendiente = st.session_state.get("foto_a_borrar", None)

    # Si esta foto SÍ tiene confirmación pendiente
    if foto_pendiente == id_foto:
        # Mostramos aviso amarillo + botón de confirmación
        st.warning("¿Seguro? Pulsa otra vez para borrar.")
        if st.button("🗑️ Confirmar borrado", key=f"confirmar_{id_foto}"):
            # Eliminamos la foto del disco
            eliminar_imagen(ruta_imagen)
            # Limpiamos el estado
            st.session_state.foto_a_borrar = None
            st.rerun()
    else:
        # Botón normal de borrar (primer paso de la confirmación)
        if st.button("🗑️ Borrar", key=f"borrar_{id_foto}"):
            # Marcamos esta foto como "pendiente de confirmar"
            st.session_state.foto_a_borrar = id_foto
            st.rerun()


def quitar_id_del_nombre(nombre_archivo):
    """Quita el ID único del inicio del nombre del archivo."""
    if "_" in nombre_archivo:
        partes = nombre_archivo.split("_", 1)
        if len(partes) == 2:
            return partes[1]
    return nombre_archivo