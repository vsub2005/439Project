import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc


def draw_half_court(ax=None, line_color="black", lw=2):
    """
    Draws a simple NBA-style half court in the same coordinate system
    as the Kaggle data: x in [-50, 50], y in [0, 50].
    Hoop is at (0, 5).
    Baseline at y = 0
    Half-court line at y = 50.
    """
    if ax is None:
        ax = plt.gca()

    # Outer half-court border
    outer = Rectangle(
        (-50, 0),
        100,
        50,
        fill=False,
        linewidth=lw,
        edgecolor=line_color,
    )
    ax.add_patch(outer)

    # Hoop
    hoop = Circle((0, 5), radius=1, fill=False, linewidth=lw, edgecolor=line_color)
    ax.add_patch(hoop)

    # Backboard
    backboard = Rectangle((-3, 4), 6, 0.2, fill=False, linewidth=lw, edgecolor=line_color)
    ax.add_patch(backboard)

    # Paint
    paint = Rectangle((-8, 0), 16, 19, fill=False, linewidth=lw, edgecolor=line_color)
    ax.add_patch(paint)

    # Free throw circle
    ft_circle = Arc((0, 19), 12, 12, theta1=0, theta2=180, linewidth=lw, edgecolor=line_color)
    ax.add_patch(ft_circle)

    # Restricted area
    restricted = Arc((0, 5), 8, 8, theta1=0, theta2=180, linewidth=lw, edgecolor=line_color)
    ax.add_patch(restricted)

    # 3-point side lines
    left_3 = Rectangle((-22, 0), 0.1, 14, fill=False, linewidth=lw, edgecolor=line_color)
    right_3 = Rectangle((22, 0), 0.1, 14, fill=False, linewidth=lw, edgecolor=line_color)
    ax.add_patch(left_3)
    ax.add_patch(right_3)

    # 3-point arc
    three_arc = Arc((0, 5), 47.5, 47.5, theta1=22, theta2=158, linewidth=lw, edgecolor=line_color)
    ax.add_patch(three_arc)

    # Half-court line at y = 50
    ax.plot([-50, 50], [50, 50], color=line_color, linewidth=lw)

    # Formatting
    ax.set_xlim(-50, 50)
    ax.set_ylim(0, 50)
    ax.set_aspect("equal")
    ax.axis("off")

    return ax


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "clean_shots_with_zones.csv")

    # Load cleaned data
    df = pd.read_csv(csv_path)

    # NOTE: BELOW IS JUST A TEST SCATTER PLOT OF ALL THE POINTS ---- CAN DELETE THIS AND REPLACE WITH BUBBLE CHART CODE
    sample = df.sample(20000, random_state=0)

    fig, ax = plt.subplots(figsize=(8, 6))
    draw_half_court(ax)

    # Scatter shots in the same coordinate system as the court
    ax.scatter(
        sample["LOC_X"],
        sample["LOC_Y"],
        s=3,
        alpha=0.3,
        zorder=10,
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
