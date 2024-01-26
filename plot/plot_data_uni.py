import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps

resolution_order = ['320x180', '480x270', '640x360',  '768x432', '960x540', '1024x576', '1280x720', '1920x1080', '2560x1440', '3840x2160']

# Function to convert HH:MM format to seconds
def convert_to_seconds(timestr):
    m, s = map(int, timestr.split(':'))
    return m * 60 + s

# Read data from CSV file
data = pd.read_csv('statistics/uni/data_uni_2.csv')
data['Time'] = data['Time'].apply(convert_to_seconds)

resolution_data = pd.read_csv('statistics/uni/resolutionData_uni_2.csv')
resolution_data['Time'] = resolution_data['Time'].apply(convert_to_seconds)

droppedFrames_data = pd.read_csv('statistics/uni/droppedFrames_uni_2.csv')
droppedFrames_data['Time'] = droppedFrames_data['Time'].apply(convert_to_seconds)

# Convert 'Resolution' values to their indices in resolution_order
resolution_data['ResolutionIndex'] = resolution_data['Resolution'].apply(lambda x: resolution_order.index(x))


# Get the colormap and create an iterator for it
colors = iter(colormaps.get_cmap('Set1')(np.arange(len(data.columns[1:]))))

# Plot data
plt.figure()
for column in data.columns[1:]:
    plt.plot(data['Time'], data[column], label=column, color=next(colors))
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

# Plot resolution data
plt.figure()
plt.plot(resolution_data['Time'], resolution_data['ResolutionIndex'], label='Resolution')
plt.yticks(range(len(resolution_order)), resolution_order) # Set y-tick labels to resolution_order
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

# Plot dropped frames data
plt.figure()
plt.plot(droppedFrames_data['Time'], droppedFrames_data['Dropped Frames'], label='Dropped Frames')
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

plt.show()