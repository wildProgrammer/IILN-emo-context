import flask
from flask import Flask
from flask import request
from flask import jsonify
import classifier
import process_data
import utils
import flask_cors
from flask_cors import cross_origin
from prepare_for_bayes import prepare_test_data_row
app = Flask(__name__)
cors = flask_cors.CORS(app, resources={r"/api/*": {"origins": "*"}})

import utility_lib

# @app.route('/', methods=['GET'])
# def get_index_page():
#     return app.send_static_file('index.html')

@app.route('/emotion', methods=['POST'])
@cross_origin()
def post_emotion():
    data = request.get_json()
    if "conversation" not in data:
        return jsonify({"error": "Wrong structure of json. No 'conversation' member"})
    preprocessed = prepare_test_data_row(data["conversation"])
    result = utils.bayes(utility_lib.flatten(preprocessed["replies"]))
    response = {"emotion" : result}
    return jsonify(response)
