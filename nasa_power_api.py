import os
import json
import requests
import pandas as pd

def create_regular_grid(min_lat, min_lon, max_lat, max_lon, step=0.5):

    '''
    This function creates a regular grid of points within the given bounding box.

    Parameters:
        min_lat (float): Minimum latitude of the bounding box
        min_lon (float): Minimum longitude of the bounding box
        max_lat (float): Maximum latitude of the bounding box
        max_lon (float): Maximum longitude of the bounding box
        step (float): Step size for the grid

    Returns:
        grid_points (list): List of tuples containing the latitude and longitude of the grid points

    '''

    grid_points = []
    lat = max_lat
    while lat >= min_lat:
        lon = min_lon
        while lon <= max_lon:
            grid_points.append((lat, lon))
            lon += step
        lat -= step
    return grid_points

def download_param(bounding_box, param = 'T2M', community = 'AG', start_date = '20150101', end_date = '20150331', 
                   dest_folder = os.getcwd()):
    
    '''
    This function downloads the data for the given parameter and bounding box from the NASA POWER API.

    Parameters:
        bounding_box (list): List containing the minimum and maximum latitude and longitude of the bounding box
        param (str): Parameter to be downloaded. Default is 'T2M' (2-meter air temperature)
        community (str): Community to be used for the download. Default is 'AG'
        start_date (str): Start date for the download in YYYYMMDD format. Default is '20150101'
        end_date (str): End date for the download in YYYYMMDD format. Default is '20150331'
        dest_folder (str): Destination folder for the downloaded data. Default is the current working directory

    Returns:
        df (DataFrame): DataFrame containing the downloaded data

    '''
    
    # Ref: https://power.larc.nasa.gov/#resources
    # param: ['T2M_MAX', 'T2M_MIN', 'RH2M', 'PRECTOTCORR', 'WS2M', 'ALLSKY_SFC_SW_DWN']
    # community: AG, RE, SB 
    # date: YYYYMMDD
    # 
    
    opf = os.path.join(dest_folder, f'{param}')
    os.makedirs(opf, exist_ok = True)
    
    locations = create_regular_grid(*bounding_box)
    n = 1
    
    # Initialize the index data
    index_data = [['ID', 'NAME', 'LAT', 'LONG', 'ELEVATION']]
    idx = 1

    if param == 'T2M':
        # Download T2M_MAX data
        data_dict_max = {}
        for latitude, longitude in locations:
            url = f'https://power.larc.nasa.gov/api/temporal/daily/point?'
            url += f'parameters=T2M_MAX&community={community}&longitude={longitude}&latitude={latitude}&start={start_date}&end={end_date}&format=JSON'
            print(f'Downloading "T2M_MAX" [{(latitude, longitude)}]: {(n/len(locations))*100:.2f}%', end='\r')
            response = requests.get(url=url, verify=True, timeout=30.00)
            content = json.loads(response.content.decode('utf-8'))
            properties = content['properties']['parameter']['T2M_MAX']
            data_dict_max[(latitude, longitude)] = properties
            
            # Prepare data for the index file
            filename = f"T2M{latitude}{longitude}".replace(".", "")
            elevation = -999.000  # Use -999.000 as a constant value for elevation
            index_data.append([idx, filename, latitude, longitude, elevation])
            idx += 1
            
            n += 1

        df_max = pd.DataFrame.from_dict(data_dict_max, orient='index')
        df_max = df_max.transpose()

        # Download T2M_MIN data
        data_dict_min = {}
        n = 1
        for latitude, longitude in locations:
            url = f'https://power.larc.nasa.gov/api/temporal/daily/point?'
            url += f'parameters=T2M_MIN&community={community}&longitude={longitude}&latitude={latitude}&start={start_date}&end={end_date}&format=JSON'
            print(f'Downloading "T2M_MIN" [{(latitude, longitude)}]: {(n/len(locations))*100:.2f}%', end='\r')
            response = requests.get(url=url, verify=True, timeout=30.00)
            content = json.loads(response.content.decode('utf-8'))
            properties = content['properties']['parameter']['T2M_MIN']
            data_dict_min[(latitude, longitude)] = properties
            n += 1

        df_min = pd.DataFrame.from_dict(data_dict_min, orient='index')
        df_min = df_min.transpose()
        
        # Combine the values in df_max and df_min into a single column with comma-separated values
        combined_df = df_max.astype(str) + ',' + df_min.astype(str)
        combined_df.columns = [f"T2M{lat}{lon}".replace(".", "") for lat, lon in combined_df.columns]
        date_row = pd.DataFrame({col: [start_date] for col in combined_df.columns})
        combined_df = pd.concat([date_row, combined_df], ignore_index=True)
        df = combined_df
        for column in df.columns:
            file_name = f"{column}.txt"
            file_path = os.path.join(opf, file_name)
            df[column].to_csv(file_path, header=False, index=False, sep='\t')
            
        # Save index data to a separate CSV file
        index_df = pd.DataFrame(index_data[1:], columns=index_data[0])
        index_df.to_csv(os.path.join(opf, f"{param}.txt"), index=False)
    
    else:
        data_dict = {}
        for latitude, longitude in locations:
            url = f'https://power.larc.nasa.gov/api/temporal/daily/point?'
            url += f'parameters={param}&community={community}&longitude={longitude}&latitude={latitude}&start={start_date}&end={end_date}&format=JSON'
            print(f'Downloading [{(latitude, longitude)}]: {(n/len(locations))*100:.2f}%', end='\r')
            response = requests.get(url=url, verify=True, timeout=30.00)
            content = json.loads(response.content.decode('utf-8'))
            properties = content['properties']['parameter'][param]
            data_dict[(latitude, longitude)] = properties
            
            # Prepare data for the index file
            filename = f"{param}{str(latitude)}{str(longitude)}".replace(".", "")
            elevation = -999.000  # Use -999.000 as a constant value for elevation
            index_data.append([idx, filename, latitude, longitude, elevation])
            idx += 1
            
            n += 1
            
        df = pd.DataFrame.from_dict(data_dict, orient='index')
        df = df.transpose()
        df.columns = [f"{param}{str(lat)}{str(lon)}".replace(".", "") for lat, lon in locations]

        # Insert start date in the first row
        date_row = pd.DataFrame(columns = df.columns)
        date_row.loc[0] = start_date
        df = pd.concat([date_row, df]).reset_index(drop = True)

        for column in df.columns:
            file_name = f"{column}.txt"
            file_path = os.path.join(opf, file_name)
            df[column].to_csv(file_path, header = False, index = False)
            
        # Save index data to a separate CSV file
        index_df = pd.DataFrame(index_data[1:], columns=index_data[0])
        index_df.to_csv(os.path.join(opf, f"{param}.txt"), index=False)
        
    return df
