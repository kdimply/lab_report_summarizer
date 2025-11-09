import matplotlib.pyplot as plt

def create_visual_summary(analyzed_df):
    """
    Creates a horizontal bar chart showing test values and color-coded status.
    """
    if analyzed_df.empty or "Test Name" not in analyzed_df.columns:
        return None

    # Extract data
    test_names = analyzed_df["Test Name"].tolist()
    values = analyzed_df["Value"].astype(float).tolist()
    statuses = analyzed_df["Status"].tolist()

    # Color map based on status
    color_map = {"High": "red", "Low": "orange", "Normal": "green"}
    colors = [color_map.get(status, "gray") for status in statuses]

    # Plot
    fig, ax = plt.subplots(figsize=(9, len(test_names) * 0.4))
    y_positions = range(len(test_names))

    ax.barh(y_positions, values, color=colors)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(test_names)
    ax.invert_yaxis()  # highest test on top
    ax.set_xlabel("Value")
    ax.set_title("🩺 Test Results Overview", fontsize=14, weight="bold")

    # Add grid for readability
    ax.grid(axis='x', linestyle='--', alpha=0.4)

    # Label values beside bars
    for i, v in enumerate(values):
        ax.text(v + 0.1, i, str(v), va='center', fontsize=9)

    plt.tight_layout()
    return fig
