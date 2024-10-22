import webbrowser
import matplotlib.pyplot as plt
from rectpack import newPacker, PackingBin, SORT_AREA, GuillotineBssfMaxas, MaxRectsBssf, MaxRectsBaf
import os
from django.conf import settings
from django.utils.timezone import now
import math


def calcular_cant_etiquetas_por_superficie(ancho_hoja, alto_hoja, ancho_elemento, alto_elemento, separacion, cantidad_deseada, algoritmo):

    cant_elementos_empaquetados = elementos_empaquetados = 0
    mostrar_solapamientos = False
    tipo_vinilo = False
    if alto_hoja == 10000:
        print('Es un vinilo/lona')
        tipo_vinilo = True

    # Empaquetar elementos
    if tipo_vinilo:
        # Si es impresión en material vinilo/lona siempre se van a empaquetar todos los elementos necesarios, solo resta saber que área ocupan.
        cant_elementos_empaquetados = cantidad_deseada
        mostrar_solapamientos = False
        elementos_empaquetados, altura_max_ocupada = empaquetar_elementos_vinilo(
            ancho_hoja, alto_hoja, ancho_elemento, alto_elemento, separacion, algoritmo, cantidad_deseada
        )
        # Verificar si es vinilo y necesita división
        if len(elementos_empaquetados) == 0:
            print('Es un diseño que necesita dividirse')
            mostrar_solapamientos = True
            elementos_empaquetados = dividir_vinilo_en_partes(
                ancho_hoja, alto_elemento, ancho_elemento, separacion)
            # Para estos casos la altura máxima va a ser 2 veces el alto del elemento mas la consideración de la separación y un margen de 5%
            altura_max_ocupada = len(
                elementos_empaquetados) * alto_elemento + 2 * separacion * 1.05
            area_ocupada = altura_max_ocupada * ancho_hoja / 10000

        else:
            print('Es un vinilo sin división')
            area_ocupada = (ancho_hoja * altura_max_ocupada * 1.1) / 10000
    else:
        cant_elementos_empaquetados, elementos_empaquetados = empaquetar_elementos(
            ancho_hoja, alto_hoja, ancho_elemento, alto_elemento, separacion, algoritmo, cantidad_deseada)
        cant_pliegos = math.ceil(
            cantidad_deseada / cant_elementos_empaquetados)

    # Generar gráfico de la hoja con las etiquetas o partes divididas
    if tipo_vinilo:
        grafico_url = generar_grafico_vinilo(
            elementos_empaquetados, ancho_hoja, alto_hoja, separacion, altura_max_ocupada, cantidad_deseada, ancho_elemento, alto_elemento)
    else:
        grafico_url = generar_grafico(
            elementos_empaquetados, ancho_hoja, alto_hoja, separacion, cantidad_deseada, ancho_elemento, alto_elemento)
    if tipo_vinilo:
        return cant_elementos_empaquetados, grafico_url, area_ocupada
    else:
        return cant_elementos_empaquetados, grafico_url, cant_pliegos


def ajustar_elementos(ancho_elemento, alto_elemento, separacion):
    """Ajusta las dimensiones del elemento considerando la separación."""
    ancho_elemento_ajustado = ancho_elemento + separacion
    alto_elemento_ajustado = alto_elemento + separacion
    return ancho_elemento_ajustado, alto_elemento_ajustado


def empaquetar_elementos_vinilo(ancho_hoja, alto_hoja, ancho_elemento, alto_elemento, separacion, algoritmo, cantidad_deseada):
    """Empaqueta los elementos en una hoja y devuelve los elementos empaquetados o detecta si es imposible."""
    ancho_elemento_ajustado, alto_elemento_ajustado = ajustar_elementos(
        ancho_elemento, alto_elemento, separacion)

    packer_area = seleccionar_packer(algoritmo)
    # === Cálculo B: Área ocupada por la cantidad exacta de elementos ===

    # Alto arbitrario para permitir varias filas (alto_hoja=10000)
    packer_area.add_bin(ancho_hoja, alto_hoja)

    # Empaquetamos solo la cantidad solicitada
    for _ in range(cantidad_deseada):
        packer_area.add_rect(ancho_elemento_ajustado, alto_elemento_ajustado)

    # Empaquetamos los elementos para el Cálculo B
    packer_area.pack()

    elementos_area = []

    for abin in packer_area:
        for rect in abin:
            rectangulo_ajustado = (
                rect.x, rect.y, rect.width - separacion, rect.height - separacion)
            elementos_area.append(rectangulo_ajustado)

    # Calcular la altura máxima ocupada por las etiquetas en este empaquetado
    altura_max_ocupada = 0
    for rect in elementos_area:
        altura_max_ocupada = max(
            altura_max_ocupada, rect[1] + rect[3] + separacion / 2)

    return elementos_area, altura_max_ocupada


def empaquetar_elementos(ancho_hoja, alto_hoja, ancho_elemento, alto_elemento, separacion, algoritmo, cantidad_deseada):
    """Empaqueta los elementos en una hoja y devuelve los elementos empaquetados o detecta si es imposible."""
    ancho_elemento_ajustado, alto_elemento_ajustado = ajustar_elementos(
        ancho_elemento, alto_elemento, separacion)

    packer = seleccionar_packer(algoritmo)
    # === Cálculo A: Cuántos elementos entran en un pliego ===

    # Creamos un emboltorio (bin) con las dimensiones de la hoja
    packer.add_bin(ancho_hoja, alto_hoja)

    # Agregamos muchos elementos para ver cuántos caben
    # Un número grande para determinar la capacidad total del pliego
    num_elementos_a_empaquetar = 10000
    for _ in range(num_elementos_a_empaquetar):
        packer.add_rect(ancho_elemento_ajustado, alto_elemento_ajustado)
    # Empaquetamos los elementos para el Cálculo A
    packer.pack()

    # Iniciamos una lista para almacenar las etiquetas empaquetadas
    elementos_empaquetados = []
    for abin in packer:
        for rect in abin:
            rectangulo_ajustado = (
                rect.x, rect.y, rect.width - separacion, rect.height - separacion)
            elementos_empaquetados.append(rectangulo_ajustado)

    # Usamos len para averiguar cuantos elementos entraron en un pliego
    cant_elementos_empaquetados = len(elementos_empaquetados)

    return cant_elementos_empaquetados, elementos_empaquetados


def dividir_vinilo_en_partes(ancho_hoja, alto_elemento, ancho_elemento, separacion):
    """
    Divide un vinilo en partes, sin considerar solapamientos por ahora.
    margen_reserva es la cantidad de centímetros que dejamos de reserva en cada lado.
    """
    # Margen de reserva en cada lado
    margen_reserva = 1
    repeticion_solapamiento = 2
    ancho_disponible = ancho_hoja - 2 * margen_reserva
    # Calculamos cuántas divisiones serán necesarias
    num_partes = math.ceil(ancho_elemento / ancho_disponible)

    # Inicializamos la lista de partes
    partes = []

    # Ancho inicial
    ancho_restante = ancho_elemento

    # Calcular la primera parte
    parte_ancho = min(ancho_disponible, ancho_restante)
    parte_y = 0  # La posición Y de la primera parte
    partes.append((margen_reserva, parte_y, parte_ancho,
                  alto_elemento, f'{parte_ancho}x{alto_elemento} cm'))

    # Actualizar ancho restante
    ancho_restante -= parte_ancho

    # Comenzar a calcular las partes subsecuentes
    for i in range(1, num_partes):
        if ancho_restante > 0:
            if i < num_partes - 1:  # Si no es la última parte
                # Mantener ancho constante
                parte_ancho = min(ancho_disponible, ancho_restante)
                parte_y = i * (alto_elemento + separacion)
                partes.append((margen_reserva, parte_y, parte_ancho,
                              alto_elemento, f'{parte_ancho}x{alto_elemento} cm'))
                ancho_restante -= parte_ancho  # Restar el ancho usado
                # Restar el solapamiento para la siguiente parte
                ancho_restante -= repeticion_solapamiento
            else:  # Última parte
                parte_ancho = ancho_restante + repeticion_solapamiento * \
                    (1 + i)  # +2 para el solapamiento
                parte_y = i * (alto_elemento + separacion)
                partes.append((margen_reserva, parte_y, parte_ancho,
                              alto_elemento, f'{parte_ancho}x{alto_elemento} cm'))

    return partes


def generar_grafico_vinilo(elementos_empaquetados, ancho_hoja, alto_hoja, separacion, altura_max_ocupada=0, cantidad_deseada=0, ancho_elemento=0, alto_elemento=0):
    fig, ax = plt.subplots()
    ax.set_xlim(0, ancho_hoja)
    alto_hoja_area = altura_max_ocupada * 1.1  # Añadimos un 10% de margen
    elementos = elementos_empaquetados
    ax.set_ylim(0, alto_hoja_area)

    # Fondo blanco del gráfico
    ax.add_patch(plt.Rectangle((0, 0), ancho_hoja,
                 alto_hoja_area, color='white', alpha=0.5))

    # Lista para las etiquetas de dimensiones de los rectángulos (solo si es necesario)
    leyenda_dimensiones = []
    leyenda_requerida = False

    # Dibujar los elementos empaquetados
    for i, rect in enumerate(elementos_empaquetados):
        rect_x = rect[0]  # Posición X de la parte
        rect_y = rect[1]  # Posición Y de la parte
        rect_ancho = rect[2]  # Ancho del rectángulo
        rect_alto = rect[3]  # Alto del rectángulo
        # Etiqueta con dimensiones
        etiqueta = rect[4] if len(rect) == 5 else f'{i+1}'

        # Dibujamos el rectángulo
        ax.add_patch(plt.Rectangle((rect_x, rect_y), rect_ancho, rect_alto,
                     fill=True, edgecolor='blue', facecolor='green', alpha=0.5))

        # Añadimos el texto de la etiqueta en el centro del rectángulo
        text_x = rect_x + rect_ancho / 2
        text_y = rect_y + rect_alto / 2
        ax.text(text_x, text_y, str(i + 1), ha='center',
                va='center', fontsize=10, color='white')

        # Solo agregamos la etiqueta a la leyenda si es diferente (len == 5)
        if len(rect) == 5:
            leyenda_dimensiones.append(
                f"{i + 1}: {etiqueta}")
            leyenda_requerida = True
            if i != 0:
                ax.add_patch(plt.Rectangle((rect_x, rect_y), 2, rect_alto,
                                           fill=True, edgecolor='red', facecolor='lightcoral', alpha=0.5))

    ax.set_aspect('equal', adjustable='box')
    plt.gca().invert_yaxis()

    # Generamos la leyenda si es necesaria
    if leyenda_requerida:
        leyenda_texto = "\n".join(leyenda_dimensiones)
        # Colocamos la leyenda al costado del gráfico
        plt.figtext(0.65, 0.5, leyenda_texto, ha="left", fontsize=10, bbox={
                    "facecolor": "white", "alpha": 0.5, "pad": 5})

    plt.title(
        f'Cantidad deseada: {cantidad_deseada}, Ancho: {ancho_elemento}, Alto: {alto_elemento}, Separación: {separacion}.')

    # Guardar el gráfico
    timestamp_str = now().strftime("%Y%m%d_%H%M%S")
    img_filename = f'surface_{timestamp_str}.png'
    relative_path = 'presupuestos/graficos/' + img_filename
    save_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    grafico_url = settings.MEDIA_URL + relative_path
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)

    return grafico_url


def generar_grafico(elementos_empaquetados, ancho_hoja, alto_hoja, separacion, cantidad_deseada=0, ancho_elemento=0, alto_elemento=0):
    """Genera el gráfico de los elementos empaquetados o partes divididas, con etiquetas numeradas y, si es necesario, áreas solapadas."""
    fig, ax = plt.subplots()
    ax.set_xlim(0, ancho_hoja)

    elementos = elementos_empaquetados
    ax.set_ylim(0, alto_hoja)
    rect = plt.Rectangle((0, 0), ancho_hoja, alto_hoja,
                         color='white', alpha=0.5)

    # Crea un rectángulo para representar la superficie de la hoja
    rect = plt.Rectangle((0, 0), ancho_hoja, alto_hoja,
                         color='white', alpha=0.5)
    ax.add_patch(rect)

    # Dibujar los elementos
    for i, rect in enumerate(elementos):
        rect_x = rect[0] + separacion / 2
        rect_y = rect[1] + separacion / 2
        ax.add_patch(plt.Rectangle(
            (rect_x, rect_y), rect[2], rect[3], fill=True, edgecolor='blue', facecolor='green', alpha=0.5))

        # Calcula la posición del texto
        text_x = rect_x + rect[2] / 2  # Centrado en el ancho del rectángulo
        text_y = rect_y + rect[3] / 2  # Centrado en la altura del rectángulo

        # Establece el tamaño del texto en función del tamaño del rectángulo
        # Ajusta el tamaño del texto
        font_size = max(8, min(20, int(min(rect[2], rect[3]) / 3)))

        # Dibuja el número dentro del rectángulo
        ax.text(text_x, text_y, str(i + 1), ha='center',
                va='center', fontsize=font_size, color='white')

    ax.set_aspect('equal', adjustable='box')
    plt.gca().invert_yaxis()

    plt.title(
        f'Cantidad deseada: {cantidad_deseada}, Ancho: {ancho_elemento}, Alto: {alto_elemento}, Separación: {separacion}.')
    # Guardar el gráfico
    timestamp_str = now().strftime("%Y%m%d_%H%M%S")
    img_filename = f'surface_{timestamp_str}.png'
    relative_path = 'presupuestos/graficos/' + img_filename
    save_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    grafico_url = settings.MEDIA_URL + relative_path
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)
    return grafico_url


def seleccionar_packer(algoritmo):
    """Selecciona y retorna el packer según el algoritmo elegido."""
    if algoritmo == 'Guillotine':
        return newPacker(pack_algo=GuillotineBssfMaxas, sort_algo=SORT_AREA, rotation=True)
    elif algoritmo == 'MaxRects':
        return newPacker(pack_algo=MaxRectsBaf, sort_algo=SORT_AREA, rotation=True)
    else:
        # Por defecto
        return newPacker(pack_algo=GuillotineBssfMaxas, sort_algo=SORT_AREA, rotation=True)
