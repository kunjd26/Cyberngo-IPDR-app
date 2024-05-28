from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from src.upload_file import upload_file
from append_fields import process_file
from general_parser import parse_file
from analysis_data import get_analysis_data

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
def execute_file():
    try:
        token = request.args.get('token')
        if not token:
            return jsonify({"error": {"message": "No token provided"}}), 400
        
        # Parse file through general parser
        return_value = parse_file(token)
        
        if (return_value != 0):
            return jsonify({"error": {"message": return_value}}), 400
        
        # Append extra fields to the file
        return_value = process_file(token)

        if (return_value != 0):
            return jsonify({"error": {"message": return_value}}), 400
        
        return jsonify({"data": {"token": token, "message": "File executed successfully."}}), 200
    
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500


# Download endpoint
@app.route('/api/download/', methods=['GET'])
def download_file():
    try:
        token = request.args.get('token')
        
        token = request.args.get('token')
        if not token:
            return jsonify({"error": {"message": "No token provided"}}), 400
        
        # Get the filename associated with the token
        filename = f"appended_{token}.csv"
        filepath = os.path.join('files', 'appended', filename)
        
        # Check if the file exists
        if not os.path.isfile(filepath):
            return jsonify({"error": {"message": "File not found"}}), 404
        
        # Send the file for download
        return send_file(filepath, as_attachment=True, download_name=f"{token}.csv")
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500


# Analysis endpoint
@app.route('/api/analysis/', methods=['GET'])
def analysis_file():
    try:
        token = request.args.get('token')
        
        token = request.args.get('token')
        if not token:
            return jsonify({"error": {"message": "No token provided"}}), 400
        
        n = request.args.get('n')
        if not n:
            n = 10
        else:
            n = int(n)

        columns = request.args.get('columns')
        if not columns:
            return_value, analyzed_data = get_analysis_data(token, n)
        else:
            return_value, analyzed_data = get_analysis_data(token, n, columns)
            
        if (return_value != 0):
            return jsonify({"error": {"message": return_value}}), 400
        
        return jsonify({"data": {"message": "Analysis completed successfully.", "analysis" :analyzed_data}}), 200
    
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)