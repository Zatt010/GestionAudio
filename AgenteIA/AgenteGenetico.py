import numpy as np
import random
from scipy.io import wavfile
import librosa
import matplotlib.pyplot as plt
import os
from pydub import AudioSegment

# Parámetros genéticos
TAMANO_POBLACION = 10 
GENERACIONES = 10      
TASA_MUTACION = 0.1    

# Función para crear individuos (configuraciones de compresión y mejora)
def crear_individuo():
    return {
        'bitrate': random.choice([32000, 64000, 96000, 128000, 160000, 192000]),  
        'threshold': random.uniform(-60, -20),
        'ratio': random.uniform(1.5, 5.0),
        'attack': random.uniform(0.01, 0.05),
        'release': random.uniform(0.05, 0.2)
    }

# Función de evaluación del "fitness" de cada individuo
def fitness(individuo, audio_data, sample_rate):
    # Aplicamos compresión y mejora acústica
    processed_audio = aplicar_compresion(audio_data, sample_rate, individuo)
    
    # Guardar el audio comprimido temporalmente en formato MP3 con el bitrate especificado
    save_as_mp3("temp_audio.mp3", processed_audio, sample_rate, individuo['bitrate'])
    compressed_size = os.path.getsize("temp_audio.mp3")

    # Calcular la calidad percibida entre original y procesado
    quality_metric = calcular_calidad(audio_data, processed_audio)

    # Fitness basado en tamaño comprimido y calidad percibida
    return compressed_size * (1 - quality_metric)

# Función de selección de los mejores individuos
def seleccion(poblacion, audio_data, sample_rate):
    return sorted(poblacion, key=lambda x: fitness(x, audio_data, sample_rate))[:2]

# Cruce de dos individuos
def cruce(padre1, padre2):
    hijo = {param: padre1[param] if random.random() > 0.5 else padre2[param] for param in padre1.keys()}
    return hijo

# Mutación en el individuo
def mutacion(individuo):
    mutante = individuo.copy()
    param = random.choice(list(mutante.keys()))
    if param == 'bitrate':
        mutante[param] = random.choice([32000, 64000, 96000, 128000, 160000, 192000])
    elif param == 'threshold':
        mutante[param] = random.uniform(-60, -20)
    elif param == 'ratio':
        mutante[param] = random.uniform(1.5, 5.0)
    elif param == 'attack':
        mutante[param] = random.uniform(0.01, 0.05)
    elif param == 'release':
        mutante[param] = random.uniform(0.05, 0.2)
    return mutante

# Algoritmo genético principal
def algoritmo_genetico(audio_data, sample_rate):
    print("Iniciando el algoritmo genético...")
    poblacion = [crear_individuo() for _ in range(TAMANO_POBLACION)]
    fitness_evolucion = []

    for generacion in range(GENERACIONES):
        print(f"Generación {generacion}/{GENERACIONES}")
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

        if generacion % 2 == 0:
            print(f"Generación {generacion}, Fitness: {fitness(mejor, audio_data, sample_rate)}, Configuración: {mejor}")

    # Graficar la evolución del fitness
    plt.plot(range(GENERACIONES), fitness_evolucion)
    plt.xlabel('Generación')
    plt.ylabel('Mejor Fitness')
    plt.title('Evolución del Fitness a lo Largo de Generaciones')
    plt.show()

    return seleccion(poblacion, audio_data, sample_rate)[0]

# Función para aplicar compresión en audio
def aplicar_compresion(audio_data, sample_rate, individuo):
    threshold = individuo['threshold']
    ratio = individuo['ratio']
    attack = individuo['attack']
    release = individuo['release']

    print(f"Aplicando compresión con threshold: {threshold}, ratio: {ratio}")

    compressed_audio = np.maximum(audio_data - threshold, 0) / ratio
    return compressed_audio

# Función para evaluar la calidad de audio entre original y procesado
def calcular_calidad(original, procesado):
    original = librosa.util.normalize(original)
    procesado = librosa.util.normalize(procesado)
    quality_metric = np.mean(np.abs(original - procesado))
    return quality_metric

# Función para guardar como MP3 con el bitrate especificado
def save_as_mp3(filename, audio_data, sample_rate, bitrate):
    temp_wav = "temp_audio.wav"
    wavfile.write(temp_wav, sample_rate, audio_data.astype(np.int16))
    audio = AudioSegment.from_wav(temp_wav)
    audio.export(filename, format="mp3", bitrate=f"{bitrate // 1000}k")  # Cambiado a 'k' para kilobits
    os.remove(temp_wav)

# Cargar archivo de audio y ejecutar el algoritmo genético
sample_rate, audio_data = wavfile.read("Thisboy.wav")
audio_data = audio_data.astype(float)

# Ejecutar algoritmo genético y obtener la mejor configuración de audio
mejor_configuracion = algoritmo_genetico(audio_data, sample_rate)
print(f"Mejor configuración encontrada: {mejor_configuracion}")

# Aplicar compresión y guardar el resultado como MP3 con el mejor bitrate
audio_procesado = aplicar_compresion(audio_data, sample_rate, mejor_configuracion)
save_as_mp3("audio_procesado.mp3", audio_procesado, sample_rate, mejor_configuracion['bitrate'])

# Prueba de tamaño de archivo
original_size = os.path.getsize("Thisboy.wav")
processed_size = os.path.getsize("audio_procesado.mp3")
print(f"Tamaño original: {original_size / 1024:.2f} KB")
print(f"Tamaño comprimido: {processed_size / 1024:.2f} KB")
