import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from statistics_complete_data_mininet import parse_multiple_data_files_and_give_statistic

# Define the bandwidth, delay, loss, and number of runs
bandwidths = [3, 5, 10, 20, 50]
delays = [20, 100]
losses = [0, 2]
number_of_runs = 3


def calculate_statistics(bw, delay, loss, number_of_runs):
    result = parse_multiple_data_files_and_give_statistic(bw, delay, loss, number_of_runs)
    return {
        'Bandwidth': bw,
        'Delay': delay,
        'Loss': loss,
        'Download Rate': result['avg_all_runs_avg_data']['Download Rate'],
        'Avg Bandwith Utilization %': result['avg_bandwidth_utilization_for_each_run'],
        'Download Rate Std': result['std_all_runs_avg_data']['Download Rate'],
        'Std Bandwith Utilization %': result['std_bandwidth_utilization_for_each_run'],
        'Buffer Length': result['avg_all_runs_avg_data']['Buffer Length'],
        'Buffer Length Std': result['std_all_runs_avg_data']['Buffer Length'],
        'Avg Dropped Frames': result['avg_all_runs_avg_data']['Dropped Frames'],
        'Avg Dropped Frames %': result['avg_droppedFrames_percentage_for_each_run'],
        'Std Dropped Frames': result['std_all_runs_avg_data']['Dropped Frames'],
        'Std Dropped Frames %': result['std_droppedFrames_percentage_for_each_run'],
        'Avg Resolution Changes': result['std_resolution_changes_for_each_run'],
        'Std Resolution Changes': result['std_resolution_changes_for_each_run'],
        'Avg Rebuffering Events': result['avg_rebuffering_events_for_each_run'],
        'Std Rebuffering Events': result['std_rebuffering_events_for_each_run'],

    }



def run_statistics_for_combinations(bandwidths, delays, losses, number_of_runs):
    all_results = [calculate_statistics(bw, delay, loss, number_of_runs)
                   for bw in bandwidths
                   for delay in delays
                   for loss in losses]

    df_rate_buffer = pd.DataFrame([result for result in all_results if result])
    df_dropped_frames = pd.DataFrame([result for result in all_results if result])
    df_dropped_frames_buffer = pd.DataFrame([result for result in all_results if result])
    df_dropped_frames_rate = pd.DataFrame([result for result in all_results if result])
    df_dropped_frames_percentage_resolution_changes = pd.DataFrame([result for result in all_results if result])
    df_rebuffering_events = pd.DataFrame([result for result in all_results if result])

    # Compute correlations
    correlation_download_rate_buffer = df_rate_buffer['Download Rate'].corr(df_rate_buffer['Buffer Length'])
    correlation_avg_dropped_frames_buffer = df_dropped_frames_buffer['Avg Dropped Frames'].corr(df_dropped_frames_buffer['Buffer Length'])
    correlation_avg_dropped_frames_rate = df_dropped_frames_rate['Avg Dropped Frames'].corr(df_dropped_frames_rate['Download Rate'])
    correlation_avg_dropped_frames_resolution_changes = df_dropped_frames_percentage_resolution_changes['Avg Dropped Frames %'].corr(df_dropped_frames_percentage_resolution_changes['Avg Resolution Changes'])

    print(f"Correlation between 'Download Rate' and 'Buffer Length': {correlation_download_rate_buffer}")
    print(f"Correlation between 'Avg Dropped Frames' and 'Buffer Length': {correlation_avg_dropped_frames_buffer}")
    print(f"Correlation between 'Avg Dropped Frames' and 'Download Rate': {correlation_avg_dropped_frames_rate}")
    print(f"Correlation between 'Avg Dropped Frames' and 'Resolution Changes': {correlation_avg_dropped_frames_resolution_changes}")

    # print(df_rebuffering_events)

    return df_rate_buffer, df_dropped_frames, df_dropped_frames_buffer, df_dropped_frames_rate, df_dropped_frames_percentage_resolution_changes, df_rebuffering_events

# Call the function with the defined parameters
df_rate_buffer, df_dropped_frames, df_dropped_frames_buffer, df_dropped_frames_rate, df_dropped_frames_percentage_resolution_changes, df_rebuffering_events  = run_statistics_for_combinations(bandwidths, delays, losses, number_of_runs)

# Sort the DataFrames
df_dropped_frames = df_dropped_frames.sort_values(by=['Avg Dropped Frames', 'Std Dropped Frames'])
df_rate_buffer = df_rate_buffer.sort_values(by=['Download Rate', 'Buffer Length'])
df_dropped_frames_buffer = df_dropped_frames_buffer.sort_values(by=['Buffer Length', 'Avg Dropped Frames'])
df_dropped_frames_rate = df_dropped_frames_rate.sort_values(by=['Download Rate', 'Avg Dropped Frames'])

# Create a scatter plot with error bars for the standard deviation
plt.figure(figsize=(10, 6))

# Use seaborn to create a scatter plot with color coding based on the combination of delay, loss, and bandwidth
sns.scatterplot(data=df_rate_buffer, x='Buffer Length', y='Download Rate', hue='Bandwidth', style='Loss', size='Delay', sizes=(50, 200), palette='deep')

plt.xlabel('Buffer Length')
plt.ylabel('Download Rate')
plt.title('Download Rate vs Buffer Length')
plt.grid(True)
plt.show()

# Create a scatter plot with error bars for the standard deviation
plt.figure(figsize=(10, 6))

# Use seaborn to create a scatter plot with color coding based on the combination of delay, loss, and bandwidth
sns.scatterplot(data=df_rate_buffer, x='Buffer Length', y='Avg Bandwith Utilization %', hue='Bandwidth', style='Loss', size='Delay', sizes=(50, 200), palette='deep')

plt.xlabel('Buffer Length')
plt.ylabel('Avg Bandwith Utilization %')
plt.title('Avg Bandwith Utilization % vs Buffer Length')
plt.grid(True)
plt.show()

# Create a scatter plot for 'Dropped Frames' vs 'Buffer Length'
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_dropped_frames_buffer, x='Buffer Length', y='Avg Dropped Frames', hue='Bandwidth', style='Loss', size='Delay', sizes=(50, 200), palette='deep')

plt.xlabel('Buffer Length')
plt.ylabel('Avg Dropped Frames')
plt.title('Avg Dropped Frames vs Buffer Length')
plt.grid(True)
plt.show()

# Create a scatter plot for 'Dropped Frames' vs 'Download Rate'
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_dropped_frames_rate, x='Download Rate', y='Avg Dropped Frames', hue='Bandwidth', style='Loss', size='Delay', sizes=(50, 200), palette='deep')

plt.xlabel('Download Rate')
plt.ylabel('Avg Dropped Frames')
plt.title('Avg Dropped Frames vs Download Rate')
plt.grid(True)
plt.show()

# Define the custom x-axis labels
x_labels = ['low delay no loss', 'high delay no loss', 'low delay high loss', 'high delay high loss']

# Create a new DataFrame for the heatmap
heatmap_data = pd.DataFrame(columns=x_labels, index=bandwidths)

heatmap_std = pd.DataFrame(columns=x_labels, index=bandwidths)

# Fill the DataFrame with the average dropped frames for each combination
for bw in bandwidths:
    for label, (delay, loss) in zip(x_labels, [(20, 0), (100, 0), (20, 2), (100, 2)]):
        # Filter the data for the current combination
        filtered_data = df_dropped_frames[(df_dropped_frames['Bandwidth'] == bw) & (df_dropped_frames['Delay'] == delay) & (df_dropped_frames['Loss'] == loss)]
        # Compute the average dropped frames for the current combination
        avg_dropped_frames = filtered_data['Avg Dropped Frames'].mean()
        # Compute the standard deviation for the average dropped frames
        std_dropped_frames = filtered_data['Std Dropped Frames'].mean()
        # Add the average dropped frames to the heatmap data
        heatmap_data.loc[bw, label] = avg_dropped_frames
        # Add the standard deviation to the heatmap data
        heatmap_std.loc[bw, label] = std_dropped_frames

# Convert the data to numeric type and fill NaN values with 0
heatmap_data = heatmap_data.apply(pd.to_numeric, errors='coerce').fillna(0)
heatmap_std = heatmap_std.apply(pd.to_numeric, errors='coerce').fillna(0)

# Round the data to two decimal places
heatmap_data = heatmap_data.round(2)
heatmap_std = heatmap_std.round(2)

# Convert the data to strings and add parentheses around the standard deviation
heatmap_labels = heatmap_data.astype(str).apply(lambda x: x.apply(lambda y: "{:.2f}".format(float(y)))) + " (± " + heatmap_std.astype(str).apply(lambda x: x.apply(lambda y: "{:.2f}".format(float(y)))) + ")"


# Create the heatmap
plt.figure(figsize=(10, 8))
ax = sns.heatmap(heatmap_data, annot=heatmap_labels.values, fmt="", cmap='YlGnBu')
ax.invert_yaxis()
plt.title('Average Dropped Frames (± Standard Deviation) for each combination')
plt.xlabel('Network Conditions')
plt.ylabel('Bandwidth')
plt.show()

# Define the custom x-axis labels
x_labels = ['low delay no loss', 'high delay no loss', 'low delay high loss', 'high delay high loss']

# Create a new DataFrame for the heatmap
heatmap_data_percentage = pd.DataFrame(columns=x_labels, index=bandwidths)
heatmap_std_percentage = pd.DataFrame(columns=x_labels, index=bandwidths)

# Fill the DataFrame with the average dropped frames for each combination
for bw in bandwidths:
    for label, (delay, loss) in zip(x_labels, [(20, 0), (100, 0), (20, 2), (100, 2)]):
        # Filter the data for the current combination
        filtered_data = df_dropped_frames[(df_dropped_frames['Bandwidth'] == bw) & (df_dropped_frames['Delay'] == delay) & (df_dropped_frames['Loss'] == loss)]
        # Compute the average dropped frames for the current combination
        avg_dropped_frames_percentage = filtered_data['Avg Dropped Frames %'].mean()
        # Compute the standard deviation for the average dropped frames
        std_dropped_frames_percentage = filtered_data['Std Dropped Frames %'].mean()
        # Add the average dropped frames to the heatmap data
        heatmap_data_percentage.loc[bw, label] = avg_dropped_frames_percentage
        # Add the standard deviation to the heatmap data
        heatmap_std_percentage.loc[bw, label] = std_dropped_frames_percentage

# Convert the data to numeric type and fill NaN values with 0
heatmap_data_percentage = heatmap_data_percentage.apply(pd.to_numeric, errors='coerce').fillna(0)
heatmap_std_percentage = heatmap_std_percentage.apply(pd.to_numeric, errors='coerce').fillna(0)

# Round the data to two decimal places
heatmap_data_percentage = heatmap_data_percentage.round(2)
heatmap_std_percentage = heatmap_std_percentage.round(2)

# Convert the data to strings and add parentheses around the standard deviation
heatmap_labels_percentage = heatmap_data_percentage.astype(str).apply(lambda x: x.apply(lambda y: "{:.2f}%".format(float(y)))) + " (± " + heatmap_std_percentage.astype(str).apply(lambda x: x.apply(lambda y: "{:.2f}%".format(float(y)))) + ")"

# Create the heatmap
plt.figure(figsize=(10, 8))
ax = sns.heatmap(heatmap_data_percentage, annot=heatmap_labels_percentage.values, fmt="", cmap='YlGnBu')
ax.invert_yaxis()
plt.title('Average Dropped Frames Percentage (± Standard Deviation) for each combination')
plt.xlabel('Network Conditions')
plt.ylabel('Bandwidth')
plt.show()

# Create a scatter plot for 'Avg Dropped Frames %' vs 'Avg Resolution Changes'
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_dropped_frames_percentage_resolution_changes, x='Avg Resolution Changes', y='Avg Dropped Frames %', hue='Bandwidth', style='Loss', size='Delay', sizes=(50, 200), palette='deep')

plt.xlabel('Avg Resolution Changes')
plt.ylabel('Avg Dropped Frames %')
plt.title('Avg Dropped Frames % vs Avg Resolution Changes')
plt.grid(True)
plt.show()

# Create a scatter plot for 'Avg Dropped Frames %' vs 'Avg Rebuffering Events'
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_rebuffering_events, x='Avg Rebuffering Events', y='Avg Dropped Frames %', hue='Bandwidth', style='Loss', size='Delay', sizes=(50, 200), palette='deep')

plt.xlabel('Avg Rebuffering Events')
plt.ylabel('Avg Dropped Frames %')
plt.title('Avg Dropped Frames % vs Avg Rebuffering Events')
plt.grid(True)
plt.show()

# Create a scatter plot for 'Avg Resolution Changes' vs 'Avg Rebuffering Events'
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_rebuffering_events, x='Avg Rebuffering Events', y='Avg Resolution Changes', hue='Bandwidth', style='Loss', size='Delay', sizes=(50, 200), palette='deep')

plt.xlabel('Avg Rebuffering Events')
plt.ylabel('Avg Resolution Changes')
plt.title('Avg Resolution Changes vs Avg Rebuffering Events')
plt.grid(True)
plt.show()

# Define the custom x-axis labels
x_labels = ['low delay no loss', 'high delay no loss', 'low delay high loss', 'high delay high loss']

# Create a new DataFrame for the heatmap
heatmap_data = pd.DataFrame(columns=x_labels, index=bandwidths)

heatmap_std = pd.DataFrame(columns=x_labels, index=bandwidths)

# Fill the DataFrame with the average dropped frames for each combination
for bw in bandwidths:
    for label, (delay, loss) in zip(x_labels, [(20, 0), (100, 0), (20, 2), (100, 2)]):
        # Filter the data for the current combination
        filtered_data = df_dropped_frames[(df_dropped_frames['Bandwidth'] == bw) & (df_dropped_frames['Delay'] == delay) & (df_dropped_frames['Loss'] == loss)]
        # Compute the average dropped frames for the current combination
        avg_dropped_frames = filtered_data['Avg Resolution Changes'].mean()
        # Compute the standard deviation for the average dropped frames
        std_dropped_frames = filtered_data['Std Resolution Changes'].mean()
        # Add the average dropped frames to the heatmap data
        heatmap_data.loc[bw, label] = avg_dropped_frames
        # Add the standard deviation to the heatmap data
        heatmap_std.loc[bw, label] = std_dropped_frames

# Convert the data to numeric type and fill NaN values with 0
heatmap_data = heatmap_data.apply(pd.to_numeric, errors='coerce').fillna(0)
heatmap_std = heatmap_std.apply(pd.to_numeric, errors='coerce').fillna(0)

# Round the data to two decimal places
heatmap_data = heatmap_data.round(2)
heatmap_std = heatmap_std.round(2)

# Convert the data to strings and add parentheses around the standard deviation
heatmap_labels = heatmap_data.astype(str).apply(lambda x: x.apply(lambda y: "{:.2f}".format(float(y)))) + " (± " + heatmap_std.astype(str).apply(lambda x: x.apply(lambda y: "{:.2f}".format(float(y)))) + ")"

# Create the heatmap
plt.figure(figsize=(10, 8))
ax = sns.heatmap(heatmap_data, annot=heatmap_labels.values, fmt="", cmap='YlGnBu')
ax.invert_yaxis()
plt.title('Average Resolution Changes (± Standard Deviation) for each combination')
plt.xlabel('Network Conditions')
plt.ylabel('Bandwidth')
plt.show()