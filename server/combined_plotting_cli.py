import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import json
import argparse
from datetime import datetime

resolution_order = ['320x180', '480x270', '640x360',  '768x432', '960x540', '1024x576', '1280x720', '1920x1080']

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('Bandwidth', metavar='bandwidth', type=int, choices=[3, 5, 10])
    args = parser.parse_args()
    return args

def read_and_filter_data(bandwidth):
    df1 = pd.read_csv(f"server/statistics/test_resolution_{bandwidth}MB.csv")
    df2 = pd.read_csv(f"server/statistics/test_download_{bandwidth}MB.csv")

    df1 = df1[df1['Resolution'].notna() & (df1['Resolution'] != 'resolution=no_resolution')]
    df1['Resolution'] = df1['Resolution'].str.replace('resolution=', '')

    df2['Elapsed Time'] = df2['Rel Start'] - df2['Rel Start'].iloc[0]
    df2['Download Rate'] = df2['Bits/s B → A'] / 1024**2

    df1['Elapsed Time'] = df1['Time'] - df2['Rel Start'].iloc[0]

    df = pd.merge_asof(df1.sort_values('Elapsed Time'), df2.sort_values('Elapsed Time'), on='Elapsed Time')
    df = df.sort_values(['Elapsed Time', 'Resolution'])

    return df

def read_json_file(bandwidth):
    with open(f"server/statistics/stats_{bandwidth}MB.json", 'r') as f:
        lines = f.readlines()

    stats = [json.loads(line) for line in lines]
    times_resolutions = [(datetime.strptime(stat['time'], '%M:%S'), stat['resolution']) for stat in stats if stat['resolution'] != 'no_resolution']

    times = [x[0] for x in times_resolutions]
    resolutions = [resolution_order.index(r[1]) for r in times_resolutions]

    return times, resolutions

def plot_graphs(df, times, resolutions, bandwidth):
    sns.set_style("darkgrid")

    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    plt.subplots_adjust(wspace=0.3, hspace=0.5)

    axs[0, 0].plot(df['Elapsed Time'], df['Download Rate'], color='blue')
    axs[0, 0].set(xlabel='Elapsed Time (s)', ylabel='Download Rate (Mbps)', title=f'Download Rate over Time for {bandwidth}MB')

    axs[0, 1].bar(df.index, df['Download Rate'], width=0.5, color='green')
    axs[0, 1].set_xticks(df.index)
    axs[0, 1].set_xticklabels(df['Resolution'], rotation=90)
    axs[0, 1].set(xlabel='Resolution', ylabel='Download Rate (Mbps)', title=f'Download Rate over Resolution for {bandwidth}MB')

    axs[1, 0].plot(times, resolutions, marker='o', linestyle='-', color='b')
    axs[1, 0].set_yticks(range(len(resolution_order)))
    axs[1, 0].set_yticklabels(resolution_order)
    axs[1, 0].set_xlabel('Time', fontsize=14)
    axs[1, 0].set_ylabel('Resolution', fontsize=14)
    axs[1, 0].set_title('Resolution over time', fontsize=20)

    axs[1, 1].hist(resolutions, bins=range(len(resolution_order)+1), color='g', edgecolor='black', align='left')
    axs[1, 1].set_xticks(range(len(resolution_order)))
    axs[1, 1].set_xticklabels(resolution_order, rotation=45)
    axs[1, 1].set_xlabel('Resolution', fontsize=14)
    axs[1, 1].set_ylabel('Frequency', fontsize=14)
    axs[1, 1].set_title('Resolution Frequency Distribution', fontsize = 20)

    for ax in axs.flat:
        ax.title.set_size(20)
        ax.xaxis.label.set_size(15)
        ax.yaxis.label.set_size(15)

    return fig, axs

if __name__ == "__main__":
    args = parse_arguments()
    df = read_and_filter_data(args.Bandwidth)
    times, resolutions = read_json_file(args.Bandwidth)
    plot_graphs(df, times, resolutions, args.Bandwidth)
    plt.show()