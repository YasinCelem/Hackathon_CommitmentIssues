from flask import Blueprint, jsonify, request
from app.services import user_service
from app.helpers import to_json

user_bp = Blueprint("users", __name__)
    
@user_bp.get("/")
def list_users():
    """List all users
    ---
    tags: [Users]
    responses:
      200:
        description: OK
    """
    docs = [to_json(u) for u in user_service.list_all()]
    return jsonify(docs), 200

@user_bp.post("/")
def create_user():
    """Create a new user
    ---
    tags: [Users]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username: { type: string }
              email: { type: string }
            required: [username, email]
            example: { username: "johndoe", email: "john@example.com" }
    responses:
      201:
        description: Created
    """
    user = request.get_json(silent=True) or {}
    if "username" not in user or "email" not in user:
        return jsonify({"error": "username and email required"}), 400
    inserted_id = user_service.create(user)
    return jsonify({"_id": inserted_id}), 201
