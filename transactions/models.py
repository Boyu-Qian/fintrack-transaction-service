import uuid
from db import db
from datetime import datetime
from enum import Enum

class Type(Enum):
    INCOME = "income"
    EXPENSE = "expense"

class IncomeCategory(Enum):
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENT = "investment"

class ExpenseCategory(Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    HOMEBILLS = "homebills"
    SELFCARE = "selfcare"
    SHOPPING = "shopping"
    HEALTH = "health"

class Category(Enum):
    # Income
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENT = "investment"

    # Expense
    FOOD = "food"
    TRANSPORT = "transport"
    HOMEBILLS = "homebills"
    SELFCARE = "selfcare"
    SHOPPING = "shopping"
    HEALTH = "health"

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    user_id = db.Column(db.String(36), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.Enum(Type), nullable=False)
    category = db.Column(db.Enum(Category), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Transaction {self.id} {self.type.value} {self.amount}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "type": self.type.value,
            "date": self.date.strftime("%Y-%m-%d"),
            "category": self.category.value,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }