import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps

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

def plot_data(data, file_name, y_label=None, exclude_columns=None, ax=None, label_suffix='', is_traffic=False, cmap=None, linestyle='-'):
    if ax is None:
        fig, ax = plt.subplots()
    cmap = cmap if cmap else ('hot' if is_traffic else 'cool')
    colors = iter(colormaps.get_cmap(cmap)(np.linspace(0, 1, len(data.columns[1:]))))
    for column in data.columns[1:]:
        if exclude_columns and column in exclude_columns:
            continue
        ax.plot(data['Time'], data[column], label=column + label_suffix, color=next(colors), linestyle=linestyle)
    if y_label:
        ax.set_yticks(range(len(y_label)), y_label)
    ax.axvline(x=60, color='grey', linestyle='--')  # Add vertical line at 60 seconds
    ax.axvline(x=240, color='grey', linestyle='--')  # Add vertical line at 240 seconds
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.savefig(file_name, dpi=300)

def main(params):
    data = read_and_process_data(f'statistics/{params["aws"]}/data_{params["aws"]}_{params["run"]}.csv')
    resolution_data = read_and_process_data(f'statistics/{params["aws"]}/resolutionData_{params["aws"]}_{params["run"]}.csv')
    resolution_data['Resolution '] = resolution_data['Resolution'].apply(lambda x: params['resolution_order'].index(x))
    droppedFrames_data = read_and_process_data(f'statistics/{params["aws"]}/droppedFrames_{params["aws"]}_{params["run"]}.csv')

    data_traffic = read_and_process_data(f'statistics/{params["uni"]}/data_{params["uni"]}_{params["run"]}.csv')
    resolution_data_traffic = read_and_process_data(f'statistics/{params["uni"]}/resolutionData_{params["uni"]}_{params["run"]}.csv')
    resolution_data_traffic['Resolution '] = resolution_data_traffic['Resolution'].apply(lambda x: params['resolution_order'].index(x))
    droppedFrames_data_traffic = read_and_process_data(f'statistics/{params["uni"]}/droppedFrames_{params["uni"]}_{params["run"]}.csv')

    fig, ax = plt.subplots()
    plot_data(data, f'statistics/{params["aws"]}/data_{params["aws"]}.png', exclude_columns=['Effective Bitrate'], ax=ax, label_suffix=' (aws)', linestyle='-')
    plot_data(data_traffic, f'statistics/{params["uni"]}/data_{params["uni"]}.png', exclude_columns=['Effective Bitrate'], ax=ax, label_suffix=' (uni)', is_traffic=True, linestyle='--')

    fig, ax1 = plt.subplots()

    # Plot resolution data
    plot_data(resolution_data, f'statistics/{params["aws"]}/resolution_{params["aws"]}.png', params['resolution_order'], ['Resolution'], ax=ax1, label_suffix=' (aws)', cmap='cool', linestyle='-')
    plot_data(resolution_data_traffic, f'statistics/{params["uni"]}/resolution_{params["uni"]}.png', params['resolution_order'], ['Resolution'], ax=ax1, label_suffix=' (uni)', is_traffic=True, cmap='coolwarm', linestyle='--')

    # Create a second y-axis that shares the same x-axis
    ax2 = ax1.twinx()

    # Plot dropped frames data with a different colormap
    plot_data(droppedFrames_data, f'statistics/{params["aws"]}/dropped_frames_{params["aws"]}.png', ax=ax2, label_suffix=' (aws)', cmap='spring', linestyle='-.')
    plot_data(droppedFrames_data_traffic, f'statistics/{params["uni"]}/dropped_frames_{params["uni"]}s.png', ax=ax2, label_suffix=' (uni)', is_traffic=True, cmap='summer', linestyle=':')

    # Gather all lines and labels from both Axes objects
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

    plt.show()

if __name__ == "__main__":
    main(PARAMETERS)