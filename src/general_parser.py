import os
import pandas as pd

# Folder to store uploaded files and generated files
UPLOAD_FOLDER = os.path.join("files", 'uploaded')
PARSED_FOLDER = os.path.join("files", 'parsed')

def parse_file(file_token):
    try:
        file_name = f"uploaded-{file_token}.csv"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        if not os.path.isfile(file_path):
            return 1, "File not found."

        # Process the file
        df = read_csv_with_header_detection(file_path)

        # Strip whitespace from column names
        df.columns = df.columns.str.strip()

        # Mapping of output columns to possible input columns
        column_mapping = {
            'Phone Number': ['MSISDN', 'Landline/MSISDN/MDN/Leased Circuit ID for Internet Access', 'Phone Number'],
            'Roaming Circle': ['Home_Roaming_Circle', 'Roaming Circle'],
            'Source IP': ['Source_IP', 'Source IP', 'Public IP Address'],
            'Source Port': ['Source Port', 'Public IP Port', 'Source_Port'],
            'Destination IP': ['Destination IP', 'Destination IP Address', 'Destination_IP'],
            'Destination Port': ['Destination Port', 'Destination_Port'],
            'IMEI/MAC ID': ['IMEI', 'Source MAC-ID Address/Other device Identification number', 'MAC ID', 'IMEI/MAC ID'],
            'IMSI': ['IMSI'],
            'Cell Global ID': ['CGI ID', 'First Cell ID-Name/Location', 'CELL ID', 'Cell Global ID'],
            'Access Point Name': ['Access Point Name', 'Access_Point_Name'],
            'Data Uplink Volume': ['Data Volume Uplink', 'Uplink_Vol', 'Data Uplink Volume'],
            'Data Downlink Volume': ['Data Volume Downlink', 'Downlink_Vol', 'Data Downlink Volume'],
            'RAT': ['RAT', '2g/3g/4g/5g'],
            'PGW/GGSN IP': ['PGW IP address', 'PGW_GGSN_IP_Address', 'PGW/GGSN IP'],
            'Billing Type': ['Billing Type'],
            'timestamp': ['TIME1 (dd/MM/yyyy HH:mm:ss)', 'Session Start date & time', 'Session_Start_Time', 'timestamp'],
            'Duration': ['Duration in sec', 'Session Duration', 'Duration'],
            'IPV6': ['Public_IPv6', 'IPV6']
        }

        # Create a dictionary for extracted columns
        extracted_data = {}

        # Extract the columns based on the mapping
        for output_col, input_cols in column_mapping.items():
            col_name = find_column(df, input_cols)
            if col_name:
                extracted_data[output_col] = df[col_name]
            else:
                # print(f"Warning: None of the possible columns for '{output_col}' were found in the input file.")
                extracted_data[output_col] = None

        # Create a new DataFrame with the extracted data
        extracted_df = pd.DataFrame(extracted_data)

        # Create the upload folder if it doesn't exist.
        os.makedirs(PARSED_FOLDER, exist_ok=True)

        output_csv = f'parsed-{file_token}.csv'
        output_csv_path = os.path.join(PARSED_FOLDER, output_csv)

        # Write the extracted data to the output CSV file
        extracted_df.to_csv(output_csv_path, index=False)
        
        return 0, None

    except Exception as e:
        return 2, str(e)


def read_csv_with_header_detection(file_path):
    delimiters = [',', ';', '\t', '|']
    expected_columns = [ 'Phone Number', 'Roaming Circle', 'Source IP', 'Source Port', 'Destination IP', 'Destination Port', 'IMEI/MAC ID', 'IMSI', 'Cell Global ID', 'Access Point Name', 'Data Uplink Volume', 'Data Downlink Volume', 'RAT', 'PGW/GGSN IP', 'Billing Type', 'timestamp', 'Duration', 'IPV6']

    for delimiter in delimiters:
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            header_row = 0
            for i, line in enumerate(lines):
                if any(col in line for col in expected_columns):
                    header_row = i
                    break

            df = pd.read_csv(file_path, delimiter=delimiter, skiprows=header_row)
            return df
        except pd.errors.ParserError:
            continue
    
    raise pd.errors.ParserError("Unable to parse the CSV file with the given delimiters.")


# Function to find the correct column from the possible options
def find_column(df, possible_columns):
    for col in possible_columns:
        stripped_col = col.strip()
        if stripped_col in df.columns:
            return stripped_col