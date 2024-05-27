from flask import Flask, request, jsonify, send_file
import os, time, random
from append_fields1 import process_file
from general_parser import parse_file
from analysis_data import get_analysis_data

app = Flask(__name__)

# Helper function to check if the file has an allowed extension
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


# Upload endpoint
@app.route('/api/upload/', methods=['POST'])
def upload_file():
    try:
        # Allowed file extensions
        allowed_extensions = {'csv'}


        if 'file' not in request.files:
            return jsonify({"error": {"message": "No file part in the request"}}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": {"message": "No file selected for uploading"}}), 400

        # Check if the file has an allowed extension
        if not allowed_file(file.filename, allowed_extensions):
            return jsonify({"error": {"message": "File type not allowed"}}), 400

        # Generate a token for the file
        token = f"{int(time.time())}_{random.randint(1000, 9999)}"
        new_filename = f"uploaded_{token}.csv"

        # Create the upload folder if it doesn't exist
        upload_folder = os.path.join("files", 'uploaded')
        os.makedirs(upload_folder, exist_ok=True)

        # Define the file path
        file_path = os.path.join(upload_folder, new_filename)

        # Save the file, overwriting if it already exists
        file.save(file_path)

        return jsonify({"data": {"token": token, "message": "File uploaded successfully"}}), 200
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500
    

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