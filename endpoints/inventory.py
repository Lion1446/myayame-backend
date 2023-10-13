import datetime
from datetime import timedelta
from sqlalchemy import func
from flask import Blueprint
from flask import make_response, request
import json
from models import Inventory, Item, Ingredients
from constants import *
from models import db

inventory_blueprint = Blueprint('inventory_blueprint', __name__)


@inventory_blueprint.route('/inventory_starting', methods = ["POST", "GET", "DELETE", "PATCH"])
def inventory_starting():
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
                        ingredient_body = ingredient.to_map()
                        body = dict(item_body)
                        body.update((k, v) for k, v in ingredient_body.items() if k not in item_body)
                        response_body["items"].append(body)
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
        elif request.method == "PATCH":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                starting_item = Item.query.filter(Item.id == request_data["id"]).first()
                if starting_item:
                    starting_item.quantity = request_data["quantity"]
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
                else:
                    resp = make_response({"status": 404, "remarks": "Item not found"})
            else:
                resp = make_response({"status": 403, "remarks": "Access denied"})
    except Exception as e:
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@inventory_blueprint.route('/inventory_closing', methods = ["POST", "GET", "PATCH"])
def inventory_closing():
    try:
        if request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                # get the closing inventory based on date and branch
                formatted_date = datetime.datetime.strptime(request_data['date'], "%m/%d/%Y %H:%M:%S")
                closing_inventory = Inventory.query.filter(
                    func.DATE(Inventory.datetime_created) == formatted_date.date(),
                    Inventory.is_starting == False,
                    Inventory.branch_id == request_data["branch_id"]
                    ).first()
                if closing_inventory is None:
                    closing_inventory = Inventory(
                        branch_id = request_data["branch_id"],
                        datetime_created = formatted_date,
                        is_starting = False
                    )
                    db.session.add(closing_inventory)
                    db.session.commit()
                    closing_inventory = Inventory.query.filter(
                        func.DATE(Inventory.datetime_created) == formatted_date.date(),
                        Inventory.is_starting == False,
                        Inventory.branch_id == request_data["branch_id"]
                        ).first()
                
                
                # create the succeeding day opening inventory
                next_day = formatted_date + timedelta(days=1)
                opening_inventory = Inventory.query.filter(
                    func.DATE(Inventory.datetime_created) == next_day.date(),
                    Inventory.is_starting == True,
                    Inventory.branch_id == request_data["branch_id"]
                    ).first()
                if opening_inventory is None:
                    opening_inventory = Inventory(
                        branch_id = request_data["branch_id"],
                        datetime_created = next_day,
                        is_starting = True
                    )
                    db.session.add(opening_inventory)
                    db.session.commit()
                    opening_inventory = Inventory.query.filter(
                        func.DATE(Inventory.datetime_created) == next_day.date(),
                        Inventory.is_starting == True,
                        Inventory.branch_id == request_data["branch_id"]
                        ).first()

                # create the items
                for item in request_data["closing_items"]:
                    # create an instance of that item
                    closing_item = Item(
                        ingredient_id = item["ingredient_id"],
                        inventory_id = closing_inventory.id,
                        quantity = item["new_quantity"],
                        consumed = item["consumed"],
                        expired = item["expired"],
                        spoiled = item["spoiled"],
                        bad_order = item["bad_order"]
                    )
                    db.session.add(closing_item)
                    db.session.commit()
                    opening_item = Item(
                        ingredient_id = item["ingredient_id"],
                        inventory_id = opening_inventory.id,
                        quantity = item["new_quantity"],
                        consumed = item["consumed"],
                        expired = item["expired"],
                        spoiled = item["spoiled"],
                        bad_order = item["bad_order"]
                    )
                    db.session.add(opening_item)
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
                        Inventory.is_starting == False,
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
                        ingredient_body = ingredient.to_map()
                        body = dict(item_body)
                        body.update((k, v) for k, v in ingredient_body.items() if k not in item_body)
                        response_body["items"].append(body)
                    response_body["inventory"] = inventory.to_map()
                    response_body["status"] = 200
                    response_body["remarks"] = "Success"
                    resp = make_response(response_body)
                

    except Exception as e:
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

