import matplotlib.pyplot as plt

def create_visual_summary(analyzed_df):
    """
    Creates a clean, readable horizontal bar chart with color-coded results.
    Supports Slightly/Moderately/Severely variations.
    """
    if analyzed_df.empty or "Test Name" not in analyzed_df.columns:
        return None

    # Extract data
    test_names = analyzed_df["Test Name"].tolist()
    values = analyzed_df["Value"].astype(float).tolist()
    statuses = analyzed_df["Status"].tolist()

    # Full color map for all cases
    color_map = {
        "Normal": "#2ecc71",            # green
        "Slightly Low": "#f1c40f",      # yellow
        "Low": "#f39c12",               # orange
        "Severely Low": "#e67e22",      # dark orange
        "Slightly High": "#e67e22",     # dark orange
        "Moderately High": "#d35400",   # deeper orange
        "High": "#e74c3c",              # red
        "Severely High": "#c0392b",     # dark red
    }

    # Assign colors
    colors = [color_map.get(status, "gray") for status in statuses]

    # Plot
    fig, ax = plt.subplots(figsize=(9, len(test_names) * 0.45))
    y_positions = range(len(test_names))

    ax.barh(y_positions, values, color=colors, edgecolor='black', linewidth=0.4)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(test_names, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Value", fontsize=10)
    ax.set_title("🩺 Test Results Overview", fontsize=15, weight="bold")

    # Grid
    ax.grid(axis="x", linestyle="--", alpha=0.35)

    # Add labels on bars
    for i, v in enumerate(values):
        ax.text(v + (max(values) * 0.02), i, str(v), va="center", fontsize=8)

    # ------------------ COLOR LEGEND ------------------
    legend_items = [
        plt.Line2D([0], [0], marker='s', color="#2ecc71", markersize=10, linestyle='None', label='Normal (Green)'),
        plt.Line2D([0], [0], marker='s', color="#f1c40f", markersize=10, linestyle='None', label='Slightly Low (Yellow)'),
        plt.Line2D([0], [0], marker='s', color="#f39c12", markersize=10, linestyle='None', label='Low (Orange)'),
        plt.Line2D([0], [0], marker='s', color="#e67e22", markersize=10, linestyle='None', label='Slightly High (Dark Orange)'),
        plt.Line2D([0], [0], marker='s', color="#d35400", markersize=10, linestyle='None', label='Moderately High'),
        plt.Line2D([0], [0], marker='s', color="#e74c3c", markersize=10, linestyle='None', label='High (Red)'),
        plt.Line2D([0], [0], marker='s', color="#c0392b", markersize=10, linestyle='None', label='Severely High (Dark Red)'),
        plt.Line2D([0], [0], marker='s', color="gray", markersize=10, linestyle='None', label='No Range / Unknown')
    ]

    ax.legend(handles=legend_items, title="Color Meaning", loc="lower right", fontsize=8, title_fontsize=9)

    plt.tight_layout()

    return fig
