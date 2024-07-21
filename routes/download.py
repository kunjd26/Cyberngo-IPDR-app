from flask import Blueprint, request, jsonify, send_file
from src.download_file import download_file

download_bp = Blueprint("download", __name__)


# Download endpoint
@download_bp.route("/api/ipdr-files/download", methods=["GET"])
def download_file_endpoint():
    """
    Download File Endpoint
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: The token of the file to be downloaded.
    responses:
      200:
        description: File downloaded successfully.
      400:
        description: Token not provided or error occurred while downloading the file.
      500:
        description: Error occurred while downloading the file or unknown error occurred.
    """
    try:
        # Check if the token is provided.
        file_token = request.args.get("token")
        if not file_token:
            return jsonify({"status": "fail", "message": "Token not provided."}), 400

        status, result = download_file(file_token)

        if status == 0:
            return send_file(
                result, as_attachment=True, download_name=f"{file_token}.csv"
            )
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
