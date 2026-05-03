# =====================================================================
# paginas/galeria.py
# =====================================================================
# Galería de imágenes de un proyecto.
#
# El usuario puede:
#   - Ver todas las fotos del proyecto en una rejilla
#   - Subir nuevas fotos (desde móvil o escritorio)
#   - Optimizar fotos con OpenCV + IA Real-ESRGAN (Fase 4)
#   - Comparar original/optimizada con slider deslizante
#   - Re-optimizar (borra solo la versión optimizada y reprocesa)
#   - Eliminar fotos con doble confirmación
#
# Las fotos se guardan en: datos/imagenes/[id_proyecto]/
# Las versiones optimizadas se guardan en: datos/imagenes/[id_proyecto]/optimizadas/
# =====================================================================

import streamlit as st
from streamlit_image_comparison import image_comparison  # Slider antes/después

# Funciones auxiliares (Fase 3 + Fase 4)
from utils.helpers import (
    guardar_imagen,
    listar_imagenes,
    eliminar_imagen,
    ruta_imagen_optimizada,
    existe_version_optimizada,
    limpiar_archivos_temporales,
)

# Capa 1: optimización con OpenCV (Fase 4)
# Importante: usamos 'guardar_imagen_cv' (no 'guardar_imagen') para
# evitar conflicto con la función del mismo nombre en helpers.py
from procesamiento.optimizar import (
    leer_imagen,
    guardar_imagen_cv,
    reducir_ruido,
    balancear_color,
    ajustar_brillo_contraste,
    mejorar_nitidez,
)

# Capa 2: optimización con IA (Real-ESRGAN vía Replicate)
from procesamiento.optimizar_ia import (
    hay_clave_replicate,
    optimizar_con_ia,
)


def mostrar():
    """Muestra la galería de imágenes del proyecto seleccionado."""

    # -----------------------------------------------------------------
    # Botón de volver (siempre arriba)
    # -----------------------------------------------------------------
    if st.button("← Volver", key="volver_galeria"):
        st.session_state.foto_a_borrar = None
        st.session_state.pagina = "dashboard"
        st.rerun()

    # -----------------------------------------------------------------
    # Buscar el proyecto actual en la lista
    # -----------------------------------------------------------------
    proyecto = obtener_proyecto_actual()

    if proyecto is None:
        st.warning("No se encontró el proyecto. Volviendo al dashboard...")
        st.session_state.pagina = "dashboard"
        st.rerun()
        return

    # Limpiar archivos temporales que pudieran haber quedado
    # de procesos de optimización interrumpidos previamente
    limpiar_archivos_temporales(proyecto)

    # -----------------------------------------------------------------
    # Cabecera: nombre del proyecto
    # -----------------------------------------------------------------
    st.markdown(f"## 🏠 {proyecto['nombre']}")

    # -----------------------------------------------------------------
    # Zona de subida de fotos
    # -----------------------------------------------------------------
    st.markdown("### 📤 Subir fotos")

    archivos_subidos = st.file_uploader(
        label="Arrastra tus fotos aquí o pulsa para seleccionarlas",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=f"uploader_{proyecto['id']}",
    )

    if archivos_subidos:
        procesar_archivos_subidos(archivos_subidos, proyecto)

    st.markdown("---")

    # -----------------------------------------------------------------
    # Galería: mostrar las fotos del proyecto
    # -----------------------------------------------------------------
    imagenes = listar_imagenes(proyecto)
    total = len(imagenes)

    st.markdown(f"### 📷 Galería ({total} fotos)")

    if total == 0:
        st.info(
            "Aún no has subido ninguna foto a este proyecto. "
            "Usa el botón de arriba para añadir las primeras."
        )
    else:
        mostrar_rejilla_imagenes(imagenes, proyecto)


def obtener_proyecto_actual():
    """Busca en la lista el proyecto seleccionado."""
    proyecto_id = st.session_state.get("proyecto_actual", None)

    if proyecto_id is None:
        return None

    for p in st.session_state.get("proyectos", []):
        if p["id"] == proyecto_id:
            return p

    return None


def procesar_archivos_subidos(archivos_subidos, proyecto):
    """
    Guarda en el disco SOLO las fotos que aún no se hayan procesado.
    Streamlit mantiene los archivos en file_uploader entre reruns,
    por eso usamos un conjunto de IDs procesados para no duplicar.
    """
    clave_estado = f"archivos_procesados_{proyecto['id']}"

    if clave_estado not in st.session_state:
        st.session_state[clave_estado] = set()

    procesados = st.session_state[clave_estado]
    cantidad_guardada = 0

    for archivo in archivos_subidos:
        if archivo.file_id in procesados:
            continue

        try:
            guardar_imagen(archivo, proyecto)
            procesados.add(archivo.file_id)
            cantidad_guardada += 1
        except Exception as error:
            st.error(f"Error al guardar **{archivo.name}**: {error}")

    if cantidad_guardada > 0:
        st.success(f"✅ {cantidad_guardada} foto(s) guardada(s) correctamente.")
        st.session_state.foto_a_borrar = None
        st.rerun()


def mostrar_rejilla_imagenes(imagenes, proyecto):
    """Muestra las imágenes en una rejilla de 3 columnas, con botones."""
    columnas_por_fila = 3

    for i in range(0, len(imagenes), columnas_por_fila):
        cols = st.columns(columnas_por_fila)

        for j in range(columnas_por_fila):
            indice = i + j
            if indice < len(imagenes):
                ruta_imagen = imagenes[indice]
                with cols[j]:
                    mostrar_miniatura_completa(ruta_imagen, proyecto)


def mostrar_miniatura_completa(ruta_imagen, proyecto):
    """
    Muestra una miniatura de la imagen + botones de acción.

    Si la foto NO está optimizada:
      - Muestra solo la original (a tamaño completo).
      - Botón "✨ Optimizar".
      - Botón "🗑️ Borrar".

    Si la foto SÍ está optimizada:
      - Muestra slider deslizante con original y optimizada.
      - Indicador "✅ Optimizada".
      - Botón "🔄 Re-optimizar" (borra solo la optimizada y reoptimiza).
      - Botón "🗑️ Borrar" (borra ambas, con doble confirmación).
    """
    # ----- Identificador único de esta foto -----
    id_foto = str(ruta_imagen)

    # ----- Comprobación de borrado pendiente -----
    foto_pendiente = st.session_state.get("foto_a_borrar", None)

    if foto_pendiente == id_foto:
        # Modo confirmación de borrado
        st.image(str(ruta_imagen), use_container_width=True)
        st.warning("¿Seguro? Pulsa otra vez para borrar.")
        if st.button("🗑️ Confirmar borrado", key=f"confirmar_{id_foto}"):
            eliminar_foto_completa(ruta_imagen, proyecto)
        return

    # ----- Estado: ¿está optimizada? -----
    optimizada = existe_version_optimizada(ruta_imagen, proyecto)

    if optimizada:
        # ===== MODO COMPARACIÓN: slider deslizante interactivo =====
        ruta_optimizada = ruta_imagen_optimizada(ruta_imagen, proyecto)

        # Slider que el usuario puede arrastrar para comparar
        # las dos versiones de la imagen.
        image_comparison(
            img1=str(ruta_imagen),
            img2=str(ruta_optimizada),
            label1="Original",
            label2="✨ Optimizada",
            width=500,
            starting_position=50,
            show_labels=True,
            make_responsive=True,
            in_memory=True,
        )
    else:
        # ===== MODO NORMAL: solo la original =====
        st.image(str(ruta_imagen), use_container_width=True)

    # ----- Nombre limpio del archivo (común a ambos modos) -----
    nombre_limpio = quitar_id_del_nombre(ruta_imagen.name)
    st.markdown(
        f"<p style='font-size: 0.75rem; color: #A0A6AC; "
        f"text-align: center; margin: 0.4rem 0 0.3rem 0;'>"
        f"{nombre_limpio}</p>",
        unsafe_allow_html=True,
    )

    # ----- Botones de acción -----
    if optimizada:
        # Indicador verde de optimizada
        st.markdown(
            "<p style='text-align: center; color: #27AE60; "
            "font-size: 0.85rem; font-weight: 600; margin: 0.3rem 0;'>"
            "✅ Optimizada</p>",
            unsafe_allow_html=True,
        )

        # Botón de re-optimizar (borra solo la optimizada y reoptimiza)
        if st.button("🔄 Re-optimizar", key=f"reoptimizar_{id_foto}"):
            reoptimizar_foto(ruta_imagen, proyecto)
    else:
        # Botón para optimizar (foto sin optimizar todavía)
        if st.button("✨ Optimizar", key=f"optimizar_{id_foto}"):
            optimizar_foto(ruta_imagen, proyecto)

    # ----- Botón borrar (siempre visible) -----
    if st.button("🗑️ Borrar", key=f"borrar_{id_foto}"):
        st.session_state.foto_a_borrar = id_foto
        st.rerun()


def optimizar_foto(ruta_imagen, proyecto):
    """
    Aplica el pipeline híbrido a una foto:
      CAPA 1: OpenCV (siempre)
      CAPA 2: Real-ESRGAN vía Replicate (si está configurado y disponible)

    Si la CAPA 2 falla por cualquier motivo (sin internet, sin créditos,
    error del servidor), guardamos el resultado de la CAPA 1.
    El usuario nunca se queda con las manos vacías.

    El procesamiento se descompone en 6 fases visibles:
      1. Lectura + reducción de ruido
      2. Balance de color
      3. Brillo y contraste
      4. Nitidez
      5. (Opcional) Mejora con IA en la nube
      6. Guardado del resultado final
    """
    import time

    # Calculamos dónde guardar la versión optimizada
    ruta_destino = ruta_imagen_optimizada(ruta_imagen, proyecto)

    # -----------------------------------------------------------------
    # Comprobamos si podemos usar la capa de IA
    # -----------------------------------------------------------------
    usar_ia = hay_clave_replicate()

    # -----------------------------------------------------------------
    # Crear los componentes visuales de la animación
    # -----------------------------------------------------------------
    contenedor_mensaje = st.empty()
    barra_progreso = st.progress(0)

    # Archivo temporal donde guardar el resultado de OpenCV
    # antes de enviarlo a la IA
    ruta_intermedia = ruta_imagen_optimizada(ruta_imagen, proyecto)

    try:
        # -------------------------------------------------------------
        # FASE 1: Leer imagen + reducir ruido
        # -------------------------------------------------------------
        contenedor_mensaje.info("🧹 Limpiando ruido de la imagen...")
        barra_progreso.progress(10)

        imagen = leer_imagen(ruta_imagen)
        if imagen is None:
            contenedor_mensaje.error(
                "No se pudo leer la imagen. Inténtalo de nuevo."
            )
            return

        imagen = reducir_ruido(imagen)
        barra_progreso.progress(25 if usar_ia else 35)
        time.sleep(0.2)

        # -------------------------------------------------------------
        # FASE 2: Balance de color
        # -------------------------------------------------------------
        contenedor_mensaje.info("🎨 Equilibrando los colores...")
        imagen = balancear_color(imagen)
        barra_progreso.progress(40 if usar_ia else 55)
        time.sleep(0.2)

        # -------------------------------------------------------------
        # FASE 3: Brillo y contraste
        # -------------------------------------------------------------
        contenedor_mensaje.info("💡 Mejorando la iluminación...")
        imagen = ajustar_brillo_contraste(imagen)
        barra_progreso.progress(50 if usar_ia else 75)
        time.sleep(0.2)

        # -------------------------------------------------------------
        # FASE 4: Nitidez
        # -------------------------------------------------------------
        contenedor_mensaje.info("🔪 Realzando los detalles...")
        imagen = mejorar_nitidez(imagen)
        barra_progreso.progress(60 if usar_ia else 90)
        time.sleep(0.2)

        # -------------------------------------------------------------
        # FASE 5 (opcional): Mejora con IA en la nube
        # -------------------------------------------------------------
        if usar_ia:
            # Primero guardamos el resultado de OpenCV en un archivo
            # temporal, porque la función de IA recibe una RUTA, no
            # una matriz. Reutilizamos la ruta destino pero la
            # sobrescribiremos al final.
            guardar_imagen_cv(imagen, ruta_intermedia)

            contenedor_mensaje.info(
                "🤖 Aplicando IA profesional (Real-ESRGAN)..."
            )
            barra_progreso.progress(75)

            # Llamamos a Replicate. Esta llamada puede tardar 5-15s.
            imagen_ia = optimizar_con_ia(ruta_intermedia)

            if imagen_ia is not None:
                # ✅ La IA funcionó: usamos su resultado
                imagen = imagen_ia
                contenedor_mensaje.success(
                    "✨ ¡IA aplicada correctamente!"
                )
            else:
                # ⚠️ La IA falló: nos quedamos con el resultado de OpenCV
                contenedor_mensaje.warning(
                    "⚠️ La IA no estuvo disponible. "
                    "Se usará el resultado de la optimización clásica."
                )

            barra_progreso.progress(90)
            time.sleep(0.4)

        # -------------------------------------------------------------
        # FASE 6: Guardar resultado final
        # -------------------------------------------------------------
        contenedor_mensaje.info("💾 Guardando la versión optimizada...")
        guardar_imagen_cv(imagen, ruta_destino)
        barra_progreso.progress(100)
        time.sleep(0.3)

        # -------------------------------------------------------------
        # Final: mensaje de éxito y recarga
        # -------------------------------------------------------------
        contenedor_mensaje.success(
            "✅ ¡Foto optimizada correctamente!"
        )
        time.sleep(0.6)
        st.rerun()

    except Exception as error:
        contenedor_mensaje.error(f"Error al optimizar: {error}")
        barra_progreso.empty()


def reoptimizar_foto(ruta_imagen, proyecto):
    """
    Borra solo la versión optimizada y vuelve a procesarla.

    La imagen original NO se toca: queda intacta.
    Útil cuando el usuario no está conforme con el resultado y
    quiere generar una nueva versión optimizada desde cero.
    """
    # 1. Borramos la versión optimizada existente
    ruta_optimizada = ruta_imagen_optimizada(ruta_imagen, proyecto)
    if ruta_optimizada.exists():
        eliminar_imagen(ruta_optimizada)

    # 2. Volvemos a optimizar la foto original
    # (esto reutiliza toda la animación de progreso de optimizar_foto)
    optimizar_foto(ruta_imagen, proyecto)


def eliminar_foto_completa(ruta_imagen, proyecto):
    """
    Elimina una foto y, si existe, también su versión optimizada.
    """
    # Borrar original
    eliminar_imagen(ruta_imagen)

    # Si existe la versión optimizada, también la borramos
    ruta_optimizada = ruta_imagen_optimizada(ruta_imagen, proyecto)
    if ruta_optimizada.exists():
        eliminar_imagen(ruta_optimizada)

    # Limpiar estado y recargar
    st.session_state.foto_a_borrar = None
    st.rerun()


def quitar_id_del_nombre(nombre_archivo):
    """Quita el ID único del inicio del nombre del archivo."""
    if "_" in nombre_archivo:
        partes = nombre_archivo.split("_", 1)
        if len(partes) == 2:
            return partes[1]
    return nombre_archivo