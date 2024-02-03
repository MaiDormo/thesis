from tqdm import tqdm
from plot_mininet_har_complete import mininet_har
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Define the bandwidth, delay, loss, and number of runs
bandwidths = [3, 5, 10, 20, 50]
delays = [20, 100]
losses = [0, 2]
number_of_runs = 3

# Initialize lists to store the results
data_avg_timings = []
data_total_time_and_startup_delay = []

# Calculate the total number of iterations
total_iterations = len(bandwidths) * len(delays) * len(losses)
# Iterate over all possible combinations with a progress bar
with tqdm(total=total_iterations, desc="Processing") as pbar:
    for bw in bandwidths:
        for delay in delays:
            for loss in losses:
                # Call mininet_har with the current combination
                df_avg_timings, df_total_time_and_startup_delay = mininet_har(bw, delay, loss, number_of_runs)
                data_avg_timings.append(df_avg_timings)
                data_total_time_and_startup_delay.append(df_total_time_and_startup_delay)
                # Update the progress bar
                pbar.update(1)

# Convert lists to dataframe
df_avg_timings = pd.concat(data_avg_timings)
df_total_time_and_startup_delay = pd.concat(data_total_time_and_startup_delay)

print(df_total_time_and_startup_delay)

# Create a new column that combines the 'Delay' and 'Loss' columns into a single column
conditions = {
    (20, 0): 'low delay low loss',
    (100, 0): 'high delay low loss',
    (20, 2): 'low delay high loss',
    (100, 2): 'high delay high loss'
}
df_total_time_and_startup_delay['Conditions'] = df_total_time_and_startup_delay.apply(lambda row: conditions[(row['Delay'], row['Loss'])], axis=1)

# Create pivot table for heatmap
pivot_table = df_total_time_and_startup_delay.pivot_table(values='Startup Delay (avg ms)', index='Bandwidth', columns='Conditions', aggfunc='first')

# Create a copy of the pivot table for annotations
annot_table = df_total_time_and_startup_delay.pivot_table(values='Startup Delay (std ms)', index='Bandwidth', columns='Conditions', aggfunc='first')

# Create a pivot table that combines the mean and std into a single string
annot_pivot_table = pd.DataFrame(index=pivot_table.index, columns=pivot_table.columns)
for row in annot_table.index:
    for col in annot_table.columns:
        mean = round(pivot_table.at[row, col], 2)
        std = round(annot_table.at[row, col], 2)
        annot_pivot_table.at[row, col] = f"{mean} (± {std})"

# Create heatmap with annotations
plt.figure(figsize=(10, 8))
ax = sns.heatmap(pivot_table, annot=annot_pivot_table, fmt="", cmap='coolwarm')
ax.invert_xaxis()
ax.invert_yaxis()
plt.title('Heatmap of Startup Delay (ms)')
plt.ylabel('Bandwidth')
plt.xlabel('Conditions')
plt.show()