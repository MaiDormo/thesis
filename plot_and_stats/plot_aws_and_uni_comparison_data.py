import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps
import matplotlib as mpl

# Set global font size
mpl.rcParams['font.size'] = 11

PARAMETERS = {
    'resolution_order': ['320x180', '480x270', '640x360',  '768x432', '940x540', '1024x576', '1280x720', '1920x1080', '2560x1440', '3840x2160'],
    'number_of_runs': 3,
    'run': 2,
    'aws': 'aws',
    'uni': 'uni',
}

def convert_to_seconds(timestr):
    m, s = map(int, timestr.split(':'))
    return m * 60 + s

def read_and_process_data(file_path):
    data = pd.read_csv(file_path)
    data['Time'] = data['Time'].apply(convert_to_seconds)
    return data

def plot_data(data, file_name, y_label=None, exclude_columns=None, ax=None, label_suffix='', is_traffic=False, cmap=None, linestyle='-', save=True):
    if ax is None:
        fig, ax = plt.subplots()
    cmap = cmap if cmap else ('hot' if is_traffic else 'cool')
    colors = iter(colormaps.get_cmap(cmap)(np.linspace(0, 1, len(data.columns[1:]))))
    lines = []
    for column in data.columns[1:]:
        if exclude_columns and column in exclude_columns:
            continue
        # Use y_label transformation if y_label is not None, else use original data
        y_data = data[column].map(lambda x: y_label.index(x) if y_label and x in y_label else x) if y_label else data[column]
        line, = ax.plot(data['Time'], y_data, label=column + label_suffix, color=next(colors), linestyle=linestyle)
        lines.append(line)
    if y_label:
        ax.set_yticks(np.arange(len(y_label)))
        ax.set_yticklabels(y_label)
    ax.axvline(x=60, color='grey', linestyle='--')  # Add vertical line at 60 seconds
    ax.axvline(x=240, color='grey', linestyle='--')  # Add vertical line at 240 seconds
    if save:
        plt.savefig(file_name, dpi=300)
    return lines

def process_and_plot_data(params, data_type, data_used, y_label=None, exclude_columns=None, ax=None, label_suffix='', is_traffic=False, cmap=None, linestyle='-', save=True):
    data = read_and_process_data(f'statistics/{params[data_type]}/{data_used}_{data_type}_{params["run"]}.csv')
    return plot_data(data, f'statistics/{params[data_type]}/{data_type}_{data_used}_{params["run"]}.png', y_label=y_label, exclude_columns=exclude_columns, ax=ax, label_suffix=f' ({data_type})', is_traffic=is_traffic, linestyle=linestyle, save=save)

def main(params):
    fig, ax = plt.subplots(figsize=(12,7))
    process_and_plot_data(params, 'aws', 'data', exclude_columns=['Effective Bitrate'], ax=ax, linestyle='-', save=False)
    process_and_plot_data(params, 'uni', 'data', exclude_columns=['Effective Bitrate'], ax=ax, is_traffic=True, linestyle='--', save=False)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.035), fancybox=True, shadow=True, ncol=5)
    plt.subplots_adjust(bottom=0.15)  # Adjust the top padding
    plt.savefig(f'statistics/data_comparison_{params["run"]}.png', dpi=300)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot resolution data
    line_aws_resolutionData = process_and_plot_data(params, 'aws', 'resolutionData', y_label=params['resolution_order'], ax=ax1, cmap='cool', linestyle='-', save=False)
    line_uni_resolutionData = process_and_plot_data(params, 'uni', 'resolutionData', y_label=params['resolution_order'], ax=ax1, is_traffic=True, cmap='coolwarm', linestyle='--', save=False)

    # Create a second y-axis that shares the same x-axis
    ax2 = ax1.twinx()

    # Plot dropped frames data with a different colormap
    line_aws_droppedFrames = process_and_plot_data(params, 'aws', 'droppedFrames', ax=ax2, cmap='spring', linestyle='-.', save=False)
    lines_uni_droppedFrames = process_and_plot_data(params, 'uni', 'droppedFrames', ax=ax2, is_traffic=True, cmap='summer', linestyle=':', save=False)

    # Create a dictionary that maps labels to lines
    lines = line_aws_resolutionData + line_uni_resolutionData + line_aws_droppedFrames + lines_uni_droppedFrames
    labels = [line.get_label() for line in lines]
    line_dict = {label: line for line, label in zip(lines, labels)}

    # Create lists of unique lines and labels
    unique_lines = list(line_dict.values())
    unique_labels = list(line_dict.keys())

    ax2.legend(unique_lines, unique_labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.savefig(f'statistics/resolution_droppedFrames_comparison_{params["run"]}.png', dpi=300)

    plt.show()

if __name__ == "__main__":
    main(PARAMETERS)