import os

# Folder path for uploaded files.
PROCESSED_FOLDER = os.path.join("files", 'processed')

def download_file(file_token):
    try:
                
        # Get the filename associated with the token.
        file_name = f"processed-{file_token}.csv"
        file_path = os.path.join(PROCESSED_FOLDER, file_name)
        
        # Check if the file exists.
        if not os.path.isfile(file_path):
            return 1, "File not found."
        
        return 0, file_path
    
    except Exception as e:
        return 2, str(e)
