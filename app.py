# =====================================================================
# TrueSnapp - Aplicación principal
# =====================================================================
# Este es el punto de entrada de la app. Cuando ejecutas en la terminal:
#     streamlit run app.py
# Streamlit lee este archivo y carga la interfaz en el navegador.
#
# En la Fase 1 (actual) solo mostramos una pantalla de bienvenida
# para confirmar que el entorno está bien configurado.
# En las próximas fases añadiremos: login, dashboard, subida de fotos, etc.
# =====================================================================

import streamlit as st


# ---------------------------------------------------------------------
# Configuración general de la página
# ---------------------------------------------------------------------
# Esta función SIEMPRE debe ir al inicio, antes que cualquier otra
# instrucción de Streamlit. Define cómo se ve la pestaña del navegador.
st.set_page_config(
    page_title="TrueSnapp",            # Título que aparece en la pestaña
    page_icon="📸",                     # Icono de la pestaña
    layout="centered",                  # Diseño centrado (mejor para móvil)
    initial_sidebar_state="collapsed",  # Sin barra lateral al inicio
)


# ---------------------------------------------------------------------
# Inicialización del estado de sesión
# ---------------------------------------------------------------------
# st.session_state es la "memoria" de la app entre interacciones.
# Aquí guardaremos la pantalla actual, el usuario logueado, etc.
# Por ahora solo creamos la variable "pagina" para la navegación.
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"


# ---------------------------------------------------------------------
# Pantalla de bienvenida (provisional - Fase 1)
# ---------------------------------------------------------------------
# En la Fase 2 esto será reemplazado por el sistema de navegación real
# que dirige al login, dashboard, etc. según el estado de session_state.
def mostrar_bienvenida():
    """Muestra la pantalla inicial de TrueSnapp."""

    # Título principal de la app
    st.title("📸 TrueSnapp")

    # Subtítulo descriptivo
    st.subheader("Optimiza, certifica y descarga las fotos de tu alojamiento")

    # Línea separadora
    st.divider()

    # Mensaje de bienvenida
    st.write(
        "Bienvenido a **TrueSnapp**, la herramienta que te permite mejorar "
        "automáticamente las fotos de tu alojamiento turístico con "
        "inteligencia artificial y certificarlas con blockchain."
    )

    # Mensaje informativo (verde) confirmando que la app funciona
    st.success("✅ La aplicación se ha iniciado correctamente.")

    # Información sobre la fase actual del desarrollo
    st.info(
        "🚧 **Fase 1 completada:** entorno, estructura y repositorio listos.\n\n"
        "Las siguientes pantallas (login, dashboard, subida de fotos) "
        "se implementarán en las próximas fases."
    )


# ---------------------------------------------------------------------
# Punto de arranque del programa
# ---------------------------------------------------------------------
# Aquí decidimos qué pantalla mostrar según session_state.pagina.
# Por ahora solo existe la pantalla de bienvenida.
if st.session_state.pagina == "inicio":
    mostrar_bienvenida()
