#Note: This script is not currently being used in the project.
#TODO: add this script to the project with the correct changes, in order to utilize the data from csv file

from datetime import datetime
import matplotlib.pyplot as plt
import json

# Open the JSON file
with open('streaming_stats/stats_20240124_14:31:30.json', 'r') as f:
    lines = f.readlines()

# Parse the JSON objects in the file
stats = [json.loads(line) for line in lines]

# Define the order of the resolutions
resolution_order = ['320x180', '480x270', '640x360',  '768x432', '960x540', '1024x576', '1280x720', '1920x1080', '2560x1440', '3840x2160']

# Extract the times and resolutions, skipping entries with 'no_resolution'
times_resolutions = [(datetime.strptime(stat['time'], '%M:%S'), stat['resolution']) for stat in stats if stat['resolution'] != 'no_resolution']

# Separate the sorted times and resolutions into two lists
times = [x[0] for x in times_resolutions]
resolutions = [resolution_order.index(r[1]) for r in times_resolutions]

# Create a figure and a set of subplots
fig, axs = plt.subplots(2)

# Plot the data in the first subplot
axs[0].plot(times, resolutions, marker='o', linestyle='-', color='b')
axs[0].set_yticks(range(len(resolution_order)))
axs[0].set_yticklabels(resolution_order)
axs[0].set_xlabel('Time', fontsize=14)
axs[0].set_ylabel('Resolution', fontsize=14)
axs[0].set_title('Resolution over time', fontsize=20)
axs[0].grid(True)

# Plot the data in the second subplot as a histogram
axs[1].hist(resolutions, bins=range(len(resolution_order)+1), color='g', edgecolor='black', align='left')
axs[1].set_xticks(range(len(resolution_order)))
axs[1].set_xticklabels(resolution_order, rotation=45)
axs[1].set_xlabel('Resolution', fontsize=14)
axs[1].set_ylabel('Frequency', fontsize=14)
axs[1].set_title('Resolution Frequency Distribution', fontsize=20)
axs[1].grid(True)

# Adjust the space between the subplots
plt.tight_layout()

# Show the plot
plt.show()