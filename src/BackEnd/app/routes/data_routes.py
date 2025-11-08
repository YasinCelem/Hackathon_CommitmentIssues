from flask import Blueprint, jsonify, request
from datetime import datetime
from ..db import get_db
from ..helpers import to_json

data_bp = Blueprint("data", __name__)

@data_bp.get("/")
def list_data():
    """List all data
    ---
    tags: [Data]
    responses:
      200:
        description: OK
    """
    col = get_db()["data"]
    docs = [to_json(d) for d in col.find().sort("_id", -1)]
    return jsonify(docs), 200

@data_bp.post("/")
def create_data():
    """Insert a new record
    ---
    tags: [Data]
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
    res = get_db()["data"].insert_one(data)
    return jsonify({"_id": str(res.inserted_id)}), 201
