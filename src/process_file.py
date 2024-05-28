import ipaddress
import ipinfo
import os
import pandas as pd
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

        # Get unique Destination Ports
        unique_ports = df['destination port'].unique()

        # Establish a connection to the SQLite database.
        connection = sqlite3.connect('cyberngo.db')

        # Fetch port descriptions for each unique port
        port_desc_list = []
        for port in unique_ports:
            try:
                # SQL query to fetch port description for the current port
                sql_query = f"SELECT port_no, port_description FROM port_desc WHERE port_no = {port}"

                # Execute the SQL query and fetch data into a new DataFrame
                port_desc_df = pd.read_sql_query(sql_query, connection)

                # Append port description to the list
                port_desc_list.append(port_desc_df)

            except Exception as e:
                # print(f"Error fetching details for port {port}: {e}")
                continue

        # Close the connection to the SQLite database.
        connection.close()

        # Concatenate the list of DataFrames into a single DataFrame
        port_desc_df = pd.concat(port_desc_list)

        # Merge original DataFrame with the new DataFrame on the 'Destination Port' and 'port_no' columns
        df = pd.merge(df, port_desc_df, left_on='destination port', right_on='port_no', how='left')

        if static_database_only == True:
            # Get unique Destination IPs
            unique_ips = df['destination ip'].unique()
            df['destination ip int'] = df['destination ip'].apply(convert_ip)

            # Establish a connection to the SQLite database.
            connection = sqlite3.connect('cyberngo.db')

            # Fetch IP details for each unique IP
            ip_details_list = []
            print(len(unique_ips))
            for ip in unique_ips:
                try:
                    print(f"\r{len(ip_details_list)}", end="")
                    # SQL query to fetch IP details for the current IP
                    converted_int_ip = convert_ip(ip)
                    sql_query = f"SELECT * FROM country_asn WHERE {converted_int_ip} BETWEEN start_ip_int AND end_ip_int"

                    # Execute the SQL query and fetch data into a new DataFrame
                    ip_details_df = pd.read_sql_query(sql_query, connection)
                    ip_details_df['converted_int_ip'] = converted_int_ip

                    # Append IP details to the list
                    ip_details_list.append(ip_details_df)
                except Exception as e:
                    # Handle any errors gracefully
                    # print(f"Error fetching details for IP {ip}: {e}")
                    continue
            print()

            # Close the connection to the SQLite database.
            connection.close()

            # Concatenate the list of DataFrames into a single DataFrame
            ip_details_df = pd.concat(ip_details_list)

            # Merge original DataFrame with the new DataFrame on the 'destination ip int' and 'port_no' columns
            df = pd.merge(df, ip_details_df, left_on='destination ip int', right_on='converted_int_ip', how='left')

            append_columns = [ 'ip', 'city', 'region', 'loc', 'org', 'postal', 'timezone', 'isEU', 'privacy.vpn', 'privacy.proxy', 'privacy.tor', 'privacy.relay', 'privacy.hosting', 'privacy.service', 'anycast']

            # Adding new columns with None values
            for col in append_columns:
                df[col] = None
        else:
            # Get unique Destination IPs
            unique_ips = df['destination ip'].unique()
            df['destination ip int'] = df['destination ip'].apply(convert_ip)

            # Access token and handler setup
            handler = ipinfo.getHandler(ACCESS_TOKEN)

            # Establish a connection to the SQLite database.
            connection = sqlite3.connect('cyberngo.db')

            # Fetch IP details for each unique IP
            ip_details_list_from_static_db = []
            ip_details_list_from_api = []
            print(len(unique_ips))
            for ip in unique_ips:
                try:
                    # Fetch IP details from ipinfo API.
                    details = handler.getDetails(ip).all

                    ip_details_list_from_api.append(details)

                    # SQL query to fetch IP details for the current IP
                    converted_int_ip = convert_ip(ip)
                    sql_query = f"SELECT * FROM country_asn WHERE {converted_int_ip} BETWEEN start_ip_int AND end_ip_int"

                    # Execute the SQL query and fetch data into a new DataFrame
                    ip_details_df = pd.read_sql_query(sql_query, connection)
                    ip_details_df['converted_int_ip'] = converted_int_ip

                    # Append IP details to the list
                    ip_details_list_from_static_db.append(ip_details_df)

                    print(f"\r{len(ip_details_list_from_static_db)}", end="")
                except Exception as e:
                    # Handle any errors gracefully
                    # print(f"Error fetching details for IP {ip}: {e}")
                    continue
            print()

            # Close the connection to the SQLite database.
            connection.close()

            # Concatenate the list of DataFrames into a single DataFrame
            ip_details_df = pd.concat(ip_details_list_from_static_db)

            # Merge original DataFrame with the new DataFrame on the 'destination ip int' and 'port_no' columns
            df = pd.merge(df, ip_details_df, left_on='destination ip int', right_on='converted_int_ip', how='left')

            # Convert list of details to DataFrame
            ip_details_df = pd.DataFrame(ip_details_list_from_api)

            # Normalize nested fields
            ip_details_df = json_normalize(ip_details_list_from_api)

            # Select the required columns
            selected_columns = [ 'ip', 'city', 'region', 'loc', 'org', 'postal', 'timezone', 'isEU', 'privacy.vpn', 'privacy.proxy', 'privacy.tor', 'privacy.relay', 'privacy.hosting', 'privacy.service', 'anycast']

            # Check for the existence of these columns to avoid KeyErrors
            available_columns = [col for col in selected_columns if col in ip_details_df.columns]
            ip_details_df = ip_details_df[available_columns]

            # Merge original DataFrame with new DataFrame based on 'Destination IP' and 'ip'
            df = pd.merge(df, ip_details_df, left_on='destination ip', right_on='ip', how='left')

        # Drop unnecessary columns from the df
        columns_to_drop = ['start_ip', 'end_ip', 'index', 'port_no', 'ip', 'country_flag.emoji', 'country_flag.unicode', 'country_flag_url', 'country_currency.symbol', 'destination ip int', 'start_ip_int', 'end_ip_int', 'converted_int_ip']
        df.drop(columns=columns_to_drop, errors='ignore', inplace=True)

        # Rename columns
        column_rename_dict = {'privacy.vpn': 'is_vpn', 'privacy.proxy': 'is_proxy', 'privacy.tor': 'is_tor', 'privacy.relay': 'is_relay', 'privacy.hosting': 'is_hosting', 'privacy.service': 'is_service', 'port_description': 'port description', 'country_name': 'country name', 'continent_name': 'continent name'}
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
        return "0"
    try:
        return str(int(ipaddress.IPv4Address(ip)))
    except ipaddress.AddressValueError:
        try:
            return str(int(ipaddress.IPv6Address(ip)))
        except ipaddress.AddressValueError:
            return "0"
