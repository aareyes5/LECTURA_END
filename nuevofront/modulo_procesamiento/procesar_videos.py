#procesar_videos.py
import cv2
import os
from deepface import DeepFace
import uuid
import sys

class FrameExtractor:
    def __init__(self, video_folder, output_folder, frame_skip=12, image_extension=('.jpg')):
        self.video_folder = video_folder
        self.output_folder = output_folder
        self.frame_skip = frame_skip
        self.image_extension = image_extension
        self.processed_videos = set()  # Mantener un registro de los videos procesados para evitar duplicados

    def extract_frames(self):
        video_files = [f for f in os.listdir(self.video_folder) if f.endswith('.mp4')]
        image_count = 1  # Contador para nombrar las imágenes secuencialmente
        for video_file in video_files:
            if video_file not in self.processed_videos:  # Evitar procesar el mismo video dos veces
                video_path = os.path.join(self.video_folder, video_file)
                image_count = self._process_video(video_path, image_count)
                self.processed_videos.add(video_file)  # Marcar el video como procesado

    def _process_video(self, video_path, image_count):
        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Guardar el frame si cumple la condición de salto
            if frame_count % self.frame_skip == 0:
                img_filename = os.path.join(self.output_folder, f"Imagen{image_count}.jpg")
                cv2.imwrite(img_filename, frame)
                image_count += 1

            frame_count += 1

        cap.release()
        print(f"Frames extracted from {video_path} and saved successfully!")
        return image_count

    def run_deep_face_script(self, datos_file_path):
        os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
        acumulado = 0
        num_images = len([f for f in os.listdir(self.output_folder) if f.lower().endswith(tuple(self.image_extension))])

        for i in range(1, num_images + 1):
            image_path = f"Imagen{i}.jpg"
            full_image_path = os.path.join(self.output_folder, image_path)
            img = cv2.imread(full_image_path)

            try:
                emotion_result = DeepFace.analyze(img_path=full_image_path, actions=['emotion'], enforce_detection=False)
                dominant_emotion = emotion_result[0]['dominant_emotion']
            except Exception as e:
                dominant_emotion = None
                print(f"Error analyzing image {full_image_path}: {e}")

            puntuacion = 0
            if dominant_emotion == "sad":
                puntuacion = 1

            acumulado += puntuacion

        final_score = (acumulado * 6) / num_images if num_images > 0 else 0
        puntuacion = round(final_score)

        # Guardar la puntuación usando la nueva función
        self._guardar_puntuacion_en_datos(datos_file_path, puntuacion)

    def _guardar_puntuacion_en_datos(self, datos_file_path, puntuacion):
        score_text = f"Puntuacion pregunta 1: {puntuacion}"
        save_score_if_not_exists(datos_file_path, score_text)  # Usar la función para guardar la puntuación

def save_score_if_not_exists(file_path, score_text):
    try:
        # Leer el archivo y comprobar si ya existe la puntuación
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if score_text in line:
                    print(f"Puntuación '{score_text}' ya existe en el archivo.")
                    return  # Salir de la función si ya existe

        # Si no se encuentra la puntuación, agregarla al archivo
        with open(file_path, 'a') as file:
            file.write(score_text + '\n')
            print(f"Puntuación '{score_text}' agregada al archivo.")

    except FileNotFoundError:
        # Si el archivo no existe, crear uno nuevo y escribir la puntuación
        with open(file_path, 'w') as file:
            file.write(score_text + '\n')
            print(f"Archivo creado y puntuación '{score_text}' agregada.")

if __name__ == "__main__":
   
    if len(sys.argv) < 2:
        print("Error: UUID not provided.")
        sys.exit(1)

    user_uuid = sys.argv[1]
   
   
    video_folder = os.path.join(os.path.dirname(__file__), '../MP4',user_uuid,'Videos/')
    output_folder = os.path.join(os.path.dirname(__file__), '../MP4',user_uuid,'Imagenes/')
    datos_folder = os.path.join(os.path.dirname(__file__), '../MP4',user_uuid,'Datos/')

    # Encontrar el archivo de datos más reciente que siga el formato Datos_(#).txt
    datos_files = [f for f in os.listdir(datos_folder) if f.startswith('Datos_') and f[6:-4].isdigit()]
    datos_files.sort(key=lambda f: int(f[6:-4]))  # Ordenar por el número en el nombre del archivo
    datos_file_path = os.path.join(datos_folder, datos_files[-1]) if datos_files else os.path.join(datos_folder, 'Datos_1.txt')

    extractor = FrameExtractor(video_folder, output_folder, frame_skip=5)
    extractor.extract_frames()
    extractor.run_deep_face_script(datos_file_path)
