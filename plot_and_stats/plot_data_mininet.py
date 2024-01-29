import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps

resolution_order = ['320x180', '480x270', '640x360',  '768x432', '960x540', '1024x576', '1280x720', '1920x1080', '2560x1440', '3840x2160']

def convert_to_seconds(timestr):
    m, s = map(int, timestr.split(':'))
    return m * 60 + s

def read_and_process_data(file_path):
    data = pd.read_csv(file_path)
    data['Time'] = data['Time'].apply(convert_to_seconds)
    return data

def plot_data(data, file_name, y_label=None, exclude_columns=None):
    colors = iter(colormaps.get_cmap('Set1')(np.arange(len(data.columns[1:]))))
    plt.figure()
    for column in data.columns[1:]:
        if exclude_columns and column in exclude_columns:
            continue
        plt.plot(data['Time'], data[column], label=column, color=next(colors))
    if y_label:
        plt.yticks(range(len(y_label)), y_label)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
    plt.savefig(file_name, dpi=300)

data = read_and_process_data('statistics/mininet/50_100_2/data_50_100_2_3.csv')
resolution_data = read_and_process_data('statistics//mininet/50_100_2/resolutionData_50_100_2_3.csv')
resolution_data['Resolution '] = resolution_data['Resolution'].apply(lambda x: resolution_order.index(x))
droppedFrames_data = read_and_process_data('statistics/mininet/50_100_2/droppedFrames_50_100_2_3.csv')

plot_data(data, 'statistics/mininet/mininet_data.png')
plot_data(resolution_data, 'statistics/mininet/mininet_resolution.png', resolution_order, ['Resolution'])
plot_data(droppedFrames_data, 'statistics/mininet/mininet_dropped_frames.png')

plt.show()