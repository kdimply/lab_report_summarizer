# backend/comparator.py
import pandas as pd
import matplotlib.pyplot as plt
from .analyzer import STANDARD_RANGES  # Import normal ranges for overlay

def generate_trend_analysis(history_df):
    """Analyzes a user's report history to find meaningful changes and critical deviations."""
    if history_df.empty or len(history_df['upload_date'].unique()) < 2:
        return "This is your first report. Upload future reports to track trends!", {}

    summary = "## 📈 Your Health Trends\n\nHere's how your latest report compares to the previous one:\n"
    
    # Convert to datetime
    history_df['upload_date'] = pd.to_datetime(history_df['upload_date'], errors='coerce')
    all_dates = sorted(history_df['upload_date'].dropna().unique())
    latest_date = all_dates[-1]
    previous_date = all_dates[-2]

    latest_report = history_df[history_df['upload_date'] == latest_date]
    previous_report = history_df[history_df['upload_date'] == previous_date]

    trends = {}
    critical_change = None  # track biggest deviation
    max_change = 0

    all_test_names = history_df['test_name'].unique()

    for test_name in all_test_names:
        trends.setdefault(test_name, {'dates': [], 'values': []})
        
        # Add historical values for plotting
        all_values = history_df[history_df['test_name'] == test_name].sort_values(by='upload_date')
        trends[test_name]['dates'] = list(all_values['upload_date'])
        trends[test_name]['values'] = list(all_values['value'])

        current_test = latest_report[latest_report['test_name'] == test_name]
        prev_test = previous_report[previous_report['test_name'] == test_name]

        if not current_test.empty and not prev_test.empty:
            prev_val = prev_test.iloc[0]['value']
            curr_val = current_test.iloc[0]['value']
            curr_status = current_test.iloc[0]['status']
            prev_status = prev_test.iloc[0]['status']

            # Compute percentage change
            if prev_val != 0:
                change_percent = ((curr_val - prev_val) / abs(prev_val)) * 100
            else:
                change_percent = 0

            if abs(change_percent) > max_change:
                max_change = abs(change_percent)
                critical_change = (test_name, change_percent, curr_status)

            # Build summary
            if curr_status != 'Normal' and prev_status == 'Normal':
                summary += f"\n- **(⚠️ New Alert)** {test_name}: Became **{curr_status}** ({curr_val:.2f}) from 'Normal'."
            elif curr_status == 'Normal' and prev_status != 'Normal':
                summary += f"\n- **(✅ Improvement)** {test_name}: Returned to **Normal** ({curr_val:.2f}) from '{prev_status}'."
            elif curr_status != 'Normal' and curr_status != prev_status:
                summary += f"\n- **(Change)** {test_name}: Shifted from '{prev_status}' to **'{curr_status}'** ({curr_val:.2f})."
            elif curr_status != 'Normal':
                direction = "increased" if change_percent > 0 else "decreased"
                if abs(change_percent) > 1:
                    summary += f"\n- **(Monitoring)** {test_name}: Still **{curr_status}**, {direction} by {abs(change_percent):.1f}%."

    # Add highlight for the largest deviation
    if critical_change:
        name, change, status = critical_change
        direction = "increased" if change > 0 else "decreased"
        summary = f"### ⚠️ Biggest Change: **{name}** ({status}) — {direction} by {abs(change):.1f}%\n\n" + summary

    if summary.strip().endswith("previous one:"):
        summary += "\nNo significant changes from your previous report. Keep up the good work!"

    return summary, trends



def create_trend_plot(trend_data, test_to_plot):
    """Creates a Matplotlib figure for a specific test trend."""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    if test_to_plot not in trend_data or not trend_data[test_to_plot]['dates']:
        ax.set_title(f"No data available for {test_to_plot}")
        plt.close(fig)
        return fig
        
    data = trend_data[test_to_plot]
    
    if len(data['dates']) == 1:
        ax.plot(data['dates'], data['values'], 'o', color='blue')
    else:
        ax.plot(data['dates'], data['values'], marker='o', linestyle='-', linewidth=2, color='blue')
    
    # Add standard normal range shading
    matched_key = next((key for key in STANDARD_RANGES if key in test_to_plot.upper()), None)
    if matched_key and isinstance(STANDARD_RANGES[matched_key][0], (int, float)):
        low, high = STANDARD_RANGES[matched_key]
        ax.axhspan(low, high, color='green', alpha=0.15, label=f"Normal Range ({low}-{high})")
        ax.legend()

    ax.set_title(f"Trend for {test_to_plot}", fontsize=13, pad=10)
    ax.set_ylabel("Value", fontsize=11)
    ax.set_xlabel("Date", fontsize=11)
    plt.xticks(rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.close(fig)
    return fig
