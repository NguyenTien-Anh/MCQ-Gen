from flask import Flask, request, jsonify, render_template
from mcq_gen import mcqGen
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/mcq', methods=['POST'])
def mcq():
    data = request.form
    topic = data.get('topic')
    quantity = data.get('quantity')
    difficulty = data.get('difficulty')
    file = request.files['file'] if 'file' in request.files else None
    inputText = data.get('inputText')
    status = data.get('status')
    isSingleChoice = data.get('isSingleChoice')

    print('topic:', topic)
    print('quantity:', quantity)
    print('difficulty:', difficulty)
    print('status:', status)
    print('isSingleChoice:', isSingleChoice)

    try:
        mcqs = mcqGen(topic, quantity, difficulty, file, inputText, status, isSingleChoice)

        return jsonify({'mcqs': mcqs})
    except ValueError:
        return jsonify({'error': 'Error'}), 400


if __name__ == '__main__':
    app.run(debug=True)
