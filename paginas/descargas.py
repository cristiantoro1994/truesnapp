# Pantalla centralizada de descargas:
#   - Imagen original
#   - Imagen optimizada con IA
#   - Certificado TrueSnapp en JPG/PNG
#   - Paquete completo (imagen + certificado)

import streamlit as st


def mostrar():
    """Muestra la pantalla de descargas."""

    # Botón de volver

    if st.button("← Volver al dashboard", key="volver_descargas"):
        st.session_state.pagina = "dashboard"
        st.rerun()

    # Título de la pantalla
    
    st.markdown("## ⬇️ Descargas")

    st.markdown("---")

    # Mensaje provisional

    st.info(
        "🚧 **Pantalla en construcción**\n\n"
        "Desde aquí podrás descargar con un solo clic:\n"
        "- 📷 La imagen original\n"
        "- ✨ La imagen optimizada con IA\n"
        "- 🔐 El certificado TrueSnapp\n"
        "- 📦 El paquete completo (imagen + certificado)\n\n"
    
    )