from tqdm import tqdm
from statistics_aws_and_uni_har_complete import load_data
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

PARAMETERS = {
    'number_of_runs': 3,
    'cases': ['aws', 'uni'],
    'timings': ['blocked', 'connect', 'send', 'wait', 'receive', '_blocked_queueing'],
}

def create_heatmap(df, value_column, std_column, title):
    pivot_table = df.pivot_table(values=value_column, index='Category', columns='case', aggfunc='first')
    annot_table = df.pivot_table(values=std_column, index='Category', columns='case', aggfunc='first')

    annot_pivot_table = pd.DataFrame(index=pivot_table.index, columns=pivot_table.columns)
    for row in annot_table.index:
        for col in annot_table.columns:
            mean = round(pivot_table.at[row, col], 2)
            std = round(annot_table.at[row, col], 2)
            annot_pivot_table.at[row, col] = f"{mean} (± {std})"

    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(pivot_table, annot=annot_pivot_table, fmt="", cmap='coolwarm')
    ax.invert_yaxis()
    ax.invert_xaxis()
    plt.title(title)
    plt.ylabel('timings')
    plt.xlabel('cases')
    plt.show()

def create_bar_chart(df, value_column, std_column, title):
    plt.figure(figsize=(10, 8))
    sns.barplot(x='case', y=value_column, data=df, yerr=df[std_column])
    plt.title(title)
    plt.ylabel('Average Startup Delay (ms)')
    plt.xlabel('Cases')
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
            'Startup Delay (std ms)': df_aws_total_time_and_startup_delay.at[0, 'Startup Delay (std ms)'],
            'case': 'aws'
        },
        {
            'Startup Delay (avg ms)': df_uni_total_time_and_startup_delay.at[0, 'Startup Delay (avg ms)'],
            'Startup Delay (std ms)': df_uni_total_time_and_startup_delay.at[0, 'Startup Delay (std ms)'],
            'case': 'uni'
        }
    ])

    create_heatmap(df_combined, 'Mean (avg ms)', 'Deviation (avg ms)', 'Heatmap of Timings (ms)')
    create_bar_chart(df_startup_delay, 'Startup Delay (avg ms)', 'Startup Delay (std ms)', 'Bar Chart of Average Startup Delay')

if __name__ == "__main__":
    main(PARAMETERS)