from flask import Blueprint, request, jsonify
from src.process_data import analysis_data

analysis_bp = Blueprint("analysis", __name__)


# Analysis endpoint
@analysis_bp.route("/api/ipdr-files/analysis", methods=["GET"])
def analysis_file_endpoint():
    """
    Analysis File Endpoint
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: The token of the file to be analyzed.
      - name: n
        in: query
        type: integer
        required: false
        description: The number of rows to be analyzed. Default is 10.
      - name: columns
        in: query
        type: string
        required: false
        description: The columns to be analyzed. If not provided, all columns are analyzed.
    responses:
      200:
        description: File analyzed successfully.
      400:
        description: Token not provided or error occurred while analyzing the file.
      500:
        description: Error occurred while analyzing the file or unknown error occurred.
    """
    try:
        # Check if the token is provided.
        file_token = request.args.get("token")
        if not file_token:
            return jsonify({"status": "fail", "message": "Token not provided."}), 400

        n = request.args.get("n")
        if not n:
            n = 10
        else:
            n = int(n)

        columns = request.args.get("columns")
        if not columns:
            status, result = analysis_data(file_token, n)
        else:
            status, result = analysis_data(file_token, n, columns)

        if status == 0:
            return jsonify({"status": "success", "data": result}), 200
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
