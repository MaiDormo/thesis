import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import json
from datetime import datetime
from matplotlib.widgets import Button

sns.set_style("darkgrid")

resolution_order = ['320x180', '480x270', '640x360',  '768x432', '960x540', '1024x576', '1280x720', '1920x1080']
bandwidths = [3, 5, 10]
current_page = 0

fig, axs_list = plt.subplots(2, 2, figsize=(15, 10))
plt.subplots_adjust(bottom=0.2)

def clear_plots():
    for axs in axs_list.flat:
        axs.clear()

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
    plt.subplots_adjust(wspace=0.3, hspace=0.5)

    axs_list[0, 0].plot(df['Elapsed Time'], df['Download Rate'], color='blue')
    axs_list[0, 0].set(xlabel='Elapsed Time (s)', ylabel='Download Rate (Mbps)', title=f'Download Rate over Time for {bandwidth}MB')

    axs_list[0, 1].bar(df.index, df['Download Rate'], width=0.5, color='green')
    axs_list[0, 1].set_xticks(df.index)
    axs_list[0, 1].set_xticklabels(df['Resolution'], rotation=90)
    axs_list[0, 1].set(xlabel='Resolution', ylabel='Download Rate (Mbps)', title=f'Download Rate over Resolution for {bandwidth}MB')

    axs_list[1, 0].plot(times, resolutions, marker='o', linestyle='-', color='b')
    axs_list[1, 0].set_yticks(range(len(resolution_order)))
    axs_list[1, 0].set_yticklabels(resolution_order)
    axs_list[1, 0].set_xlabel('Time', fontsize=14)
    axs_list[1, 0].set_ylabel('Resolution', fontsize=14)
    axs_list[1, 0].set_title(f'Resolution over time for {bandwidth}MB', fontsize=20)

    axs_list[1, 1].hist(resolutions, bins=range(len(resolution_order)+1), color='g', edgecolor='black', align='left')
    axs_list[1, 1].set_xticks(range(len(resolution_order)))
    axs_list[1, 1].set_xticklabels(resolution_order, rotation=45)
    axs_list[1, 1].set_xlabel('Resolution', fontsize=14)
    axs_list[1, 1].set_ylabel('Frequency', fontsize=14)
    axs_list[1, 1].set_title(f'Resolution Frequency Distribution for {bandwidth}MB', fontsize=20)

    for ax in axs_list.flat:
        ax.title.set_size(20)
        ax.xaxis.label.set_size(15)
        ax.yaxis.label.set_size(15)

    fig.canvas.draw()

def update_plots(page):
    clear_plots()

    bandwidth = bandwidths[page]
    df = read_and_filter_data(bandwidth)
    times, resolutions = read_json_file(bandwidth)

    plot_graphs(df, times, resolutions, bandwidth)

def next_page(event):
    global current_page
    current_page = (current_page + 1) % len(bandwidths)
    update_plots(current_page)

def prev_page(event):
    global current_page
    current_page = (current_page - 1) % len(bandwidths)
    update_plots(current_page)

next_button = Button(plt.axes([0.85, 0.01, 0.07, 0.05]), 'Next')
next_button.on_clicked(next_page)
prev_button = Button(plt.axes([0.75, 0.01, 0.07, 0.05]), 'Previous')
prev_button.on_clicked(prev_page)

update_plots(current_page)

plt.show()