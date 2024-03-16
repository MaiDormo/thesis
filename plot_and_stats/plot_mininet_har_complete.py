import json
import re
import numpy as np
import pandas as pd
from progress.bar import Bar
from datetime import datetime, timedelta
from termcolor import colored

DEBUG = 1

bw = 10
delay = 20
loss = 0

def get_timing_data(entry, timings):
    timing_data = {timing: [] for timing in timings}
    for timing in timings:
        time = entry['timings'].get(timing, 0)
        timing_data[timing].append(max(0, time if time != -1 else 0))
    return timing_data

def get_startup_delay(startup_time, last_dash1_end_time):
    if startup_time is not None and last_dash1_end_time is not None:
        return (last_dash1_end_time - startup_time).total_seconds() * 1000
    return None

def print_startup_delay_and_res(startup_delay, startup_res, first_resolution):
    if DEBUG == 1 and startup_delay is not None:
        print(colored(f"\nStartup delay: {startup_delay} ms\n", 'green'))
        print(colored(f"Resolution of first segment: {startup_res}\n", 'green'))
        print(colored(f"First resolution displayed: {first_resolution}\n", 'green'))


def print_total_waiting_time(total_times, index):
    if DEBUG == 1:
        print(colored(f"Total waiting time: {total_times[index]} ms\n", 'blue'))

def print_dataframe(timings, contributions, means, sums, deviations, index):
    if DEBUG == 1:
        df = pd.DataFrame([
            {
                'Category': timing, 
                'Contribution (%)': contributions[index][timing],
                'Mean (ms)': means[index][timing], 
                'Deviation (ms)': deviations[index][timing], 
                'Sum (ms)': sums[index][timing]
            } for timing in timings
        ])
        print(df)
        print("\n" + "="*80 + "\n")

def print_averages(timings, total_times, contributions, means, sums, deviations, filenames):
    if DEBUG == 1:
        print(colored("Averages:", 'yellow'))
        print(f"Total Waiting Time: {sum(total_times)/len(filenames)/1000} seconds")
        contributions_avg = {timing: sum(d[timing] for d in contributions) / len(contributions) for timing in timings}
        means_avg = {timing: sum(d[timing] for d in means) / len(means) for timing in timings}
        sums_avg = {timing: sum(d[timing] for d in sums) / len(sums) for timing in timings}
        deviations_avg = {timing: sum(d[timing] for d in deviations) / len(deviations) for timing in timings}

        df = pd.DataFrame([
            {
                'Category': timing, 
                'Contribution (avg %)': contributions_avg[timing], 
                'Mean (avg ms)': means_avg[timing], 
                'Deviation (avg ms)': deviations_avg[timing], 
                'Sum (avg ms)': sums_avg[timing]
            } for timing in timings
        ])
        print(df)

def calculate_resolution_changes(resolution_data):
    # Convert the list of strings to a list of integers using a generator expression
    resolution_data = (int(res) for res in resolution_data)
    # Calculate the number of resolution changes
    resolution_changes = np.count_nonzero(np.diff(list(resolution_data)) != 0)
    return resolution_changes

def get_averages(timings, total_times, contributions, means, sums, deviations, filenames, startup_delays, bw, delay, loss, resolution_changes):
        avg_total_waiting_segment_time = sum(total_times)/len(filenames)/1000
        contributions_avg = {timing: sum(d[timing] for d in contributions) / len(contributions) for timing in timings}
        means_avg = {timing: sum(d[timing] for d in means) / len(means) for timing in timings}
        sums_avg = {timing: sum(d[timing] for d in sums) / len(sums) for timing in timings}
        deviations_avg = {timing: sum(d[timing] for d in deviations) / len(deviations) for timing in timings}
        avg_startup_delay = sum(startup_delays) / len(startup_delays)
        startup_delays_std = np.std(startup_delays)
        avg_resolution_changes = np.mean(resolution_changes)
        std_resolution_changes = np.std(resolution_changes) 

        df_total_avg_timings = pd.DataFrame([
            {
                'Bandwidth': bw,
                'Delay': delay,
                'Loss': loss,
                'Category': timing, 
                'Contribution (avg %)': contributions_avg[timing], 
                'Mean (avg ms)': means_avg[timing], 
                'Deviation (avg ms)': deviations_avg[timing], 
                'Sum (avg ms)': sums_avg[timing]
            } for timing in timings
        ])


        df_total_time_and_startup_delay = pd.DataFrame([
            {
                'Bandwidth': bw,
                'Delay': delay,
                'Loss': loss,
                'Total Waiting Time (avg s)': avg_total_waiting_segment_time,
                'Startup Delay (avg ms)': avg_startup_delay,
                'Startup Delay (std ms)': startup_delays_std
            }
        ])

        df_resolution_changes = pd.DataFrame([
            {
                'Bandwidth': bw,
                'Delay': delay,
                'Loss': loss,
                'Resolution Changes (avg)': avg_resolution_changes,
                'Resolution Changes (std)': std_resolution_changes
            }
        ])

        return df_total_avg_timings, df_total_time_and_startup_delay, df_resolution_changes

def print_avg_startup_delay(startup_delays):
    if DEBUG == 1:
        if startup_delays:
            avg_startup_delay = sum(startup_delays) / len(startup_delays)
            print(colored(f"\nAverage startup delay: {avg_startup_delay} ms\n", 'red'))

def parse_multiple_har_files(filenames, bw, delay, loss):
    timings = ['blocked', 'connect', 'send', 'wait', 'receive', '_blocked_queueing']
    
    resolution_changes = []
    total_times = []
    contributions = []
    means = []
    sums = []
    deviations = []
    startup_delays = []

    for index, filename in enumerate(filenames):
        timing_data = {timing: [] for timing in timings}
        resolutions = []
        startup_time = None
        last_dash1_time = None
        startup_res = None

        resolution_data = pd.read_csv(f'statistics/mininet/{bw}_{delay}_{loss}/resolutionData_{bw}_{delay}_{loss}_{index+1}.csv')
        first_resolution = resolution_data['Resolution'].iloc[0]
        first_resolution = first_resolution.split('x')[1]
        
        with open(filename, 'r') as f:
            har_data = json.load(f)
        
        for entry in har_data['log']['entries']:
            url = entry['request']['url']
            if url.startswith('http://10.0.0.1:1337/bbb_sunflower_2160p_30fps_normal_'):
                match = re.search(r'normal_(\d+)', url)
                if match:
                    res = match.group(1)
                    resolutions.append(res)
                    entry_timing_data = get_timing_data(entry, timings)
                    for timing in timings:
                        timing_data[timing].extend(entry_timing_data[timing])

            if '.mpd' in url and startup_time is None:
                startup_time = datetime.strptime(entry['startedDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')

            if 'dash1.m4s' in url:
                last_dash1_time = datetime.strptime(entry['startedDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                last_dash1_total_time = entry['time'] / 1000  # convert from ms to s
                last_dash1_end_time = last_dash1_time + timedelta(seconds=last_dash1_total_time)
                startup_res = res

        total_times.append(sum(sum(timing_data[timing]) for timing in timings))
        contributions.append({timing: sum(timing_data[timing]) / total_times[index] * 100 for timing in timings})
        means.append({timing: np.mean(timing_data[timing]) for timing in timings})
        sums.append({timing: sum(timing_data[timing]) for timing in timings})
        deviations.append({timing: np.std(timing_data[timing]) for timing in timings})
        resolution_changes.append(calculate_resolution_changes(resolutions))

        startup_delay = get_startup_delay(startup_time, last_dash1_end_time)
        if startup_delay is not None:
            startup_delays.append(startup_delay)
        
    df_total_avg_timings, df_total_time_and_startup_delay, df_resolution_changes  = get_averages(timings, total_times, contributions, means, sums, deviations, filenames, startup_delays, bw, delay, loss, resolution_changes)

    return df_total_avg_timings, df_total_time_and_startup_delay, df_resolution_changes

def mininet_har(bw, delay, loss, number_of_runs):
    filenames = []
    for i in range(1, number_of_runs+1):
        filenames.append(f'statistics/mininet/{bw}_{delay}_{loss}/mininet_{bw}_{delay}_{loss}_{i}.har')

    return parse_multiple_har_files(filenames, bw, delay, loss)