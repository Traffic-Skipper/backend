from flask import Flask, request

app = Flask(__name__)


@app.route('/prediction', methods=['GET'])
def getPrediction():
    args = request.args
    print(args['date'])
    return 'Prediction date {}'.format(args['date'])