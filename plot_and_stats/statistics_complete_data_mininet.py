import pandas as pd
import numpy as np
from termcolor import colored

resolution_order = ['320x180', '480x270', '640x360',  '768x432', '960x540', '1024x576', '1280x720', '1920x1080', '2560x1440', '3840x2160']

bw = 50
delay = 100
loss = 2
number_of_runs = 3
buffer_length_treshold = 0.5
fps = 30

def convert_to_seconds(timestr):
    """Converts a time string in HH:MM format to seconds."""
    m, s = map(int, timestr.split(':'))
    return m * 60 + s

def read_and_process_data(file_name):
    """Reads data from a CSV file and processes it."""
    data = pd.read_csv(file_name)
    data['Time'] = data['Time'].apply(convert_to_seconds)
    return data

def calculate_and_print_statistics(run, data, resolution_data, droppedFrames_data):
    """Calculates and prints statistics for a given run."""
    data['Buffer Length Drop'] = data['Buffer Length'].diff()
    rebuffering_events = (data['Buffer Length'] < buffer_length_treshold).sum()
    print(colored(f"Rebuffering events for run {run}: {rebuffering_events}", 'yellow'))

    resolution_data['ResolutionIndex'] = resolution_data['Resolution'].apply(lambda x: resolution_order.index(x))
    bandwidth_utilization = round(data['Download Rate'].mean() / bw * 100, 2)
    droppedFrames_percentage = round(droppedFrames_data['Dropped Frames'].max() / droppedFrames_data['Time'].max() * 100, 2)
    print(colored(f"Bandwidth utilization for run {run}: {bandwidth_utilization} %", 'green'))
    print(colored(f"Dropped frames for run {run}: {droppedFrames_data['Dropped Frames'].max()} / {droppedFrames_data['Time'].max()} * 100 = {droppedFrames_percentage} %", 'red'))

    avg_data = pd.DataFrame({
        'Run': [run],
        'Download Rate': [data['Download Rate'].mean()], 
        'Buffer Length': [data['Buffer Length'].mean()], 
        'Effective Bitrate': [data['Effective Bitrate'].mean()], 
        'Bitrate': [data['Bitrate'].mean()]
    })

    resolution_counts = resolution_data['Resolution'].value_counts()
    bitrate_counts = data['Bitrate'].value_counts()
    
    resolution_counts = resolution_counts.apply(lambda x: round(x/sum(resolution_counts) *100, 2))
    bitrate_counts = bitrate_counts.apply(lambda x: round(x/sum(bitrate_counts) *100, 2))

    print(resolution_counts)
    print(bitrate_counts)
    print(avg_data)
    

    return bandwidth_utilization, rebuffering_events

def parse_multiple_data_files_and_give_statistic():
    """Parses multiple data files and calculates and displays bandwidth utilization statistics."""
    avg_bandwidth_utilization_for_each_run = []
    avg_rebuffering_events_for_each_run = []

    for run in range(1, number_of_runs + 1):
        base_path = f'statistics/mininet/{bw}_{delay}_{loss}/'
        data_file = f'{base_path}data_{bw}_{delay}_{loss}_{run}.csv'
        resolution_file = f'{base_path}resolutionData_{bw}_{delay}_{loss}_{run}.csv'
        droppedFrames_file = f'{base_path}droppedFrames_{bw}_{delay}_{loss}_{run}.csv'

        data = read_and_process_data(data_file)
        resolution_data = read_and_process_data(resolution_file)
        droppedFrames_data = read_and_process_data(droppedFrames_file)

        bandwidth_utilization, rebuffering_events = calculate_and_print_statistics(run, data, resolution_data, droppedFrames_data)
        avg_bandwidth_utilization_for_each_run.append(bandwidth_utilization)
        avg_rebuffering_events_for_each_run.append(rebuffering_events)
    print ("-----------------------------------------------------------------------")

    print(colored(f"Average bandwidth utilization for all runs: {round(np.mean(avg_bandwidth_utilization_for_each_run), 2)}%", 'green'))
    print(colored(f"Standard deviation of bandwidth utilization for all runs: {round(np.std(avg_bandwidth_utilization_for_each_run), 2)}%", 'green'))
    print(colored(f"Average rebuffering events for all runs: {round(np.mean(avg_rebuffering_events_for_each_run), 2)}", 'yellow'))
    print(colored(f"Standard deviation of rebuffering events for all runs: {round(np.std(avg_rebuffering_events_for_each_run), 2)}", 'yellow'))

# Call the function
parse_multiple_data_files_and_give_statistic()