import os
import pandas as pd
import ipinfo
from pandas import json_normalize
import sqlite3

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
        print(len(unique_ips))

        # Get details for each unique IP
        ip_details_list = []
        for ip in unique_ips:
            print(f"\r{len(ip_details_list)}", end="")
            try:
                details = handler.getDetails(ip).all
                ip_details_list.append(details)
            except Exception as e:
                # print(f"Error fetching details for IP {ip}: {e}")
                continue
        print()

        # Convert list of details to DataFrame
        ip_details_df = pd.DataFrame(ip_details_list)

        # Normalize nested fields
        ip_details_df = json_normalize(ip_details_list)

        # Merge original DataFrame with new DataFrame based on 'Destination IP' and 'ip'
        df = pd.merge(df, ip_details_df, left_on='Destination IP', right_on='ip', how='left')

        # Establish a connection to the SQLite database
        conn = sqlite3.connect('cyberngo.db')

        # Write a SQL query to fetch the data from the country_asn table
        query = "SELECT start_ip, end_ip, asn, as_name, as_domain FROM country_asn"
        
        country_asn_df = pd.read_sql_query(query, conn)
        df = pd.merge(df, country_asn_df, left_on='Destination IP', right_on='start_ip', how='left')

        # Write a SQL query to fetch the data from the port_desc table
        query = "SELECT port_no, port_description FROM port_desc"

        # Execute the SQL query and fetch the data into a new DataFrame
        port_desc_df = pd.read_sql_query(query, conn)

        # Close the connection to the SQLite database
        conn.close()

        # Merge the original DataFrame with the new DataFrame on the 'Destination Port' and 'port_no' columns
        df = pd.merge(df, port_desc_df, left_on='Destination Port', right_on='port_no', how='left')

        # Drop unwanted columns if they exist
        columns_to_drop = ['ip', 'country_flag.emoji', 'country_flag.unicode', 'country_flag_url', 'country_currency.symbol', 'start_ip', 'end_ip', 'port_no']
        existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
        if existing_columns_to_drop:
            df = df.drop(columns=existing_columns_to_drop)

        # Rename columns
        column_rename_dict = {'privacy.vpn': 'is_vpn', 'privacy.proxy': 'is_proxy', 'privacy.tor': 'is_tor', 'privacy.relay': 'is_relay', 'privacy.hosting': 'is_hosting', 'privacy.service': 'is_service', 'country_name': 'country name', 'country_currency.code': 'currency code', 'continent.code': 'continent code', 'continent.name': 'continent name', 'port_description': 'Port Description'}
        df = df.rename(columns=column_rename_dict)

        # Save the updated dataframe to a new CSV file in the .files/generate1 directory
        new_dir = os.path.join('files', 'appended')
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        new_filepath = os.path.join(new_dir, f"appended_{file_token}.csv")
        df.to_csv(new_filepath, index=False)
        return 0
    except Exception as e:
        return f"An error occurred: {e}"