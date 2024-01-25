import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file into a DataFrame
df = pd.read_csv('/mnt/67922b3c-11d9-4a57-9dda-06dd8163ed30/thesis/server/test.csv')

# Convert bits to Mbps (1 Mbps = 1e6 bits)
for column in df.columns:
 if 'bits' in column:
     df[column] = df[column] / 1e6

# Separate the DataFrame into two DataFrames based on the column names
df_bits = df.filter(like='bits')
df_packets = df.filter(like='packets')

# Create a figure with two subplots
fig, ax1 = plt.subplots(figsize=(10, 5))

# Plot the first graph for bits on the left y-axis
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Value (Mbps)', color='tab:blue')
ax1.set_title('Bits over Time')
ax1.grid(True)

colors = ['tab:blue', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']

lines = []
labels = []

for i, column in enumerate(df_bits.columns):
 if column != 'Interval start':
     line, = ax1.plot(df['Interval start'], df_bits[column], label=column, color=colors[i])
     lines.append(line)
     labels.append(column)

ax1.tick_params(axis='y', labelcolor='tab:blue')

# Create a second y-axis for the packets data
ax2 = ax1.twinx()

# Plot the second graph for packets on the right y-axis
ax2.set_ylabel('Packets', color='tab:orange')

for i, column in enumerate(df_packets.columns):
 if column != 'Interval start':
     line, = ax2.plot(df['Interval start'], df_packets[column], label=column, color=colors[i+len(df_bits.columns)])
     lines.append(line)
     labels.append(column)

ax2.tick_params(axis='y', labelcolor='tab:orange')

# Manually adjust the position of the legend
plt.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)

plt.show()