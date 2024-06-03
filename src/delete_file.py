import os
import sqlite3

# Folder path for uploaded files.
UPLOAD_FOLDER = os.path.join("files", "uploaded")
PARSED_FOLDER = os.path.join("files", "parsed")
PROCESSED_FOLDER = os.path.join("files", "processed")

def delete_file(file_token):
    try:
        # Connect to the database.
        connection = sqlite3.connect('cyberngo.db')

        cursor = connection.cursor()

        # Check if the file_token exists in the table.
        cursor.execute('SELECT status FROM file_records WHERE file_token = ?', (file_token,))
        data = cursor.fetchone()

        if data is None:
            return 1, "File not found."
        elif data[0] == 1:
            return 1, "File is being processed. Cannot delete the file."
        else:
            # If the file_token exists, update its status.
            cursor.execute('DELETE FROM file_records WHERE file_token = ?', (file_token,))

            connection.commit()

            # Close the connection.
            connection.close()

            # Delete the file from the folder.
            file_path = os.path.join(UPLOAD_FOLDER, f"uploaded-{file_token}.csv")
            if os.path.exists(file_path):
                os.remove(file_path)

            file_path = os.path.join(PARSED_FOLDER, f"parsed-{file_token}.csv")
            if os.path.exists(file_path):
                os.remove(file_path)

            file_path = os.path.join(PROCESSED_FOLDER, f"processed-{file_token}.csv")
            if os.path.exists(file_path):
                os.remove(file_path)

        return 0, "File deleted successfully."

    except Exception as e:
        return 2, str(e)
