import datetime
from sqlalchemy import func
from flask import Blueprint
from flask import make_response, request
import json
from models import Inventory, Item, Ingredients
from constants import *
from models import db

inventory_blueprint = Blueprint('inventory_blueprint', __name__)

@inventory_blueprint.route('/inventory_starting', methods = ["POST", "GET", "DELETE"])
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
                    Inventory.branch_id == request_data["branch_id"]
                    ).first()
                if query:
                    item_query = Item.query.filter(Item.ingredient_id == request_data["ingredient_id"]).first()
                    if item_query:
                        item_query.quantity = item_query.quantity + request_data["quantity"]
                    else:
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
                        is_starting = True,
                        branch_id = request_data["ingredient_id"]
                    )
                    db.session.add(inventory_instance)
                    db.session.commit()
                    query = Inventory.query.filter(
                        func.DATE(Inventory.datetime_created) == formatted_date.date(),
                        Inventory.is_starting == True,
                    ).first()
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
        elif request.method == "GET":
            date = request.args.get('date')
            branch_id = request.args.get('branch_id')
            if date is None or branch_id is None:
                resp = make_response({"status": 400, "remarks": "Missing required parameters in the query string"})
            else:
                formatted_date = datetime.datetime.strptime(date, "%m/%d/%Y %H:%M:%S")
                inventory = Inventory.query.filter(
                        func.DATE(Inventory.datetime_created) == formatted_date.date(),
                        Inventory.is_starting == True,
                        Inventory.branch_id == branch_id
                    ).first()
                if inventory is None:
                    resp = make_response({"status": 404, "remarks": "Inventory does not exist."})
                else:
                    response_body = {}
                    response_body["items"] = []
                    items = Item.query.filter(Item.inventory_id == inventory.id).all()
                    for item in items:
                        item_body = item.to_map()
                        ingredient = Ingredients.query.filter(Ingredients.id == item.ingredient_id).first()
                        item_body.update(ingredient.to_map())
                        response_body["items"].append(item_body)
                    response_body["inventory"] = inventory.to_map()
                    response_body["status"] = 200
                    response_body["remarks"] = "Success"
                    resp = make_response(response_body)
        elif request.method == "DELETE":
            item_id = request.args.get('item_id')
            if item_id is not None:
                item_starting = Item.query.filter(Item.id == item_id).first()
                inventory_starting = Inventory.query.filter(Inventory.id == item_starting.inventory_id).first()
                inventory_closing = Inventory.query.filter(func.DATE(Inventory.datetime_created) == func.DATE(inventory_starting.datetime_created), Inventory.is_starting == False).first()
                if inventory_closing:
                    item_closing = Item.query.filter(Item.inventory_id == inventory_closing.id, Item.ingredient_id == item_starting.ingredient_id).first()
                    if item_closing:
                        db.session.delete(item_closing)
                        db.session.commit()
                if item_starting:
                    db.session.delete(item_starting)
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
                else:
                    resp = make_response({"status": 404, "remarks": "Item not found"})
            else:
                resp = make_response({"status": 400, "remarks": "Missing item_id parameter"})
    except Exception as e:
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
