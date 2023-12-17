import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import json
import argparse
from datetime import datetime


# Create the parser
parser = argparse.ArgumentParser(description='Choose a value for the bandwidth')

# Add the arguments
parser.add_argument('Bandwidth', metavar='bandwidth', type=int, choices=[3, 5, 10],
                    help='an integer for the bandwidth (Mbps) (3, 5, 10)')

# Execute the parse_args() method
args = parser.parse_args()

# Use the 'seaborn' style
sns.set_style("darkgrid")

# Read the CSV files
df1 = pd.read_csv(f"server/statistics/test_resolution_{args.Bandwidth}MB.csv")
df2 = pd.read_csv(f"server/statistics/test_download_{args.Bandwidth}MB.csv")

# Filter the data
df1 = df1[df1['Resolution'].notna() & (df1['Resolution'] != 'resolution=no_resolution')]

# Remove 'resolution=' from the 'Resolution' column values
df1['Resolution'] = df1['Resolution'].str.replace('resolution=', '')

# Calculate the elapsed time for the first row
df2['Elapsed Time'] = df2['Rel Start'] - df2['Rel Start'].iloc[0]

# Calculate the download rate in Mbps
df2['Download Rate'] = df2['Bits/s B → A'] / 1024**2

# Calculate the elapsed time for df1
df1['Elapsed Time'] = df1['Time'] - df2['Rel Start'].iloc[0]

# Merge df1 and df2 on the 'Elapsed Time' column
df = pd.merge_asof(df1.sort_values('Elapsed Time'), df2.sort_values('Elapsed Time'), on='Elapsed Time')

# Sort the merged dataframe by 'Elapsed Time' and 'Resolution Order'
df = df.sort_values(['Elapsed Time', 'Resolution'])

# Open the JSON file
with open(f"server/statistics/stats_{args.Bandwidth}MB.json", 'r') as f:
    lines = f.readlines()

# Parse the JSON objects in the file
stats = [json.loads(line) for line in lines]

# Define the order of the resolutions
resolution_order = ['320x180', '480x270', '640x360',  '768x432', '960x540', '1024x576', '1280x720', '1920x1080']

# Extract the times and resolutions, skipping entries with 'no_resolution'
times_resolutions = [(datetime.strptime(stat['time'], '%M:%S'), stat['resolution']) for stat in stats if stat['resolution'] != 'no_resolution']

# Separate the sorted times and resolutions into two lists
times = [x[0] for x in times_resolutions]
resolutions = [resolution_order.index(r[1]) for r in times_resolutions]

# Create a figure with two subplots
fig, axs = plt.subplots(2, 2, figsize=(15, 10))

# Adjust the spacing between the subplots
plt.subplots_adjust(wspace=0.3, hspace=0.5)

# Plot the first graph on the first subplot
axs[0, 0].plot(df['Elapsed Time'], df['Download Rate'], color='blue')
axs[0, 0].set(xlabel='Elapsed Time (s)', ylabel='Download Rate (Mbps)', title='Download Rate over Time')

# Plot the second graph on the second subplot as a bar chart with smaller bars
axs[0, 1].bar(df.index, df['Download Rate'], width=0.5, color='green')
axs[0, 1].set_xticks(df.index)
axs[0, 1].set_xticklabels(df['Resolution'], rotation=90)
axs[0, 1].set(xlabel='Resolution', ylabel='Download Rate (Mbps)', title='Download Rate over Resolution')

# Plot the data in the first subplot
axs[1, 0].plot(times, resolutions, marker='o', linestyle='-', color='b')
axs[1, 0].set_yticks(range(len(resolution_order)))
axs[1, 0].set_yticklabels(resolution_order)
axs[1, 0].set_xlabel('Time', fontsize=14)
axs[1, 0].set_ylabel('Resolution', fontsize=14)
axs[1, 0].set_title('Resolution over time', fontsize=20)

# Plot the data in the second subplot as a histogram
axs[1, 1].hist(resolutions, bins=range(len(resolution_order)+1), color='g', edgecolor='black', align='left')
axs[1, 1].set_xticks(range(len(resolution_order)))
axs[1, 1].set_xticklabels(resolution_order, rotation=45)
axs[1, 1].set_xlabel('Resolution', fontsize=14)
axs[1, 1].set_ylabel('Frequency', fontsize=14)
axs[1, 1].set_title('Resolution Frequency Distribution', fontsize=20)

# Increase the font size of the labels and titles
for ax in axs.flat:
    ax.title.set_size(20)
    ax.xaxis.label.set_size(15)
    ax.yaxis.label.set_size(15)

# Display the figure with the subplots
plt.show()