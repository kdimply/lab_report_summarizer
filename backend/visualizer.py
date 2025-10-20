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