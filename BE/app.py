from flask import Flask, request, jsonify
from mcq_gen import mcqGen
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return "PTIT AI tools"


@app.route('/api/mcq', methods=['POST'])
def mcq():
    data = request.form
    topic = data.get('topic')
    quantity = data.get('quantity')
    difficulty = data.get('difficulty')
    file = request.files['file'] if 'file' in request.files else None
    inputText = data.get('inputText')
    status = data.get('status')
    questionType = data.get('questionType')
    numAnswer = int(data.get('numAnswer'))
    isRecheck = True if data.get('isRecheck') == 'true' else False

    try:
        mcqs, notify = mcqGen(topic, quantity, difficulty, file, inputText, status, questionType, numAnswer, isRecheck)

        return jsonify({
            'mcqs': mcqs,
            'notify': notify
        })
    except ValueError:
        return jsonify({'error': 'Error'}), 400


if __name__ == '__main__':
    app.run(debug=True)