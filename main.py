import os
from flask import Flask
from flask import jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

MONGO_URI = os.getenv('MONGO_URI')

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)


@app.route("/driver", methods=['GET'])
def driver():
  login = request.args.get("login")

  if not login:
      return jsonify({"error": "Login is required"}), 400

  user = mongo.db.drivers.find_one({"login": login})

  if user:
      return jsonify(user)
  else:
      return jsonify({"error": "User not found"}), 404

# Регистрация
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')

    if not login or not password:
        return jsonify({"error": "Логин и пароль обязательны"}), 400

    if mongo.db.drivers.find_one({"login": login}):
        return jsonify({"error": "Пользователь уже существует"}), 409

    hashed_password = generate_password_hash(password)
    mongo.db.drivers.insert_one({"login": login, "password": hashed_password})

    return jsonify({"message": "Регистрация успешна"}), 201

# Логин
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')
    
    print(login, password)

    if not login or not password:
        return jsonify({"error": "Логин и пароль обязательны"}), 400

    user = mongo.db.drivers.find_one({"login": login})
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Неверный пароль"}), 401

    return jsonify({"message": "Вход выполнен успешно"}), 200
  
@app.route('/getDeliveries', methods=['GET'])
def getDeliveries():
  login = request.args.get("login")

  if not login:
      return jsonify({"error": "Login is required"}), 400

  user = mongo.db.drivers.find_one({"login": login}, {"_id": 0, "delivery": 1})

  if user and "delivery" in user:
      return jsonify(user["delivery"])
  else:
      return jsonify({"error": "User not found or no delivery data"}), 404


@app.route('/seeddb', methods=['GET'])
def seeddb():
    try:
        mongo.db.drivers.insert_one(
            {
                "login": "admin",
                "password": generate_password_hash("admin"),
                "first_name": "Андрей",
                "second_name": "Фамилия",
                "experince": 2,
                "age": 34,
                "category": "B",
                "delivery":
                    [
                        {
                            "id": 1,
                            "from": "Барановичи",
                            "to": "Минск",
                            "product_id": 123,
                            "amount": 12,
                        },
                        {
                            "id": 2,
                            "from": "Барановичи",
                            "to": "Брест",
                            "product_id": 98,
                            "amount": 6,
                        },
                ],
            }
        )
        return jsonify({"message": "Drivers created"}), 201
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/seeddb_products', methods=['GET'])
def seeddb_products():
    try:
        mongo.db.products.insert_one(
            {
              "name": "Машина для перемешивания фарша МПФ-30.В1",
              "quantity": 100,
              "description": "Промышленная машина для перемешивания фарша.",
              "weight": 20,
              "dimentions": "50, 50, 80",
              "storage_id": 1,
            }
        )
        return jsonify({"message": "Products created"}), 201
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/seeddb_logists', methods=['GET'])
def seeddb_logists():
    try:
        mongo.db.logists.insert_one(
            {
              "name": "Agent",
              "super_rights": "true",
              "storage_id": 1,
              "drivers": [
                1, 2
              ]
            }
        )
        return jsonify({"message": "Logists created"}), 201
    except Exception as e:
        return {"error": str(e)}, 500