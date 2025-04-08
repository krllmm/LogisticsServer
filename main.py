import os
from flask import Flask
from flask import jsonify, request 
from flask_cors import CORS
from flask_pymongo import PyMongo

MONGO_URI = os.getenv('MONGO_URI')

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)

@app.route("/", methods=['GET'])
def find_user():
  try:
    cursor = mongo.db.drivers.find()
    return jsonify([str(doc) for doc in cursor]) 
  except Exception as e:
    return {"error": str(e)}, 500