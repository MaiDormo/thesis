import json
import re
import argparse
import numpy as np
import pandas as pd
from progress.bar import Bar
from datetime import datetime, timedelta
from termcolor import colored

def get_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-bw', type=int, required=True, help='Bandwidth')
    parser.add_argument('-delay', type=int, required=True, help='Delay')
    parser.add_argument('-loss', type=int, required=True, help='Loss')
    return parser.parse_args()

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

def print_startup_delay_and_res(startup_delay, startup_res):
    if startup_delay is not None:
        print(colored(f"\nStartup delay: {startup_delay} ms\n", 'green'))
        print(colored(f"Startup resolutions: {startup_res}\n", 'green'))

def print_total_waiting_time(total_times, index):
    print(colored(f"Total waiting time: {total_times[index]} ms\n", 'blue'))

def print_dataframe(timings, contributions, means, sums, deviations, index):
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

def print_avg_startup_delay(startup_delays):
    if startup_delays:
        avg_startup_delay = sum(startup_delays) / len(startup_delays)
        print(colored(f"\nAverage startup delay: {avg_startup_delay} ms\n", 'red'))

def parse_multiple_har_files(filenames):
    timings = ['blocked', 'connect', 'send', 'wait', 'receive', '_blocked_queueing']
    
    urls = []
    total_times = []
    contributions = []
    means = []
    sums = []
    deviations = []
    startup_delays = []

    for index, filename in enumerate(filenames):
        timing_data = {timing: [] for timing in timings}
        startup_time = None
        last_dash1_time = None
        startup_res = []

        with open(filename, 'r') as f:
            har_data = json.load(f)
        
        startup_time = datetime.strptime(har_data['log']['entries'][0]['startedDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')

        with Bar('Processing...', max=len(har_data['log']['entries'])) as bar:
            for entry in har_data['log']['entries']:
                url = entry['request']['url']
                if url.startswith('http://10.0.0.1:1337/bbb_sunflower_2160p_30fps_normal_'):
                    match = re.search(r'normal_(\d+)', url)
                    if match:
                        res = match.group(1) + 'p'
                        urls.append(res)
                        entry_timing_data = get_timing_data(entry, timings)
                        for timing in timings:
                            timing_data[timing].extend(entry_timing_data[timing])

                # if '.mpd' in url and startup_time is None:
                #     startup_time = datetime.strptime(entry['startedDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')

                if 'dash1.m4s' in url:
                    last_dash1_time = datetime.strptime(entry['startedDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    last_dash1_total_time = entry['time'] / 1000  # convert from ms to s
                    last_dash1_end_time = last_dash1_time + timedelta(seconds=last_dash1_total_time)
                    startup_res.append(res)

                bar.next()

        total_times.append(sum(sum(timing_data[timing]) for timing in timings))
        contributions.append({timing: sum(timing_data[timing]) / total_times[index] * 100 for timing in timings})
        means.append({timing: np.mean(timing_data[timing]) for timing in timings})
        sums.append({timing: sum(timing_data[timing]) for timing in timings})
        deviations.append({timing: np.std(timing_data[timing]) for timing in timings})

        startup_delay = get_startup_delay(startup_time, last_dash1_end_time)
        if startup_delay is not None:
            startup_delays.append(startup_delay)
        print_startup_delay_and_res(startup_delay,startup_res)
        print_total_waiting_time(total_times, index)
        print_dataframe(timings, contributions, means, sums, deviations, index)
    
    print_averages(timings, total_times, contributions, means, sums, deviations, filenames)
    print_avg_startup_delay(startup_delays)

def main():
    args = get_args()
    bw = args.bw
    delay = args.delay
    loss = args.loss

    number_of_runs = 3
    filenames = []
    for i in range(1, number_of_runs+1):
        filenames.append(f'statistics/mininet/{bw}_{delay}_{loss}/mininet_{bw}_{delay}_{loss}_{i}.har')

    parse_multiple_har_files(filenames)

if __name__ == "__main__":
    main()