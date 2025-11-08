from flask import Flask, jsonify, redirect
from flasgger import Swagger
from pymongo import MongoClient
from bson import ObjectId
import os

# ----------------------------
# Flask setup
# ----------------------------
app = Flask(__name__)
Swagger(app)  # Swagger UI available at /apidocs

# ----------------------------
# MongoDB setup
# ----------------------------
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://testdb:test12345@commitment-issues-clust.2uplkb6.mongodb.net/?retryWrites=true&w=majority",
)

# Connect to MongoDB
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
db = client["financial_commitments"]  # Database
col = db["data"]                      # Collection

# ----------------------------
# Utility functions
# ----------------------------
def to_json(doc: dict) -> dict:
    """Convert MongoDB ObjectId to string for JSON serialization"""
    return {**doc, "_id": str(doc["_id"])}

# ----------------------------
# Routes
# ----------------------------

@app.get("/")
def home():
    """Redirect to Swagger UI"""
    return redirect("/apidocs")

@app.get("/health")
def health():
    """Health check endpoint
    ---
    tags:
      - Meta
    responses:
      200:
        description: API is healthy
    """
    return {"status": "ok"}

@app.get("/data")
def get_data():
    """Get all documents from MongoDB
    ---
    tags:
      - Data
    responses:
      200:
        description: List of documents
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
    """
    docs = [to_json(d) for d in col.find()]
    return jsonify(docs), 200

@app.post("/data")
def create_data():
    """Insert a new document
    ---
    tags:
      - Data
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            example:
              name: "Expense A"
              amount: 100
              category: "Food"
    responses:
      201:
        description: Created
    """
    from flask import request
    data = request.json
    result = col.insert_one(data)
    return jsonify({"_id": str(result.inserted_id)}), 201

@app.put("/data/<string:item_id>")
def update_data(item_id):
    """Update a document by ID
    ---
    tags:
      - Data
    parameters:
      - name: item_id
        in: path
        required: true
        schema:
          type: string
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            example:
              amount: 200
    responses:
      200:
        description: Updated
    """
    from flask import request
    update = request.json
    result = col.update_one({"_id": ObjectId(item_id)}, {"$set": update})
    if result.matched_count == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"updated": True}), 200

@app.delete("/data/<string:item_id>")
def delete_data(item_id):
    """Delete a document by ID
    ---
    tags:
      - Data
    parameters:
      - name: item_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Deleted
    """
    result = col.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"deleted": True}), 200

# ----------------------------
# Run the app
# ----------------------------
if __name__ == "__main__":
    # host="0.0.0.0" allows access from other devices on the network
    app.run(debug=True, host="0.0.0.0", port=5000)
