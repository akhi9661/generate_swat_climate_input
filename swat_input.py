import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import tkintermapview
from tkcalendar import DateEntry
from datetime import datetime

import os
import json
import requests
import pandas as pd

import ee

def get_elevation(latitude, longitude):
<<<<<<< HEAD

    '''
    This function returns the elevation of a given latitude and longitude using the Google Earth Engine API. 

    Parameters:
        latitude (float): The latitude of the location
        longitude (float): The longitude of the location

    Returns:
        dem_value_float (float): The elevation of the location

    '''
=======
>>>>>>> 8253f451113b639b53cc74d19c6965ad5bfad589
    
    if not ee.data._credentials:
        ee.Authenticate()
    if not ee.data._initialized:
        ee.Initialize()
        
    point = ee.Geometry.Point([longitude, latitude])
    srtm = ee.Image("USGS/SRTMGL1_003")
    elevation = srtm.reduceRegion(reducer=ee.Reducer.first(), geometry=point)
    dem_value = elevation.get('elevation')
    dem_value_float = float(dem_value.getInfo())

    return dem_value_float

def create_regular_grid(min_lat, min_lon, max_lat, max_lon, step=0.5):

    '''
    This function creates a regular grid of points within a given bounding box. 
    The units of the bounding box and step size are in degrees.

    Parameters:
        min_lat (float): The minimum latitude of the bounding box
        min_lon (float): The minimum longitude of the bounding box
        max_lat (float): The maximum latitude of the bounding box
        max_lon (float): The maximum longitude of the bounding box
        step (float): The step size for the grid. Default is 0.5

    Returns:
        grid_points (list): A list of tuples containing the latitude and longitude of the grid points

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

def download_param(bounding_box, param = 'PRECTOTCORR', community = 'AG', temporal = 'daily', 
                   start_date = '20150101', end_date = '20150331', dest_folder = os.getcwd()):
    
    '''
    This function downloads the data for a given parameter from the NASA POWER API. 
    The data is downloaded for a given bounding box and time period. 

    Parameters:
        bounding_box (list): A list containing the minimum and maximum latitude and longitude of the bounding box
        param (str): The parameter to download. Default is 'PRECTOTCORR'. Other options are 'T2M_MAX', 'T2M_MIN', 'RH2M', 'WS2M', 'ALLSKY_SFC_SW_DWN'
        community (str): The community to download the data from. Default is 'AG'. Other options are 'RE', 'SB'
        temporal (str): The temporal resolution of the data. Default is 'daily'. Other options are 'monthly', 'climatology'
        start_date (str): The start date of the data in YYYYMMDD format. Default is '20150101'. Format is YYYYMMDD. 
        end_date (str): The end date of the data in YYYYMMDD format. Default is '20150331'. Format is YYYYMMDD.
        dest_folder (str): The destination folder to save the data. Default is the current working directory

    Returns:
        df (pandas.DataFrame): A pandas dataframe containing the downloaded data

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
    
    old_message = status_label.get("1.0", tk.END)

    if param == 'T2M':
        # Download T2M_MAX data
        data_dict_max = {}
        for latitude, longitude in locations:
            elevation = get_elevation(latitude, longitude)
            url = f'https://power.larc.nasa.gov/api/temporal/{temporal}/point?'
            url += f'parameters=T2M_MAX&community={community}&longitude={longitude}&latitude={latitude}&start={start_date}&end={end_date}&format=JSON'
            response = requests.get(url=url, verify=True, timeout=30.00)
            content = json.loads(response.content.decode('utf-8'))
            properties = content['properties']['parameter']['T2M_MAX']
            data_dict_max[(latitude, longitude)] = properties
            progress_percent = (n / len(locations)) * 100
            status_text = f'{old_message}Downloading "T2M_MAX" [{(latitude, longitude)}]: {progress_percent:.2f}%'
            status_label.delete(1.0, tk.END)
            status_label.insert(tk.END, status_text)
            status_label.see(tk.END)
            status_label.update_idletasks()
            
            # Prepare data for the index file
            filename = f"T2M{str(latitude)}{str(longitude)}".replace(".", "")
            index_data.append([idx, filename, latitude, longitude, elevation])
            idx += 1
            
            n += 1

        status_label.insert(tk.END, '\nDownload complete!\n')
        status_label.see(tk.END)
        status_label.update()
        df_max = pd.DataFrame.from_dict(data_dict_max, orient='index')
        df_max = df_max.transpose()

        # Download T2M_MIN data
        data_dict_min = {}
        n = 1
        for latitude, longitude in locations:
            url = f'https://power.larc.nasa.gov/api/temporal/{temporal}/point?'
            url += f'parameters=T2M_MIN&community={community}&longitude={longitude}&latitude={latitude}&start={start_date}&end={end_date}&format=JSON'
            response = requests.get(url=url, verify=True, timeout=30.00)
            content = json.loads(response.content.decode('utf-8'))
            properties = content['properties']['parameter']['T2M_MIN']
            data_dict_min[(latitude, longitude)] = properties
            progress_percent = (n / len(locations)) * 100
            status_text = f'{old_message}Downloading "T2M_MIN" [{(latitude, longitude)}]: {progress_percent:.2f}%'
            status_label.delete(1.0, tk.END)
            status_label.insert(tk.END, status_text)
            status_label.see(tk.END)
            status_label.update_idletasks()
            n += 1

        status_label.insert(tk.END, '\nDownload complete!\n')
        status_label.see(tk.END)
        status_label.update()
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
            elevation = get_elevation(latitude, longitude)
            url = f'https://power.larc.nasa.gov/api/temporal/{temporal}/point?'
            url += f'parameters={param}&community={community}&longitude={longitude}&latitude={latitude}&start={start_date}&end={end_date}&format=JSON'
            url += f''
            #print(f'Downloading [{(latitude, longitude)}]: {(n/len(locations))*100:.2f}%', end='\r')
            response = requests.get(url=url, verify=True, timeout=30.00)
            content = json.loads(response.content.decode('utf-8'))
            properties = content['properties']['parameter'][param]
            data_dict[(latitude, longitude)] = properties
            progress_percent = (n / len(locations)) * 100
            status_text = f'{old_message}Downloading [{(latitude, longitude)}]: {progress_percent:.2f}%'
            status_label.delete(1.0, tk.END)
            status_label.insert(tk.END, status_text)
            status_label.see(tk.END)
            status_label.update_idletasks()
            
            # Prepare data for the index file
            filename = f"{param}{str(latitude)}{str(longitude)}".replace(".", "")
            index_data.append([idx, filename, latitude, longitude, elevation])
            idx += 1
            
            n += 1
        
        status_label.insert(tk.END, '\nDownload complete!\n')
        status_label.see(tk.END)
        status_label.update()
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
    
def browse_dest_ee_folder():

    '''
    This function is called when the user clicks the "Browse" button next to the "Destination folder" entry box.
    It opens a file dialog box to allow the user to select a folder.

    '''

    dest_folder = filedialog.askdirectory()
    dest_fol_entry.delete(0, tk.END)
    dest_fol_entry.insert(0, dest_folder)

def on_menu_selected(event, event_type):

    '''
    This function is called when the user selects an item from the comboboxes. It displays the selected item in the status label.

    Parameters: 
        event (event): The event that called this function
        event_type (str): The type of event that called this function

    '''


    selected_task = event.widget.get()
    event_type_messages = {
        "param": "Parameter",
        "com": "Community",
        # Add more date type messages as needed
    }

    if event_type in event_type_messages:
        event_label = event_type_messages[event_type]

        status_label.insert(tk.END, f'{event_label}: {selected_task}\n')
        status_label.see(tk.END)
        status_label.update()

main_window = tk.Tk()
main_window.title("SWAT Weather Data Downloader")
main_window.geometry("800x500+10+10")

# Task combobox
task_list = ["Select Parameter",
             "Precipitation",
             "Temperature",
             "Wind",
             "Solar Radiation",
             "Relative Humidity"]
    
# Function to handle date selection
def on_date_selected(event, date_type):

    '''
    This function is called when the user selects a date from the calendar. It displays the selected date in the status label.

    Parameters:
        event (event): The event that called this function
        date_type (str): The type of date that was selected
    '''

    if date_type == "temporal":
        selected_date = event.widget.get()
    else:
        selected_date = event.widget.get_date()
    
    date_type_messages = {
        "start": "Start Date",
        "end": "End Date",
        "temporal": "Temporal Scale",
        # Add more date type messages as needed
    }

    if date_type in date_type_messages:
        date_label = date_type_messages[date_type]

        status_label.insert(tk.END, f'{date_label}: {selected_date}\n')
        status_label.see(tk.END)
        status_label.update()
    
def polygon_click(polygon):
    print(f"polygon clicked - text: {polygon.name}")
    
def convert_date_format(date_str):

    '''
    This function converts a date string from the format DD-MM-YYYY to YYYYMMDD.

    Parameters:
        date_str (str): The date string to be converted

    Returns:
        formatted_date (str): The date string in the format YYYYMMDD

    '''

    date_obj = datetime.strptime(date_str, '%d-%m-%Y')
    formatted_date = date_obj.strftime('%Y%m%d')
    return formatted_date
    
# Function to handle fetching power data and creating a bounding box
def fetch_power_data():

    '''
    This function is called when the user clicks the "Fetch Power Data" button. 
    It fetches the power data from the API and creates a bounding box on the map widget. 
    '''

    try:
        # Get the entered values for latitude and longitude
        bottom_left_lat = float(bottom_left_lat_entry.get())
        bottom_left_lon = float(bottom_left_lon_entry.get())
        upper_right_lat = float(upper_right_lat_entry.get())
        upper_right_lon = float(upper_right_lon_entry.get())

        bbox = [bottom_left_lat, bottom_left_lon, upper_right_lat, upper_right_lon]

        # Create the bounding box list with tuples
        bounding_box = [
            (upper_right_lat, bottom_left_lon),  # Top-Left
            (upper_right_lat, upper_right_lon),  # Top-Right
            (bottom_left_lat, upper_right_lon),  # Bottom-Right
            (bottom_left_lat, bottom_left_lon)   # Bottom-Left
        ]
    
        
        polygon = map_widget.set_polygon(bounding_box, fill_color=None, outline_color="red", border_width=2,
                                         command=lambda:polygon_click(),
                                         name="Bounding Box")
        
        # first coordinate is the top-left corner and the second coordinate is the bottom-right corner
        map_widget.fit_bounding_box(bounding_box[0], bounding_box[2])
        
        status_label.insert(tk.END, f'Bounding Box: {bounding_box}')
        status_label.see(tk.END)
        status_label.update()
        
        # Mapping of task_var options to parameters
        task_to_param = {
            'Precipitation': 'PRECTOTCORR',
            'Temperature': 'T2M',
            'Solar Radiation': 'ALLSKY_SFC_SW_DWN',
            'Relative Humidity': 'RH2M',
            'Wind': 'WS2M',}

        # Mapping of com_var options to communities
        com_to_community = {
            'Agroclimatology (AG)': 'AG',
            'Sustainable Buildings (SB)': 'SB',
            'Renewable Energy (RE)': 'RE',}

        param = task_to_param.get(task_var.get(), None)
        community = com_to_community.get(com_var.get(), None)

        temporal = time_var.get()
        temporal = temporal.lower()
        dest_folder = dest_fol_entry.get()

        start_date = convert_date_format(date_str = start_date_entry.get())
        end_date = convert_date_format(date_str = end_date_entry.get())

        df = download_param(bbox, param, community, temporal, start_date, end_date, dest_folder)
        
    except ValueError:
<<<<<<< HEAD
        messagebox.showerror('Error', "Invalid input. Please enter valid inputs.")
=======
        messagebox.showerror('Error', "Invalid input. Please enter valid numeric values for latitude and longitude.")
>>>>>>> 8253f451113b639b53cc74d19c6965ad5bfad589

# Create a frame for the inputs
input_frame = ttk.LabelFrame(main_window, text="Data Inputs")
input_frame.grid(row = 0, sticky = 'news', padx=10, pady=10)

# Create a frame for the "1. Select Parameter/Community" section
param_frame = ttk.LabelFrame(input_frame, text="1. Select Parameter and Community", borderwidth=2, relief=tk.RIDGE)
param_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

task_var = tk.StringVar(param_frame)
task_var.set("Select Parameter")
task_combobox = ttk.Combobox(param_frame, textvariable=task_var, values=task_list)
task_combobox.grid(row=0, column=0, sticky = 'news', padx=5, pady=5)
task_combobox.bind("<<ComboboxSelected>>", lambda event: on_menu_selected(event, "param"))

com_var = tk.StringVar(param_frame)
com_var.set("Agroclimatology (AG)")
com_combobox = ttk.Combobox(param_frame, textvariable=com_var, values=['Agroclimatology (AG)', 'Sustainable Buildings (SB)',
                                                                        'Renewable Energy (RE)'])
com_combobox.grid(row=0, column=1, sticky = 'news', padx=5, pady=5)
com_combobox.bind("<<ComboboxSelected>>", lambda event: on_menu_selected(event, "com"))

# Add a separator between Parameter and "2. Enter Date Range" sections
separator = ttk.Separator(input_frame, orient=tk.HORIZONTAL)
separator.grid(row=1, column=0, columnspan=2, pady=10, sticky='ew')

# Create a frame for the "2. Enter Date Range" section
date_frame = ttk.LabelFrame(input_frame, text="2. Date Range and Temporal Scale")
date_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

# Start Date Input with Calendar
start_date_label = ttk.Label(date_frame, text="Start Date")
start_date_label.grid(row=0, column=0, padx=5, pady=5, sticky='news')
start_date_entry = DateEntry(date_frame, date_pattern='dd-mm-yyyy')
start_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='news')
start_date_unit_label = ttk.Label(date_frame, text=" (DD-MM-YYYY)")
start_date_unit_label.grid(row=0, column=2, padx=5, pady=5, sticky='news')
start_date_entry.bind("<<DateEntrySelected>>", lambda event: on_date_selected(event, "start"))

# End Date Input with Calendar
end_date_label = ttk.Label(date_frame, text="End Date")
end_date_label.grid(row=1, column=0, padx=5, pady=5, sticky='news')
end_date_entry = DateEntry(date_frame, date_pattern='dd-mm-yyyy')
end_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky='news')
end_date_unit_label = ttk.Label(date_frame, text=" (DD-MM-YYYY)")
end_date_unit_label.grid(row=1, column=2, padx=5, pady=5, sticky='news')
end_date_entry.bind("<<DateEntrySelected>>", lambda event: on_date_selected(event, "end"))

# Temporal Scale Combobox
time_label = ttk.Label(date_frame, text='Temporal Scale')
time_label.grid(row=2, column=0, padx=5, pady=5, sticky='news')
time_var = tk.StringVar(date_frame)
time_var.set("Daily")
time_combobox = ttk.Combobox(date_frame, textvariable=time_var, values=['Daily', 'Monthly', 'Yearly'])
time_combobox.grid(row=2, column=1, sticky='news', padx=5, pady=5)
time_combobox.bind("<<ComboboxSelected>>", lambda event: on_date_selected(event, "temporal"))

# Corner coordinates 
# Add a separator between End Date and "3. Enter Lat/Lon" sections
separator = ttk.Separator(input_frame, orient=tk.HORIZONTAL)
separator.grid(row=3, column=0, columnspan=2, pady=10, sticky='ew')

# Create a frame for the "3. Enter Lat/Lon" section
lat_lon_frame = ttk.LabelFrame(input_frame, text="3. Enter Lat/Lon")
lat_lon_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

# Bottom-left Lat Input
bottom_left_lat_label = ttk.Label(lat_lon_frame, text="Bottom-left Lat:")
bottom_left_lat_label.grid(row=0, column=0, padx=5, pady=5, sticky = 'news')
bottom_left_lat_entry = ttk.Entry(lat_lon_frame)
bottom_left_lat_entry.grid(row=0, column=1, padx=5, pady=5, sticky = 'news')
bottom_left_lat_unit_label = ttk.Label(lat_lon_frame, text=" (Decimal Degrees)")
bottom_left_lat_unit_label.grid(row=0, column=2, padx=5, pady=5, sticky = 'news')

# Bottom-left Lon Input
bottom_left_lon_label = ttk.Label(lat_lon_frame, text="Bottom-left Lon:")
bottom_left_lon_label.grid(row=1, column=0, padx=5, pady=5, sticky = 'news')
bottom_left_lon_entry = ttk.Entry(lat_lon_frame)
bottom_left_lon_entry.grid(row=1, column=1, padx=5, pady=5, sticky = 'news')
bottom_left_lon_unit_label = ttk.Label(lat_lon_frame, text=" (Decimal Degrees)")
bottom_left_lon_unit_label.grid(row=1, column=2, padx=5, pady=5, sticky = 'news')

# Upper-right Lat Input
upper_right_lat_label = ttk.Label(lat_lon_frame, text="Upper-right Lat:")
upper_right_lat_label.grid(row=2, column=0, padx=5, pady=5, sticky = 'news')
upper_right_lat_entry = ttk.Entry(lat_lon_frame)
upper_right_lat_entry.grid(row=2, column=1, padx=5, pady=5, sticky = 'news')
upper_right_lat_unit_label = ttk.Label(lat_lon_frame, text=" (Decimal Degrees)")
upper_right_lat_unit_label.grid(row=2, column=2, padx=5, pady=5, sticky = 'news')

# Upper-right Lon Input
upper_right_lon_label = ttk.Label(lat_lon_frame, text="Upper-right Lon:")
upper_right_lon_label.grid(row=3, column=0, padx=5, pady=5, sticky = 'news')
upper_right_lon_entry = ttk.Entry(lat_lon_frame)
upper_right_lon_entry.grid(row=3, column=1, padx=5, pady=5, sticky = 'news')
upper_right_lon_unit_label = ttk.Label(lat_lon_frame, text=" (Decimal Degrees)")
upper_right_lon_unit_label.grid(row=3, column=2, padx=5, pady=5, sticky = 'news')

separator = ttk.Separator(input_frame, orient=tk.HORIZONTAL)
separator.grid(row=5, column=0, columnspan=2, pady=10, sticky='ew')

opf_frame = ttk.LabelFrame(input_frame, text = '4. Output Folder')
opf_frame.grid(row = 6, column = 0, columnspan = 2, padx = 10, pady = 10, sticky = 'ew')

dest_fol_button = ttk.Button(opf_frame, text="Browse Destination Folder", command=browse_dest_ee_folder)
dest_fol_button.grid(row=0, column=0, padx=5, pady=5, sticky="nw")
dest_fol_entry = ttk.Entry(opf_frame)
dest_fol_entry.grid(row=0, column=1, columnspan = 2, padx=5, pady=5, sticky="news")

separator = ttk.Separator(input_frame, orient=tk.HORIZONTAL)
separator.grid(row=7, column=0, columnspan=2, pady=10, sticky='ew')

# Fetch Data Button
fetch_button = ttk.Button(input_frame, text="Fetch Data", command=fetch_power_data)
fetch_button.grid(row=8, column=0, columnspan=2, padx=5, pady=10, sticky = 'news')

# -------------- Map -----------
map_label = ttk.LabelFrame(main_window)
map_label.grid(row = 0, column = 1, sticky = 'news', padx = 10, pady = 10)

map_widget = tkintermapview.TkinterMapView(map_label, width=800, height=600, corner_radius=0)
map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
map_widget.grid(row = 0, columnspan = 2, sticky = 'news')
map_widget.set_position(20.5937, 78.9629)  
map_widget.set_zoom(4.5)

# ------ Console ------ 
separator = ttk.Separator(map_label, orient=tk.HORIZONTAL)
separator.grid(row=1, column=0, columnspan=2, pady=10, sticky='ew')

status_label = scrolledtext.ScrolledText(map_label, width=80, height=5)
status_label.grid(row = 2, columnspan = 2, sticky = 'news')

# ----- Attribution text -----------
attribution_text = (
    "Disclaimer:\n\n"
    "The boundaries of countries and territories shown on the map do not imply any judgment on the legal status of these regions or endorsement or acceptance of such boundaries.\n\n"
    "I do not claim responsibility for the accuracy, completeness, or reliability of the map or weather data or any errors or omissions that may occur. Users are advised to verify the information independently and exercise their own judgment when using the map or the derived weather data.\n\n"
    "The map and data is provided \"as is\" without any representations or warranties, express or implied. By using this map or any derived data, you agree that I shall not be liable for any damages, losses, or liabilities arising from the use of this map or reliance on the information displayed/derived.\n\n"
    "For the most current and accurate information, users are encouraged to refer to official sources and seek professional advice when needed.\n\n"
    "Provided under MIT License\n\n"
    "Created by: Akhilesh Kumar\n(https://github.com/akhi9661/generate_swat_climate_input)"
)

# Frame for attribution
attribution_frame = tk.Frame(main_window, width=800, height=20, bd=1, relief='solid')
attribution_frame.grid(row = 0, column = 2, padx=10, pady=10)

# Attribution label
attribution_label = tk.Label(
    attribution_frame, text=attribution_text, justify='left', wraplength=270, font=('Arial', 9))
attribution_label.grid(padx=5, pady=5)

main_window.mainloop()

# ---------------------------------------------------------------------------------------------- #
