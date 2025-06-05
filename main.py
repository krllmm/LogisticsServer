from datetime import datetime
import os
from flask import Flask
from flask import jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import random
import string
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

    user = mongo.db.drivers.find_one(
        {"login": login}, {"_id": 0, "delivery": 1})

    def serialize_date(delivery):
        return {
            "from": delivery["from"],
            "from_address": delivery["from_address"],
            "to": delivery["to"],
            "to_address": delivery["to_address"],
            "product_id": delivery["product_id"],
            "amount": delivery["amount"],
            # "datetime": delivery["datetime"].isoformat()
        }

    deliveries = [serialize_date(e) for e in user.get("delivery", [])]

    if user and "delivery" in user:
        return jsonify(user["delivery"])
    else:
        return jsonify({"error": "User not found or no delivery data"}), 404


@app.route('/getProduct', methods=['GET'])
def getProduct():
    id = request.args.get("id")

    print(id)

    if not id:
        return jsonify({"error": "Product id is required"}), 400

    product = mongo.db.products.find_one({"custom_id": int(id)})

    print(product)

    if product:
        return jsonify(product)
    else:
        return jsonify({"error": "Product not found"}), 404


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
                            "from_address": "ул. Чернышевского 61",
                            "to": "Минск",
                            "to_address": "ул. Азгура 3",
                            "product_id": 1,
                            "amount": 12,
                        },
                        {
                            "id": 2,
                            "from": "Барановичи",
                            "from_address": "ул. Чернышевского 61",
                            "to": "Брест",
                            "to_address": "ул. Кижеватова 76",
                            "product_id": 2,
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
        # mongo.db.products.insert_one(
        #     {
        #         "custom_id": 3,
        #         "name": "Машина тестомесильная МТ-25-01 двухскоростная",
        #         "quantity": 200,
        #         "description": "Машина, которая месит тесто. Имеет две настройки скорости.",
        #         "weight": 33,
        #         "dimentions": "70, 70, 80",
        #         "storage_id": 1,
        #     }
        # )
        # mongo.db.products.insert_one(
        #     {
        #         "custom_id": 4,
        #         "name": "Слайсер ЛР-220",
        #         "quantity": 150,
        #         "description": "Промышленный слайсер.",
        #         "weight": 24,
        #         "dimentions": "50, 60, 40",
        #         "storage_id": 1,
        #     }
        # )
        # mongo.db.products.insert_one(
        #     {
        #         "custom_id": 5,
        #         "name": "Машина для переработки овощей МПО-1",
        #         "quantity": 50,
        #         "description": "Перерабатывет многие виды овощей.",
        #         "weight": 20,
        #         "dimentions": "30, 70, 70",
        #         "storage_id": 1,
        #     }
        # )
        # mongo.db.products.insert_one(
        #     {
        #         "custom_id": 1,
        #         "name": "Машина для перемешивания фарша МПФ-30.В1",
        #         "quantity": 100,
        #         "description": "Промышленная машина для перемешивания фарша.",
        #         "weight": 20,
        #         "dimentions": "50, 50, 80",
        #         "storage_id": 1,
        #     }
        # )
        # mongo.db.products.insert_one(
        #     {
        #         "custom_id": 2,
        #         "name": "Машина тестораскаточная ТРМ-500",
        #         "quantity": 80,
        #         "description": "Промышленная машина для раскатывания теста.",
        #         "weight": 13,
        #         "dimentions": "60, 40, 60",
        #         "storage_id": 1,
        #     }
        # )
        return jsonify({"message": "Products created"}), 201
    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/seeddb_logists', methods=['GET'])
def seeddb_logists():
    try:
        mongo.db.logists.insert_one(
            {
                "first_name": "Игорь",
                "second_name": "Алексеев",
                "login": "",
                "password": generate_password_hash("password"),
                "super_rights": "true",
                "storage_id": 1,
                "drivers": []
            }
        )
        mongo.db.logists.insert_one(
            {
                "first_name": "",
                "second_name": "",
                "login": "Agent 2",
                "password": generate_password_hash("password 2"),
                "super_rights": "false",
                "storage_id": 1,
                "drivers": []
            }
        )
        return jsonify({"message": "Logists created"}), 201
    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/loginLogist', methods=["POST"])
def loginLogist():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')

    print(login, password)

    if not login or not password:
        return jsonify({"error": "Логин и пароль обязательны"}), 400

    user = mongo.db.logists.find_one({"login": login})
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404

    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Неверный пароль"}), 401

    return jsonify({"message": "Вход выполнен успешно", "user": user}), 200


@app.route('/getAllDrivers', methods=["GET"])
def getAllDrivers():
    drivers = mongo.db.drivers.find()
    
    result = [serialize_doc(item) for item in drivers]

    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Error happend on server"}), 404


@app.route('/addDriver', methods=["POST"])
def addDriver():
    try:
        data = request.get_json()
        name = data.get('firstName')
        second_name = data.get('secondName')
        sex = data.get("sex")
        experience = data.get("experience")
        age = data.get("age")
        category = data.get("category")
        login = data.get('login')
        password = data.get('password')

        print(name)
        print(second_name)
        print(sex)
        print(experience)
        print(age)
        print(category)
        print(login)
        print(password)

        mongo.db.drivers.insert_one(
            {
                "login": login,
                "password": generate_password_hash(password),
                "first_name": name,
                "second_name": second_name,
                "experince": experience,
                "sex": sex,
                "age": age,
                "category": category,
                "delivery": [],
            })
        return jsonify({"message": "Driver is created"}), 201
    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/addDelivery', methods=["POST"])
def addDelivery():
    try:
        data = request.get_json()
        fromCity = data.get('from')
        fromAddress = data.get('from_address')
        toCity = data.get('to')
        toAddress = data.get('to_address')

        product_id = data.get("product_id")
        amount = data.get("amount")
        iso_str = data.get("datetime")
        date = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        id = data.get("id")

        print(fromCity)
        print(fromAddress)
        print(toCity)
        print(toAddress)
        print(product_id)
        print(amount)
        print(date)
        print(id)
        result = ''.join(random.choices(
            string.ascii_letters + string.digits, k=24))
        print(result)

        if not id:
            return jsonify({"error": "id обязателен"}), 400

        result = mongo.db.drivers.update_one(
            {"_id": ObjectId(id)},
            {"$addToSet": {"delivery": {
                "id": result,
                "from": fromCity,
                "from_address": fromAddress,
                "to": toCity,
                "to_address": toAddress,
                "product_id": product_id,
                "amount": amount,
                "date": date,
            }}}
        )
        if result.modified_count == 1:
            return jsonify({"message": "Перевозка добавлена"}), 200
        else:
            return jsonify({"message": "Пользователь не найден или не обновлён"}), 404
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/getAvailableDrivers", methods=["GET"])
def getAvailableDrivers():
    try:
        result = mongo.db.drivers.find(
            {}, {"_id": 1, "first_name": 1, "second_name": 1})

        items = [{"_id": str(doc["_id"]), "first_name": doc.get(
            "first_name", ""), "second_name": doc.get("second_name", "")} for doc in result]

        return jsonify(items)
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/closeDelivery", methods=["POST"])
def closeDelivery():
    data = request.get_json()
    deliveryId = data.get('deliveryId')
    driverLogin = data.get('driverLogin')

    print(deliveryId, driverLogin)
    try:
        user = mongo.db.drivers.find_one({'login': driverLogin})
        if not user:
            return 'User not found'

        # Найти нужный объект из массива
        item_to_move = next((item for item in user.get(
            'delivery', []) if str(item.get('id')) == deliveryId), None)

        if not item_to_move:
            return 'Item not found in user'
        
        item_to_move["driver_name"] = user["first_name"]
        item_to_move["driver_second_name"] = user["second_name"]

        # Добавить в другую коллекцию
        mongo.db.delivery_history.insert_one(item_to_move)

        # Удалить из массива
        mongo.db.drivers.update_one(
            {'login': driverLogin},
            {'$pull': {'delivery': {'id': deliveryId}}}
        )

        return 'Item moved successfully'
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/getDeliveryHistory", methods=["GET"])
def getDeliveryHistory():
    history = mongo.db.delivery_history.find()

    if history:
        return jsonify(history)
    else:
        return jsonify({"error": "Error happend on server"}), 404


@app.route("/getProducts", methods=["GET"])
def getProducts():
    products = mongo.db.products.find()

    if products:
        return jsonify(products)
    else:
        return jsonify({"error": "Error happend on server"}), 404


@app.route("/getLogists", methods=["GET"])
def getLogists():
    logists = mongo.db.logists.find()

    result = [serialize_doc(item) for item in logists]

    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Error happend on server"}), 404


@app.route('/addLogist', methods=["POST"])
def addLogist():
    try:
        data = request.get_json()
        name = data.get('first_name')
        second_name = data.get('second_name')
        login = data.get('login')
        password = data.get('password')
        super = data.get("super_rights")

        print(name)
        print(second_name)
        print(login)
        print(password)
        print(super)

        mongo.db.logists.insert_one(
            {
                "login": login,
                "password": generate_password_hash(password),
                "first_name": name,
                "second_name": second_name,
                "super_rights": super,
                # "storage_id": 1,
                "drivers": []
            })
        return jsonify({"message": "Driver is created"}), 201
    except Exception as e:
        return {"error": str(e)}, 500


def serialize_doc(doc):
    doc['_id'] = str(doc['_id'])
    return doc


@app.route("/getFreeDrivers", methods=["GET"])
def getFreeDrivers():
    try:

        drivers = mongo.db.drivers.find({'$or': [
            {'logist_id': {'$exists': False}},
            {'logist_id': ''},
        ]}, {"_id": 1, "first_name": 1, "second_name": 1})
        
        result = [serialize_doc(item) for item in drivers]

        return jsonify(result)
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/assignDriverToLogist", methods=["POST"])
def assignDriverToLogist():
    try: 
        data = request.get_json()
        
        driverId = ObjectId(data.get("driverId"))
        logistId = ObjectId(data.get("logistId"))
        
        mongo.db.drivers.update_one(
            {'_id': driverId, 'logist_id': {'$exists': False}},  
            {'$set': {'logist_id': data.get("logistId")}}
        )
        
        mongo.db.logists.update_one(
            {'_id': logistId},
            {'$addToSet': {'drivers': data.get("driverId")}}  
        )
            
        return jsonify({'status': 'updated'}), 200
    except Exception as e:
        return {"error": str(e)}, 500
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)