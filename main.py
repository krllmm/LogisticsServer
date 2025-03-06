from dotenv import load_dotenv
import os
import certifi
from flask import Flask
from flask import jsonify, request 
from flask_cors import CORS
from flask_pymongo import PyMongo

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
# print(MONGO_URI)

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app, tlsCAFile=certifi.where())

@app.route("/", methods=['GET'])
def find_user():
    user = mongo.db.drivers.find_one({"name": "Dave"})
    
    return jsonify(user)  