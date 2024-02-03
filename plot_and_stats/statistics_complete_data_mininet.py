import pandas as pd
import numpy as np
from termcolor import colored

DEBUG = 0

resolution_order = ['320x180', '480x270', '640x360',  '768x432', '940x540', '1024x576', '1280x720', '1920x1080', '2560x1440', '3840x2160']

buffer_length_treshold = 0.5
fps = 30

def debug_print(*args):
    if DEBUG:
        print(*args)

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

def calculate_and_print_statistics(run, data, resolution_data, droppedFrames_data, bw):
    data['Buffer Length Drop'] = data['Buffer Length'].diff()
    rebuffering_events = (data['Buffer Length'] < buffer_length_treshold).sum()

    resolution_data['ResolutionIndex'] = resolution_data['Resolution'].apply(lambda x: resolution_order.index(x))
    bandwidth_utilization = round(data['Download Rate'].mean() / bw * 100, 2)
    droppedFrames_percentage = round(droppedFrames_data['Dropped Frames'].max() / (droppedFrames_data['Time'].max() * fps) * 100, 2)
    resolution_changes = calculate_resolution_changes(resolution_data)
    correlation = data['Download Rate'].corr(data['Buffer Length'])

    debug_print(colored(f"Rebuffering events for run {run}: {rebuffering_events}", 'yellow'))
    debug_print(colored(f"Bandwidth utilization for run {run}: {bandwidth_utilization} %", 'green'))
    debug_print(colored(f"Dropped frames for run {run}: {droppedFrames_percentage} %", 'red'))
    debug_print(colored(f"Resolution changes for run {run}: {resolution_changes}", 'blue'))
    debug_print(colored(f"Correlation between download rate and buffer length for run {run}: {correlation}", 'cyan'))

    avg_effective_bitrate = data['Effective Bitrate'].mean()

    avg_data = pd.DataFrame({
        'Download Rate': [data['Download Rate'].mean()], 
        'Buffer Length': [data['Buffer Length'].mean()], 
        'Effective Bitrate': [avg_effective_bitrate], 
        'Bitrate': [data['Bitrate'].mean()],
        'Dropped Frames': [droppedFrames_data['Dropped Frames'].max()],
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
    
    debug_print(resolution_counts)
    debug_print(bitrate_counts)
    debug_print(avg_data)

    

    return bandwidth_utilization, rebuffering_events, avg_effective_bitrate, resolution_changes, correlation, avg_data

def parse_multiple_data_files_and_give_statistic(bw, delay, loss, number_of_runs):
    bandwidth_utilization_for_each_run = []
    rebuffering_events_for_each_run = []
    effective_bitrate_for_each_run = []
    resolution_changes_for_each_run = []
    droppedFrames_percentage_for_each_run = []
    correlation_for_each_run = []
    all_runs_avg_data = pd.DataFrame()

    for run in range(1, number_of_runs + 1):
        base_path = f'statistics/mininet/{bw}_{delay}_{loss}/'
        data_file = f'{base_path}data_{bw}_{delay}_{loss}_{run}.csv'
        resolution_file = f'{base_path}resolutionData_{bw}_{delay}_{loss}_{run}.csv'
        droppedFrames_file = f'{base_path}droppedFrames_{bw}_{delay}_{loss}_{run}.csv'

        data = read_and_process_data(data_file)
        resolution_data = read_and_process_data(resolution_file)
        droppedFrames_data = read_and_process_data(droppedFrames_file)

        bandwidth_utilization, rebuffering_events, effective_bitrate, resolution_changes, correlation, avg_data = calculate_and_print_statistics(run, data, resolution_data, droppedFrames_data, bw)
        bandwidth_utilization_for_each_run.append(bandwidth_utilization)
        rebuffering_events_for_each_run.append(rebuffering_events)
        effective_bitrate_for_each_run.append(effective_bitrate)
        resolution_changes_for_each_run.append(resolution_changes)
        droppedFrames_percentage_for_each_run.append(droppedFrames_data['Dropped Frames'].max() / (droppedFrames_data['Time'].max() * fps) * 100)
        correlation_for_each_run.append(correlation)
        all_runs_avg_data = pd.concat([all_runs_avg_data,avg_data])
    debug_print ("-----------------------------------------------------------------------")

    avg_bandwidth_utilization_for_each_run = round(np.mean(bandwidth_utilization_for_each_run), 2)
    std_bandwidth_utilization_for_each_run = round(np.std(bandwidth_utilization_for_each_run), 2)
    avg_rebuffering_events_for_each_run = round(np.mean(rebuffering_events_for_each_run), 2)
    std_rebuffering_events_for_each_run = round(np.std(rebuffering_events_for_each_run), 2)
    avg_effective_bitrate_for_each_run = round(np.mean(effective_bitrate_for_each_run), 2)
    std_effective_bitrate_for_each_run = round(np.std(effective_bitrate_for_each_run), 2)
    avg_resolution_changes_for_each_run = round(np.mean(resolution_changes_for_each_run), 2)
    std_resolution_changes_for_each_run = round(np.std(resolution_changes_for_each_run), 2)
    avg_droppedFrames_percentage_for_each_run = round(np.mean(droppedFrames_percentage_for_each_run), 2)
    std_droppedFrames_percentage_for_each_run = round(np.std(droppedFrames_percentage_for_each_run), 2)
    avg_correlation_for_each_run = round(np.mean(correlation_for_each_run), 2)
    std_correlation_for_each_run = round(np.std(correlation_for_each_run), 2)

    avg_all_runs_avg_data = all_runs_avg_data.mean()
    std_all_runs_avg_data = all_runs_avg_data.std()


    debug_print(colored(f"Average bandwidth utilization for all runs: {avg_bandwidth_utilization_for_each_run}%", 'green'))
    debug_print(colored(f"Standard deviation of bandwidth utilization for all runs: {std_bandwidth_utilization_for_each_run}%", 'green'))
    debug_print(colored(f"Average rebuffering events for all runs: {avg_rebuffering_events_for_each_run}", 'yellow'))
    debug_print(colored(f"Standard deviation of rebuffering events for all runs: {std_rebuffering_events_for_each_run}", 'yellow'))
    debug_print(colored(f"Average effective bitrate for all runs: {avg_effective_bitrate_for_each_run} Mbps", 'green'))
    debug_print(colored(f"Standard deviation of effective bitrate for all runs: {std_effective_bitrate_for_each_run} Mbps", 'green'))
    debug_print(colored(f"Average resolution changes for all runs: {avg_resolution_changes_for_each_run}", 'blue'))
    debug_print(colored(f"Standard deviation of resolution changes for all runs: {std_resolution_changes_for_each_run}", 'blue'))
    debug_print(colored(f"Average dropped frames for all runs: {avg_droppedFrames_percentage_for_each_run}%", 'red'))
    debug_print(colored(f"Standard deviation of dropped frames for all runs: {std_droppedFrames_percentage_for_each_run}%", 'red'))
    debug_print(colored(f"Average correlation between download rate and buffer length for all runs: {avg_correlation_for_each_run}", 'cyan'))
    debug_print(colored(f"Standard deviation of correlation between download rate and buffer length for all runs: {std_correlation_for_each_run}", 'cyan'))
    debug_print(all_runs_avg_data)
    debug_print(colored("Average data for all runs:", 'yellow'))
    debug_print(avg_all_runs_avg_data)
    debug_print(colored("Standard deviation of average data for all runs:", 'yellow'))
    debug_print(std_all_runs_avg_data)

    return_values = {
        "avg_bandwidth_utilization_for_each_run": avg_bandwidth_utilization_for_each_run,
        "std_bandwidth_utilization_for_each_run": std_bandwidth_utilization_for_each_run,
        "avg_rebuffering_events_for_each_run": avg_rebuffering_events_for_each_run,
        "std_rebuffering_events_for_each_run": std_rebuffering_events_for_each_run,
        "avg_effective_bitrate_for_each_run": avg_effective_bitrate_for_each_run,
        "std_effective_bitrate_for_each_run": std_effective_bitrate_for_each_run,
        "avg_resolution_changes_for_each_run": avg_resolution_changes_for_each_run,
        "std_resolution_changes_for_each_run": std_resolution_changes_for_each_run,
        "avg_droppedFrames_percentage_for_each_run": avg_droppedFrames_percentage_for_each_run,
        "std_droppedFrames_percentage_for_each_run": std_droppedFrames_percentage_for_each_run,
        "avg_correlation_for_each_run": avg_correlation_for_each_run,
        "std_correlation_for_each_run": std_correlation_for_each_run,
        "avg_all_runs_avg_data": avg_all_runs_avg_data,
        "std_all_runs_avg_data": std_all_runs_avg_data
    }
    return return_values