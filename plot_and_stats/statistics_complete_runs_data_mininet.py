import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from statistics_complete_data_mininet import parse_multiple_data_files_and_give_statistic

# Define the bandwidth, delay, loss, and number of runs
PARAMETERS = {
    'bandwidths': [3, 5, 10, 20, 50],
    'delays': [20, 100],
    'losses': [0, 2],
    'number_of_runs': 3
}

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

def run_statistics_for_combinations(params):
    all_results = [calculate_statistics(bw, delay, loss, params['number_of_runs'])
                   for bw in params['bandwidths']
                   for delay in params['delays']
                   for loss in params['losses']]

    df = pd.DataFrame([result for result in all_results if result])

    # Compute correlations
    correlations = {
        'Download Rate and Buffer Length': df['Download Rate'].corr(df['Buffer Length']),
        'Avg Dropped Frames and Buffer Length': df['Avg Dropped Frames'].corr(df['Buffer Length']),
        'Avg Dropped Frames and Download Rate': df['Avg Dropped Frames'].corr(df['Download Rate']),
        'Avg Dropped Frames and Resolution Changes': df['Avg Dropped Frames %'].corr(df['Avg Resolution Changes'])
    }

    for correlation_name, correlation_value in correlations.items():
        print(f"Correlation between {correlation_name}: {correlation_value}")

    return df

def create_scatterplot(df, x, y, hue, style, size, title):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x=x, y=y, hue=hue, style=style, size=size, sizes=(50, 200), palette='deep')
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    plt.grid(True)
    plt.show()

def create_heatmap(df, x_labels, title):
    heatmap_data = pd.DataFrame(columns=x_labels, index=PARAMETERS['bandwidths'])
    heatmap_std = pd.DataFrame(columns=x_labels, index=PARAMETERS['bandwidths'])

    for bw in PARAMETERS['bandwidths']:
        for label, (delay, loss) in zip(x_labels, [(20, 0), (100, 0), (20, 2), (100, 2)]):
            filtered_data = df[(df['Bandwidth'] == bw) & (df['Delay'] == delay) & (df['Loss'] == loss)]
            avg = filtered_data['Avg ' + title].mean()
            std = filtered_data['Std ' + title].mean()
            heatmap_data.loc[bw, label] = avg
            heatmap_std.loc[bw, label] = std

    heatmap_data = heatmap_data.apply(pd.to_numeric, errors='coerce').fillna(0)
    heatmap_std = heatmap_std.apply(pd.to_numeric, errors='coerce').fillna(0)

    heatmap_data = heatmap_data.round(2)
    heatmap_std = heatmap_std.round(2)

    heatmap_labels = heatmap_data.astype(str).apply(lambda x: x.apply(lambda y: "{:.2f}".format(float(y)))) + " (± " + heatmap_std.astype(str).apply(lambda x: x.apply(lambda y: "{:.2f}".format(float(y)))) + ")"

    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(heatmap_data, annot=heatmap_labels.values, fmt="", cmap='YlGnBu')
    ax.invert_yaxis()
    plt.title('Average ' + title + ' (± Standard Deviation) for each combination')
    plt.xlabel('Network Conditions')
    plt.ylabel('Bandwidth')
    plt.show()

# Call the function with the defined parameters
df = run_statistics_for_combinations(PARAMETERS)

# Sort the DataFrame
df = df.sort_values(by=['Avg Dropped Frames', 'Std Dropped Frames', 'Download Rate', 'Buffer Length'])

x_labels = ['low delay no loss', 'high delay no loss', 'low delay high loss', 'high delay high loss']

create_scatterplot(df, 'Buffer Length', 'Download Rate', 'Bandwidth', 'Loss', 'Delay', 'Download Rate vs Buffer Length')
create_scatterplot(df, 'Buffer Length', 'Avg Bandwith Utilization %', 'Bandwidth', 'Loss', 'Delay', 'Avg Bandwith Utilization % vs Buffer Length')
create_scatterplot(df, 'Buffer Length', 'Avg Dropped Frames', 'Bandwidth', 'Loss', 'Delay', 'Avg Dropped Frames vs Buffer Length')
create_scatterplot(df, 'Download Rate', 'Avg Dropped Frames', 'Bandwidth', 'Loss', 'Delay', 'Avg Dropped Frames vs Download Rate')
create_heatmap(df, x_labels, 'Dropped Frames')
create_heatmap(df, x_labels, 'Dropped Frames %')
create_scatterplot(df, 'Avg Resolution Changes', 'Avg Dropped Frames %', 'Bandwidth', 'Loss', 'Delay', 'Avg Dropped Frames % vs Avg Resolution Changes')
create_scatterplot(df, 'Avg Rebuffering Events', 'Avg Dropped Frames %', 'Bandwidth', 'Loss', 'Delay', 'Avg Dropped Frames % vs Avg Rebuffering Events')
create_scatterplot(df, 'Avg Rebuffering Events', 'Avg Resolution Changes', 'Bandwidth', 'Loss', 'Delay', 'Avg Resolution Changes vs Avg Rebuffering Events')
create_heatmap(df, x_labels, 'Resolution Changes')