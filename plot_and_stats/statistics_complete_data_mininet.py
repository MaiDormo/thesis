import argparse
import pandas as pd
import numpy as np
from termcolor import colored

resolution_order = ['320x180', '480x270', '640x360',  '768x432', '940x540', '1024x576', '1280x720', '1920x1080', '2560x1440', '3840x2160']

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--bw', type=int, required=True, help='Bandwidth')
parser.add_argument('--delay', type=int, required=True, help='Delay')
parser.add_argument('--loss', type=int, required=True, help='Loss')

args = parser.parse_args()

bw = args.bw
delay = args.delay
loss = args.loss
number_of_runs = 3
buffer_length_treshold = 0.5
fps = 30

def convert_to_seconds(timestr):
    m, s = map(int, timestr.split(':'))
    return m * 60 + s

def read_and_process_data(file_name):
    data = pd.read_csv(file_name)
    data['Time'] = data['Time'].apply(convert_to_seconds)
    return data

def calculate_resolution_changes(resolution_data):
    resolution_changes = (resolution_data['Resolution'] != resolution_data['Resolution'].shift()).sum()
    return resolution_changes

def calculate_and_print_statistics(run, data, resolution_data, droppedFrames_data):
    data['Buffer Length Drop'] = data['Buffer Length'].diff()
    rebuffering_events = (data['Buffer Length'] < buffer_length_treshold).sum()
    print(colored(f"Rebuffering events for run {run}: {rebuffering_events}", 'yellow'))

    resolution_data['ResolutionIndex'] = resolution_data['Resolution'].apply(lambda x: resolution_order.index(x))
    bandwidth_utilization = round(data['Download Rate'].mean() / bw * 100, 2)
    droppedFrames_percentage = round(droppedFrames_data['Dropped Frames'].max() / (droppedFrames_data['Time'].max() * fps) * 100, 2)
    print(colored(f"Bandwidth utilization for run {run}: {bandwidth_utilization} %", 'green'))
    print(colored(f"Dropped frames for run {run}: {droppedFrames_percentage} %", 'red'))
    resolution_changes = calculate_resolution_changes(resolution_data)
    print(colored(f"Resolution changes for run {run}: {resolution_changes}", 'blue'))

    avg_effective_bitrate = data['Effective Bitrate'].mean()

    avg_data = pd.DataFrame({
        'Run': [run],
        'Download Rate': [data['Download Rate'].mean()], 
        'Buffer Length': [data['Buffer Length'].mean()], 
        'Effective Bitrate': [avg_effective_bitrate], 
        'Bitrate': [data['Bitrate'].mean()]
    })

    resolution_counts = resolution_data['Resolution'].value_counts()
    bitrate_counts = data['Bitrate'].value_counts()
    
    # Order resolution_counts by the order found inside resolution_order
    resolution_counts = resolution_counts.reindex(resolution_order).dropna()

    # Convert the index to int, sort by index, and then convert the index back to str
    bitrate_counts.index = bitrate_counts.index.astype(float)
    bitrate_counts = bitrate_counts.sort_index()
    bitrate_counts.index = bitrate_counts.index.astype(str)

    resolution_counts = resolution_counts.apply(lambda x: round(x/sum(resolution_counts) *100, 2))
    bitrate_counts = bitrate_counts.apply(lambda x: round(x/sum(bitrate_counts) *100, 2))

    print(resolution_counts)
    print(bitrate_counts)
    print(avg_data)

    

    return bandwidth_utilization, rebuffering_events, avg_effective_bitrate, resolution_changes

def parse_multiple_data_files_and_give_statistic():
    avg_bandwidth_utilization_for_each_run = []
    avg_rebuffering_events_for_each_run = []
    avg_effective_bitrate_for_each_run = []
    avg_resolution_changes_for_each_run = []

    for run in range(1, number_of_runs + 1):
        base_path = f'statistics/mininet/{bw}_{delay}_{loss}/'
        data_file = f'{base_path}data_{bw}_{delay}_{loss}_{run}.csv'
        resolution_file = f'{base_path}resolutionData_{bw}_{delay}_{loss}_{run}.csv'
        droppedFrames_file = f'{base_path}droppedFrames_{bw}_{delay}_{loss}_{run}.csv'

        data = read_and_process_data(data_file)
        resolution_data = read_and_process_data(resolution_file)
        droppedFrames_data = read_and_process_data(droppedFrames_file)

        bandwidth_utilization, rebuffering_events, effective_bitrate, resolution_changes = calculate_and_print_statistics(run, data, resolution_data, droppedFrames_data)
        avg_bandwidth_utilization_for_each_run.append(bandwidth_utilization)
        avg_rebuffering_events_for_each_run.append(rebuffering_events)
        avg_effective_bitrate_for_each_run.append(effective_bitrate)
        avg_resolution_changes_for_each_run.append(resolution_changes)
    print ("-----------------------------------------------------------------------")

    print(colored(f"Average bandwidth utilization for all runs: {round(np.mean(avg_bandwidth_utilization_for_each_run), 2)}%", 'green'))
    print(colored(f"Standard deviation of bandwidth utilization for all runs: {round(np.std(avg_bandwidth_utilization_for_each_run), 2)}%", 'green'))
    print(colored(f"Average rebuffering events for all runs: {round(np.mean(avg_rebuffering_events_for_each_run), 2)}", 'yellow'))
    print(colored(f"Standard deviation of rebuffering events for all runs: {round(np.std(avg_rebuffering_events_for_each_run), 2)}", 'yellow'))
    print(colored(f"Average effective bitrate for all runs: {round(np.mean(avg_effective_bitrate_for_each_run), 2)} Mbps", 'green'))
    print(colored(f"Standard deviation of effective bitrate for all runs: {round(np.std(avg_effective_bitrate_for_each_run), 2)} Mbps", 'green'))
    print(colored(f"Average resolution changes for all runs: {round(np.mean(avg_resolution_changes_for_each_run), 2)}", 'blue'))
    print(colored(f"Standard deviation of resolution changes for all runs: {round(np.std(avg_resolution_changes_for_each_run), 2)}", 'blue'))

parse_multiple_data_files_and_give_statistic()