import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import json
from datetime import datetime
from matplotlib.widgets import Button

# Use the 'seaborn' style
sns.set_style("darkgrid")

# Define the order of the resolutions
resolution_order = ['320x180', '480x270', '640x360',  '768x432', '960x540', '1024x576', '1280x720', '1920x1080']

# Create a figure and a list to store the subplots
fig, axs_list = plt.subplots(2, 2, figsize=(15, 10))
plt.subplots_adjust(bottom=0.2)

# Create a list to store the bandwidth values
bandwidths = [3, 5, 10]

# Create a variable to store the current page index
current_page = 0

# Define a function to update the plots
def update_plots(page):
    # Clear the current plots
    for axs in axs_list.flat:
        axs.clear()

    # Get the bandwidth for the current page
    bandwidth = bandwidths[page]

    # Read the CSV files
    df1 = pd.read_csv(f"server/statistics/test_resolution_{bandwidth}MB.csv")
    df2 = pd.read_csv(f"server/statistics/test_download_{bandwidth}MB.csv")

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
    with open(f"server/statistics/stats_{bandwidth}MB.json", 'r') as f:
        lines = f.readlines()

    # Parse the JSON objects in the file
    stats = [json.loads(line) for line in lines]

    # Extract the times and resolutions, skipping entries with 'no_resolution'
    times_resolutions = [(datetime.strptime(stat['time'], '%M:%S'), stat['resolution']) for stat in stats if stat['resolution'] != 'no_resolution']

    # Separate the sorted times and resolutions into two lists
    times = [x[0] for x in times_resolutions]
    resolutions = [resolution_order.index(r[1]) for r in times_resolutions]

    

    # Adjust the spacing between the subplots
    plt.subplots_adjust(wspace=0.3, hspace=0.5)

    # Plot the first graph on the first subplot
    axs_list[0, 0].plot(df['Elapsed Time'], df['Download Rate'], color='blue')
    axs_list[0, 0].set(xlabel='Elapsed Time (s)', ylabel='Download Rate (Mbps)', title=f'Download Rate over Time for {bandwidth}MB')

    # Plot the second graph on the second subplot as a bar chart with smaller bars
    axs_list[0, 1].bar(df.index, df['Download Rate'], width=0.5, color='green')
    axs_list[0, 1].set_xticks(df.index)
    axs_list[0, 1].set_xticklabels(df['Resolution'], rotation=90)  # Rotate the x-axis labels
    axs_list[0, 1].set(xlabel='Resolution', ylabel='Download Rate (Mbps)', title=f'Download Rate over Resolution for {bandwidth}MB')

    # Plot the data in the first subplot
    axs_list[1, 0].plot(times, resolutions, marker='o', linestyle='-', color='b')
    axs_list[1, 0].set_yticks(range(len(resolution_order)))
    axs_list[1, 0].set_yticklabels(resolution_order)
    axs_list[1, 0].set_xlabel('Time', fontsize=14)
    axs_list[1, 0].set_ylabel('Resolution', fontsize=14)
    axs_list[1, 0].set_title(f'Resolution over time for {bandwidth}MB', fontsize=20)

    # Plot the data in the second subplot as a histogram
    axs_list[1, 1].hist(resolutions, bins=range(len(resolution_order)+1), color='g', edgecolor='black', align='left')
    axs_list[1, 1].set_xticks(range(len(resolution_order)))
    axs_list[1, 1].set_xticklabels(resolution_order, rotation=45)
    axs_list[1, 1].set_xlabel('Resolution', fontsize=14)
    axs_list[1, 1].set_ylabel('Frequency', fontsize=14)
    axs_list[1, 1].set_title(f'Resolution Frequency Distribution for {bandwidth}MB', fontsize=20)

    # Increase the font size of the labels and titles
    for ax in axs_list.flat:
        ax.title.set_size(20)
        ax.xaxis.label.set_size(15)
        ax.yaxis.label.set_size(15)

    # Display the figure with the subplots
    fig.canvas.draw()

# Define a function to go to the next page
def next_page(event):
    global current_page
    current_page = (current_page + 1) % len(bandwidths)
    update_plots(current_page)

# Define a function to go to the previous page
def prev_page(event):
    global current_page
    current_page = (current_page - 1) % len(bandwidths)
    update_plots(current_page)

# Create the 'Next' and 'Previous' buttons
next_button = Button(plt.axes([0.85, 0.01, 0.07, 0.05]), 'Next')  # Smaller and closer to the bottom right corner
next_button.on_clicked(next_page)
prev_button = Button(plt.axes([0.75, 0.01, 0.07, 0.05]), 'Previous')  # Smaller and closer to the bottom right corner
prev_button.on_clicked(prev_page)

# Display the first page of plots
update_plots(current_page)

# Start the event loop
plt.show()