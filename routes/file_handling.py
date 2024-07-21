from flask import Blueprint, request, jsonify
from src.dynamic_parser import get_file_header
from src.file_status import update_file_status

file_header_bp = Blueprint("file_header", __name__)


# Get header of file
@file_header_bp.route("/api/ipdr-files/header", methods=["GET"])
def get_file_header_endpoint():
    """
    Get File Header Endpoint
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: The token of the file to retrieve the header from.
    responses:
      200:
        description: Header retrieved successfully.
      400:
        description: Token not provided or error occurred while parsing the file.
      500:
        description: Error occurred while updating the file status or unknown error occurred.
    """
    try:
        # Check if the token is provided.
        file_token = request.args.get("token")
        if not file_token:
            return jsonify({"status": "fail", "message": "Token not provided."}), 400

        # Parse file through general parser.
        status, result = get_file_header(file_token)

        if status == 1:
            return jsonify({"status": "fail", "message": result}), 400
        elif status == 2:
            # Update the file status to 3 (error in parsing).
            status1, result1 = update_file_status(file_token, 3)
            if status1 == 0:
                return jsonify({"status": "error", "message": result}), 500
            else:
                return jsonify({"status": "error", "message": result1}), 500
        else:
            return jsonify({"status": "success", "message": result}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
