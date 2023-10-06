from flask import Blueprint
from flask import make_response, request
import json
from models import Ingredients
from constants import *
from models import db

ingredient_blueprint = Blueprint('ingredient_blueprint', __name__)


# curl -X POST -d "{\"admin_auth_token\": \"WvNM3UJL2kHZQ1ewI7RzGxVh0n8o6YKS\", \"name\": \"Ayame - SM Seaside\"}" -H "Content-Type: application/json" http://127.0.0.1:5000/branch
@ingredient_blueprint.route('/ingredient', methods = ["POST", "GET"])
def ingredient():
    try:
        if request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                query = Ingredients.query.filter(
                    Ingredients.name == request_data["name"],
                    Ingredients.unit == request_data["unit"],
                    Ingredients.branch_id == request_data["branch_id"],
                    Ingredients.tolerance == request_data["tolerance"],
                    Ingredients.category == request_data["category"],
                    ).all()
                if query:
                    resp = make_response({"status": 400, "remarks": "User already exists."})
                else:
                    instance = Ingredients(
                        name = request_data["name"],
                        unit = request_data["unit"],
                        branch_id = request_data["branch_id"],
                        tolerance = request_data["tolerance"],
                        category = request_data["category"]
                    )
                    db.session.add(instance)
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
            else:
                resp = make_response({"status": 403, "remarks": "Access denied"})
        elif request.method:
            id = request.args.get('id')
            if id is None:
                resp = make_response({"status": 400, "remarks": "Missing id in the query string"})
            else:
                instance = Ingredients.query.filter(Ingredients.id == id).first()
                if instance is None:
                    resp = make_response({"status": 404, "remarks": "Ingredient does not exist."})
                else:
                    response_body = instance.to_map()
                    response_body["status"] = 200
                    response_body["remarks"] = "Success"
                    resp = make_response(response_body)
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": "Internal server error"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp