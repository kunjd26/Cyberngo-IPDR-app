from flask import Blueprint, request, jsonify
from src.delete_file import delete_file

delete_bp = Blueprint("delete", __name__)


# Delete file endpoint
@delete_bp.route("/api/ipdr-files", methods=["DELETE"])
def delete_file_endpoint():
    """
    Delete File Endpoint
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: The token of the file to be deleted.
    responses:
      200:
        description: File deleted successfully.
      400:
        description: Token not provided or error occurred while deleting the file.
      500:
        description: Error occurred while deleting the file or unknown error occurred.
    """
    try:
        # Check if the token is provided.
        file_token = request.args.get("token")
        if not file_token:
            return jsonify({"status": "fail", "message": "Token not provided."}), 400

        status, result = delete_file(file_token)

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
