import os
import pandas as pd

# Folder path for uploaded files.
PROCESSED_FOLDER = os.path.join("files", 'processed')

def analysis_data(file_token, n=10, columns=None):
    try:
        analyzed_data = {}

        # Get the filename associated with the token.
        file_name = f"processed-{file_token}.csv"
        file_path = os.path.join(PROCESSED_FOLDER, file_name)

        if not os.path.isfile(file_path):
            return 1, "File not found."

        # Read CSV file
        df = pd.read_csv(file_path, low_memory=False)

        # Convert DataFrame column names to lower case for case insensitive comparison
        df.columns = df.columns.str.lower()

        # columns has column name separated by comma
        if columns:
            columns = columns.split(",")
            # Now we will get the top N values for each column
            for column in columns:
                column = column.strip().lower()
                if column not in df.columns:
                    return 1, f"Column {column} does not exist."
                else:
                    top_values = df[column].value_counts().nlargest(n).index.tolist()
                    analyzed_data[column] = top_values
        else:
            top_ips = df['destination ip'].value_counts().nlargest(n).index.tolist()
            top_ports = df['destination port'].value_counts().nlargest(n).index.tolist()
            top_asn = df['asn'].value_counts().nlargest(n).index.tolist()
            top_as_domain = df['as_domain'].value_counts().nlargest(n).index.tolist()
            top_country = df['country name'].value_counts().nlargest(n).index.tolist()

            # Put in a dictionary
            analyzed_data = {
                'destination ip': top_ips,
                'destination port': top_ports,
                'asn': top_asn,
                'as_domain': top_as_domain,
                'country_name': top_country
            }
            
        return 0, analyzed_data

    except Exception as e:
        return 2, str(e)
