from flask import Flask, request, render_template, jsonify
import os
import speech_recognition as SR
from pydub import AudioSegment
from nltk.tokenize import sent_tokenize
from flask_sqlalchemy import SQLAlchemy
import nltk
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Configuración de la aplicación Flask
app = Flask(__name__, static_url_path='/static')

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:8098541951@localhost/transcripciones_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelo de la base de datos
class Transcripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    archivo_nombre = db.Column(db.String(255), nullable=False)
    transcripcion = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())

# Crear tablas si no existen
with app.app_context():
    db.create_all()

def check_audio_format(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        print(f'Audio format: {audio.format}')
    except Exception as e:
        print(f'Error reading audio file: {str(e)}')

def split_audio(file_path, segment_length):
    audio = AudioSegment.from_file(file_path)
    segments = []
    for i in range(0, len(audio), segment_length * 1000):
        segments.append(audio[i:i + segment_length * 1000])
    return segments

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audioBlob' not in request.files and 'audioFile' not in request.files:
        return 'No se encontró el archivo de audio'

    file = request.files.get('audioBlob') or request.files.get('audioFile')

    if file.filename == '':
        return 'No file selected'

    try:
        file_ext = os.path.splitext(file.filename)[1].lower()
        audio_path_with_ext = os.path.join('uploads', file.filename)
        file.save(audio_path_with_ext)

        check_audio_format(audio_path_with_ext)

        if file_ext != '.wav':
            audio = AudioSegment.from_file(audio_path_with_ext)
            audio_path_wav = os.path.splitext(audio_path_with_ext)[0] + '.wav'
            audio.export(audio_path_wav, format="wav")
            audio_path = audio_path_wav
        else:
            audio_path = audio_path_with_ext

        segments = split_audio(audio_path, 60)
        recognizer = SR.Recognizer()
        transcript = ""

        for i, segment in enumerate(segments):
            segment_path = f"{audio_path}_segment_{i}.wav"
            segment.export(segment_path, format="wav")

            with SR.AudioFile(segment_path) as source:
                audio_data = recognizer.record(source)

            try:
                segment_transcript = recognizer.recognize_google(audio_data, language='es-ES')
                transcript += segment_transcript + " "
            except SR.UnknownValueError:
                transcript += "[Inaudible] "
            except SR.RequestError:
                transcript += "[Error de reconocimiento] "

        # Guarda la transcripción en la base de datos
        nueva_transcripcion = Transcripcion(archivo_nombre=file.filename, transcripcion=transcript.strip())
        db.session.add(nueva_transcripcion)
        db.session.commit()

        return transcript.strip()

    except Exception as e:
        return f'Error: {str(e)}'

@app.route('/transcripciones', methods=['GET'])
def obtener_transcripciones():
    transcripciones = Transcripcion.query.all()
    resultado = [
        {"id": t.id, "archivo_nombre": t.archivo_nombre, "transcripcion": t.transcripcion, "fecha": t.fecha}
        for t in transcripciones
    ]
    return jsonify(resultado)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    question = request.json.get('question', '').lower()

    if not question:
        return jsonify({'answer': 'Por favor, haga una pregunta.'})

    with open('transcriptions.txt', 'r', encoding='utf-8') as f:
        transcriptions = f.read()

    sentences = sent_tokenize(transcriptions)
    relevant_sentences = [sentence for sentence in sentences if question in sentence.lower()]

    if relevant_sentences:
        answer = ' '.join(relevant_sentences[:5])
    else:
        answer = 'No tengo información sobre eso en las transcripciones.'

    return jsonify({'answer': answer})

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    nltk.download('punkt')
    app.run(debug=True)
