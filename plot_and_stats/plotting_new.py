import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import Counter
from datetime import datetime

# Initialize lists for time, resolution, and resolution count
time = []
resolution = []
resolution_order = ['320x180', '480x270', '640x360',  '768x432', '960x540', '1024x576', '1280x720', '1920x1080', '2560x1440', '3840x2160']

# Open the file
# Open the file
with open('streaming_stats/stats_20240121_18:34:42.json', 'r') as f:
    for line in f:
        # Load each JSON object individually
        entry = json.loads(line)

        # Check if resolution is 'no_resolution'
        if entry['resolution'] != 'no_resolution':
            # Extract time and resolution data
            time.append(datetime.strptime(entry['time'], '%M:%S'))  # Include seconds when parsing time
            resolution.append(resolution_order.index(entry['resolution']))

# Count the occurrence of each resolution
resolution_counter = Counter(resolution)

# Modify resolution_order to use simplified format
resolution_order_simplified = [res.split('x')[-1] + 'p' for res in resolution_order]

# Plot resolution over time
plt.figure(figsize=(10, 5))
plt.plot(time, resolution)
plt.yticks(range(len(resolution_order_simplified)), resolution_order_simplified)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))  # Include seconds in the labels
plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30))  # Set interval to desired number of minutes
plt.gcf().autofmt_xdate()
plt.xlabel('Time')
plt.ylabel('Resolution')
plt.title('Resolution over Time')
plt.show()

# Initialize a list of zeros for the counts of each resolution
resolution_counts = [0] * len(resolution_order)

# Update the counts from resolution_counter
for res_index, count in resolution_counter.items():
    resolution_counts[res_index] = count

# Plot histogram of resolution counts
plt.figure(figsize=(10, 5))
plt.bar(resolution_order_simplified, resolution_counts)
plt.xlabel('Resolution')
plt.ylabel('Count')
plt.title('Histogram of Resolution Counts')
plt.show()