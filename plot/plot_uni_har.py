import json
import matplotlib.pyplot as plt
import re
import numpy as np
import pandas as pd
from progress.bar import Bar

def parse_and_plot_har_file(filename):
    urls = []
    blocked_times = []
    connect_times = []
    send_times = []
    wait_times = []
    receive_times = []
    _blocked_queueing_times = []

    with open(filename, 'r') as f:
        har_data = json.load(f)

    with Bar('Processing...', max=len(har_data['log']['entries'])) as bar:
        for entry in har_data['log']['entries']:
            url = entry['request']['url']
            if url.startswith('http://10.203.0.207:1337/bbb_sunflower_2160p_30fps_normal_'):
                match = re.search(r'_(\d+)p', url)
                if match:
                    res = match.group(1) + 'p'
                    urls.append(res)

                    blocked = entry['timings'].get('blocked', 0)
                    blocked_times.append(max(0, blocked))

                    connect = entry['timings'].get('connect', 0)
                    connect_times.append(max(0, connect))

                    send = entry['timings'].get('send', 0)
                    send_times.append(max(0, send))

                    wait = entry['timings'].get('wait', 0)
                    wait_times.append(max(0, wait))

                    receive = entry['timings'].get('receive', 0)
                    receive_times.append(max(0, receive))

                    _blocked_queueing = entry['timings'].get('_blocked_queueing', 0)
                    _blocked_queueing_times.append(max(0, _blocked_queueing))

            bar.next()

    # Calculate total time
    total_time = sum(max(0, x) for x in blocked_times + connect_times + send_times + wait_times + receive_times + _blocked_queueing_times)

    # Check if total time is not less than 0
    if total_time < 0:
        print("Total time is less than 0")
    else:
        # Calculate contributions
        blocked_contrib = sum(max(0, x) for x in blocked_times) / total_time * 100
        connect_contrib = sum(max(0, x) for x in connect_times) / total_time * 100
        send_contrib = sum(max(0, x) for x in send_times) / total_time * 100
        wait_contrib = sum(max(0, x) for x in wait_times) / total_time * 100
        receive_contrib = sum(max(0, x) for x in receive_times) / total_time * 100
        _blocked_queueing_contrib = sum(max(0, x) for x in _blocked_queueing_times) / total_time * 100

        # Create a dictionary to hold the contributions
        contributions = {
            'Blocked Time': blocked_contrib,
            'Connect Time': connect_contrib,
            'Send Time': send_contrib,
            'Wait Time': wait_contrib,
            'Receive Time': receive_contrib,
            'Blocked Queueing Time': _blocked_queueing_contrib
        }

        # Create a DataFrame to display the contributions
        df = pd.DataFrame(list(contributions.items()), columns=['Category', 'Contribution'])
        print(df)

    plt.figure(figsize=(10, 6))

    width = 0.35
    ind = np.arange(len(urls))

    plt.bar(ind, blocked_times, width, label='Blocked Time')
    plt.bar(ind, connect_times, width, bottom=blocked_times, label='Connect Time')
    plt.bar(ind, send_times, width, bottom=[a+b for a, b in zip(blocked_times, connect_times)], label='Send Time')
    plt.bar(ind, wait_times, width, bottom=[a+b+c for a, b, c in zip(blocked_times, connect_times, send_times)], label='Wait Time')
    plt.bar(ind, receive_times, width, bottom=[a+b+c+d for a, b, c, d in zip(blocked_times, connect_times, send_times, wait_times)], label='Receive Time')
    plt.bar(ind, _blocked_queueing_times, width, bottom=[a+b+c+d+e for a, b, c, d, e in zip(blocked_times, connect_times, send_times, wait_times, receive_times)], label='Blocked Queueing Time')

    plt.xlabel('Resolution')
    plt.ylabel('Time (ms)')
    plt.title('Timing Information per Resolution')
    plt.xticks(ind, urls, rotation=45)
    plt.legend()

    plt.tight_layout()
    plt.show()



parse_and_plot_har_file('statistics/uni/uni.har')
