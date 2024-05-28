import os
import uuid

# Folder path for uploaded files.
UPLOAD_FOLDER = os.path.join("files", "uploaded")

# Allowed file extensions.
allowed_extensions = {'csv'}

def upload_file(file):
    try:
        # Check if the file has an allowed extension.
        if not allowed_file(file.filename, allowed_extensions):
            return 1, "File type not allowed."
        
        # Generate a token for the file.
        token = uuid.uuid4()
        new_filename = f"uploaded-{token}.csv"

        # Create the upload folder if it doesn't exist.
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Define the file path
        file_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, new_filename))

        # Save the file, overwriting if it already exists
        file.save(file_path)

        return 0, token
    
    except Exception as e:
        return 2, str(e)
    
# Helper function to check if the file has an allowed extension
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
