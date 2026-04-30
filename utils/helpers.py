# Funciones auxiliares reutilizables en toda la app.
#
# Aquí centralizamos:
#   - La inicialización del estado de sesión (variables por defecto)
#   - La función para cambiar de pantalla
#   - El "router" que decide qué pantalla mostrar

import streamlit as st



# Inicialización del estado de sesión

def inicializar_estado():
    """
    Crea las variables básicas de st.session_state si no existen.
    Se llama UNA sola vez al inicio de app.py.

    Variables que prepara:
      - pagina: nombre de la pantalla actual
      - usuario_logueado: True/False según si el usuario entró
      - email_usuario: email del usuario logueado
      - proyecto_actual: ID del proyecto que el usuario está viendo
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


# Cambiar de pantalla

def cambiar_pagina(nombre_pagina):
    """
    Cambia la pantalla activa de la app.

    Parámetros:
      nombre_pagina: texto con el nombre de la pantalla a mostrar.
                     Valores válidos: "login", "dashboard", "galeria",
                     "certificado", "descargas".

    Uso desde otro archivo:
      from utils.helpers import cambiar_pagina
      cambiar_pagina("dashboard")
    """
    st.session_state.pagina = nombre_pagina
    st.rerun()



# Router: decide qué pantalla mostrar

def mostrar_pagina_actual():
    """
    Lee st.session_state.pagina y muestra la pantalla correspondiente.
    Esta función se llama desde app.py.

    Funciona como un "portero": recibe el nombre de la pantalla y
    llama a la función mostrar() del archivo correcto.
    """

    # Importamos las pantallas aquí dentro (no arriba) para evitar
    # importaciones circulares (que dos archivos se llamen entre sí
    # y se queden en bucle).
    from paginas import login, dashboard, galeria, certificado, descargas

    # Protección de acceso: si el usuario NO está logueado,
    # solo puede ver la pantalla de login (sin importar lo que pida).
    if not st.session_state.usuario_logueado:
        login.mostrar()
        return

    # Si está logueado, mostramos la pantalla que tenga seleccionada
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
    else:
        # Si llega un nombre desconocido, volvemos al dashboard por defecto
        st.warning(f"Pantalla desconocida: '{pagina}'. Volviendo al dashboard.")
        st.session_state.pagina = "dashboard"
        dashboard.mostrar()