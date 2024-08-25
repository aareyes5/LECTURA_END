import pyaudio
import wave
import keyboard
import speech_recognition as sr
import tensorflow as tf
from tensorflow.keras.models import load_model
import joblib
import numpy as np
import os
import sys
from itertools import combinations

sexo = None
edad = None
valores = []

def leer_valores(ruta):
    """Lee los valores desde el archivo y los almacena en una lista."""
    valores = []
    if os.path.exists(ruta):
        with open(ruta, 'r') as archivo:
            for linea in archivo:
                try:
                    valor = int(linea.strip())
                    valores.append(valor)
                except ValueError:
                    print(f"No se pudo convertir '{linea.strip()}' a entero.")
    return valores

def escribir_valores(ruta, valores):
    """Escribe los valores en el archivo, uno por línea."""
    with open(ruta, 'w') as archivo:
        for valor in valores:
            archivo.write(f"{valor}\n")

def guardar_puntaje_en_datos(datos_file_path, puntaje, pregunta_num):
    """Guarda el puntaje en el archivo de datos especificado."""
    score_text = f"Puntuacion pregunta {pregunta_num}: {puntaje}"
    save_score_if_not_exists(datos_file_path, score_text)

def save_score_if_not_exists(file_path, score_text):
    """Guarda el puntaje si no existe ya en el archivo."""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if score_text in line:
                    print(f"Puntuación '{score_text}' ya existe en el archivo.")
                    return

        with open(file_path, 'a') as file:  # 'a' mode para añadir sin borrar
            file.write(score_text + '\n')
            print(f"Puntuación '{score_text}' agregada al archivo.")

    except FileNotFoundError:
        with open(file_path, 'w') as file:  # Si el archivo no existe, se crea
            file.write(score_text + '\n')
            print(f"Archivo creado y puntuación '{score_text}' agregada.")

def audio_a_texto(file):
    r = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio_data = r.record(source)
        texto = r.recognize_google(audio_data, language='es-ES')
        return texto
    
# Evaluar el texto y asignar un puntaje
def evaluar_texto(texto):
    # Palabras clave para cada nivel de tristeza
    niveles = {
        0: ["duermo bien", "descanso bien", "sueño normal"],
        1: ["ligeramente alterado", "ocasionalmente alterado", "dificultad ocasional para dormir"],
        2: ["a veces despierto", "dificultad para dormir de vez en cuando", "insomnio leve"],
        3: ["dificultad frecuente para dormir", "despertar en medio de la noche", "insomnio moderado"],
        4: ["insomnio severo", "dificultad grave para dormir", "no duermo bien", "despertar temprano"],
        5: ["no puedo dormir", "insomnio extremo", "despertar continuo", "graves problemas de sueño"],
        6: ["totalmente incapaz de dormir", "insomnio desesperado", "trastorno del sueño severo"]
    }
    
    for palabra in palabras:
        for nivel, palabras_clave in niveles.items():
            if palabra in palabras_clave:
                if nivel > max_nivel:
                    max_nivel = nivel

    # Análisis de combinaciones de 2 a n palabras
    for n in range(2, len(palabras) + 1):
        for comb in combinations(palabras, n):
            frase = ' '.join(comb)
            for nivel, palabras_clave in niveles.items():
                for palabra_clave in palabras_clave:
                    if palabra_clave in frase:
                        if nivel > max_nivel:
                            max_nivel = nivel

    return max_nivel

# Cargar el modelo y el scaler
ruta_red = os.path.join(os.path.dirname(__file__),'..','Red','madrs_model.h5')
model = load_model(ruta_red)
scaler = joblib.load(os.path.join(os.path.dirname(__file__),'scaler.pkl'))


# Función para predecir el puntaje de la Pregunta 4
def predecir_puntaje(edad, sexo, puntaje4):
    # Crear un array con las entradas necesarias
    entrada = np.array([[edad, sexo, 0, 0, puntaje4, 0, 0, 0, 0, 0, 0]])  # Los valores de las preguntas 3-10 se inicializan en 0
    entrada_estandarizada = scaler.transform(entrada)
    predicciones = model.predict(entrada_estandarizada)
    puntaje_predicho = predicciones[0][0]  # La predicción de la Pregunta 2 es el primer valor
    print(f'Puntaje predicho sin redondeo: {puntaje_predicho}')
    
    #Codigo para rendondear el puntaje
    if puntaje_predicho < 0:
        puntaje_redondeado = 0
    elif puntaje_predicho > 6:
        puntaje_redondeado = 6
    else:
        decimal = abs(puntaje_predicho) - int(abs(puntaje_predicho))
        if decimal < 0.5:
            puntaje_redondeado = int(puntaje_predicho)
        else:
            puntaje_redondeado = int(puntaje_predicho) + 1
    return puntaje_redondeado

"""
# Capturar audio
print("Presiona 'r' para iniciar la grabación.")
keyboard.wait('r')
grabar_audio()

# Convertir el audio a texto
texto = audio_a_texto(WAVE_OUTPUT_FILENAME)
print(f'Texto del audio: {texto}')
"""

def leer_genero_edad(datos_folder):
    """Leer género y edad del archivo más reciente en la carpeta DATOS."""
    datos_files = sorted([f for f in os.listdir(datos_folder) if f.startswith('Datos_') and f.endswith('.txt')], reverse=True)

    if not datos_files:
        return None, None  # No se encontraron archivos de datos

    latest_file = os.path.join(datos_folder, datos_files[0])

    genero = None
    edad = None

    with open(latest_file, 'r') as file:
        for line in file:
            if line.startswith('Género:'):
                genero = line.split(':')[1].strip()
            elif line.startswith('Edad:'):
                edad = line.split(':')[1].strip()

    return genero, edad  

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python Audio2.py <uuid> <ruta_datos>")
        sys.exit(1)

    user_uuid = sys.argv[1]
    datos_folder = os.path.join(os.path.dirname(__file__), '../../MP4',user_uuid,'Datos/')
    audio_folder = os.path.join(os.path.dirname(__file__), '../../MP4',user_uuid,'Audios/')

    # Identificar el archivo de datos más reciente o crear uno nuevo
    datos_files = [f for f in os.listdir(datos_folder) if f.startswith('Datos_') and f.endswith('.txt')]
    if datos_files:
        datos_files.sort(key=lambda f: int(f.split('_')[1].split('.')[0]))  # Ordenar por el número en el nombre del archivo
        datos_file_path = os.path.join(datos_folder, datos_files[-1])  # Archivo más reciente
    else:
        datos_file_path = os.path.join(datos_folder, 'Datos_1.txt')  # Crear uno nuevo si no existe

    audio_filename = os.path.join(audio_folder, f'Audio_4.wav')

    texto = audio_a_texto(audio_filename)
    puntaje_inicial = evaluar_texto(texto)
    print(f'Puntaje evaluado de la Pregunta 4: {puntaje_inicial}')

    valores = leer_valores(datos_file_path)
    sexo, edad = leer_genero_edad(datos_folder)

    puntaje_predicho = predecir_puntaje(edad, sexo, puntaje_inicial)
    print(f'Puntaje predicho para la Pregunta 4: {puntaje_predicho}')

    # Guardar el puntaje en el archivo de datos del usuario sin borrar los datos existentes
    guardar_puntaje_en_datos(datos_file_path, puntaje_predicho, pregunta_num=4)

