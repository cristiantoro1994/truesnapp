#   - Ver sus proyectos activos
#   - Crear un nuevo proyecto
#   - Abrir la galería de un proyecto
#   - Cerrar sesión

import streamlit as st


def mostrar():
    """Muestra el dashboard principal con los proyectos del usuario."""

    if "proyectos" not in st.session_state:
        st.session_state.proyectos = [
            {
                "id": 1,
                "nombre": "Apartamento Centro",
                "fotos_totales": 8,
                "fotos_optimizadas": 5,
                "fotos_certificadas": 3,
            },
            {
                "id": 2,
                "nombre": "Casa de Playa",
                "fotos_totales": 12,
                "fotos_optimizadas": 12,
                "fotos_certificadas": 12,
            },
        ]

    # Cabecera: saludo + botón de cerrar sesión
    # Dividimos la cabecera en dos columnas (saludo a la izq, salir a la der)
    columna_saludo, columna_salir = st.columns([3, 1])

    with columna_saludo:
        # Saludamos al usuario con su email (guardado en login)
        email = st.session_state.get("email_usuario", "Usuario")
        # Mostramos solo la parte antes del @ para que sea más corto
        nombre_corto = email.split("@")[0] if "@" in email else email
        st.markdown(f"### 👋 Hola, **{nombre_corto}**")

    with columna_salir:
        # Botón pequeño para cerrar sesión
        if st.button("Salir", key="boton_salir"):
            # Borramos los datos del usuario de la memoria
            st.session_state.usuario_logueado = False
            st.session_state.email_usuario = ""
            # Volvemos a la pantalla de login
            st.session_state.pagina = "login"
            st.rerun()

    # Línea separadora
    st.markdown("---")

    # Título de la sección

    st.markdown("## 📂 Mis proyectos")

    # Botón principal: crear nuevo proyecto
   
    # Acción principal de la pantalla, siempre visible y arriba
    if st.button("➕ Nuevo proyecto", key="boton_nuevo_proyecto"):
        st.session_state.pagina = "nuevo_proyecto"
        st.rerun()

    # Espacio antes de las tarjetas
    st.write("")

    # Lista de tarjetas de proyectos
    
    # Si no hay proyectos, mostramos un mensaje amigable
    if len(st.session_state.proyectos) == 0:
        st.info(
            "Aún no tienes proyectos. Pulsa **➕ Nuevo proyecto** "
            "para empezar."
        )
    else:
        # Recorremos la lista de proyectos y mostramos una tarjeta por cada uno
        for proyecto in st.session_state.proyectos:
            mostrar_tarjeta_proyecto(proyecto)


def mostrar_tarjeta_proyecto(proyecto):
    """
    Dibuja una tarjeta visual para un proyecto.
    Recibe un diccionario con los datos del proyecto.
    """

    # Usamos un contenedor con borde para que se vea como tarjeta
    with st.container(border=True):

        # Fila superior: nombre del proyecto + botón "Abrir"
        columna_info, columna_boton = st.columns([3, 1])

        with columna_info:
            # Nombre destacado del proyecto
            st.markdown(f"### 🏠 {proyecto['nombre']}")

            # Estado en formato compacto y claro
            estado = (
                f"📷 {proyecto['fotos_totales']} fotos &nbsp;·&nbsp; "
                f"✨ {proyecto['fotos_optimizadas']} optimizadas &nbsp;·&nbsp; "
                f"🔐 {proyecto['fotos_certificadas']} certificadas"
            )
            st.markdown(
                f"<p style='color: #7F8C8D; font-size: 0.95rem;'>{estado}</p>",
                unsafe_allow_html=True,
            )

        with columna_boton:
            # Espacio vertical para alinear con el título
            st.write("")
            # Botón para entrar al proyecto
            if st.button("Abrir", key=f"abrir_{proyecto['id']}"):
                # Guardamos qué proyecto está abierto y vamos a la galería
                st.session_state.proyecto_actual = proyecto["id"]
                st.session_state.pagina = "galeria"
                st.rerun()