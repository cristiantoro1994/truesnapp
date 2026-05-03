# Funciones para mejorar imágenes usando OpenCV (sin IA).
#
# Esta es la CAPA 1 del sistema híbrido de optimización de TrueSnapp.
# Se aplica SIEMPRE a cada foto, garantizando una mejora visible
# aunque la capa de IA externa (Replicate) no esté disponible.
# Operaciones que realiza:
#   1. Ajuste automático de brillo y contraste (CLAHE)
#   2. Balance de color automático (gray world)
#   3. Mejora de nitidez (afilado de bordes)
#   4. Reducción de ruido suave
#   5. Escritura atómica con validación (Paso 7)


import cv2          # OpenCV: procesamiento de imágenes
import numpy as np  # NumPy: operaciones con matrices


# 1. Lectura y escritura de imágenes


def leer_imagen(ruta):
    """
    Lee una imagen del disco usando OpenCV.

    Parámetros:
      ruta: ruta del archivo (Path o string).

    Devuelve la imagen como una matriz de NumPy.
    Si no se puede leer, devuelve None.
    """
    # Convertimos la ruta a string por si llega como Path
    imagen = cv2.imread(str(ruta))
    return imagen


def guardar_imagen_cv(imagen, ruta):
    """
    Guarda una matriz de imagen (NumPy) en el disco usando OpenCV.

    Implementa ESCRITURA ATÓMICA + VALIDACIÓN para garantizar la
    integridad del archivo:
      1. Escribe primero a un archivo temporal con sufijo .tmp.[ext].
      2. Comprueba que el archivo temporal es válido (se puede leer).
      3. Solo si la validación pasa, renombra al nombre final.
      4. Si algo falla, limpia el archivo temporal.

    Resultado: nunca queda un archivo corrupto en el destino final.
    O todo, o nada.

    IMPORTANTE: esta función es solo para imágenes ya procesadas
    (matrices NumPy). Para guardar archivos subidos por el usuario,
    usa la función guardar_imagen() de utils/helpers.py.

    Parámetros:
      imagen: matriz NumPy con la imagen.
      ruta: ruta donde guardar el archivo (Path o string).

    Devuelve True si todo salió bien, False si hubo algún problema.
    """
    from pathlib import Path

    # Convertimos a Path para poder operar con él
    ruta_final = Path(ruta)

    # Ruta temporal: insertamos ".tmp" ANTES de la extensión.
    # Importante: OpenCV decide el formato a guardar mirando la
    # extensión del archivo (.jpg, .png, etc.). Por eso la extensión
    # real (.jpg, .png) debe quedar al final del nombre.
    # Ejemplo: foto.jpg → foto.tmp.jpg (OpenCV reconoce .jpg)
    ruta_temporal = ruta_final.with_name(
        ruta_final.stem + ".tmp" + ruta_final.suffix
    )

    #  1. Escribir al archivo temporal 
    parametros = [cv2.IMWRITE_JPEG_QUALITY, 95]
    exito_escritura = cv2.imwrite(str(ruta_temporal), imagen, parametros)

    if not exito_escritura:
        # OpenCV no pudo escribir el archivo
        # Intentamos limpiar por si dejó algo a medias
        if ruta_temporal.exists():
            ruta_temporal.unlink()
        return False

    # 2. Validar que el archivo temporal se puede leer 
    imagen_validacion = cv2.imread(str(ruta_temporal))

    if imagen_validacion is None:
        # El archivo se escribió pero no se puede leer 
        if ruta_temporal.exists():
            ruta_temporal.unlink()
        return False

    #  3. Renombrar el .tmp al nombre final
    # Si ya existía un archivo final previo, lo borramos primero
    if ruta_final.exists():
        ruta_final.unlink()

    # rename() es una operación atómica en sistemas de archivos:
    # o se hace por completo, o no se hace.
    ruta_temporal.rename(ruta_final)

    return True


# 2. Ajuste de brillo y contraste con CLAHE


def ajustar_brillo_contraste(imagen):
    """
    Mejora el brillo y contraste de la imagen usando CLAHE.

    CLAHE (Contrast Limited Adaptive Histogram Equalization) ajusta
    el contraste por zonas pequeñas, lo que funciona mucho mejor que
    un ajuste global. Es ideal para fotos de interiores con luz
    desigual (típicas de alojamientos turísticos).

    Trabajamos en el espacio de color LAB para no alterar los colores,
    solo la luminosidad.
    """
    # Convertimos de BGR (formato OpenCV) a LAB
    # En LAB: L = luminosidad, A = verde-rojo, B = azul-amarillo
    lab = cv2.cvtColor(imagen, cv2.COLOR_BGR2LAB)

    # Separamos los tres canales
    canal_l, canal_a, canal_b = cv2.split(lab)

    # Creamos el algoritmo CLAHE
    # clipLimit: cuánto contraste aplicar (2.0 = moderado, no exagera)
    # tileGridSize: en cuántas zonas se divide la imagen (8x8 = estándar)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    # Aplicamos CLAHE solo al canal L (luminosidad)
    canal_l_mejorado = clahe.apply(canal_l)

    # Volvemos a unir los tres canales
    lab_mejorado = cv2.merge((canal_l_mejorado, canal_a, canal_b))

    # Convertimos de vuelta a BGR
    imagen_mejorada = cv2.cvtColor(lab_mejorado, cv2.COLOR_LAB2BGR)

    return imagen_mejorada


# 3. Balance de color automático (Gray World)


def balancear_color(imagen):
    """
    Corrige tonos amarillentos o azulados usando el algoritmo
    'Gray World' (mundo gris).

    Idea: si la foto tuviera colores neutros, el promedio de cada
    canal (R, G, B) debería ser similar. Si uno destaca mucho, hay
    una dominante de color. Esta función equilibra los tres canales.
    """
    # Convertimos a float para hacer cálculos sin perder precisión
    imagen_float = imagen.astype(np.float32)

    # Calculamos el promedio de cada canal (B, G, R en OpenCV)
    promedio_b = np.mean(imagen_float[:, :, 0])
    promedio_g = np.mean(imagen_float[:, :, 1])
    promedio_r = np.mean(imagen_float[:, :, 2])

    # Promedio gris ideal: la media de los tres canales
    promedio_gris = (promedio_b + promedio_g + promedio_r) / 3

    # Calculamos el factor de corrección para cada canal
    # Si un canal está por debajo del gris ideal, lo subimos.
    # Si está por encima, lo bajamos.
    factor_b = promedio_gris / promedio_b if promedio_b > 0 else 1
    factor_g = promedio_gris / promedio_g if promedio_g > 0 else 1
    factor_r = promedio_gris / promedio_r if promedio_r > 0 else 1

    # Aplicamos los factores a cada canal
    imagen_float[:, :, 0] *= factor_b
    imagen_float[:, :, 1] *= factor_g
    imagen_float[:, :, 2] *= factor_r

    # Aseguramos que los valores se queden entre 0 y 255 (rango válido)
    imagen_balanceada = np.clip(imagen_float, 0, 255).astype(np.uint8)

    return imagen_balanceada



# 4. Mejora de nitidez (afilado de bordes)


def mejorar_nitidez(imagen):
    """
    Realza los bordes y detalles de la imagen para que se vea
    más nítida. Usa la técnica de 'unsharp masking', que es
    el estándar profesional.

    Funciona así:
      1. Crea una versión borrosa de la imagen.
      2. Resta esa versión borrosa de la original.
      3. Ese resultado son SOLO los bordes y detalles.
      4. Suma los detalles de vuelta a la original con peso.
    """
    # Creamos una versión ligeramente borrosa (Gaussian blur)
    # (5, 5) es el tamaño del filtro; valores más grandes = más borroso
    imagen_borrosa = cv2.GaussianBlur(imagen, (5, 5), 1.5)

    # Combinamos la imagen original con la borrosa
    # Fórmula: (1.5 * original) - (0.5 * borrosa) = imagen con bordes realzados
    # 1.5 y -0.5 son los pesos; suman 1 para no cambiar la luminosidad
    imagen_nitida = cv2.addWeighted(imagen, 1.5, imagen_borrosa, -0.5, 0)

    return imagen_nitida



# 5. Reducción de ruido suave


def reducir_ruido(imagen):
    """
    Reduce el ruido (grano) de la imagen sin perder demasiado detalle.
    Útil para fotos hechas con poca luz o con teléfonos antiguos.

    Usamos 'Non-Local Means', un algoritmo que sabe distinguir entre
    bordes reales y ruido aleatorio.
    """
    # Parámetros ajustados para una reducción suave:
    #   h = 10: fuerza de la reducción de ruido (10 es moderado)
    #   hColor = 10: igual pero para los colores
    #   templateWindowSize = 7: tamaño de las ventanas de comparación
    #   searchWindowSize = 21: tamaño del área de búsqueda
    imagen_limpia = cv2.fastNlMeansDenoisingColored(
        imagen,
        None,
        h=10,
        hColor=10,
        templateWindowSize=7,
        searchWindowSize=21,
    )

    return imagen_limpia



# 6. PIPELINE CENTRAL DE OPTIMIZACIÓN

# Función principal que combina todas las mejoras en una sola llamada.



def optimizar_imagen_opencv(imagen, aplicar_reduccion_ruido=True):
    """
    Aplica todas las mejoras de OpenCV a una imagen, en el orden óptimo.

    Esta función es la CAPA 1 del sistema híbrido de TrueSnapp.
    Se aplica SIEMPRE (con o sin Replicate disponible).

    Parámetros:
      imagen: matriz NumPy con la imagen original (formato BGR de OpenCV).
      aplicar_reduccion_ruido: si True, aplica reducción de ruido.
                               Es la operación más lenta del pipeline.

    Devuelve la imagen optimizada como matriz NumPy.

    Orden de aplicación (importante, no cambiar):
      1. Reducción de ruido    → limpia el grano
      2. Balance de color      → corrige tonos
      3. Brillo y contraste    → mejora la luminosidad
      4. Nitidez               → realza los bordes
    """

    # Hacemos una copia para no modificar la imagen original
    imagen_actual = imagen.copy()

    #  PASO 1: Reducción de ruido 
    if aplicar_reduccion_ruido:
        imagen_actual = reducir_ruido(imagen_actual)

    #  PASO 2: Balance de color 
    imagen_actual = balancear_color(imagen_actual)

    #  PASO 3: Brillo y contraste con CLAHE 
    imagen_actual = ajustar_brillo_contraste(imagen_actual)

    #  PASO 4: Nitidez 
    imagen_actual = mejorar_nitidez(imagen_actual)

    return imagen_actual


def optimizar_archivo(ruta_origen, ruta_destino, aplicar_reduccion_ruido=True):
    """
    Versión "todo en uno" para procesar un archivo del disco.

    Lee la imagen, la optimiza, y la guarda con escritura atómica.

    Devuelve True si todo salió bien, False si hubo algún problema
    (lectura, procesamiento o guardado).
    """

    #  1. Leemos la imagen original 
    imagen = leer_imagen(ruta_origen)

    # Si no se pudo leer, abandonamos
    if imagen is None:
        return False

    #  2. Aplicamos el pipeline de optimización 
    imagen_optimizada = optimizar_imagen_opencv(
        imagen,
        aplicar_reduccion_ruido=aplicar_reduccion_ruido,
    )

    #  3. Guardamos la imagen optimizada 
    # guardar_imagen_cv ahora devuelve True/False según si tuvo éxito
    return guardar_imagen_cv(imagen_optimizada, ruta_destino)