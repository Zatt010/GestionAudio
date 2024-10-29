import numpy as np
import random
from scipy.io import wavfile
from scipy import signal
import librosa
import matplotlib.pyplot as plt
import os

# Parametros geneticos
TAMANO_POBLACION = 10
GENERACIONES = 100
TASA_MUTACION = 0.1

# Funcion para crear individuos (configuraciones de compresión y mejora)
def crear_individuo():
    return {
        'bitrate': random.choice([32, 64, 128, 256, 320]),
        'threshold': random.uniform(-60, 0),  
        'ratio': random.uniform(1.0, 10.0),  
        'attack': random.uniform(0.001, 0.1),  
        'release': random.uniform(0.01, 0.5)
    }

# Funcion de evaluación del "fitness" de cada individuo
def fitness(individuo, audio_data, sample_rate):
    # Aplicamos compresion y mejora acustica
    processed_audio = aplicar_compresion(audio_data, sample_rate, individuo)
    size_metric = len(processed_audio)
    quality_metric = calcular_calidad(audio_data, processed_audio)
    return size_metric * (1 - quality_metric)

# Funcion de selección de los mejores individuos
def seleccion(poblacion, audio_data, sample_rate):
    return sorted(poblacion, key=lambda x: fitness(x, audio_data, sample_rate))[:2]

# Cruce de dos individuos
def cruce(padre1, padre2):
    hijo = {param: padre1[param] if random.random() > 0.5 else padre2[param] for param in padre1.keys()}
    return hijo

# Mutacion de un individuo
def mutacion(individuo):
    mutante = individuo.copy()
    param = random.choice(list(mutante.keys()))
    if param == 'bitrate':
        mutante[param] = random.choice([32, 64, 128, 256, 320])
    elif param == 'threshold':
        mutante[param] = random.uniform(-60, 0)
    elif param == 'ratio':
        mutante[param] = random.uniform(1.0, 10.0)
    elif param == 'attack':
        mutante[param] = random.uniform(0.001, 0.1)
    elif param == 'release':
        mutante[param] = random.uniform(0.01, 0.5)
    return mutante

# Algoritmo genético principal con evolucion del fitness
def algoritmo_genetico(audio_data, sample_rate):
    poblacion = [crear_individuo() for _ in range(TAMANO_POBLACION)]
    fitness_evolucion = []

    for generacion in range(GENERACIONES):
        padres = seleccion(poblacion, audio_data, sample_rate)
        nueva_poblacion = []

        for _ in range(TAMANO_POBLACION):
            hijo = cruce(*padres)
            if random.random() < TASA_MUTACION:
                hijo = mutacion(hijo)
            nueva_poblacion.append(hijo)

        poblacion = nueva_poblacion
        mejor = seleccion(poblacion, audio_data, sample_rate)[0]
        fitness_evolucion.append(fitness(mejor, audio_data, sample_rate))

        if generacion % 10 == 0:
            print(f"Generación {generacion}, Fitness: {fitness(mejor, audio_data, sample_rate)}, Configuración: {mejor}")

    # Graficar la evolucion del fitness
    plt.plot(range(GENERACIONES), fitness_evolucion)
    plt.xlabel('Generación')
    plt.ylabel('Mejor Fitness')
    plt.title('Evolución del Fitness a lo Largo de Generaciones')
    plt.show()

    return seleccion(poblacion, audio_data, sample_rate)[0]

# Funcion para aplicar compresion en audio
def aplicar_compresion(audio_data, sample_rate, individuo):
    threshold = individuo['threshold']
    ratio = individuo['ratio']
    attack = individuo['attack']
    release = individuo['release']

    compressed_audio = signal.lfilter([1], [1, -0.99], np.maximum(audio_data - threshold, 0) / ratio)
    return compressed_audio

# Funcion para evaluar la calidad de audio entre original y procesado
def calcular_calidad(original, procesado):
    try:
        original = librosa.util.normalize(original)
        procesado = librosa.util.normalize(procesado)
        quality_metric = np.mean(np.abs(original - procesado))
        return quality_metric
    except Exception as e:
        print(f"Error en la evaluación de calidad: {e}")
        return 1

# Cargar archivo de audio y ejecutar el algoritmo genetico
sample_rate, audio_data = wavfile.read("archivo_audio.wav")
audio_data = audio_data.astype(float)

# Ejecutar algoritmo genetico y obtener la mejor configuracion de audio
mejor_configuracion = algoritmo_genetico(audio_data, sample_rate)
print(f"Mejor configuración encontrada: {mejor_configuracion}")

# Aplicar compresion
audio_procesado = aplicar_compresion(audio_data, sample_rate, mejor_configuracion)
wavfile.write("audio_procesado.wav", sample_rate, audio_procesado.astype(np.int16))

# Prueba de tamano de archivo
original_size = os.path.getsize("archivo_audio.wav")
processed_size = os.path.getsize("audio_procesado.wav")
print(f"Tamaño original: {original_size / 1024:.2f} KB")
print(f"Tamaño comprimido: {processed_size / 1024:.2f} KB")
