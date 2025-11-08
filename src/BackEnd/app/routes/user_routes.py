from flask import Blueprint, jsonify, request
from ..services import user_service
from ..helpers import to_json

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
              password: { type: string }
              phone: { type: string }
              company: { type: string }
              language: { type: string }
              timezone: { type: string }

            required: [username, email, password]
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


# Put: Update user
@user_bp.put("/<user_id>")
def update_user(user_id):
    """Update an existing user
    ---
    tags: [Users]
    parameters:
      - in: path
        name: user_id
        schema:
          type: string
        required: true
        description: The user ID
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username: { type: string }
              email: { type: string }
            example: { username: "janedoe", email: "jane@example.com" }   
    responses:
      200:
        description: OK
      404:
        description: Not Found
    """
    user = request.get_json(silent=True) or {}
    updated_count = user_service.update(user_id, user)
    if updated_count == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"updated": updated_count}), 200
  