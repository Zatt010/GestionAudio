import numpy as np
import random
from scipy.io import wavfile
import librosa
import matplotlib.pyplot as plt
import os
from pydub import AudioSegment

TAMANO_POBLACION = 10
GENERACIONES = 10
TASA_MUTACION = 0.2

def crear_individuo():
    return {
        'bitrate': random.choice([32000, 64000, 96000, 128000, 160000, 192000]),
        'threshold': random.uniform(-60, -20),
        'ratio': random.uniform(1.5, 5.0),
        'attack': random.uniform(0.01, 0.05),
        'release': random.uniform(0.05, 0.2)
    }

def fitness(individuo, audio_data, sample_rate):
    processed_audio = aplicar_compresion(audio_data, sample_rate, individuo)
    save_as_mp3("temp_audio.mp3", processed_audio, sample_rate, individuo['bitrate'])
    compressed_size = os.path.getsize("temp_audio.mp3")
    quality_metric = calcular_calidad(audio_data, processed_audio)
    return compressed_size * (1 - quality_metric)

def seleccion(poblacion, audio_data, sample_rate):
    return sorted(poblacion, key=lambda x: fitness(x, audio_data, sample_rate))[:2]

def cruce(padre1, padre2):
    return {param: padre1[param] if random.random() > 0.5 else padre2[param] for param in padre1.keys()}

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

def algoritmo_genetico(audio_data, sample_rate):
    print("Iniciando el algoritmo genético...")
    poblacion = [crear_individuo() for _ in range(TAMANO_POBLACION)]
    fitness_evolucion = []

    for generacion in range(GENERACIONES):
        print(f"Generación {generacion}/{GENERACIONES}")
        padres = seleccion(poblacion, audio_data, sample_rate)
        nueva_poblacion = [cruce(*padres) if random.random() >= TASA_MUTACION else mutacion(cruce(*padres)) for _ in range(TAMANO_POBLACION)]

        poblacion = nueva_poblacion
        mejor = seleccion(poblacion, audio_data, sample_rate)[0]
        fitness_evolucion.append(fitness(mejor, audio_data, sample_rate))

        if generacion % 2 == 0:
            print(f"Generación {generacion}, Fitness: {fitness(mejor, audio_data, sample_rate)}, Configuración: {mejor}")

    plt.plot(range(GENERACIONES), fitness_evolucion)
    plt.xlabel('Generación')
    plt.ylabel('Mejor Fitness')
    plt.title('Evolución del Fitness a lo Largo de Generaciones')
    plt.show()

    return seleccion(poblacion, audio_data, sample_rate)[0]

def aplicar_compresion(audio_data, sample_rate, individuo):
    threshold = individuo['threshold']
    ratio = individuo['ratio']
    attack = individuo['attack']
    release = individuo['release']

    print(f"Aplicando compresión con threshold: {threshold}, ratio: {ratio}")

    audio_data = np.clip(audio_data, -1, 1)
    gain_reduction = np.maximum(0, audio_data - threshold) / ratio
    compressed_audio = audio_data - gain_reduction
    compressed_audio = librosa.util.normalize(compressed_audio)

    print("Nivel de amplitud promedio después de compresión:", np.mean(np.abs(compressed_audio)))

    return compressed_audio

def calcular_calidad(original, procesado):
    original = librosa.util.normalize(original)
    procesado = librosa.util.normalize(procesado)
    return np.mean(np.abs(original - procesado))

def save_as_mp3(filename, audio_data, sample_rate, bitrate):
    temp_wav = "temp_audio.wav"
    audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)
    wavfile.write(temp_wav, sample_rate, audio_data)
    audio = AudioSegment.from_wav(temp_wav)
    audio.export(filename, format="mp3", bitrate=f"{bitrate // 1000}k")
    os.remove(temp_wav)

sample_rate, audio_data = wavfile.read("Thisboy.wav")
audio_data = librosa.util.normalize(audio_data.astype(float))

mejor_configuracion = algoritmo_genetico(audio_data, sample_rate)
print(f"Mejor configuración encontrada: {mejor_configuracion}")

audio_procesado = aplicar_compresion(audio_data, sample_rate, mejor_configuracion)
save_as_mp3("audio_procesado.mp3", audio_procesado, sample_rate, mejor_configuracion['bitrate'])

original_size = os.path.getsize("Thisboy.wav")
processed_size = os.path.getsize("audio_procesado.mp3")
print(f"Tamaño original: {original_size / 1024:.2f} KB")
print(f"Tamaño comprimido: {processed_size / 1024:.2f} KB")
