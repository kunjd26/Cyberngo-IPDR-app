import os
import pandas as pd

# Folder to store uploaded files and generated files
UPLOAD_FOLDER = os.path.join("files", "uploaded")
PARSED_FOLDER = os.path.join("files", "parsed")
PROCESSED_FOLDER = os.path.join("files", "processed")


def get_file_header(file_token):
    try:
        file_name = f"uploaded-{file_token}.csv"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)

        if not os.path.isfile(file_path):
            return 1, "File not found."

        # Process the file
        df = read_csv_with_header_detection(file_path)

        if len(df.columns) <= 1:
            return 1, "No columns detected."

        # Strip whitespace from column names
        df.columns = df.columns.str.strip()

        # Convert column names to lower case for case insensitive comparison
        df.columns = df.columns.str.lower()

        return 0, df.columns.tolist()

    except Exception as e:
        return 2, str(e)


def get_processed_file_header(file_token):
    try:
        file_name = f"processed-{file_token}.csv"
        file_path = os.path.join(PROCESSED_FOLDER, file_name)

        if not os.path.isfile(file_path):
            return 1, "File not found."

        # Process the file
        df = read_csv_with_header_detection(file_path)

        if len(df.columns) <= 1:
            return 1, "No columns detected."

        # Strip whitespace from column names
        df.columns = df.columns.str.strip()

        # Convert column names to lower case for case insensitive comparison
        df.columns = df.columns.str.lower()

        return 0, df.columns.tolist()

    except Exception as e:
        return 2, str(e)


def dynamic_parse_file(file_token, column_mapping):
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

        # Check column mapping dict contain at least following keys destination ip, destination port
        if not all(
            col in column_mapping for col in ["destination ip", "destination port"]
        ):
            return (
                1,
                "Column mapping must contain 'destination ip' and 'destination port' keys.",
            )

        # Check all keys data type must be list
        if not all(isinstance(column_mapping[col], list) for col in column_mapping):
            return 1, "All values in column mapping must be array(list)."

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

        output_csv = f"parsed-{file_token}.csv"
        output_csv_path = os.path.join(PARSED_FOLDER, output_csv)

        # Write the extracted data to the output CSV file
        extracted_df.to_csv(output_csv_path, index=False)

        return 0, None

    except Exception as e:
        return 2, str(e)


def read_csv_with_header_detection(file_path):
    delimiters = [",", ";", "\t", "|"]
    expected_columns = [
        "phone number",
        "roaming circle",
        "source ip",
        "source port",
        "destination ip",
        "destination port",
        "imei",
        "mac id",
        "imsi",
        "cell global id",
        "access point name",
        "data uplink volume",
        "data downlink volume",
        "rat",
        "pgw/ggsn ip",
        "billing type",
        "timestamp",
        "duration",
        "ipv6",
    ]

    for delimiter in delimiters:
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()

            header_row = 0
            for i, line in enumerate(lines):
                if any(col in line for col in expected_columns):
                    header_row = i
                    break

            df = pd.read_csv(
                file_path, delimiter=delimiter, skiprows=header_row, low_memory=False
            )
            return df
        except pd.errors.ParserError:
            continue

    raise pd.errors.ParserError(
        "Unable to parse the CSV file with the given delimiters."
    )


def find_column(df, possible_columns):
    lower_case_df_columns = [col.lower() for col in df.columns]
    for col in possible_columns:
        stripped_col = col.strip().lower()
        if stripped_col in lower_case_df_columns:
            return stripped_col
