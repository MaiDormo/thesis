import json
import matplotlib.pyplot as plt
import re
import numpy as np
import pandas as pd
from progress.bar import Bar

def parse_and_plot_har_file(filename):
    timings = ['blocked', 'connect', 'send', 'wait', 'receive', '_blocked_queueing']
    timing_data = {timing: [] for timing in timings}
    urls = []

    with open(filename, 'r') as f:
        har_data = json.load(f)

    with Bar('Processing...', max=len(har_data['log']['entries'])) as bar:
        for entry in har_data['log']['entries']:
            url = entry['request']['url']
            if url.startswith('http://localhost:1337/bbb_sunflower_2160p_30fps_normal_'):
                match = re.search(r'_(\d+)p', url)
                if match:
                    res = match.group(1) + 'p'
                    urls.append(res)
                    for timing in timings:
                        time = entry['timings'].get(timing, 0)
                        timing_data[timing].append(max(0, time if time != -1 else 0))
            bar.next()

    total_time = sum(sum(timing_data[timing]) for timing in timings)


    contributions = {timing: sum(timing_data[timing]) / total_time * 100 for timing in timings}
    means = {timing: np.mean(timing_data[timing]) for timing in timings}
    sums = {timing: sum(timing_data[timing]) for timing in timings}
    deviation = {timing: np.std(timing_data[timing]) for timing in timings}

    df = pd.DataFrame([
        {
            'Category': timing, 
            'Contribution': contributions[timing], 
            'Mean': means[timing], 
            'Deviation': deviation[timing], 
            'Sum': sums[timing]
        } for timing in timings
    ])

    print(df)

    plt.figure(figsize=(15, 6))

    width = 0.5
    ind = np.arange(len(timing_data['blocked']))

    cum_bottom = np.zeros(len(timing_data['blocked']))
    for timing in timings:
        plt.bar(ind, timing_data[timing], width, bottom=cum_bottom, label=f'{timing.capitalize()} Time')
        cum_bottom += timing_data[timing]

    plt.xlabel('Resolution')
    plt.ylabel('Time (ms)')
    plt.title('Timing Information per Resolution')
    plt.xticks(ind, urls, rotation=45)
    plt.legend()

    plt.tight_layout()
    plt.savefig('statistics/aws/aws.png', dpi=300)
    plt.show()

parse_and_plot_har_file('statistics/aws/aws.har')