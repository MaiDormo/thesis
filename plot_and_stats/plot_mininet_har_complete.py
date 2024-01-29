import json
import re
import numpy as np
import pandas as pd
from progress.bar import Bar

def parse_multiple_har_files(filenames):
    timings = ['blocked', 'connect', 'send', 'wait', 'receive', '_blocked_queueing']
    timing_data = {timing: [] for timing in timings}
    urls = []
    total_times = []
    contributions = []
    means = []
    sums = []
    deviations = []

    for index, filename in enumerate(filenames):
        with open(filename, 'r') as f:
            har_data = json.load(f)

        with Bar('Processing...', max=len(har_data['log']['entries'])) as bar:
            for entry in har_data['log']['entries']:
                url = entry['request']['url']
                if url.startswith('http://10.0.0.1:1337/bbb_sunflower_2160p_30fps_normal_'):
                    match = re.search(r'_(\d+)p', url)
                    if match:
                        res = match.group(1) + 'p'
                        urls.append(res)
                        for timing in timings:
                            time = entry['timings'].get(timing, 0)
                            timing_data[timing].append(max(0, time if time != -1 else 0))
                bar.next()

        total_times.append(sum(sum(timing_data[timing]) for timing in timings))
        contributions.append({timing: sum(timing_data[timing]) / total_times[index] * 100 for timing in timings})
        means.append({timing: np.mean(timing_data[timing]) for timing in timings})
        sums.append({timing: sum(timing_data[timing]) for timing in timings})
        deviations.append({timing: np.std(timing_data[timing]) for timing in timings})

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
    
    #now make the avg of all the data
    print("Averages:")
    print(f"Total Waiting Time: {sum(total_times)/len(filenames)/1000/60} seconds")
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


bw = 50
delay = 100
loss = 0
number_of_runs = 3
filenames = []
for i in range(1, number_of_runs+1):
    filenames.append(f'statistics/mininet/{bw}_{delay}_{loss}/mininet_{bw}_{delay}_{loss}_{i}.har')

parse_multiple_har_files(filenames)

