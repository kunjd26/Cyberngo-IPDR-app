import os
import pandas as pd
import ipinfo
from pandas import json_normalize
import json

def process_file(file_token, access_token='1fc6dc155d276a'):
    try:
        # Access token and handler setup
        handler = ipinfo.getHandler(access_token, request_options={'timeout': 5})

        # Check if file exists
        filename = f"parsed_{file_token}.csv"
        filepath = os.path.join('files', 'parsed', filename)
        if not os.path.isfile(filepath):
            return f"File does not exist."

        # Read CSV file
        df = pd.read_csv(filepath, low_memory=False)

        # Get unique Destination IPs
        unique_ips = df['Destination IP'].unique()

        # Get details for each unique IP
        ip_details_list = []
        for ip in unique_ips:
            try:
                details = handler.getDetails(ip).all
                details['ip'] = ip  # Add the IP address to the details dictionary
                ip_details_list.append(details)
            except Exception as e:
                # print(f"Error fetching details for IP {ip}: {e}")
                continue

        # Convert list of details to DataFrame
        ip_details_df = pd.DataFrame(ip_details_list)

        # Normalize nested fields
        ip_details_df = json_normalize(ip_details_list)

        # Drop unwanted columns if they exist
        columns_to_drop = ['country_flag.emoji', 'country_flag.unicode', 'country_flag_url', 'country_currency.symbol']
        existing_columns_to_drop = [col for col in columns_to_drop if col in ip_details_df.columns]
        if existing_columns_to_drop:
            ip_details_df = ip_details_df.drop(columns=existing_columns_to_drop)

        # Rename columns
        column_rename_dict = {'privacy.vpn': 'is_vpn', 'privacy.proxy': 'is_proxy', 'privacy.tor': 'is_tor', 'privacy.relay': 'is_relay', 'privacy.hosting': 'is_hosting', 'privacy.service': 'is_service', 'country_currency.code': 'currency code', 'continent.code': 'continent code', 'continent.name': 'continent name'}
        ip_details_df = ip_details_df.rename(columns=column_rename_dict)

        # Extract first word from 'org' field and rename as 'ASN'
        ip_details_df['ASN'] = ip_details_df['org'].str.split(' ').str[0]

        # Merge original DataFrame with new DataFrame based on 'Destination IP' and 'ip'
        df_merged = pd.merge(df, ip_details_df, left_on='Destination IP', right_on='ip', how='left')

        # Reorder columns
        column_order = list(df.columns) + ['ASN', 'is_vpn', 'is_proxy', 'is_tor', 'is_relay', 'is_hosting', 'is_service', 'currency code', 'continent code', 'continent name', 'country', 'region', 'city', 'postal', 'latitude', 'longitude', 'loc', 'timezone', 'org']
        df_merged = df_merged.reindex(columns=column_order)

        # Load ports.json
        with open('ports.json', 'r') as f:
            ports_data = json.load(f)

        # Extract port descriptions
        ports = {}
        for port, details in ports_data['ports'].items():
            if isinstance(details, list):
                descriptions = [d.get('description', 'No description found') for d in details]
                ports[int(port)] = "; ".join(descriptions)
            else:
                ports[int(port)] = details.get('description', 'No description found')
        
        # Map 'Destination Port' to port descriptions
        df_merged['Port Description'] = df_merged['Destination Port'].map(ports).fillna('No description found')

        # Save the updated dataframe to a new CSV file in the .files/generate1 directory
        new_dir = os.path.join('files', 'appended')
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        new_filepath = os.path.join(new_dir, f"appended_{file_token}.csv")
        df_merged.to_csv(new_filepath, index=False)
        return 0
    except Exception as e:
        return f"An error occurred: {e}"