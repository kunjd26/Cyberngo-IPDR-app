import os
import pandas as pd

def get_analysis_data(file_token, n=10, columns=None):
    try:
        analyzed_data = {}
        # Check if file exists
        filename = f"appended_{file_token}.csv"
        filepath = os.path.join('files', 'appended', filename)
        if not os.path.isfile(filepath):
            return f"File does not exist.", None

        # Read CSV file
        df = pd.read_csv(filepath, low_memory=False)

        # columns has column name separated by comma
        if columns:
            columns = columns.split(",")
            # Now we will get the top N values for each column
            for column in columns:
                if column not in df.columns:
                    return f"Column {column} does not exist.", None
                else:
                    top_values = df[column].value_counts().nlargest(n).index.tolist()
                    analyzed_data[column] = top_values
        else:
            top_ips = df['Destination IP'].value_counts().nlargest(n).index.tolist()
            top_ports = df['Destination Port'].value_counts().nlargest(n).index.tolist()
            top_asn = df['asn'].value_counts().nlargest(n).index.tolist()
            top_as_domain = df['as_domain'].value_counts().nlargest(n).index.tolist()
            top_country = df['country name'].value_counts().nlargest(n).index.tolist()

            # Put in a dictionary
            analyzed_data = {
                "Top IPs": top_ips,
                "Top Ports": top_ports,
                "Top ASN": top_asn,
                "Top AS Domain": top_as_domain,
                "Top Country": top_country
            }
            
        return 0, analyzed_data
    except Exception as e:
        return f"An error occurred: {e}", None
