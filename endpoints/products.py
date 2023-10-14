import datetime
from datetime import timedelta
from sqlalchemy import func
from flask import Blueprint
from flask import make_response, request
import json
from models import Inventory, Item, Ingredients, Products
from constants import *
from models import db


products_blueprint = Blueprint('products_blueprint', __name__)

@products_blueprint.route('/products', methods = ["POST", "GET", "DELETE", "PATCH"])
def products():
    try:
        if request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                product_query = Products.query.filter(Products.branch_id == request_data["branch_id"], Products.name == request_data["name"]).first()
                if product_query:
                    resp = make_response({"status": 400, "remarks": "Ingredient already exists."})
                else:
                    product = Products(
                        branch_id = request_data["branch_id"],
                        name = request_data["name"]
                    )
                    db.session.add(product)
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
            else:
                resp = make_response({"status": 403, "remarks": "Access denied"})
        elif request.method == "GET":
            branch_id = request.args.get('branch_id')
            if branch_id is None:
                resp = make_response({"status": 400, "remarks": "Missing branch id in the query string"})
            else:
                products = Products.query.filter(Products.branch_id == branch_id).all()
                if products is None:
                    resp = make_response({"status": 404, "remarks": "Store doesn't have products yet."})
                else:
                    response_body = {}
                    response_body["products"] = []
                    for product in products:
                        response_body["products"].add(product.to_map())
                    response_body["status"] = 200
                    response_body["remarks"] = "Success"
                    resp = make_response(response_body)
        elif request.method == "DELETE":
            product = Products.query.get(id)
            if product is None:
                resp = make_response({"status": 404, "remarks": "Product not found"})
            else:
                db.session.delete(product)
                db.session.commit()
                resp = make_response({"status": 200, "remarks": "Success"})
        elif request.method == "PATCH":
            product = Products.query.get(id)
            if product is None:
                resp = make_response({"status": 404, "remarks": "Product not found"})
            else:
                request_data = request.data
                request_data = json.loads(request_data.decode('utf-8')) 
                if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                    product.name = request_data["name"]
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
                else:
                    resp = make_response({"status": 403, "remarks": "Access denied"})
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

