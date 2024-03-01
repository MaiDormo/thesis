import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from statistics_complete_data_mininet import parse_multiple_data_files_and_give_statistic
from matplotlib.ticker import FuncFormatter

# Set global font size
plt.rcParams['font.size'] = 11

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
        'Buffer Length': result['avg_all_runs_avg_data']['Buffer Length'],
        'Avg Dropped Frames': result['avg_all_runs_avg_data']['Dropped Frames'],
        'Avg Dropped Frames %': result['avg_droppedFrames_percentage_for_each_run'],
        'Avg number of Resolution Changes': result['avg_resolution_changes_for_each_run'],
        'Avg Rebuffering Events': result['avg_rebuffering_events_for_each_run'],
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
        'Avg Dropped Frames and Resolution Changes': df['Avg Dropped Frames %'].corr(df['Avg number of Resolution Changes'])
    }

    for correlation_name, correlation_value in correlations.items():
        print(f"Correlation between {correlation_name}: {correlation_value}")

    return df

def create_scatterplot(df, x, y, hue, style, size, title):
    sns.set_theme(rc={'figure.figsize':(12,6), 'font.size':12, 'axes.labelsize':12})  # Increase the font size
    sns.set_style("whitegrid")  # Set the background color to white
    scatter_plot = sns.scatterplot(data=df, x=x, y=y, hue=hue, style=style, size=size, sizes=(50, 200), palette='deep')
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    plt.grid(True)

    # Adjust x-axis limits
    # xmin, xmax = scatter_plot.get_xlim()
    # plt.xlim(xmin * 0.6, xmax * 1.4)  # Reduce white space by 5%

    plt.savefig(f"statistics/{title.replace(' ', '_')}_scatterplot.png", dpi=300)
    plt.show()

def create_heatmap(df, x_labels, title):
    heatmap_data = pd.DataFrame(columns=x_labels, index=PARAMETERS['bandwidths'])

    for bw in PARAMETERS['bandwidths']:
        for label, (delay, loss) in zip(x_labels, [(20, 0), (100, 0), (20, 2), (100, 2)]):
            filtered_data = df[(df['Bandwidth'] == bw) & (df['Delay'] == delay) & (df['Loss'] == loss)]
            avg = filtered_data['Avg ' + title].mean()
            heatmap_data.loc[bw, label] = avg

    heatmap_data = heatmap_data.apply(pd.to_numeric, errors='coerce').fillna(0)
    heatmap_data = heatmap_data.round(2)

    plt.figure(figsize=(10, 6))
    ax = sns.heatmap(heatmap_data, annot=True, fmt=".3g", cmap='YlGnBu', annot_kws={"size": 12})
    ax.invert_yaxis()
    plt.title('Average ' + title + ' for each combination')
    plt.xlabel('Network Conditions')
    plt.ylabel('Bandwidth')

    plt.savefig(f"statistics/{title.replace(' ', '_')}_heatmap.png", dpi=300)

    plt.show()

# Call the function with the defined parameters
df = run_statistics_for_combinations(PARAMETERS)

# Sort the DataFrame
df = df.sort_values(by=['Avg Dropped Frames', 'Download Rate', 'Buffer Length'])

x_labels = ['low delay zero loss', 'high delay zero loss', 'low delay low loss', 'high delay low loss']

create_scatterplot(df, 'Buffer Length', 'Download Rate', 'Bandwidth', 'Loss', 'Delay', 'Download Rate vs Buffer Length')
create_scatterplot(df, 'Buffer Length', 'Avg Bandwith Utilization %', 'Bandwidth', 'Loss', 'Delay', 'Avg Bandwith Utilization % vs Buffer Length')
create_scatterplot(df, 'Buffer Length', 'Avg Dropped Frames', 'Bandwidth', 'Loss', 'Delay', 'Avg Dropped Frames vs Buffer Length')
create_scatterplot(df, 'Download Rate', 'Avg Dropped Frames', 'Bandwidth', 'Loss', 'Delay', 'Avg Dropped Frames vs Download Rate')
create_heatmap(df, x_labels, 'Dropped Frames')
create_heatmap(df, x_labels, 'Dropped Frames %')
create_scatterplot(df, 'Avg number of Resolution Changes', 'Avg Dropped Frames %', 'Bandwidth', 'Loss', 'Delay', 'Avg Dropped Frames % vs Avg number of Resolution Changes')
create_scatterplot(df, 'Avg Rebuffering Events', 'Avg Dropped Frames %', 'Bandwidth', 'Loss', 'Delay', 'Avg Dropped Frames % vs Avg Rebuffering Events')
create_scatterplot(df, 'Avg Rebuffering Events', 'Avg number of Resolution Changes', 'Bandwidth', 'Loss', 'Delay', 'Avg number of Resolution Changes vs Avg Rebuffering Events')
create_heatmap(df, x_labels, 'number of Resolution Changes')