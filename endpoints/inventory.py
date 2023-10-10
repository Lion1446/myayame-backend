import datetime
from sqlalchemy import func
from flask import Blueprint
from flask import make_response, request
import json
from models import Inventory, Item
from constants import *
from models import db

inventory_blueprint = Blueprint('inventory_blueprint', __name__)

@inventory_blueprint.route('/inventory_starting', methods = ["POST"])
def inventory():
    try:
        if request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                formatted_date = datetime.datetime.strptime(request_data['datetime_created'], "%m/%d/%Y %H:%M:%S")
                query = Inventory.query.filter(
                    func.DATE(Inventory.datetime_created) == formatted_date.date(),
                    Inventory.is_starting == True,
                    ).all()
                if query:
                    item = Item(
                        ingredient_id = request_data["ingredient_id"],
                        inventory_id = query.id,
                        quantity = request_data["quantity"],
                        consumed = 0,
                        expired = 0,
                        spoiled = 0,
                        bad_order = 0
                    )
                    db.session.add(item)
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
                else:
                    inventory_instance = Inventory(
                        datetime_created = formatted_date,
                        is_starting = True
                    )
                    db.session.add(inventory_instance)
                    db.session.commit()
                    query = Inventory.query.filter(
                        func.DATE(Inventory.datetime_created) == formatted_date.date(),
                        Inventory.is_starting == True,
                    ).all()
                    item = Item(
                        ingredient_id = request_data["ingredient_id"],
                        inventory_id = query.id,
                        quantity = request_data["quantity"],
                        consumed = 0,
                        expired = 0,
                        spoiled = 0,
                        bad_order = 0
                    )
                    db.session.add(item)
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
            else:
                resp = make_response({"status": 403, "remarks": "Access denied"})
    except Exception as e:
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
