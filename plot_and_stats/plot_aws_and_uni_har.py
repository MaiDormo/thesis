from tqdm import tqdm
from statistics_aws_and_uni_har_complete import load_data
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib as mpl

# Set global font size
mpl.rcParams['font.size'] = 11

PARAMETERS = {
    'number_of_runs': 3,
    'cases': ['aws', 'uni'],
    'timings': ['blocked', 'connect', 'send', 'wait', 'receive', '_blocked_queueing'],
}

def create_heatmap(df, value_column, title):
    pivot_table = df.pivot_table(values=value_column, index='Category', columns='case', aggfunc='first')

    plt.figure(figsize=(9, 6))
    ax = sns.heatmap(pivot_table, annot=True, fmt=".3g", cmap='coolwarm', annot_kws={"size": 12})  # Increase text size with annot_kws
    ax.invert_yaxis()
    ax.invert_xaxis()
    plt.title(title)
    plt.ylabel('timings')
    plt.xlabel('cases')

    # Format color bar with three significant digits
    colorbar = ax.collections[0].colorbar
    colorbar.formatter = FuncFormatter(lambda x, pos: f'{x:.3g}')
    colorbar.update_ticks()

    # Adjust the margins
    plt.subplots_adjust(left=0.20)

    # Save the figure before showing it
    plt.savefig(f"statistics/{title.replace(' ', '_')}_heatmap.png", dpi=300)

    plt.show()

def create_bar_chart(df, value_column, title):
    plt.figure(figsize=(9, 6))
    ax = sns.barplot(x='case', y=value_column, data=df)
    plt.title(title)
    plt.ylabel('Average Startup Delay (ms)')
    plt.xlabel('Cases')

    # Format y-axis with three significant digits
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.3g}'.format(y)))

    # Save the figure before showing it
    plt.savefig(f"statistics/{title.replace(' ', '_')}_barchart.png", dpi=300)

    plt.show()

def main(params):
    df_aws_avg_timings, df_aws_total_time_and_startup_delay, df_aws_resolution_changes = load_data(params['cases'][0])
    df_uni_avg_timings, df_uni_total_time_and_startup_delay, df_uni_resolution_changes = load_data(params['cases'][1])

    df_aws_avg_timings['case'] = 'aws'
    df_uni_avg_timings['case'] = 'uni'

    df_combined = pd.concat([df_aws_avg_timings, df_uni_avg_timings])

    df_startup_delay = pd.DataFrame([
        {
            'Startup Delay (avg ms)': df_aws_total_time_and_startup_delay.at[0, 'Startup Delay (avg ms)'],
            'case': 'aws'
        },
        {
            'Startup Delay (avg ms)': df_uni_total_time_and_startup_delay.at[0, 'Startup Delay (avg ms)'],
            'case': 'uni'
        }
    ])

    create_heatmap(df_combined, 'Mean (avg ms)', 'Heatmap of Timings (ms)')
    create_bar_chart(df_startup_delay, 'Startup Delay (avg ms)', 'Bar Chart of Average Startup Delay')

if __name__ == "__main__":
    main(PARAMETERS)