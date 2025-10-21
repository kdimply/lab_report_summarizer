# backend/visualizer.py

import matplotlib.pyplot as plt
import numpy as np

def create_visual_summary(analyzed_df):
    """Creates a horizontal bar chart to visualize the results."""
    if analyzed_df.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, len(analyzed_df) * 0.5))

    # Bar colors based on status
    colors = {'Normal': 'green', 'Low': 'orange', 'High': 'red', 'Check Range': 'gray'}
    bar_colors = [colors.get(status, 'gray') for status in analyzed_df['Status']]

    # Create the horizontal bars
    y_pos = np.arange(len(analyzed_df['Test Name']))
    ax.barh(y_pos, analyzed_df['Value'], align='center', color=bar_colors, height=0.6)
    
    # Add reference range lines
    for i, row in analyzed_df.iterrows():
        try:
            range_str = row['Reference Range']
            if '-' in range_str:
                low, high = map(float, range_str.split('-'))
                ax.plot([low, high], [i, i], color='black', linewidth=4, alpha=0.7, solid_capstyle='round')
        except:
            continue # Skip if range is not in "low-high" format

    ax.set_yticks(y_pos)
    ax.set_yticklabels(analyzed_df['Test Name'])
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Value')
    ax.set_title('Lab Test Results Overview')
    plt.tight_layout()
    
    return fig
# In backend/visualizer.py, add this function at the bottom
import pandas as pd # Make sure to import pandas

def create_trend_graph(test_name_to_track):
    try:
        history_df = pd.read_csv('report_history.csv')
        history_df['Date'] = pd.to_datetime(history_df['Date'])
        test_df = history_df[history_df['Test Name'] == test_name_to_track]
        
        if len(test_df) < 2:
            return None # Not enough data for a trend

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(test_df['Date'], test_df['Value'], marker='o', linestyle='-')
        ax.set_title(f'Trend for {test_name_to_track} Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        plt.grid(True)
        plt.tight_layout()
        return fig
    except FileNotFoundError:
        return None
    
    # (Keep all your existing code in visualizer.py)
# Add this new code at the very bottom of the file:
import pandas as pd # Make sure pandas is imported at the top of the file

