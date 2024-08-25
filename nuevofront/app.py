from flask import Flask, request, send_from_directory, jsonify, make_response
import os
import shutil
import subprocess
import uuid

app = Flask(__name__)

def create_user_directory():
    user_uuid = request.cookies.get('user_uuid')

    if not user_uuid:
        user_uuid = str(uuid.uuid4())
    
    user_folder = os.path.join('MP4', user_uuid)
    videos_folder = os.path.join(user_folder, 'Videos')
    audios_folder = os.path.join(user_folder, 'Audios')
    imagenes_folder = os.path.join(user_folder, 'Imagenes')
    datos_folder = os.path.join(user_folder, 'Datos')
    
    os.makedirs(videos_folder, exist_ok=True)
    os.makedirs(audios_folder, exist_ok=True)
    os.makedirs(imagenes_folder, exist_ok=True)
    os.makedirs(datos_folder, exist_ok=True)
    
    return user_uuid, videos_folder, audios_folder, imagenes_folder, datos_folder

@app.route('/')
def index():
    user_uuid, videos_folder, audios_folder, imagenes_folder, datos_folder = create_user_directory()

    response = make_response(send_from_directory('frontend', 'index.html'))
    response.set_cookie('user_uuid', user_uuid, max_age=3600)  # Almacenar el UUID en una cookie

    return response

@app.route('/<path:path>', methods=['GET'])
def static_files(path):
    return send_from_directory('frontend', path)

@app.route('/upload', methods=['POST'])
def upload_file():
    user_uuid = request.cookies.get('user_uuid')
    if not user_uuid:
        return 'UUID is required', 400
    
    videos_folder = os.path.join('MP4', user_uuid, 'Videos')
    audios_folder = os.path.join('MP4', user_uuid, 'Audios')
    datos_folder = os.path.join('MP4', user_uuid, 'Datos')

    if 'video' not in request.files:
        return 'No video file part', 400

    file = request.files['video']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        question_number = request.form.get('question_number')
        if not question_number:
            return 'Question number is required', 400

        filename = f'Video_{question_number}.mp4'
        file_path = os.path.join(videos_folder, filename)
        file.save(file_path)
        print(f"Video for question {question_number} saved at {file_path}")

        # Extraer el audio del video guardado usando ffmpeg
        try:
            audio_filename = f'Audio_{question_number}.wav'
            audio_path = os.path.join(audios_folder, audio_filename)
            ffmpeg_command = [
                'ffmpeg',
                '-i', file_path,
                '-q:a', '0',
                '-map', 'a',
                audio_path
            ]
            subprocess.run(ffmpeg_command, check=True)
            print(f"Audio extracted and saved at {audio_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio with ffmpeg: {e}")
            return 'Error processing video file', 500

        # Verificar si es la última pregunta y si ambos archivos existen
        if int(question_number) == 10:
            video_path = os.path.join(videos_folder, f'Video_10.mp4')
            audio_path = os.path.join(audios_folder, f'Audio_10.wav')
            lock_file_path = os.path.join(datos_folder, 'processing.lock')

            if os.path.exists(video_path) and os.path.exists(audio_path):
                if not os.path.exists(lock_file_path):
                    open(lock_file_path, 'w').close()
                    print("Processing started...")

                    try:
                        # Ejecutar el script de procesamiento
                        subprocess.run(["python", "modulo_procesamiento/procesar_videos.py", user_uuid], check=True)
                        print("Processing 1 completed successfully.")
                        subprocess.run(["python", "modulo_procesamiento/Audios/Audio2.py", user_uuid], check=True)                        
                        print("Processing 2 completed successfully.")
                        subprocess.run(["python", "modulo_procesamiento/Audios/Audio3.py", user_uuid], check=True)                        
                        print("Processing 3 completed successfully.")
                       
                        subprocess.run(["python", "modulo_procesamiento/Audios/Audio4.py", user_uuid], check=True)                        
                        print("Processing 4 completed successfully.")
                        subprocess.run(["python", "modulo_procesamiento/Audios/Audio5.py", user_uuid], check=True)                        
                        print("Processing 5 completed successfully.")
                        
                        subprocess.run(["python", "modulo_procesamiento/Audios/Audio6.py", user_uuid], check=True)                        
                        print("Processing 6 completed successfully.")
                        subprocess.run(["python", "modulo_procesamiento/Audios/Audio7.py", user_uuid], check=True)                        
                        print("Processing 7 completed successfully.")
                     
                        subprocess.run(["python", "modulo_procesamiento/Audios/Audio8.py", user_uuid], check=True)                        
                        print("Processing 8 completed successfully.")
                        subprocess.run(["python", "modulo_procesamiento/Audios/Audio9.py", user_uuid], check=True)                        
                        print("Processing 9 completed successfully.")
                        subprocess.run(["python", "modulo_procesamiento/Audios/Audio10.py", user_uuid], check=True)                        
                        print("Processing 10 completed successfully.")
                    except subprocess.CalledProcessError as e:
                        print(f"Error during processing: {e}")
                    finally:
                        os.remove(lock_file_path)
                        print("Lock file removed.")
                else:
                    print("Processing is already running or has been completed.")
            else:
                print("Waiting for both video and audio files to be uploaded for question 10.")

        return 'Video uploaded and audio extracted successfully', 200

def borrar_contenido_carpeta(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Error al eliminar {file_path}: {e}')

@app.route('/borrar-contenido', methods=['POST'])
def borrar_contenido():
    user_uuid = request.cookies.get('user_uuid')
    if not user_uuid:
        return 'UUID is required', 400
    
    videos_folder = os.path.join('MP4', user_uuid, 'Videos')
    audios_folder = os.path.join('MP4', user_uuid, 'Audios')
    imagenes_folder = os.path.join('MP4', user_uuid, 'Imagenes')

    try:
        borrar_contenido_carpeta(videos_folder)
        borrar_contenido_carpeta(audios_folder)
        borrar_contenido_carpeta(imagenes_folder)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/guardar-datos', methods=['POST'])
def guardar_datos():
    user_uuid = request.cookies.get('user_uuid')
    if not user_uuid:
        return 'UUID is required', 400
    datos_folder = os.path.join('MP4', user_uuid, 'Datos')
    
    try:
        existing_files = [f for f in os.listdir(datos_folder) if f.startswith('Datos_') and f.endswith('.txt')]

        max_number = 0
        for file in existing_files:
            try:
                file_number = int(file[6:-4])
                if file_number > max_number:
                    max_number = file_number
            except ValueError:
                continue

        new_file_number = max_number + 1
        filename = f'Datos_{new_file_number}.txt'

        data = request.json
        age = data.get('age')
        gender = data.get('gender')

        datos_file_path = os.path.join(datos_folder, filename)
        with open(datos_file_path, 'w') as file:
            file.write(f"Género: {gender}\n")
            file.write(f"Edad: {age}\n")

        return jsonify({'success': True, 'filename': filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calcular-puntaje', methods=['GET'])
def calcular_puntaje():
    user_uuid = request.cookies.get('user_uuid')
    if not user_uuid:
        return 'UUID is required', 400
    datos_folder = os.path.join('MP4', user_uuid, 'Datos')
    
    try:
        datos_files = sorted([f for f in os.listdir(datos_folder) if f.startswith('Datos_') and f.endswith('.txt')], reverse=True)

        if not datos_files:
            return jsonify({'error': 'No se encontraron archivos de datos.'}), 404

        latest_file = os.path.join(datos_folder, datos_files[0])
        total_score = 0

        with open(latest_file, 'r') as file:
            for line in file:
                if line.startswith('Puntuacion pregunta'):
                    try:
                        score = int(line.split(':')[-1].strip())
                        total_score += score
                    except ValueError:
                        continue

        return jsonify({'success': True, 'total_score': total_score}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start-test', methods=['POST'])
def start_test():
    try:
        user_uuid, videos_folder, audios_folder, imagenes_folder, datos_folder = create_user_directory()
        return jsonify({'uuid': user_uuid}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
