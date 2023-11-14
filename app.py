from flask import Flask, render_template, request, jsonify
from jiwer import wer  # Library for Word Error Rate calculation
import speech_recognition as sr

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    if 'audioBlob' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audioBlob']

    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    recognizer = sr.Recognizer()
    
    language = request.form.get('language', 'en')  # Get selected language, default to English ('en')

    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio_data, language=language)
            #recognized_text = recognizer.recognize_whisper(audio_data, language=language)
            #print(recognized_text)
            
            reference_sentence = request.form.get('reference')  # Get reference sentence from form
            
            if not reference_sentence:
                return jsonify({'error': 'No reference sentence provided'}), 400
            
            error_rate = wer(reference_sentence, recognized_text)
            
            return jsonify({
                'recognized_text': recognized_text,
                'reference_sentence': reference_sentence,
                'word_error_rate': error_rate
            }), 200
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand audio'}), 500
    except sr.RequestError as e:
        return jsonify({'error': f'Speech recognition service error: {e}'}), 500

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=True, host='0.0.0.0')
