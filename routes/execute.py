from flask import Blueprint, request, jsonify
from src.general_parser import parse_file
from src.process_file import append_fields
from src.file_status import update_file_status

execute_bp = Blueprint("execute", __name__)


# Execute endpoint
@execute_bp.route("/api/ipdr-files/execute", methods=["GET"])
def execute_file_endpoint():
    """
    Execute File Endpoint
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: The token of the file to be executed.
      - name: static_db_only
        in: query
        type: boolean
        required: false
        description: Whether to use only the static database or not.
    responses:
      200:
        description: File executed successfully.
      400:
        description: Token not provided or error occurred while parsing the file.
      500:
        description: Error occurred while executing the file.
    """
    try:
        # Check if the token is provided.
        file_token = request.args.get("token")
        if not file_token:
            return jsonify({"status": "fail", "message": "Token not provided."}), 400

        # Check if the static database only parameter provided.
        static_db_only = request.args.get("static_db_only")
        if not static_db_only:
            static_db_only = False
        else:
            if static_db_only.lower() == "true":
                static_db_only = True
            else:
                static_db_only = False

        # Parse file through general parser.
        status, result = parse_file(file_token)

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
            # Update the file status to 1 (processing).
            status1, result1 = update_file_status(file_token, 1)
            if status1 == 0:
                # Append the files.
                status, result = append_fields(file_token, static_db_only)
            else:
                return jsonify({"status": "error", "message": result1}), 500
            if status == 0:
                # Update the file status to 2 (processed).
                status1, result1 = update_file_status(file_token, 2)
                if status1 == 0:
                    return (
                        jsonify(
                            {
                                "status": "success",
                                "message": "File executed successfully.",
                            }
                        ),
                        200,
                    )
                else:
                    return jsonify({"status": "error", "message": result1}), 500
            elif status == 1:
                return jsonify({"status": "fail", "message": result}), 400
            elif status == 2:
                # Update the file status to 4 (error in processing).
                status1, result1 = update_file_status(file_token, 4)
                if status1 == 0:
                    return jsonify({"status": "error", "message": result}), 500
                else:
                    return jsonify({"status": "error", "message": result1}), 500
            else:
                return (
                    jsonify({"status": "error", "message": "Unknown error occurred."}),
                    500,
                )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
