# src/BackEnd/app/routes/user_routes.py
from flask import Blueprint, request, jsonify
from ..services import user_service

user_bp = Blueprint("user", __name__, url_prefix="/users")


@user_bp.post("/register")
def register():
    """
    Register a new user
    ---
    tags: [Users]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username: { type: string, example: "ted" }
              email:    { type: string, format: email, example: "ted@example.com" }
              password: { type: string, format: password, example: "S3cureP@ss!" }
            required: [username, email, password]
          example:
            username: "ted"
            email: "ted@example.com"
            password: "S3cureP@ss!"
    responses:
      201:
        description: Created
        content:
          application/json:
            schema:
              type: object
              properties:
                message: { type: string, example: "User registered successfully" }
                id:      { type: string, example: "6760f3d58d9b0b9a4c4a2f30" }
      400:
        description: Missing fields or duplicate username/email
        content:
          application/json:
            schema:
              type: object
              properties:
                error: { type: string, example: "Username already exists." }
    """
    data = request.get_json() or {}
    try:
        user_id = user_service.register(data)
        return jsonify({"message": "User registered successfully", "id": user_id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@user_bp.post("/login")
def login():
    """
    User login
    ---
    tags: [Users]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username: { type: string, example: "ted" }
              password: { type: string, format: password, example: "S3cureP@ss!" }
            required: [username, password]
          example:
            username: "ted"
            password: "S3cureP@ss!"
    responses:
      200:
        description: Login successful
        content:
          application/json:
            schema:
              type: object
              properties:
                message: { type: string, example: "Login successful" }
                user:
                  type: object
                  properties:
                    id:       { type: string, example: "6760f3d58d9b0b9a4c4a2f30" }
                    username: { type: string, example: "ted" }
      401:
        description: Invalid username or password
        content:
          application/json:
            schema:
              type: object
              properties:
                error: { type: string, example: "Invalid username or password" }
    """
    data = request.get_json() or {}
    user = user_service.login(data.get("username_or_email"), data.get("password"))
    if user:
        return jsonify({
            "message": "Login successful",
            "user": {"id": str(user["_id"]), "username": user["username"]}
        }), 200
    return jsonify({"error": "Invalid username or password"}), 401


@user_bp.get("/<user_id>")
def get_user(user_id: str):
    """
    Get user by ID
    ---
    tags: [Users]
    parameters:
      - in: path
        name: user_id
        required: true
        schema: { type: string }
        description: Mongo ObjectId of the user
        example: "6760f3d58d9b0b9a4c4a2f30"
    responses:
      200:
        description: User document (without password)
        content:
          application/json:
            schema:
              type: object
              properties:
                _id:      { type: string, example: "6760f3d58d9b0b9a4c4a2f30" }
                username: { type: string, example: "ted" }
                email:    { type: string, example: "ted@example.com" }
      404:
        description: User not found
        content:
          application/json:
            schema:
              type: object
              properties:
                error: { type: string, example: "User not found" }
    """
    user = user_service.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return jsonify(user), 200
  
@user_bp.get("/<username>/profile")
def get_user_profile(username: str):
    """
    Get user profile by username
    ---
    tags: [Users]
    parameters:
      - in: path
        name: username
        required: true
        schema: { type: string }
        description: Username of the user
        example: "ted"
    responses:
      200:
        description: User profile document (without password)
        content:
          application/json:
            schema:
              type: object
              properties:
                _id:      { type: string, example: "6760f3d58d9b0b9a4c4a2f30" }
                username: { type: string, example: "ted" }
                email:    { type: string, example: "ted@example.com" }
      404:
        description: User not found
        content:
          application/json:
            schema:
              type: object
              properties:
                error: { type: string, example: "User not found" }
    """
    user = user_service.find_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return jsonify(user), 200

@user_bp.delete("/<user_id>")
def delete_user(user_id: str):
    """
    Delete a user by ID
    ---
    tags: [Users]
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: string
        description: Mongo ObjectId of the user to delete
        example: "6760f3d58d9b0b9a4c4a2f30"
    responses:
      200:
        description: User deleted successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "User deleted successfully"
      404:
        description: User not found
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "User not found"
      400:
        description: Invalid user_id format
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Invalid user_id format"
    """
    try:
        deleted = user_service.delete(user_id)
    except Exception:
        return jsonify({"error": "Invalid user_id format"}), 400

    if not deleted:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "User deleted successfully"}), 200

