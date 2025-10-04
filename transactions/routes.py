from flask import Blueprint, jsonify, request
from datetime import datetime
from transactions.models import Transaction,Type, Category
from transactions.services import (
    create_transaction,
    get_transaction,
    delete_transaction,
    str_to_category_enum,
    get_transactions_by_month,
    get_transactions_by_date,
update_transaction
)
from db import db

transactions_bp = Blueprint('transactions_bp', __name__, url_prefix='/api/transactions')

@transactions_bp.route('/<id>', methods=['GET'])
def getTransaction(id) :
    transaction = get_transaction(id)
    if transaction is None:
        return jsonify({}), 404
    return jsonify(transaction.to_dict()), 200

@transactions_bp.route('/create-transaction', methods=['POST'])
def createTransaction() :
    data = request.get_json()
    if not data:
        return jsonify({}), 400
    category = data.get('category')
    categoryEnum = str_to_category_enum(category)
    created_transaction = create_transaction(
        user_id=data['user_id'],
        description=data['description'],
        amount=data['amount'],
        transaction_type=(Type.INCOME if data['type'] == "income" else Type.EXPENSE),
        category=categoryEnum,
        date=data['date'],
    )

    return jsonify(created_transaction.to_dict()), 201

@transactions_bp.route('/', methods=['DELETE'])
def deleteTransaction() :
    id = request.args.get('id')
    result = delete_transaction(id)
    if result:
        return jsonify({}), 204
    return jsonify({}), 404

@transactions_bp.route('/get-monthly-transactions', methods=['POST'])
def getTransactionsByMonth() :
    """
    Query parameters:
        - user_id: int
        - start_date: YYYY-MM-DD
        - end_date: YYYY-MM-DD
        - type: "income" or "outcome"
    Returns:
        JSON: { "2025-09-01": 1200.0, "2025-09-02": 800.0, ... }
    """
    user_id = request.get_json()['user_id']
    query_date = request.get_json()['query_date']
    type = request.get_json()['type']

    if not all([user_id, query_date, type]):
        return jsonify({'error': 'missing required parameters'}), 400

    query_date = datetime.strptime(query_date, '%Y-%m-%d')

    summary = get_transactions_by_month(user_id, query_date, Type.INCOME if type == "income" else Type.EXPENSE)

    return jsonify(summary), 200

@transactions_bp.route('/get-transactions', methods=['GET'])
def getTransactionsByDate() :
    user_id = request.args.get('user_id')
    query_date = request.args.get('query_date')
    query_date = datetime.strptime(query_date, "%Y-%m-%d")
    typeArg = request.args.get('type')

    if not all([user_id, query_date, typeArg]):
        return jsonify({'error': 'missing required parameters'}), 400

    result = get_transactions_by_date(user_id, query_date, Type.INCOME if typeArg == "income" else Type.EXPENSE)
    result_to_dict = [transaction.to_dict() for transaction in result]
    return jsonify(result_to_dict), 200

"""
这个function是用在expense和income graph上面的
"""
@transactions_bp.route("/get-transactions-summary-by-dates", methods=['POST'])
def getTransactionsSummaryByDates():
    data = request.get_json()
    if not data:
        return jsonify({"error": "missing json body"}), 400

    user_id = data.get('user_id')
    typeArg = data.get('type').upper()
    """
        query_dates should be an string array of date
    """
    query_dates = data.get('query_dates')
    query_dates_dateObj = [datetime.strptime(d,"%Y-%m-%d") for d in query_dates]

    if not all([user_id, query_dates, typeArg]):
        return jsonify({'error': 'missing required parameters'}), 400
    result = []
    for dateObj in query_dates_dateObj:
        sum = 0
        transactions = get_transactions_by_date(user_id,dateObj,typeArg)
        for transaction in transactions:
            sum+=transaction.amount
        temp = []
        temp.append(dateObj.isoformat().split("T")[0])
        temp.append(sum)
        result.append(temp)
    return jsonify(result), 200

"""
这个function是用在frequency map上面的
"""
@transactions_bp.route("/get-transactions-by-dates", methods=['GET'])
def getTransactionsByDates():
    data = request.get_json()
    if not data:
        return jsonify({"error": "missing json body"}), 400

    user_id = data.get('user_id')
    category = data.get('category')
    """
        query_dates should be an string array of date
    """
    query_dates = data.get('query_dates')
    query_dates_dateObj = [datetime.strptime(d,"%Y-%m-%d") for d in query_dates]

    if not all([user_id, query_dates, category]):
        return jsonify({'error': 'missing required parameters'}), 400
    result = []
    for dateObj in query_dates_dateObj:
        transactions = get_transactions_by_date(user_id,dateObj,category=category)
        transactions = [transaction.to_dict() for transaction in transactions]
        result.append(transactions)
    return jsonify(result), 200

@transactions_bp.route("/<transaction_id>", methods=["PUT"])
def updateTransaction(transaction_id):
    data = request.get_json() or {}

    description = data.get("description")
    amount = data.get("amount")

    if description is None and amount is None:
        return jsonify({"error":"No fields provided to update"}), 400

    transaction = update_transaction(transaction_id, description=description, amount=amount)
    if transaction is None:
        return jsonify({"error":"Transaction not found"}), 404

    return jsonify({
        "id": transaction.id,
        "description": transaction.description,
        "amount": transaction.amount
    }), 200

"""
这个function是用在pie chart上面的
"""
@transactions_bp.route("/get-summary-by-category-by-dates", methods=["POST"])
def getSummaryByCategoryByDates():
    data = request.get_json() or {}
    user_id = data['user_id']
    query_dates = data['query_dates']
    categories = data['categories']

    if not all([user_id,query_dates,categories]):
        return jsonify({"error": "invalid request, parameters are missing!"}), 400


    categoriesList = []
    amountList = []
    result = [categoriesList,amountList]
    for category in categories:
        sum = 0
        for date in query_dates:
            transactions = get_transactions_by_date(user_id,query_date=date,category=category.upper())
            for transaction in transactions:
                sum+= transaction.amount
        categoriesList.append(category)
        amountList.append(sum)


    return jsonify(result), 200

"""
这个function是用在frequencyMap上面的
"""
@transactions_bp.route("/get-summary-by-category-by-dates-frenquency", methods=["POST"])
def getSummaryByCategoryByDatesFrequency():
    data = request.get_json() or {}
    user_id = data['user_id']
    query_dates = data['query_dates']
    categories = data['categories']

    if not all([user_id,query_dates,categories]):
        return jsonify({"error": "invalid request, parameters are missing!"}), 400


    resultList = []
    for category in categories:
        frequencyList = []
        result = [query_dates,frequencyList]
        for date in query_dates:
            sum = 0
            transactions = get_transactions_by_date(user_id,query_date=date,category=category.upper())
            for transaction in transactions:
                sum+=1
            frequencyList.append(sum)
        resultList.append(result)


    return jsonify(resultList), 200