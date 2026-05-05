# exportacion/descargar_certificado.py
# Generador de certificados PDF para el proyecto TrueSnapp.
# Crea un documento de una página con:
#   - Cabecera con título "Certificado de Autenticidad"
#   - Foto certificada en grande
#   - Datos identificativos: proyecto, foto, fecha
#   - Huella digital SHA-256 completa
#   - Red blockchain y protocolo
#   - Pie con verificación pública y autoría
#
# El PDF se genera en memoria (no se guarda en disco) y se devuelve
# como bytes para descarga directa por el usuario.


import io
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


# Constantes de diseño


# Colores de la marca TrueSnapp (mismos que la app)
COLOR_AZUL = HexColor("#1E88E5")
COLOR_TEXTO = HexColor("#2C3E50")
COLOR_GRIS_SUAVE = HexColor("#7F8C8D")
COLOR_VERDE = HexColor("#27AE60")

# Tamaños de fuente
TAMANO_TITULO = 22
TAMANO_SUBTITULO = 14
TAMANO_SECCION = 11
TAMANO_DATO = 10
TAMANO_PEQUENO = 8

# Márgenes (en cm)
MARGEN_HORIZONTAL = 2
MARGEN_VERTICAL = 1.5


# Función principal: generar el PDF del certificado


def generar_pdf_certificado(datos):
    """
    Genera un PDF de certificado en memoria.

    Parámetros:
      datos: diccionario con las claves:
        - "nombre_proyecto"  → texto
        - "nombre_foto"      → texto
        - "ruta_imagen"      → Path o string (foto a embeber)
        - "hash"             → string de 64 caracteres
        - "fecha"            → datetime con la fecha de certificación
        - "red"              → texto (ej: "Bitcoin")
        - "protocolo"        → texto (ej: "OpenTimestamps")

    Devuelve:
      - bytes con el contenido del PDF generado.
      - None si hubo cualquier error.
    """
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        ancho, alto = A4

        # Calculamos posiciones reutilizables
        margen_x = MARGEN_HORIZONTAL * cm
        margen_y = MARGEN_VERTICAL * cm

        #  1. Cabecera 
        _dibujar_cabecera(c, ancho, alto)

        # 2. Foto certificada 
        cursor_y = alto - 5 * cm  # posición vertical inicial tras cabecera
        cursor_y = _dibujar_imagen(c, datos.get("ruta_imagen"), ancho, cursor_y)

        # 3. Datos del certificado 
        cursor_y = _dibujar_datos(c, datos, margen_x, cursor_y, ancho)

        #  4. Pie con verificación pública 
        _dibujar_pie(c, ancho, alto)

        #  5. Cerrar y devolver bytes 
        c.showPage()
        c.save()

        contenido_pdf = buffer.getvalue()
        buffer.close()

        return contenido_pdf

    except Exception:
        return None


# Funciones auxiliares de dibujo


def _dibujar_cabecera(c, ancho, alto):
    """Dibuja la cabecera con la marca TrueSnapp y el título principal."""
    # Banda azul superior (decorativa)
    c.setFillColor(COLOR_AZUL)
    c.rect(0, alto - 1.5 * cm, ancho, 1.5 * cm, fill=1, stroke=0)

    # Marca TrueSnapp en la banda azul
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(ancho / 2, alto - 1 * cm, "TrueSnapp")

    # Título principal
    c.setFillColor(COLOR_TEXTO)
    c.setFont("Helvetica-Bold", TAMANO_TITULO)
    c.drawCentredString(ancho / 2, alto - 2.8 * cm, "CERTIFICADO DE AUTENTICIDAD")

    c.setFillColor(COLOR_AZUL)
    c.setFont("Helvetica-Bold", TAMANO_SUBTITULO)
    c.drawCentredString(ancho / 2, alto - 3.6 * cm, "BLOCKCHAIN")


def _dibujar_imagen(c, ruta_imagen, ancho_pagina, cursor_y):
    """Dibuja la foto certificada centrada. Devuelve la nueva cursor_y."""
    if ruta_imagen is None:
        return cursor_y - 0.5 * cm

    ruta = Path(ruta_imagen)
    if not ruta.exists():
        return cursor_y - 0.5 * cm

    try:
        # Tamaño máximo de la imagen
        max_ancho = 10 * cm
        max_alto = 7 * cm

        imagen = ImageReader(str(ruta))
        ancho_orig, alto_orig = imagen.getSize()

        # Calculamos escala respetando proporciones
        escala = min(max_ancho / ancho_orig, max_alto / alto_orig)
        ancho_final = ancho_orig * escala
        alto_final = alto_orig * escala

        # Centramos horizontalmente
        x = (ancho_pagina - ancho_final) / 2
        y = cursor_y - alto_final

        c.drawImage(
            imagen,
            x,
            y,
            width=ancho_final,
            height=alto_final,
            preserveAspectRatio=True,
            mask="auto",
        )

        return y - 0.8 * cm

    except Exception:
        return cursor_y - 0.5 * cm


def _dibujar_datos(c, datos, margen_x, cursor_y, ancho_pagina):
    """Dibuja los datos del certificado. Devuelve la nueva cursor_y."""
    # Línea separadora superior
    c.setStrokeColor(COLOR_GRIS_SUAVE)
    c.setLineWidth(0.5)
    c.line(margen_x, cursor_y, ancho_pagina - margen_x, cursor_y)

    cursor_y -= 0.7 * cm

    # Función auxiliar para dibujar una fila "etiqueta: valor"
    def fila(etiqueta, valor, y):
        c.setFillColor(COLOR_GRIS_SUAVE)
        c.setFont("Helvetica-Bold", TAMANO_SECCION)
        c.drawString(margen_x, y, etiqueta)

        c.setFillColor(COLOR_TEXTO)
        c.setFont("Helvetica", TAMANO_DATO)
        c.drawString(margen_x + 4 * cm, y, valor)

        return y - 0.6 * cm

    cursor_y = fila("Proyecto:", datos.get("nombre_proyecto", "—"), cursor_y)
    cursor_y = fila("Foto:", datos.get("nombre_foto", "—"), cursor_y)

    fecha_str = _formatear_fecha(datos.get("fecha"))
    cursor_y = fila("Fecha de certificación:", fecha_str, cursor_y)

    cursor_y = fila("Red blockchain:", datos.get("red", "—"), cursor_y)
    cursor_y = fila("Protocolo:", datos.get("protocolo", "—"), cursor_y)

    cursor_y -= 0.3 * cm

    # Hash en su propia sección (es muy largo)
    c.setFillColor(COLOR_GRIS_SUAVE)
    c.setFont("Helvetica-Bold", TAMANO_SECCION)
    c.drawString(margen_x, cursor_y, "Huella digital (SHA-256):")
    cursor_y -= 0.5 * cm

    # El hash lo dibujamos en monoespaciada y partido en dos líneas
    # para que quepa cómodamente
    hash_completo = datos.get("hash", "")
    hash_linea_1 = hash_completo[:32]
    hash_linea_2 = hash_completo[32:]

    c.setFillColor(COLOR_TEXTO)
    c.setFont("Courier", TAMANO_DATO)
    c.drawString(margen_x, cursor_y, hash_linea_1)
    cursor_y -= 0.45 * cm
    c.drawString(margen_x, cursor_y, hash_linea_2)
    cursor_y -= 0.7 * cm

    # Línea separadora inferior
    c.setStrokeColor(COLOR_GRIS_SUAVE)
    c.line(margen_x, cursor_y, ancho_pagina - margen_x, cursor_y)

    return cursor_y - 0.5 * cm


def _dibujar_pie(c, ancho, alto):
    """Dibuja el pie de página con la verificación pública."""
    margen_x = MARGEN_HORIZONTAL * cm
    pie_y = 3 * cm

    # Texto explicativo
    c.setFillColor(COLOR_TEXTO)
    c.setFont("Helvetica", TAMANO_SECCION)
    c.drawCentredString(
        ancho / 2,
        pie_y,
        "Este certificado prueba que la fotografía existía sin modificación",
    )
    c.drawCentredString(
        ancho / 2,
        pie_y - 0.5 * cm,
        "en la fecha indicada y está registrada en blockchain.",
    )

    # Verificación pública
    c.setFillColor(COLOR_AZUL)
    c.setFont("Helvetica-Bold", TAMANO_SECCION)
    c.drawCentredString(
        ancho / 2,
        pie_y - 1.5 * cm,
        "Verificación pública: https://opentimestamps.org",
    )

    # Pie con autoría
    c.setFillColor(COLOR_GRIS_SUAVE)
    c.setFont("Helvetica-Oblique", TAMANO_PEQUENO)
    c.drawCentredString(
        ancho / 2,
        1 * cm,
        "Generado por TrueSnapp · Documento auténtico",
    )


def _formatear_fecha(fecha):
    """Convierte un datetime en texto legible en español."""
    if fecha is None:
        return "—"

    if not isinstance(fecha, datetime):
        return str(fecha)

    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    ]

    return (
        f"{fecha.day} de {meses[fecha.month - 1]} de {fecha.year}, "
        f"{fecha.hour:02d}:{fecha.minute:02d}"
    )