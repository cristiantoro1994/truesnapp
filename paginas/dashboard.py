# Panel principal del usuario (corazón de TrueSnapp).
# Desde aquí el usuario:
#   - Ve sus proyectos activos 
#   - Crea nuevos proyectos
#   - Abre la galería de un proyecto
#   - Elimina proyectos (con doble confirmación)
#   - Cierra sesión


import streamlit as st
import shutil  # Para borrar carpetas con su contenido

# Funciones auxiliares
from utils.helpers import (
    listar_imagenes,
    carpeta_proyecto,
    existe_version_optimizada,
    existe_certificado,
)

def mostrar():
    """Muestra el dashboard principal con los proyectos del usuario."""

    # Inicializar la lista de proyectos VACÍA si todavía no existe
   
    if "proyectos" not in st.session_state:
        st.session_state.proyectos = []

    # Cabecera: saludo + botón de cerrar sesión
  
    columna_saludo, columna_salir = st.columns([3, 1])

    with columna_saludo:
        email = st.session_state.get("email_usuario", "Usuario")
        nombre_corto = email.split("@")[0] if "@" in email else email
        st.markdown(f"### 👋 Hola, **{nombre_corto}**")

    with columna_salir:
        if st.button("Salir", key="boton_salir"):
            # Limpiamos cualquier confirmación pendiente al cerrar sesión
            st.session_state.proyecto_a_borrar = None
            st.session_state.usuario_logueado = False
            st.session_state.email_usuario = ""
            st.session_state.pagina = "login"
            st.rerun()

    st.markdown("---")

   
    # Título de la sección
   
    st.markdown("## 📂 Mis proyectos")

    
    # Botón principal: crear nuevo proyecto
   
    if st.button("➕ Nuevo proyecto", key="boton_nuevo_proyecto"):
        st.session_state.proyecto_a_borrar = None  # cancela confirmaciones
        st.session_state.pagina = "nuevo_proyecto"
        st.rerun()

    st.write("")  # Espacio antes de las tarjetas

    # Lista de tarjetas de proyectos
   
    if len(st.session_state.proyectos) == 0:
        st.info(
            "Aún no tienes proyectos. Pulsa **➕ Nuevo proyecto** "
            "para empezar."
        )
    else:
        for proyecto in st.session_state.proyectos:
            mostrar_tarjeta_proyecto(proyecto)


def mostrar_tarjeta_proyecto(proyecto):
    """
    Dibuja una tarjeta visual para un proyecto.
    Si está pendiente de confirmación, muestra el modo borrado.
    """
    # ¿Esta tarjeta está esperando confirmación de borrado?
    proyecto_pendiente = st.session_state.get("proyecto_a_borrar", None)

    if proyecto_pendiente == proyecto["id"]:
        # Modo confirmación
        mostrar_tarjeta_modo_borrar(proyecto)
    else:
        # Modo normal
        mostrar_tarjeta_modo_normal(proyecto)


def mostrar_tarjeta_modo_normal(proyecto):
    """Tarjeta normal con botones Abrir y 🗑️."""

    # Calcular contadores reales leyendo el disco
    imagenes = listar_imagenes(proyecto)
    total_fotos = len(imagenes)

    # Contar cuántas de esas fotos tienen versión optimizada
    # Contar cuántas de esas fotos tienen versión optimizada
    fotos_optimizadas = sum(
        1 for img in imagenes if existe_version_optimizada(img, proyecto)
    )

    # Contar cuántas de esas fotos tienen certificado blockchain (Fase 5)
    fotos_certificadas = sum(
        1 for img in imagenes if existe_certificado(img, proyecto)
    )

    with st.container(border=True):
        # 3 columnas: info | Abrir | 🗑️
        col_info, col_abrir, col_borrar = st.columns([4, 1.2, 0.8])

        with col_info:
            st.markdown(f"### 🏠 {proyecto['nombre']}")
            estado = (
                f"📷 {total_fotos} fotos &nbsp;·&nbsp; "
                f"✨ {fotos_optimizadas} optimizadas &nbsp;·&nbsp; "
                f"🔐 {fotos_certificadas} certificadas"
            )
            st.markdown(
                f"<p style='color: #7F8C8D; font-size: 0.95rem;'>{estado}</p>",
                unsafe_allow_html=True,
            )

        with col_abrir:
            st.write("")  # Espacio para alinear con el título
            if st.button("Abrir", key=f"abrir_{proyecto['id']}"):
                st.session_state.proyecto_actual = proyecto["id"]
                st.session_state.pagina = "galeria"
                st.rerun()

        with col_borrar:
            st.write("")
            if st.button("🗑️", key=f"borrar_{proyecto['id']}"):
                # Marcamos este proyecto como pendiente de confirmar
                st.session_state.proyecto_a_borrar = proyecto["id"]
                st.rerun()


def mostrar_tarjeta_modo_borrar(proyecto):
    """Tarjeta en modo confirmación: muestra aviso y botones Confirmar/Cancelar."""

    with st.container(border=True):
        st.markdown(f"### 🗑️ Eliminar **{proyecto['nombre']}**")

        st.warning(
            "⚠️ ¿Borrar este proyecto y **todas sus fotos**? "
            "Esta acción no se puede deshacer."
        )

        # Dos columnas: Confirmar | Cancelar
        col_confirmar, col_cancelar = st.columns(2)

        with col_confirmar:
            if st.button(
                "🗑️ Confirmar borrado",
                key=f"confirmar_borrar_{proyecto['id']}",
            ):
                eliminar_proyecto_completo(proyecto)

        with col_cancelar:
            if st.button(
                "Cancelar",
                key=f"cancelar_borrar_{proyecto['id']}",
            ):
                st.session_state.proyecto_a_borrar = None
                st.rerun()


def eliminar_proyecto_completo(proyecto):
    """
    Elimina un proyecto del todo:
      1. Borra la carpeta con sus fotos del disco.
      2. Quita el proyecto de la lista en session_state.
      3. Limpia el estado de confirmación.
      4. Recarga la pantalla.
    """
   # 1. Borrar la carpeta del disco (con todas las fotos dentro)
    ruta_carpeta = carpeta_proyecto(proyecto)
    if ruta_carpeta.exists():
        shutil.rmtree(ruta_carpeta)

    # 2. Quitar el proyecto de la lista en memoria
    st.session_state.proyectos = [
        p for p in st.session_state.proyectos
        if p["id"] != proyecto["id"]
    ]

    # 3. Limpiar el estado de confirmación
    st.session_state.proyecto_a_borrar = None

    # 4. Mensaje y recarga
    st.success(f"Proyecto **{proyecto['nombre']}** eliminado correctamente.")
    st.rerun()