from flask import Flask
from db import db
from flask_cors import CORS
from config import Config
from transactions.routes import transactions_bp
from transactions.models import Transaction
app = Flask(__name__)
CORS(app,origins=["http://localhost:8080,http://localhost:5173", "https://www.fintrack.site", "https://fintrack.site"],supports_credentials=True)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    print("✅ All tables already exist:", db.metadata.tables.keys())


app.register_blueprint(transactions_bp, url_prefix='/api/transactions')

if __name__ == '__main__':
    app.run(debug=True,port=32223)
