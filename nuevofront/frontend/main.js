let currentQuestion = 0;
const questions = [
    "Pregunta 2: ¿Has sentido tristeza recientemente?",
    "Pregunta 3: ¿Tienes dificultades para dormir?",
    "Pregunta 4: ¿Te sientes fatigado?",
    "Pregunta 5: ¿Tienes pensamientos negativos?",
    "Pregunta 6: ¿Has perdido interés en actividades que solías disfrutar?",
    "Pregunta 7: ¿Te sientes ansioso?",
    "Pregunta 8: ¿Has tenido cambios en el apetito?",
    "Pregunta 9: ¿Te sientes desesperanzado?",
    "Pregunta 10: ¿Has considerado hacerte daño?"
];

const videoElement = document.getElementById('videoElement');
const startTestBtn = document.getElementById('startTestBtn');
const userFormDialog = document.getElementById('userFormDialog');
const testSection = document.getElementById('testSection');
const questionDisplay = document.getElementById('questionDisplay');
const nextQuestionBtn = document.getElementById('nextQuestionBtn');
const completionDialog = document.getElementById('completionDialog');
const viewScoreBtn = document.getElementById('viewScoreBtn');
const scoreDialog = document.getElementById('scoreDialog');
const scoreDisplay = document.getElementById('scoreDisplay');

viewScoreBtn.addEventListener('click', fetchAndDisplayScore);

let mediaRecorderVideo;
let mediaRecorderAudio;
let videoChunks = [];
let audioChunks = [];

function startTest() {
    currentQuestion = 0;
    userFormDialog.style.display = 'flex';
    
}

function showQuestion() {
    questionDisplay.textContent = questions[currentQuestion];
}

function nextQuestion() {
    stopRecording(); // Detener la grabación de la pregunta anterior

    currentQuestion++;
    if (currentQuestion < questions.length) {
        showQuestion();
        startRecording(); // Iniciar la grabación para la siguiente pregunta
    } else {
        completeTest();
    }
}

function startRecording() {
    // Start video recording
    mediaRecorderVideo = new MediaRecorder(videoElement.srcObject);
    mediaRecorderVideo.ondataavailable = (event) => {
        videoChunks.push(event.data);
    };
    mediaRecorderVideo.onstop = () => {
        const videoBlob = new Blob(videoChunks, { type: 'video/mp4' });
        uploadFile(videoBlob, 'video', currentQuestion + 1);
        videoChunks = [];
    };
    mediaRecorderVideo.start();

    // Start audio recording
    navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorderAudio = new MediaRecorder(stream);
        mediaRecorderAudio.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        mediaRecorderAudio.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
            uploadFile(audioBlob, 'audio', currentQuestion + 1);
            audioChunks = [];
        };
        mediaRecorderAudio.start();
    })
    .catch(error => {
        console.error('Error accessing audio:', error);
    });
}

function stopRecording() {
    if (mediaRecorderVideo) mediaRecorderVideo.stop();
    if (mediaRecorderAudio) mediaRecorderAudio.stop();
}

function uploadFile(blob, type, questionNumber) {
    const formData = new FormData();
    formData.append(type, blob);
    formData.append('question_number', questionNumber);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            console.log(`${type.charAt(0).toUpperCase() + type.slice(1)} uploaded successfully`);
        } else {
            console.error(`Failed to upload ${type}`);
        }
    })
    .catch(error => {
        console.error(`Error uploading ${type}:`, error);
    });
}

function submitUserForm() {
    const age = document.getElementById('age').value;
    const gender = document.getElementById('gender').value;
    const ageError = document.getElementById('ageError');
    const genderError = document.getElementById('genderError');

    let valid = true;
    if (age < 5 || age > 65 || !age) {
        ageError.textContent = "La edad debe estar entre 5 y 65 años.";
        valid = false;
    } else {
        ageError.textContent = "";
    }

    if (!gender) {
        genderError.textContent = "Selecciona un género.";
        valid = false;
    } else {
        genderError.textContent = "";
    }

    if (valid) {
        fetch('/guardar-datos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ age, gender })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                userFormDialog.style.display = 'none';
                testSection.classList.remove('hidden');
                showQuestion();
                fetch('/borrar-contenido', { method: 'POST' }); // Borra el contenido existente
                startRecording(); // Inicia la grabación para la primera pregunta
            } else {
                console.error('Error al guardar los datos:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function completeTest() {
    testSection.classList.add('hidden');
    completionDialog.style.display = 'flex';
    viewScoreBtn.disabled = false;
}

function closeCompletionDialog() {
    completionDialog.style.display = 'none';
}

function viewScore() {
    scoreDialog.style.display = 'flex';
}

function closeScoreDialog() {
    scoreDialog.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then((stream) => {
        videoElement.srcObject = stream;
    })
    .catch((error) => {
        console.error('Error accessing webcam and microphone:', error);
    });
});

function fetchAndDisplayScore() {
    fetch('/calcular-puntaje')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                scoreDisplay.textContent = `Puntaje Total: ${data.total_score}`;
            } else {
                scoreDisplay.textContent = 'Error al calcular el puntaje.';
                console.error('Error:', data.error);
            }
        })
        .catch(error => {
            scoreDisplay.textContent = 'Error al conectar con el servidor.';
            console.error('Error:', error);
        });
}
