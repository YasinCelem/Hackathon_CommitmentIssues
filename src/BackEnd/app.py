# from flask import Flask, jsonify, request, redirect
# from flasgger import Swagger
# from pymongo import MongoClient
# from bson import ObjectId
# import os
# from datetime import datetime

# # --- App setup ---
# app = Flask(__name__)
# Swagger(app)  # Swagger UI at /apidocs

# # --- MongoDB connection ---
# MONGO_URI = os.getenv(
#     "MONGO_URI",
#     "mongodb+srv://testdb:test12345@commitment-issues-clust.2uplkb6.mongodb.net/?retryWrites=true&w=majority",
# )
# DB_NAME = "financial_commitments"
# COLL_NAME = "data"

# client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
# db = client[DB_NAME]
# col = db[COLL_NAME]

# # --- Helpers ---
# def to_json(doc: dict) -> dict:
#     """Convert ObjectId to string for JSON serialization."""
#     d = dict(doc)
#     if "_id" in d:
#         d["_id"] = str(d["_id"])
#     return d

# # --- Routes ---
# @app.get("/")
# def home():
#     """Redirect root to Swagger docs."""
#     return redirect("/apidocs")

# @app.get("/health")
# def health():
#     """Health check
#     ---
#     tags:
#       - Meta
#     responses:
#       200:
#         description: OK
#     """
#     return {"status": "ok", "db": DB_NAME, "collection": COLL_NAME}

# @app.get("/data")
# def get_data():
#     """Get all documents from MongoDB
#     ---
#     tags:
#       - Data
#     responses:
#       200:
#         description: List of documents
#     """
#     docs = [to_json(d) for d in col.find().sort("_id", -1)]
#     return jsonify(docs), 200

# @app.post("/data")
# def create_data():
#     """Insert a new record
#     ---
#     tags:
#       - Data
#     requestBody:
#       required: true
#       content:
#         application/json:
#           schema:
#             type: object
#             properties:
#               name:
#                 type: string
#               amount:
#                 type: number
#               category:
#                 type: string
#             required:
#               - name
#               - amount
#             example:
#               name: "Groceries"
#               amount: 75.5
#               category: "Food"
#     responses:
#       201:
#         description: Created
#       400:
#         description: Bad Request
#     """
#     try:
#         data = request.get_json(force=True)
#     except Exception:
#         return jsonify({"error": "Invalid or missing JSON body"}), 400

#     # Basic validation
#     if not isinstance(data, dict):
#         return jsonify({"error": "Request body must be an object"}), 400

#     name = data.get("name")
#     amount = data.get("amount")

#     if not name or not isinstance(name, str):
#         return jsonify({"error": "'name' must be a string"}), 400
#     if not isinstance(amount, (int, float)):
#         return jsonify({"error": "'amount' must be a number"}), 400

#     data["created_at"] = datetime.utcnow()

#     result = col.insert_one(data)
#     return jsonify({
#         "_id": str(result.inserted_id),
#         "message": "Record created successfully"
#     }), 201


# @app.put("/data/<string:item_id>")
# def update_data(item_id):
#     """Update an existing record
#     ---
#     tags:
#       - Data
#     parameters:
#       - name: item_id
#         in: path
#         required: true
#         schema:
#           type: string
#     requestBody:
#       content:
#         application/json:
#           schema:
#             type: object
#             example:
#               amount: 80
#     responses:
#       200:
#         description: Updated
#       404:
#         description: Not found
#     """
#     try:
#         oid = ObjectId(item_id)
#     except Exception:
#         return jsonify({"error": "Invalid ID"}), 400

#     update = request.get_json(silent=True) or {}
#     if not update:
#         return jsonify({"error": "Empty request body"}), 400

#     result = col.update_one({"_id": oid}, {"$set": update})
#     if result.matched_count == 0:
#         return jsonify({"error": "Not found"}), 404

#     return jsonify({"updated": True}), 200

# @app.delete("/data/<string:item_id>")
# def delete_data(item_id):
#     """Delete a record
#     ---
#     tags:
#       - Data
#     parameters:
#       - name: item_id
#         in: path
#         required: true
#         schema:
#           type: string
#     responses:
#       200:
#         description: Deleted
#       404:
#         description: Not found
#     """
#     try:
#         oid = ObjectId(item_id)
#     except Exception:
#         return jsonify({"error": "Invalid ID"}), 400

#     result = col.delete_one({"_id": oid})
#     if result.deleted_count == 0:
#         return jsonify({"error": "Not found"}), 404

#     return jsonify({"deleted": True}), 200

# # --- Run the app ---
# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)
