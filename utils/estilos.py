# Paleta TrueSnapp:
#   - Fondo:       blanco / gris claro
#   - Acento:      azul tecnológico
#   - Texto:       gris oscuro


import streamlit as st


# CONSTANTES DE COLORES (paleta TrueSnapp)

COLOR_AZUL = "#1E88E5"          # Azul tecnológico (acento principal)
COLOR_AZUL_OSCURO = "#1565C0"   # Azul oscuro (hover de botones)
COLOR_BLANCO = "#FFFFFF"        # Blanco puro (fondos)
COLOR_GRIS_CLARO = "#F5F7FA"    # Gris claro (fondos secundarios)
COLOR_GRIS_MEDIO = "#E0E4E8"    # Gris medio (bordes y separadores)
COLOR_TEXTO = "#2C3E50"         # Gris oscuro (texto principal)
COLOR_TEXTO_SUAVE = "#7F8C8D"   # Gris suave (texto secundario)
COLOR_EXITO = "#27AE60"         # Verde (mensajes de éxito)
COLOR_ALERTA = "#E67E22"        # Naranja (mensajes de alerta)



# Función principal: aplicar todos los estilos a la app

def aplicar_estilos():
    """
    Aplica los estilos visuales globales de TrueSnapp.
    Se llama UNA sola vez al inicio de app.py.
    """

    css_personalizado = f"""
    <style>

    /* ----- Botones grandes y visibles (filosofía TrueSnapp) ----- */
    .stButton > button {{
        background-color: {COLOR_AZUL};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-size: 1.05rem;
        font-weight: 600;
        width: 100%;
        transition: background-color 0.2s ease;
    }}
    .stButton > button:hover {{
        background-color: {COLOR_AZUL_OSCURO};
        color: white;
    }}

    /* ----- Botones de descarga ----- */
    .stDownloadButton > button {{
        background-color: {COLOR_AZUL};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-size: 1.05rem;
        font-weight: 600;
        width: 100%;
    }}
    .stDownloadButton > button:hover {{
        background-color: {COLOR_AZUL_OSCURO};
    }}

    /* ----- Campos de entrada (inputs) ----- */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border-radius: 10px;
        border: 1px solid {COLOR_GRIS_MEDIO};
        padding: 0.6rem;
    }}

    /* ----- Limitar el ancho central (look móvil) ----- */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 700px;
    }}

    </style>
    """

    # Inyectamos el CSS en la página
    st.markdown(css_personalizado, unsafe_allow_html=True)