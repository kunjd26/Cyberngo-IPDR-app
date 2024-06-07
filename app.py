from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from src.upload_file import upload_file
from src.general_parser import parse_file
from src.process_file import append_fields
from src.download_file import download_file
from src.process_data import analysis_data
from src.file_status import get_file_status, update_file_status, get_recent_files
from src.delete_file import delete_file
from flasgger import Swagger

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# Upload endpoint
@app.route('/api/upload', methods=['POST'])
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
        if 'file' not in request.files:
            return jsonify({"status": "fail", "message": "No file part present in request."}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "fail", "message": "No file is selected for upload."}), 400
        
        # Upload the file.
        status, result = upload_file(file)

        if status == 0:
            # Update the file status to 0 (uploaded).
            status1, result1 = update_file_status(result, 0, file.filename)
            if status1 == 0:
                return jsonify({"status": "success", "message": "File uploaded successfully.", "token": result}), 200
            else:
                return jsonify({"status": "error", "message": result1}), 500
        elif status == 1:
            return jsonify({"status": "fail", "message": result}), 400
        elif status == 2:
            return jsonify({"status": "error", "message": result}), 500
        else:
            return jsonify({"status": "error", "message": "Unknown error occurred."}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Execute endpoint
@app.route('/api/execute/', methods=['GET'])
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
        file_token = request.args.get('token')
        if not file_token:
            return jsonify({"status": "fail", "message": "Token not provided."}), 400
        
        # Check if the static database only parameter provided.
        static_db_only = request.args.get('static_db_only')
        if not static_db_only:
            static_db_only = False
        else:
            if static_db_only.lower() == 'true':
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
                    return jsonify({"status": "success", "message": "File executed successfully."}), 200
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
                return jsonify({"status": "error", "message": "Unknown error occurred."}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Download endpoint
@app.route('/api/download/', methods=['GET'])
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
        file_token = request.args.get('token')
        if not file_token:
            return jsonify({"status": "fail", "message": "Token not provided."}), 400
        
        status, result = download_file(file_token)

        if status == 0:
            return send_file(result, as_attachment=True, download_name=f"{file_token}.csv")
        elif status == 1:
            return jsonify({"status": "fail", "message": result}), 400
        elif status == 2:
            return jsonify({"status": "error", "message": result}), 500
        else:
            return jsonify({"status": "error", "message": "Unknown error occurred."}), 500

    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500


# Analysis endpoint
@app.route('/api/analysis/', methods=['GET'])
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
        file_token = request.args.get('token')
        if not file_token:
            return jsonify({"status": "fail", "message": "Token not provided."}), 400
        
        n = request.args.get('n')
        if not n:
            n = 10
        else:
            n = int(n)

        columns = request.args.get('columns')
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
            return jsonify({"status": "error", "message": "Unknown error occurred."}), 500
    
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500


# Status endpoint
@app.route('/api/status/', methods=['GET'])
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
        file_token = request.args.get('token')
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
            return jsonify({"status": "error", "message": "Unknown error occurred."}), 500
    
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500


# Recent file endpoint
@app.route('/api/recent-files', methods=['GET'])
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
        n = request.args.get('n')
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
            return jsonify({"status": "error", "message": "Unknown error occurred."}), 500
    
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500


# Delete file endpoint
@app.route('/api/delete-file', methods=['DELETE'])
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
        file_token = request.args.get('token')
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
            return jsonify({"status": "error", "message": "Unknown error occurred."}), 500
    
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500


# Run the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
