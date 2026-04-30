# Galería de imágenes del proyecto seleccionado.
# El usuario verá aquí todas las fotos que ha subido a un proyecto,
# con su estado (pendiente / optimizada / certificada).


import streamlit as st


def mostrar():
    """Muestra la galería de imágenes del proyecto seleccionado."""

    # Botón de volver (siempre arriba a la izquierda)
    #
    if st.button("← Volver al dashboard", key="volver_galeria"):
        st.session_state.pagina = "dashboard"
        st.rerun()

    
    # Título y descripción del proyecto
    
    # Buscamos el proyecto actual en la lista (si existe)
    proyecto_id = st.session_state.get("proyecto_actual", None)
    nombre_proyecto = "Proyecto"

    if proyecto_id is not None and "proyectos" in st.session_state:
        for p in st.session_state.proyectos:
            if p["id"] == proyecto_id:
                nombre_proyecto = p["nombre"]
                break

    st.markdown(f"## 🏠 {nombre_proyecto}")
    st.markdown("### 📷 Galería de fotos")

    st.markdown("---")


    st.info(
        "🚧 **Pantalla en construcción**\n\n"
        "Aquí verás todas las fotos del proyecto y podrás:\n"
        "- Subir nuevas fotos\n"
        "- Optimizar con IA\n"
        "- Ver el estado de cada imagen\n\n"
    
    )