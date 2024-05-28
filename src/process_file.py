import ipaddress
import ipinfo
import os
import pandas as pd
import numpy as np
from pandas import json_normalize
import sqlite3

# Folder to store uploaded files and generated files.
PARSED_FOLDER = os.path.join("files", 'parsed')
PROCESSED_FOLDER = os.path.join("files", 'processed')

# Access token for IPInfo API.
ACCESS_TOKEN = '1fc6dc155d276a'

def append_fields(file_token, static_database_only=False):
    try:
        file_name = f"parsed-{file_token}.csv"
        file_path = os.path.join(PARSED_FOLDER, file_name)

        if not os.path.isfile(file_path):
            return 1, "File not found."
        
        # Read the CSV file.
        df = pd.read_csv(file_path, low_memory=False)

        # Establish a connection to the SQLite database.
        connection = sqlite3.connect('cyberngo.db')

        # SQL query to fetch port description.
        sql_query = "SELECT port_no, port_description FROM port_desc"

        # Execute the SQL query and fetch the data into a new DataFrame.
        port_desc_df = pd.read_sql_query(sql_query, connection)

        # Merge the original DataFrame with the new DataFrame on the 'Destination Port' and 'port_no' columns.
        df = pd.merge(df, port_desc_df, left_on='Destination Port', right_on='port_no', how='left')

        # SQL query to fetch country + ASN details.
        sql_query = "SELECT * FROM country_asn"
        
        # Execute the SQL query and fetch the data into a new DataFrame.
        country_asn_df = pd.read_sql_query(sql_query, connection)

        # Close the connection to the SQLite database
        connection.close()

        # Convert IP addresses to integers
        df['Destination IP Int'] = df['Destination IP'].apply(convert_ip)
        country_asn_df['start_ip'] = country_asn_df['start_ip'].apply(convert_ip)
        country_asn_df['end_ip'] = country_asn_df['end_ip'].apply(convert_ip)

        # Initialize an empty list to store the merge results
        merge_results = []

        # Iterate over each row in the main DataFrame
        for idx, row in df.iterrows():
            # Get the Destination IP Int value
            dest_ip_int = row['Destination IP Int']
            # Find matching rows in country_asn_df where Destination IP Int is within the range
            match = country_asn_df[
                (country_asn_df['start_ip'] <= dest_ip_int) & 
                (country_asn_df['end_ip'] >= dest_ip_int)
            ]
            # If there are matches, append them to the results
            if not match.empty:
                for match_idx, match_row in match.iterrows():
                    merged_row = {**row.to_dict(), **match_row.to_dict()}
                    merge_results.append(merged_row)
            else:
                merge_results.append(row.to_dict())

        # Convert the list of merged results to a DataFrame
        df = pd.DataFrame(merge_results)


        if static_database_only == True:
            append_columns = [ 'ip', 'city', 'region', 'loc', 'org', 'postal', 'timezone', 'isEU', 'privacy.vpn', 'privacy.proxy', 'privacy.tor', 'privacy.relay', 'privacy.hosting', 'privacy.service', 'anycast']

            # Adding new columns with None values
            for col in append_columns:
                df[col] = None
        else:
            # Access token and handler setup
            handler = ipinfo.getHandler(ACCESS_TOKEN)

            # Get unique Destination IPs
            unique_ips = df['Destination IP'].unique()
            print(len(unique_ips))

            # Get details for each unique IP
            ip_details_list = []
            for ip in unique_ips:
                print(f"\r{len(ip_details_list)}", end="")
                try:
                    details = handler.getDetails(ip).all
                    details['ip'] = ip  # Add the IP address to the details dictionary
                    ip_details_list.append(details)
                except Exception as e:
                    # print(f"Error fetching details for IP {ip}: {e}")
                    continue
            print()

            # Convert list of details to DataFrame
            ip_details_df = pd.DataFrame(ip_details_list)

            # Normalize nested fields
            ip_details_df = json_normalize(ip_details_list)

            # Select the required columns
            selected_columns = [ 'ip', 'city', 'region', 'loc', 'org', 'postal', 'timezone', 'isEU', 'privacy.vpn', 'privacy.proxy', 'privacy.tor', 'privacy.relay', 'privacy.hosting', 'privacy.service', 'anycast']

            # Check for the existence of these columns to avoid KeyErrors
            available_columns = [col for col in selected_columns if col in ip_details_df.columns]
            ip_details_df = ip_details_df[available_columns]

            # Merge original DataFrame with new DataFrame based on 'Destination IP' and 'ip'
            df = pd.merge(df, ip_details_df, left_on='Destination IP', right_on='ip', how='left')
        
        # Drop unnecessary columns from the df
        columns_to_drop = ['start_ip', 'end_ip', 'index', 'port_no', 'ip', 'country_flag.emoji', 'country_flag.unicode', 'country_flag_url', 'country_currency.symbol']
        df.drop(columns=columns_to_drop, errors='ignore', inplace=True)

        # Rename columns
        column_rename_dict = {'privacy.vpn': 'is_vpn', 'privacy.proxy': 'is_proxy', 'privacy.tor': 'is_tor', 'privacy.relay': 'is_relay', 'privacy.hosting': 'is_hosting', 'privacy.service': 'is_service', 'port_description': 'Port Description', 'country_name': 'Country Name', 'continent_name': 'Continent Name'}
        df = df.rename(columns=column_rename_dict)

        # Create the upload folder if it doesn't exist.
        os.makedirs(PROCESSED_FOLDER, exist_ok=True)

        output_csv = f'processed-{file_token}.csv'
        output_csv_path = os.path.join(PROCESSED_FOLDER, output_csv)

        # Write the data to the output CSV file
        df.to_csv(output_csv_path, index=False)

        return 0, None

    except Exception as e:
        return 2, str(e)


def convert_ip(ip):
    if pd.isna(ip):
        return np.nan
    try:
        return int(ipaddress.IPv4Address(ip))
    except ipaddress.AddressValueError:
        try:
            return int(ipaddress.IPv6Address(ip))
        except ipaddress.AddressValueError:
            return np.nan
