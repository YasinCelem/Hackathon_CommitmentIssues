from flask import Blueprint, jsonify, request
from datetime import datetime
from src.DataStorage.services import list_all_data, create_data
from ..helpers import to_json

data_bp = Blueprint("data", __name__)

@data_bp.get("/")
def list_data():
    """List all data
    ---
    tags: [Data]
    parameters:
      - name: db_name
        in: query
        description: Database name
        required: false
        schema:
          type: string
    responses:
      200:
        description: OK
    """
    db_name = request.args.get("db_name")
    docs = [to_json(d) for d in list_all_data(db_name=db_name)]
    return jsonify(docs), 200

@data_bp.post("/")
def create_data():
    """Insert a new record
    ---
    tags: [Data]
    parameters:
      - name: db_name
        in: query
        description: Database name
        required: false
        schema:
          type: string
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name: { type: string }
              amount: { type: number }
              category: { type: string }
            required: [name, amount]
            example: { name: "Groceries", amount: 75.5, category: "Food" }
    responses:
      201:
        description: Created
    """
    data = request.get_json(silent=True) or {}
    if "name" not in data or "amount" not in data:
        return jsonify({"error": "name and amount required"}), 400
    data["created_at"] = datetime.utcnow()
    db_name = request.args.get("db_name") or (data.get("db_name") if data else None)
    update_data = {k: v for k, v in data.items() if k != "db_name"}
    doc_id = create_data(update_data, db_name=db_name)
    return jsonify({"_id": doc_id}), 201
