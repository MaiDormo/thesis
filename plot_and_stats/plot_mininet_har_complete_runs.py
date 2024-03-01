from tqdm import tqdm
from plot_mininet_har_complete import mininet_har
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib as mpl

# Set global font size
mpl.rcParams['font.size'] = 11


PARAMETERS = {
    'bandwidths': [3, 5, 10, 20, 50],
    'delays': [20, 100],
    'losses': [0, 2],
    'number_of_runs': 3,
    'conditions': {
        (20, 0): 'low delay zero loss',
        (100, 0): 'high delay zero loss',
        (20, 2): 'low delay low loss',
        (100, 2): 'high delay low loss'
    }
}

def create_heatmap(df, value_column, title):
    pivot_table = df.pivot_table(values=value_column, index='Bandwidth', columns='Conditions', aggfunc='first')

    plt.figure(figsize=(10, 6))
    ax = sns.heatmap(pivot_table, annot=True, fmt=".3g", cmap='coolwarm', annot_kws={"size": 12})  # Increase text size with annot_kws
    ax.invert_xaxis()
    ax.invert_yaxis()
    plt.title(title)
    plt.ylabel('Bandwidth')
    plt.xlabel('Conditions')

    # Format color bar with three significant digits
    colorbar = ax.collections[0].colorbar
    colorbar.formatter = FuncFormatter(lambda x, pos: f'{x:.3g}')
    colorbar.update_ticks()

    # Save the figure before showing it
    plt.savefig(f"statistics/mininet/{title.replace(' ', '_')}.png", dpi=300)

    plt.show()

def load_data(params):
    data_avg_timings = []
    data_total_time_and_startup_delay = []
    data_resolution_changes = []

    total_iterations = len(params['bandwidths']) * len(params['delays']) * len(params['losses'])
    with tqdm(total=total_iterations, desc="Processing") as pbar:
        for bw in params['bandwidths']:
            for delay in params['delays']:
                for loss in params['losses']:
                    df_avg_timings, df_total_time_and_startup_delay, df_resolution_changes = mininet_har(bw, delay, loss, params['number_of_runs'])
                    df_avg_timings = df_avg_timings.round(3)  # Round to three significant digits
                    df_total_time_and_startup_delay = df_total_time_and_startup_delay.round(3)  # Round to three significant digits
                    df_resolution_changes = df_resolution_changes.round(3)  # Round to three significant digits
                    data_avg_timings.append(df_avg_timings)
                    data_total_time_and_startup_delay.append(df_total_time_and_startup_delay)
                    data_resolution_changes.append(df_resolution_changes)
                    pbar.update(1)

    return pd.concat(data_avg_timings), pd.concat(data_total_time_and_startup_delay), pd.concat(data_resolution_changes)

def assign_conditions(df, conditions):
    df['Conditions'] = df.apply(lambda row: conditions[(row['Delay'], row['Loss'])], axis=1)
    return df

def main(params):
    df_avg_timings, df_total_time_and_startup_delay, df_resolution_changes = load_data(params)
    df_total_time_and_startup_delay = assign_conditions(df_total_time_and_startup_delay, params['conditions'])
    df_resolution_changes = assign_conditions(df_resolution_changes, params['conditions'])

    create_heatmap(df_total_time_and_startup_delay, 'Startup Delay (avg ms)', 'Startup Delay (ms)')
    create_heatmap(df_resolution_changes, 'Resolution Changes (avg)', 'Number of Resolution Changes Requested by the Client')

if __name__ == "__main__":
    main(PARAMETERS)