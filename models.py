from flask_sqlalchemy import SQLAlchemy     ## pip3 install Flask-SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Branch(db.Model):
    __tablename__ = "branch"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def to_map(self):
        return {
            "id": self.id,
            "name": self.name
        }


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    branch_id = db.Column(db.Integer, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
     
    def to_map(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "fullname": self.fullname,
            "branch_id": self.branch_id,
            "is_admin": self.is_admin
        }

class Ingredients(db.Model):
    __tablename__ = "ingredients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    branch_id = db.Column(db.Integer, nullable=False)
    tolerance = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)


    def to_map(self):
        return {
            "id": self.id,
            "name": self.name,
            "unit": self.unit,
            "branch_id": self.branch_id,
            "tolerance": self.tolerance,
            "category": self.category
        }

class Inventory(db.Model):
    __tablename__ = "inventory"
    id = db.Column(db.Integer, primary_key=True)
    datetime_created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    is_starting = db.Column(db.Boolean, nullable=False)


    def to_map(self):
        return {
            "id": self.id,
            "datetime_created": self.datetime_created,
            "is_starting": self.is_starting
        }

class Item(db.Model):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, nullable=False)
    inventory_id = db.Column(db.Integer, nullable=False)
    previous_id = db.Column(db.Integer, nullable=True)
    quantity = db.Column(db.Float, nullable=False)
    received = db.Column(db.Float, nullable=False)
    consumed = db.Column(db.Float, nullable=False)
    expired = db.Column(db.Float, nullable=False)
    spoiled = db.Column(db.Float, nullable=False)
    bad_order = db.Column(db.Float, nullable=False)

    def to_map(self):
        return {
            "id": self.id,
            "ingredient_id": self.ingredient_id,
            "inventory_id": self.inventory_id,
            "previous_id": self.previous_id,
            "quantity": self.quantity,
            "received": self.received,
            "consumed": self.consumed,
            "expired": self.expired,
            "spoiled": self.spoiled,
            "bad_order": self.bad_order
        }