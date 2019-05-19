from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask import request
from flask import jsonify


app = Flask(__name__)
api = Api(app)

@app.route("/test", methods=['GET'])
def test():
    start = request.args.get('start', None)
    end = request.args.get('end', None)
    return jsonify({"start":start, "end":end, "data":"success"}), 200

app.run(debug=True)