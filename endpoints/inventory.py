import datetime
from datetime import timedelta
from sqlalchemy import func
from flask import Blueprint
from flask import make_response, request
import json
from models import Inventory, InventoryItem, Ingredients, InventoryTransaction
from constants import *
from models import db

inventory_blueprint = Blueprint('inventory_blueprint', __name__)

@inventory_blueprint.route('/inventory_starting', methods=["GET"])
def inventory_starting():
    try:
        if request.method == "GET":
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
                    items = InventoryItem.query.filter(InventoryItem.inventory_id == inventory.id).all()
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

@inventory_blueprint.route('/inventory_closing', methods=["GET", "POST"])
def inventory_closing():
    try:
        if request.method == "GET":
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
                    items = InventoryItem.query.filter(InventoryItem.inventory_id == inventory.id).all()
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
        elif request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                # get the closing inventory based on date and branch
                formatted_date = datetime.datetime.strptime(request_data['date'], "%m/%d/%Y %H:%M:%S")
                closing_inventory = Inventory(
                    branch_id = request_data["branch_id"],
                    is_starting = False
                )
                db.session.add(closing_inventory)
                db.session.commit()
                
                # create the succeeding day opening inventory
                next_day = closing_inventory.datetime_created + timedelta(days=1)
                opening_inventory = Inventory(
                    branch_id = request_data["branch_id"],
                    is_starting = True
                )
                db.session.add(opening_inventory)
                db.session.commit()

                # create the items
                for item in request_data["closing_items"]:
                    # create an instance of that item
                    closing_item = InventoryItem(
                        ingredient_id = item["ingredient_id"],
                        inventory_id = closing_inventory.id,
                        quantity = item["new_quantity"]
                    )
                    db.session.add(closing_item)
                    db.session.commit()
                    opening_item = InventoryItem(
                        ingredient_id = item["ingredient_id"],
                        inventory_id = opening_inventory.id,
                        quantity = item["new_quantity"]
                    )
                    db.session.add(opening_item)
                    db.session.commit() 
                resp = make_response({"status": 200, "remarks": "Success"})
            else:
                resp = make_response({"status": 403, "remarks": "Access denied"})
    except Exception as e:
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@inventory_blueprint.route('/inventory_transaction', methods=["GET", "POST"])
def inventory_transaction():
    try:
        if request.method == "GET":
            date = request.args.get('date')
            branch_id = request.args.get('branch_id')
            if date is None or branch_id is None:
                resp = make_response({"status": 400, "remarks": "Missing required parameters in the query string"})
            else:
                formatted_date = datetime.datetime.strptime(date, "%m/%d/%Y %H:%M:%S")
                transactions_query = InventoryTransaction.query.filter(
                    func.DATE(InventoryTransaction.datetime_created) == formatted_date.date(),
                    InventoryTransaction.branch_id == branch_id
                ).order_by(InventoryTransaction.datetime_created.desc()).all()
                response_body = {}
                if transactions_query is None:
                    response_body["status"] = 404
                    response_body["remarks"] = "No transactions for this date"
                else:
                    response_body["status"] = 200
                    response_body["remarks"] = "Success"
                    response_body["transactions"] = []
                    for transaction_query in transactions_query:
                        transaction = {}
                        transaction["details"] = transaction_query.to_map()
                        ingredient = Ingredients.query.get(transaction_query.ingredient_id)
                        transaction["ingredient"] = ingredient.to_map()
                        response_body["transactions"].append(transaction)
                resp = make_response(response_body)
        elif request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                transaction = InventoryTransaction(
                    branch_id = request_data["branch_id"],
                    ingredient_id = request_data["ingredient_id"],
                    user_id = request_data["user_id"],
                    transaction_type = request_data["transaction_type"],
                    quantity = request_data["quantity"],
                    remarks = request_data["remarks"]
                )
                db.session.add(transaction)
                db.session.commit()
                return make_response({"status": 200, "remarks": "Success"})
            else:
                return make_response({"status": 403, "remarks": "Access denied"})
    except Exception as e:
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp