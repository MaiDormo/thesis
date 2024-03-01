import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps
import matplotlib as mpl

mpl.rcParams['font.size'] = 11

PARAMETERS = {
    'resolution_order': ['320x180', '480x270', '640x360',  '768x432', '940x540', '1024x576', '1280x720', '1920x1080', '2560x1440', '3840x2160'],
    'bw': 5,
    'delay': 100,
    'loss': 2,
    'number_of_runs': 3,
    'run': 2,
    'include_traffic': True, 
}

def convert_to_seconds(timestr):
    m, s = map(int, timestr.split(':'))
    return m * 60 + s

def read_and_process_data(file_path):
    data = pd.read_csv(file_path)
    data['Time'] = data['Time'].apply(convert_to_seconds)
    return data

def plot_data(data, file_name, y_label=None, exclude_columns=None, ax=None, label_suffix='', is_traffic=False, cmap=None, linestyle='-'):
    if ax is None:
        fig, ax = plt.subplots()
    cmap = cmap if cmap else ('hot' if is_traffic else 'cool')
    colors = iter(colormaps.get_cmap(cmap)(np.linspace(0, 1, len(data.columns[1:]))))
    lines = []
    for column in data.columns[1:]:
        if exclude_columns and column in exclude_columns:
            continue
        line, = ax.plot(data['Time'], data[column], label=column + label_suffix, color=next(colors), linestyle=linestyle)
        lines.append(line)
    if y_label:
        ax.set_yticks(np.arange(len(y_label)))
        ax.set_yticklabels(y_label)
    ax.axvline(x=60, color='grey', linestyle='--')  # Add vertical line at 60 seconds
    ax.axvline(x=240, color='grey', linestyle='--')  # Add vertical line at 240 seconds
    return lines

def main(params):
    fig, ax = plt.subplots(figsize=(12, 7))  # Set plot size
    data = read_and_process_data(f'statistics/mininet/{params["bw"]}_{params["delay"]}_{params["loss"]}/data_{params["bw"]}_{params["delay"]}_{params["loss"]}_{params["run"]}.csv')
    lines1 = plot_data(data, 'statistics/mininet/mininet_data.png', exclude_columns=['Effective Bitrate'], ax=ax, linestyle='-')

    if params['include_traffic']:
        data_traffic = read_and_process_data(f'statistics/mininet/traffic/{params["bw"]}_{params["delay"]}_{params["loss"]}/data_traffic_{params["bw"]}_{params["delay"]}_{params["loss"]}_{params["run"]}.csv')
        lines2 = plot_data(data_traffic, 'statistics/mininet/mininet_data.png', exclude_columns=['Effective Bitrate'], ax=ax, label_suffix=' (traffic)', is_traffic=True, linestyle='--')

        lines = lines1 + lines2
        labels = [line.get_label() for line in lines]
        line_dict = {label: line for line, label in zip(lines, labels)}
        unique_lines = list(line_dict.values())
        unique_labels = list(line_dict.keys())

        ax.legend(unique_lines, unique_labels, loc='upper center', bbox_to_anchor=(0.5, -0.035), fancybox=True, shadow=True, ncol=5)
        plt.subplots_adjust(bottom=0.15)  # Adjust the bottom padding
        
        plt.savefig(f'statistics/mininet/traffic_{params["bw"]}_{params["delay"]}_{params["loss"]}_data.png', dpi=300)
    else:
        lines = lines1
        labels = [line.get_label() for line in lines]
        line_dict = {label: line for line, label in zip(lines, labels)}
        unique_lines = list(line_dict.values())
        unique_labels = list(line_dict.keys())

        ax.legend(unique_lines, unique_labels, loc='upper center', bbox_to_anchor=(0.5, -0.035), fancybox=True, shadow=True, ncol=5)
        plt.subplots_adjust(bottom=0.15)  # Adjust the bottom padding
        plt.savefig(f'statistics/mininet/mininet_{params["bw"]}_{params["delay"]}_{params["loss"]}_data.png', dpi=300)

    fig, ax1 = plt.subplots(figsize=(12, 6))  # Set plot size

    resolution_data = read_and_process_data(f'statistics/mininet/{params["bw"]}_{params["delay"]}_{params["loss"]}/resolutionData_{params["bw"]}_{params["delay"]}_{params["loss"]}_{params["run"]}.csv')
    resolution_data['Resolution '] = resolution_data['Resolution'].apply(lambda x: params['resolution_order'].index(x))
    lines3 = plot_data(resolution_data, 'statistics/mininet/mininet_resolution.png', params['resolution_order'], ['Resolution'], ax=ax1, cmap='cool', linestyle='-')

    ax2 = ax1.twinx()  # Create a second y-axis that shares the same x-axis

    droppedFrames_data = read_and_process_data(f'statistics/mininet/{params["bw"]}_{params["delay"]}_{params["loss"]}/droppedFrames_{params["bw"]}_{params["delay"]}_{params["loss"]}_{params["run"]}.csv')
    lines4 = plot_data(droppedFrames_data, 'statistics/mininet/mininet_dropped_frames.png', ax=ax2, cmap='spring', linestyle='-.')

    

    if params['include_traffic']:
        resolution_data_traffic = read_and_process_data(f'statistics/mininet/traffic/{params["bw"]}_{params["delay"]}_{params["loss"]}/resolutionData_traffic_{params["bw"]}_{params["delay"]}_{params["loss"]}_{params["run"]}.csv')
        resolution_data_traffic['Resolution '] = resolution_data_traffic['Resolution'].apply(lambda x: params['resolution_order'].index(x))
        lines5 = plot_data(resolution_data_traffic, 'statistics/mininet/mininet_resolution.png', params['resolution_order'], ['Resolution'], ax=ax1, label_suffix=' (traffic)', is_traffic=True, cmap='coolwarm', linestyle='--')

        droppedFrames_data_traffic = read_and_process_data(f'statistics/mininet/traffic/{params["bw"]}_{params["delay"]}_{params["loss"]}/droppedFrames_traffic_{params["bw"]}_{params["delay"]}_{params["loss"]}_{params["run"]}.csv')
        lines6 = plot_data(droppedFrames_data_traffic, 'statistics/mininet/mininet_dropped_frames.png', ax=ax2, label_suffix=' (traffic)', is_traffic=True, cmap='summer', linestyle=':')

        # Create a dictionary that maps labels to lines
        lines = lines3 + lines4 + lines5 + lines6
        labels = [line.get_label() for line in lines]
        line_dict = {label: line for line, label in zip(lines, labels)}
        ax2.legend(unique_lines, unique_labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
        plt.subplots_adjust(bottom=0.15)  # Adjust the bottom padding
        plt.savefig(f'statistics/mininet/traffic_{params["bw"]}_{params["delay"]}_{params["loss"]}_rest.png', dpi=300)
    
    else:
         # Create a dictionary that maps labels to lines
        lines = lines3 + lines4
        labels = [line.get_label() for line in lines]
        line_dict = {label: line for line, label in zip(lines, labels)}
        ax2.legend(unique_lines, unique_labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
        plt.subplots_adjust(bottom=0.15)  # Adjust the bottom padding
        plt.savefig(f'statistics/mininet/mininet_{params["bw"]}_{params["delay"]}_{params["loss"]}_rest.png', dpi=300)

    

    plt.show()

if __name__ == "__main__":
    main(PARAMETERS)