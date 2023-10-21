from flask_sqlalchemy import SQLAlchemy     ## pip3 install Flask-SQLAlchemy
from datetime import datetime, timedelta
from enum import Enum

db = SQLAlchemy()

class UserType(Enum):
    ADMIN = 1
    AUDITOR = 2
    USER = 3

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    datetime_created = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(hours=8))
    datetime_deleted = db.Column(db.DateTime, default=None, nullable=True)

    def delete(self):
        self.datetime_deleted = datetime.utcnow() + timedelta(hours=8)
        db.session.commit()

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
    user_type = db.Column(db.Enum(UserType), nullable=False)
    
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
