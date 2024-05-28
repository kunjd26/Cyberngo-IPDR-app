from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from src.upload_file import upload_file
from src.general_parser import parse_file
from src.process_file import append_fields
from src.download_file import download_file
from src.process_data import analysis_data

app = Flask(__name__)
CORS(app)

# Upload endpoint
@app.route('/api/upload', methods=['POST'])
def upload_file_endpoint():
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
            return jsonify({"status": "success", "message": "File uploaded successfully.", "token": result}), 200
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
            return jsonify({"status": "error", "message": result}), 500
        else:
            # Append the files.
            status, result = append_fields(file_token, static_db_only)

            if status == 0:
                return jsonify({"status": "success", "message": "File executed successfully."}), 200
            elif status == 1:
                return jsonify({"status": "fail", "message": result}), 400
            elif status == 2:
                return jsonify({"status": "error", "message": result}), 500
            else:
                return jsonify({"status": "error", "message": "Unknown error occurred."}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Download endpoint
@app.route('/api/download/', methods=['GET'])
def download_file_endpoint():
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


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)