from flask import session
from sqlalchemy import func
from db import db
from transactions.models import Type, Category, Transaction
from datetime import datetime
import calendar
import time
from typing import List, Optional
import uuid

def create_transaction(user_id, transaction_type, amount, category,date,description=""):
    transaction = Transaction(
        user_id=user_id,
        type=transaction_type,
        amount=amount,
        category=category,
        description=description,
        date=datetime.strptime(date, "%Y-%m-%d"),
        created_at=datetime.utcnow().replace(second=0, microsecond=0),
    )

    db.session.add(transaction)
    db.session.commit()
    return transaction

def update_transaction(transaction_id,description=None,amount=None):
    print(transaction_id)
    transaction = get_transaction(transaction_id)
    if not transaction:
        return None
    if description is not None:
        transaction.description = description
    if amount is not None:
        transaction.amount = amount
    db.session.commit()
    return transaction


# If not such transaction, it will return None
def get_transaction(transaction_id):
    return db.session.get(Transaction,transaction_id)

def delete_transaction(transaction_id) -> bool :
    transaction = get_transaction(transaction_id)
    if transaction is None:
        return False
    db.session.delete(transaction)
    db.session.commit()
    return True

def get_transactions_by_month(user_id, query_date, transaction_type):
    date_range = calendar.monthrange(query_date.year, query_date.month)
    start_date = query_date.replace(day=1)
    end_date = query_date.replace(day=date_range[1])
    transactions = db.session.query(Transaction.date,func.sum(Transaction.amount).label('total')).filter(
        Transaction.user_id == user_id,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.type == transaction_type
    ).group_by(Transaction.date).order_by(Transaction.date.desc()).all()
    print(transactions)
    summary = {r.date.isoformat().split('T')[0]: r.total for r in transactions}

    all_days = []
    for date in range(1,date_range[1]+1):
        str = (start_date.replace(day=date)).isoformat().split('T')[0]
        all_days.append(str)
    for date in all_days:
        if date not in summary:
            summary[date] = 0
    time.sleep(.5)
    summary_list = [{"date":k,"total":v} for k,v in summary.items()]
    summary_list.sort(key=lambda x: x["date"])

    return summary_list

def get_transactions_by_date(user_id, query_date, transaction_type=None, category=None):
    transactions = db.session.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.date == query_date,
    )

    if transaction_type is not None:
        transactions = transactions.filter(Transaction.type == transaction_type)

    if category is not None:
        transactions = transactions.filter(Transaction.category == category)

    return transactions.all()



def str_to_category_enum(value: str) -> Category:
    """
    Convert a string from frontend to Category Enum.
    Raises ValueError if the string is invalid.
    """
    try:
        return Category(value)
    except ValueError:
        raise ValueError(f"Invalid category: {value}")




