from flask import Blueprint, request, jsonify
from src.file_status import get_recent_files

recent_files_bp = Blueprint("recent_files", __name__)


# Recent file endpoint
@recent_files_bp.route("/api/ipdr-files", methods=["GET"])
def recent_file_endpoint():
    """
    Recent Files Endpoint
    ---
    parameters:
      - name: n
        in: query
        type: integer
        required: false
        description: The number of recent files to be retrieved. Default is 5.
    responses:
      200:
        description: Recent files retrieved successfully.
      400:
        description: Error occurred while retrieving the recent files.
      500:
        description: Error occurred while retrieving the recent files or unknown error occurred.
    """
    try:
        # Check if the token is provided.
        n = request.args.get("n")
        if not n:
            n = 5
        else:
            n = int(n)

        status, result = get_recent_files(n)

        if status == 0:
            return jsonify({"status": "success", "data": result}), 200
        elif status == 1:
            return jsonify({"status": "fail", "message": result}), 400
        elif status == 2:
            return jsonify({"status": "fail", "message": result}), 500
        else:
            return (
                jsonify({"status": "error", "message": "Unknown error occurred."}),
                500,
            )

    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500
