import sqlite3
import time

# Status codes mapping
FILE_STATUS_CODES = {
    "0": "File uploaded.",
    "1": "File in progress.",
    "2": "File ready for analysis.",
    "3": "Error in file parsing.",
    "4": "Error in file processing.",
}

# Get the status of the file from the database.
def get_file_status(file_token):
    try:
                
        # Connect to the database.
        connection = sqlite3.connect('cyberngo.db')

        # Get the status of the file.
        cursor = connection.cursor()
        cursor.execute('SELECT status FROM file_records WHERE file_token = ?', (file_token,))
        status = cursor.fetchone()

        # Close the connection.
        connection.close()

        if status is None:
            return 1, "File not found."
        else:
            status = status[0]

        # Map status to status message.
        return 0, FILE_STATUS_CODES[str(status)]
    
    except Exception as e:
        return 2, str(e)
    

# Update or insert the file status in the database.
def update_file_status(file_token, status, file_name="None"):
    try:
        # Connect to the database.
        connection = sqlite3.connect('cyberngo.db')

        cursor = connection.cursor()

        # Check if the file_token exists in the table.
        cursor.execute('SELECT * FROM file_records WHERE file_token = ?', (file_token,))
        data = cursor.fetchone()

        if data is None:
            # If the file_token does not exist, insert it with the current timestamp and status as 0.
            timestamp = str(int(time.time()))
            cursor.execute('INSERT INTO file_records (file_name, file_token, status, timestamp) VALUES (?, ?, ?, ?)', (file_name, file_token, 0, timestamp))
        else:
            # If the file_token exists, update its status.
            cursor.execute('UPDATE file_records SET status = ? WHERE file_token = ?', (status, file_token))

        connection.commit()

        # Close the connection.
        connection.close()

        return 0, None

    except Exception as e:
        return 2, str(e)


# Get recent files_token and status from the database.
def get_recent_files(LIMIT=5):
    try:
        # Connect to the database.
        connection = sqlite3.connect('cyberngo.db')

        cursor = connection.cursor()

        # Get the recent files.
        cursor.execute('SELECT * FROM file_records ORDER BY timestamp DESC LIMIT ?', (LIMIT,))
        data = cursor.fetchall()

        # Close the connection.
        connection.close()

        if not data:
            return 1, "No files found."

        # Add status messages to the data.
        data = [{"file_name": file_name, "file_token": file_token, "file_status_code": status, "timestamp": timestamp, "file_status_message": FILE_STATUS_CODES[str(status)]} for file_name, file_token, status, timestamp  in data]

        return 0, data

    except Exception as e:
        return 2, str(e)
