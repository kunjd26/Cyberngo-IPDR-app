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

        # Convert column names to lower case for case insensitive comparison
        df.columns = df.columns.str.lower()

        # Mapping of output columns to possible input columns
        column_mapping = {
            'phone number': ['msisdn', 'landline/msisdn/mdn/leased circuit id for internet access', 'phone number'],
            'roaming circle': ['home_roaming_circle', 'roaming circle'],
            'source ip': ['source_ip', 'source ip', 'public ip address'],
            'source port': ['source port', 'public ip port', 'source_port'],
            'destination ip': ['destination ip', 'destination ip address', 'destination_ip', 'destination_ip4'],
            'destination port': ['destination port', 'destination_port'],
            'imei/mac id': ['imei', 'source mac-id address/other device identification number', 'mac id', 'imei/mac id'],
            'imsi': ['imsi'],
            'cell global id': ['cgi id', 'first cell id-name/location', 'cell id', 'cell global id'],
            'access point name': ['access point name', 'access_point_name'],
            'data uplink volume': ['data volume uplink', 'uplink_vol', 'data uplink volume'],
            'data downlink volume': ['data volume downlink', 'downlink_vol', 'data downlink volume'],
            'rat': ['rat', '2g/3g/4g/5g'],
            'pgw/ggsn ip': ['pgw ip address', 'pgw_ggsn_ip_address', 'pgw/ggsn ip'],
            'billing type': ['billing type'],
            'timestamp': ['time1 (dd/mm/yyyy hh:mm:ss)', 'session start date & time', 'session_start_time', 'timestamp'],
            'duration': ['duration in sec', 'session duration', 'duration'],
            'ipv6': ['public_ipv6', 'ipv6']
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
    expected_columns = [ 'Phone Number', 'Roaming Circle', 'Source IP', 'Source Port', 'Destination IP', 'Destination Port', 'IMEI/MAC ID', 'IMSI', 'Cell Global ID', 'Access Point Name', 'Data Uplink Volume', 'Data Downlink Volume', 'RAT', 'PGW/GGSN IP', 'Billing Type', 'Timestamp', 'Duration', 'IPV6']

    for delimiter in delimiters:
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            header_row = 0
            for i, line in enumerate(lines):
                if any(col in line for col in expected_columns):
                    header_row = i
                    break

            df = pd.read_csv(file_path, delimiter=delimiter, skiprows=header_row, low_memory=False)
            return df
        except pd.errors.ParserError:
            continue
    
    raise pd.errors.ParserError("Unable to parse the CSV file with the given delimiters.")


def find_column(df, possible_columns):
    lower_case_df_columns = [col.lower() for col in df.columns]
    for col in possible_columns:
        stripped_col = col.strip().lower()
        if stripped_col in lower_case_df_columns:
            return stripped_col
