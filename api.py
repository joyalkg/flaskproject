
from flask import jsonify, request
from flask import Flask
from app import app
from flask_pymongo import PyMongo


app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'
mongo = PyMongo(app)

app = Flask(__name__)

roles = {
    "admin": ["select", "insert", "update", "delete", "login"],
    "user": ["select", "insert", "update"]
}


def has_permission(headers, required_permission):

    authorization_header = headers.get("Authorization")
    if not authorization_header:
        return False
    required_role = authorization_header.strip().lower()


    if required_role not in roles:
        return False


    allowed_permissions = roles[required_role]
    return required_permission in allowed_permissions


@app.route("/select/<name>", methods=["GET"])
def user(name):
    if not has_permission(request.headers, "select"):
        return jsonify({"message": "Unauthorized"}), 401

    collection = mongo.db.flaskmongodb
    result = collection.find_one({"name": name})
    result["_id"] = str(result["_id"])
    resp = jsonify(result)
    return resp

@app.route("/delete/<name>", methods=["DELETE"])
def delete(name):
    if not has_permission(request.headers, "delete"):
        return jsonify({"message": "Unauthorized"}), 401

    collection = mongo.db.flaskmongodb
    result = collection.delete_one({"name": name})

    output = {"Message": "DELETED"}
    return jsonify({"result": output})

@app.route("/inst", methods=["POST"])
def inst():
    if not has_permission(request.headers, "insert"):
        return jsonify({"message": "Unauthorized"}), 401

    collection = mongo.db.flaskmongodb
    firstname = request.json["name"]
    lastname = request.json["password"]
    result = collection.insert_one({"name": firstname, "password": lastname})

    output = {"name": request.json["name"], "password": request.json["password"], "Message": "Success"}
    return jsonify({"result": output})

@app.route("/update/<name>", methods=["PUT"])
def updates(name):
    if not has_permission(request.headers, "update"):
        return jsonify({"message": "Unauthorized"}), 401

    collection = mongo.db.flaskmongodb
    firstname = request.json["name"]
    lastname = request.json["password"]
    result = collection.update_one({"name": name}, {"$set": {"name": firstname, "password": lastname}})

    output = {"name": request.json["name"], "password": request.json["password"], "Message": "Success"}
    return jsonify({"result": output})

@app.route("/login/<email>", methods=["GET"])
def login(email):
    if not has_permission(request.headers, "login"):
        return jsonify({"message": "Unauthorized"}), 401

    collection = mongo.db.flaskmongodb
    firstname = request.json["name"]
    password = request.json["password"]
    result = collection.find_one({"name": firstname, "password": email})
    if result:
        result["_id"] = str(result["_id"])
        if result["password"] == password:
            output = {"message": "log in successfully"}
            return jsonify(output)
        else:
            output = {"message": "enter a valid password"}
            return jsonify(output)
    else:
        output = {"message": "User not found"}
        return jsonify(output)





if __name__ == "__main__":
    app.debug = True
    app.run()


