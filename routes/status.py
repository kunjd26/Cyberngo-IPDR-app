from flask import Blueprint, request, jsonify
from src.file_status import get_file_status

status_bp = Blueprint("status", __name__)


# Status endpoint
@status_bp.route("/api/ipdr-files/status", methods=["GET"])
def status_file_endpoint():
    """
    Status File Endpoint
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: The token of the file to check the status.
    responses:
      200:
        description: Status retrieved successfully.
      400:
        description: Token not provided or error occurred while retrieving the status.
      500:
        description: Error occurred while retrieving the status or unknown error occurred.
    """
    try:
        # Check if the token is provided.
        file_token = request.args.get("token")
        if not file_token:
            return jsonify({"status": "fail", "message": "Token not provided."}), 400

        status, result = get_file_status(file_token)

        if status == 0:
            return jsonify({"status": "success", "message": result}), 200
        elif status == 1:
            return jsonify({"status": "fail", "message": result}), 400
        elif status == 2:
            return jsonify({"status": "error", "message": result}), 500
        else:
            return (
                jsonify({"status": "error", "message": "Unknown error occurred."}),
                500,
            )

    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500
