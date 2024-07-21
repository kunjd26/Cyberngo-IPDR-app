from flask import Blueprint, request, jsonify
from src.upload_file import upload_file
from src.file_status import update_file_status

upload_bp = Blueprint("upload", __name__)


# Upload endpoint
@upload_bp.route("/api/ipdr-files", methods=["POST"])
def upload_file_endpoint():
    """
    Upload File Endpoint
    ---
    parameters:
      - name: file
        in: formData
        type: file
        required: true
    responses:
      200:
        description: File uploaded successfully
      400:
        description: No file part present in request or no file is selected for upload
      500:
        description: Error occurred while uploading file
    """
    try:
        # Check if the request contains a file.
        if "file" not in request.files:
            return (
                jsonify(
                    {"status": "fail", "message": "No file part present in request."}
                ),
                400,
            )

        file = request.files["file"]
        if file.filename == "":
            return (
                jsonify(
                    {"status": "fail", "message": "No file is selected for upload."}
                ),
                400,
            )

        # Upload the file.
        status, result = upload_file(file)

        if status == 0:
            # Update the file status to 0 (uploaded).
            status1, result1 = update_file_status(result, 0, file.filename)
            if status1 == 0:
                return (
                    jsonify(
                        {
                            "status": "success",
                            "message": "File uploaded successfully.",
                            "token": result,
                        }
                    ),
                    200,
                )
            else:
                return jsonify({"status": "error", "message": result1}), 500
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
        return jsonify({"status": "error", "message": str(e)}), 500
