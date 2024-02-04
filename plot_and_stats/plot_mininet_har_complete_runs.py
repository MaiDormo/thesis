from tqdm import tqdm
from plot_mininet_har_complete import mininet_har
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def create_heatmap(df, value_column, std_column, title):
    pivot_table = df.pivot_table(values=value_column, index='Bandwidth', columns='Conditions', aggfunc='first')
    annot_table = df.pivot_table(values=std_column, index='Bandwidth', columns='Conditions', aggfunc='first')

    annot_pivot_table = pd.DataFrame(index=pivot_table.index, columns=pivot_table.columns)
    for row in annot_table.index:
        for col in annot_table.columns:
            mean = round(pivot_table.at[row, col], 2)
            std = round(annot_table.at[row, col], 2)
            annot_pivot_table.at[row, col] = f"{mean} (± {std})"

    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(pivot_table, annot=annot_pivot_table, fmt="", cmap='coolwarm')
    ax.invert_xaxis()
    plt.title(title)
    plt.ylabel('Bandwidth')
    plt.xlabel('Conditions')
    plt.show()

def load_data(bandwidths, delays, losses, number_of_runs):
    data_avg_timings = []
    data_total_time_and_startup_delay = []
    data_resolution_changes = []

    total_iterations = len(bandwidths) * len(delays) * len(losses)
    with tqdm(total=total_iterations, desc="Processing") as pbar:
        for bw in bandwidths:
            for delay in delays:
                for loss in losses:
                    df_avg_timings, df_total_time_and_startup_delay, df_resolution_changes = mininet_har(bw, delay, loss, number_of_runs)
                    data_avg_timings.append(df_avg_timings)
                    data_total_time_and_startup_delay.append(df_total_time_and_startup_delay)
                    data_resolution_changes.append(df_resolution_changes)
                    pbar.update(1)

    return pd.concat(data_avg_timings), pd.concat(data_total_time_and_startup_delay), pd.concat(data_resolution_changes)

def assign_conditions(df, conditions):
    df['Conditions'] = df.apply(lambda row: conditions[(row['Delay'], row['Loss'])], axis=1)
    return df

def main():
    bandwidths = [3, 5, 10, 20, 50]
    delays = [20, 100]
    losses = [0, 2]
    number_of_runs = 3

    conditions = {
        (20, 0): 'low delay low loss',
        (100, 0): 'high delay low loss',
        (20, 2): 'low delay high loss',
        (100, 2): 'high delay high loss'
    }

    df_avg_timings, df_total_time_and_startup_delay, df_resolution_changes = load_data(bandwidths, delays, losses, number_of_runs)
    df_total_time_and_startup_delay = assign_conditions(df_total_time_and_startup_delay, conditions)
    df_resolution_changes = assign_conditions(df_resolution_changes, conditions)

    create_heatmap(df_total_time_and_startup_delay, 'Startup Delay (avg ms)', 'Startup Delay (std ms)', 'Heatmap of Startup Delay (ms)')
    create_heatmap(df_resolution_changes, 'Resolution Changes (avg)', 'Resolution Changes (std)', 'Heatmap of Resolution Changes')

if __name__ == "__main__":
    main()