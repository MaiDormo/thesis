import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV files
df1 = pd.read_csv('test.csv')
df2 = pd.read_csv('test3.csv')

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

# Create a figure with two subplots
fig, axs = plt.subplots(2, figsize=(10, 10))

# Plot the first graph on the first subplot
axs[0].plot(df['Elapsed Time'], df['Download Rate'], color='blue')
axs[0].set(xlabel='Elapsed Time (s)', ylabel='Download Rate (Mbps)', title='Download Rate over Time')
axs[0].grid(True)

# Plot the second graph on the second subplot as a bar chart with smaller bars
axs[1].bar(df.index, df['Download Rate'], width=0.5, color='green')
axs[1].set_xticks(df.index)
axs[1].set_xticklabels(df['Resolution'], rotation=90)
axs[1].set(xlabel='Resolution', ylabel='Download Rate (Mbps)', title='Resolution over Time')
axs[1].grid(True)

# Increase the font size of the labels and titles
for ax in axs:
    ax.title.set_size(20)
    ax.xaxis.label.set_size(15)
    ax.yaxis.label.set_size(15)

# Display the figure with the subplots
plt.tight_layout()
plt.show()