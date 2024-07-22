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
                    value_counts = df[column].value_counts()
                    top_values = value_counts.nlargest(n).index.tolist()
                    top_counts = value_counts.nlargest(n).tolist()
                    top_percentages = (value_counts.nlargest(n) / len(df) * 100).round(2).tolist()
                    other_percentage = round(100 - sum(top_percentages), 2)
                    other_count = len(df) - sum(top_counts)
                    
                    analyzed_data[column] = [
                        {"value": val, "percentage": pct, "record_count": count}
                        for val, pct, count in zip(top_values, top_percentages, top_counts)
                    ] + [{"value": "other", "percentage": other_percentage, "record_count": other_count}]
        else:
            # Define columns to analyze by default
            default_columns = ['destination ip', 'destination port', 'asn', 'as_domain', 'country name']
            
            for column in default_columns:
                if column not in df.columns:
                    return 1, f"Column {column} does not exist."
                else:
                    value_counts = df[column].value_counts()
                    top_values = value_counts.nlargest(n).index.tolist()
                    top_counts = value_counts.nlargest(n).tolist()
                    top_percentages = (value_counts.nlargest(n) / len(df) * 100).round(2).tolist()
                    other_percentage = round(100 - sum(top_percentages), 2)
                    other_count = len(df) - sum(top_counts)
                    
                    analyzed_data[column] = [
                        {"value": val, "percentage": pct, "record_count": count}
                        for val, pct, count in zip(top_values, top_percentages, top_counts)
                    ] + [{"value": "other", "percentage": other_percentage, "record_count": other_count}]
                    
        return 0, analyzed_data

    except Exception as e:
        return 2, str(e)
