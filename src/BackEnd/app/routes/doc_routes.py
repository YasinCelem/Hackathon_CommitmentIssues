from flask import Blueprint, jsonify, request
from bson import ObjectId
from datetime import datetime
from src.DataStorage.services import (
    list_documents,
    find_document_by_id,
    create_document,
    update_document,
    delete_document
)

docs_bp = Blueprint("docs", __name__, url_prefix="/api/docs")


@docs_bp.get("/")
def list_docs():
    """List all documents (optionally filter by category and user_id)
    ---
    tags: [Documents]
    parameters:
      - name: category
        in: query
        description: Filter by category
        required: false
        schema:
          type: string
      - name: user_id
        in: query
        description: Filter by user_id
        required: false
        schema:
          type: string
    responses:
      200:
        description: Returns a list of documents
    """
    category = request.args.get("category")
    user_id = request.args.get("user_id")
    db_name = request.args.get("db_name")
    
    docs = list_documents(category=category, user_id=user_id, db_name=db_name)
    return jsonify(docs), 200

@docs_bp.post("/")
def add_doc():
    """Add a new document
    ---
    tags: [Documents]
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              category:
                type: string
                description: One of the allowed categories
              name:
                type: string
                description: Formatted as YYYY-MM-DD - CategoryLeaf - IssuerOrParty - ShortTitle
              date_received:
                type: string
                nullable: true
                description: Date received or null
              deadlines:
                type: array
                items:
                  type: array
                  items:
                    type: string
                description: Array of [date, description, recurrence/null]
            required: [category, name, deadlines]
    responses:
      201:
        description: Document created successfully
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify(success=False, message="Invalid or missing JSON body"), 400
    required_fields = ["category", "name", "deadlines"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify(success=False, message=f"Missing fields: {', '.join(missing)}"), 400
    if data.get("date_received") and data["date_received"] != "null":
        try:
            datetime.strptime(data["date_received"], "%Y-%m-%d")
        except ValueError:
            return jsonify(success=False, message="Invalid date_received format, expected YYYY-MM-DD"), 400
    else:
        data["date_received"] = None
    for deadline in data.get("deadlines", []):
        if isinstance(deadline, list):
            if len(deadline) != 3:
                return jsonify(success=False, message="Each deadline must be [date, description, recurrence/null]"), 400
        elif isinstance(deadline, dict):
            if "date" not in deadline or "description" not in deadline:
                return jsonify(success=False, message="Each deadline object must have 'date' and 'description' fields"), 400
        else:
            return jsonify(success=False, message="Each deadline must be either [date, description, recurrence] or {date, description, recurrence}"), 400
    data["created_at"] = datetime.utcnow().isoformat()
    
    db_name = request.args.get("db_name") or (request.get_json(silent=True) or {}).get("db_name")

    doc_id = create_document(data, db_name=db_name)
    return jsonify(success=True, message="Document added successfully", id=doc_id), 201


@docs_bp.put("/<doc_id>")
def update_doc(doc_id):
    """Update a document by ID
    ---
    tags: [Documents]
    parameters:
      - name: doc_id
        in: path
        required: true
        schema:
          type: string
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              category:
                type: string
              name:
                type: string
              date_received:
                type: string
              deadlines:
                type: array
                items:
                  type: array
                  items:
                    type: string
    responses:
      200:
        description: Document updated successfully
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify(success=False, message="Missing update data"), 400

    db_name = request.args.get("db_name") or (data.get("db_name") if data else None)
    update_data = {k: v for k, v in data.items() if k != "db_name"}

    updated = update_document(doc_id, update_data, db_name=db_name)
    if not updated:
        return jsonify(success=False, message="Document not found"), 404

    return jsonify(success=True, message="Document updated successfully"), 200

@docs_bp.delete("/<doc_id>")
def delete_doc(doc_id):
    """Delete a document
    ---
    tags: [Documents]
    parameters:
      - name: doc_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Document deleted successfully
    """
    db_name = request.args.get("db_name")
    
    deleted = delete_document(doc_id, db_name=db_name)
    if not deleted:
        return jsonify(success=False, message="Document not found"), 404

    return jsonify(success=True, message="Document deleted successfully"), 200
