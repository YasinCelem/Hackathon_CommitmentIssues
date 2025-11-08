from flask import Blueprint, jsonify, request
from ..services import user_service
from ..helpers import to_json

docs_bp = Blueprint("docs", __name__, url_prefix="/api/docs")


@docs_bp.get("/")
def list_docs():
    """List all documents (optionally filter by category)
    ---
    tags: [Documents]
    parameters:
      - name: category
        in: query
        description: Filter by category
        required: false
        schema:
          type: string
    responses:
      200:
        description: Returns a list of documents
    """
    category = request.args.get("category")
    query = {"category": category} if category else {}

    docs = list(mongo.db["documents"].find(query))
    for doc in docs:
        doc["_id"] = str(doc["_id"])
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
        if not isinstance(deadline, list) or len(deadline) != 3:
            return jsonify(success=False, message="Each deadline must be [date, description, recurrence/null]"), 400
    data["created_at"] = datetime.utcnow().isoformat()

    mongo.db["documents"].insert_one(data)
    return jsonify(success=True, message="Document added successfully"), 201


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

    result = mongo.db["documents"].update_one(
        {"_id": ObjectId(doc_id)},
        {"$set": data}
    )

    if result.matched_count == 0:
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
    result = mongo.db["documents"].delete_one({"_id": ObjectId(doc_id)})

    if result.deleted_count == 0:
        return jsonify(success=False, message="Document not found"), 404

    return jsonify(success=True, message="Document deleted successfully"), 200
