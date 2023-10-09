from flask import Blueprint
from flask import make_response, request
import json
from models import Inventory, Item
from constants import *
from models import db

inventory_blueprint = Blueprint('inventory_blueprint', __name__)

@inventory_blueprint.route('/inventory', methods = ["POST"])
def inventory():
    try:
        if request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                query = Inventory.query.filter(
                    Inventory.datetime_created == request_data["datetime_created"],
                    Inventory.is_starting == request_data["is_starting"],
                    ).all()
                if query:
                    item = Item(
                        ingredient_id = request_data["ingredient_id"],
                        inventory_id = query.id,
                        quantity = request_data["quantity"],
                        received = request_data["quantity"],
                        consumed = 0,
                        expired = 0,
                        spoiled = 0,
                        bad_order = 0
                    )
                    db.session.add(item)
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
                else:
                    instance = Inventory(
                        datetime_created = request_data["datetime_created"],
                        is_starting = request_data["is_starting"]
                    )
                    item = Item(
                        ingredient_id = request_data["ingredient_id"],
                        inventory_id = instance.id,
                        previous_id = None,
                        quantity = request_data["quantity"],
                        received = request_data["quantity"],
                        consumed = 0,
                        expired = 0,
                        spoiled = 0,
                        bad_order = 0
                    )
                    db.session.add(instance)
                    db.session.add(item)
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
            else:
                resp = make_response({"status": 403, "remarks": "Access denied"})
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": "Internal server error"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
