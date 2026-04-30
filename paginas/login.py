# Pantalla de inicio de sesión de TrueSnapp.

import streamlit as st


def mostrar():
    """Muestra la pantalla de login."""


    # Cabecera: logo y título
    
    # Centramos el contenido usando columnas (la del medio es más ancha)
    columna_izq, columna_centro, columna_der = st.columns([1, 3, 1])

    with columna_centro:
        # Título grande con el logo emoji
        st.markdown(
            "<h1 style='text-align: center; font-size: 2.5rem;'>📸 TrueSnapp</h1>",
            unsafe_allow_html=True,
        )

        # Subtítulo descriptivo
        st.markdown(
            "<p style='text-align: center; color: #7F8C8D; font-size: 1rem;'>"
            "Optimiza y certifica las fotos de tu alojamiento"
            "</p>",
            unsafe_allow_html=True,
        )

    # Espacio en blanco antes del formulario
    st.write("")
    st.write("")

    
    # Formulario de login
    

    # Campo de email
    email = st.text_input(
        label="Email",
        placeholder="tu@email.com",
        key="login_email",  # Identificador único para este campo
    )

    # Campo de contraseña (con asteriscos)
    contrasena = st.text_input(
        label="Contraseña",
        type="password",
        placeholder="••••••••",
        key="login_contrasena",
    )

    # Pequeño espacio antes del botón
    st.write("")

    # Botón principal: Entrar
   
    # Una sola acción principal por pantalla (filosofía TrueSnapp)
    if st.button("Entrar", key="boton_entrar"):

        # Validación mínima: que ambos campos tengan algo escrito
        if email.strip() == "" or contrasena.strip() == "":
            st.error("Por favor, completa tu email y contraseña.")
        else:
            # Guardamos en la "memoria" de la app que el usuario entró
            st.session_state.usuario_logueado = True
            st.session_state.email_usuario = email
            # Cambiamos a la pantalla del dashboard
            st.session_state.pagina = "dashboard"
            # Recargamos la app para que se vea el cambio
            st.rerun()

    
    # Enlace secundario: crear cuenta
    
    # Línea separadora
    st.markdown("---")

    # Texto centrado con la opción de crear cuenta
    columna_izq, columna_centro, columna_der = st.columns([1, 2, 1])
    with columna_centro:
        st.markdown(
            "<p style='text-align: center; color: #7F8C8D;'>"
            "¿No tienes cuenta?"
            "</p>",
            unsafe_allow_html=True,
        )

        # Botón secundario para crear cuenta (por ahora solo muestra aviso)
        if st.button("Crear cuenta nueva", key="boton_crear_cuenta"):
            st.info(
                "🔧 La creación de cuentas se habilitará en la Fase 6 "
                "(Base de datos)."
            )