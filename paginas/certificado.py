# Vista del certificado blockchain de una imagen optimizada.
# Mostrará: ID único, fecha, hash SHA-256, transacción blockchain
# y el sello visual de autenticidad descargable.

import streamlit as st


def mostrar():
    """Muestra el certificado blockchain de una imagen."""

    # Botón de volver

    if st.button("← Volver al dashboard", key="volver_certificado"):
        st.session_state.pagina = "dashboard"
        st.rerun()

    # Título de la pantalla

    st.markdown("## 🔐 Certificado TrueSnapp")

    st.markdown("---")

    # Mensaje provisional

    st.info(
        "🚧 **Pantalla en construcción**\n\n"
        "Aquí se mostrará el certificado de autenticidad de la imagen:\n"
        "- ID único de la imagen\n"
        "- Fecha y hora de certificación\n"
        "- Hash SHA-256 de verificación\n"
        "- Enlace a la transacción blockchain\n"
        "- Sello visual descargable\n\n"
        
    )