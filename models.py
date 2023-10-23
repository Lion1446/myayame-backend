from flask_sqlalchemy import SQLAlchemy     ## pip3 install Flask-SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    datetime_created = db.Column(db.DateTime, nullable=False)
    datetime_deleted = db.Column(db.DateTime, default=None, nullable=True)

    def to_map(self):
        return {
            "id": self.id,
            "datetime_created": self.datetime_created,
            "datetime_deleted": self.datetime_deleted
        }

class Branch(BaseModel):
    __tablename__ = "branch"
    name = db.Column(db.String(100), nullable=False)

    def to_map(self):
        branch_data = super().to_map()  # Call the to_map method from BaseModel
        branch_data["name"] = self.name
        return branch_data


class User(BaseModel):
    __tablename__ = "user"
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    branch_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.Integer, nullable=False)
    
    def to_map(self):
        user_data = super().to_map()  # Call the to_map method from BaseModel
        user_data.update({
            "username": self.username,
            "password": self.password,
            "fullname": self.fullname,
            "branch_id": self.branch_id,
            "user_type": self.user_type
        })
        return user_data

class Ingredients(BaseModel):
    __tablename__ = "ingredients"
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(10), nullable=False)
    branch_id = db.Column(db.Integer, nullable=False)
    tolerance = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)

    def to_map(self):
        ingredient_data = super().to_map()
        ingredient_data.update({
            "name": self.name,
            "unit": self.unit,
            "branch_id": self.branch_id,
            "tolerance": self.tolerance,
            "category": self.category
        })
        return ingredient_data

class Products(BaseModel):
    __tablename__ = "products"
    branch_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def to_map(self):
        product_data = super().to_map()
        product_data.update({
            "branch_id": self.branch_id,
            "name": self.name,
            "price": self.price
        })
        return product_data

class ProductIngredient(BaseModel):
    __tablename__ = "product_ingredient"
    product_id = db.Column(db.Integer, nullable=False)
    ingredient_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    def to_map(self):
        product_ingredient_data = super().to_map()
        product_ingredient_data.update({
            "product_id": self.product_id,
            "ingredient_id": self.ingredient_id,
            "quantity": self.quantity
        })
        return product_ingredient_data
    
class Inventory(BaseModel):
    __tablename__ = "inventory"
    branch_id = db.Column(db.Integer, nullable=False)
    is_starting = db.Column(db.Boolean, nullable=False)

    def to_map(self):
        inventory_data = super().to_map()
        inventory_data.update({
            "branch_id": self.branch_id,
            "is_starting": self.is_starting
        })
        return inventory_data
    
class InventoryItem(BaseModel):
    __tablename__ = "inventory_item"
    ingredient_id = db.Column(db.Integer, nullable=False)
    inventory_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    def to_map(self):
        inventory_item_data = super().to_map()
        inventory_item_data.update({
            "ingredient_id": self.ingredient_id,
            "inventory_id": self.inventory_id,
            "quantity": self.quantity
        })
        return inventory_item_data


class InventoryTransaction(BaseModel):
    __tablename__ = "inventory_transaction"
    branch_id = db.Column(db.Integer, nullable=False)
    ingredient_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    remarks = db.Column(db.String(100), nullable=False)

    def to_map(self):
        inventory_transaction_data = super().to_map()
        inventory_transaction_data.update({
            "branch_id": self.branch_id,
            "ingredient_id": self.ingredient_id,
            "user_id": self.user_id,
            "transaction_type": self.transaction_type,
            "quantity": self.quantity,
            "remarks": self.remarks
        })
        return inventory_transaction_data