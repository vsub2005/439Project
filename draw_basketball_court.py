import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.widgets import Button
import matplotlib.patches as mpatches


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


class DropdownMenu:
    def __init__(self, ax, options, callback):
        self.ax = ax
        self.options = options
        self.callback = callback
        self.current_idx = 0
        self.visible = False
        self.option_patches = []
        self.option_texts = []
        self.scroll_offset = 0
        self.max_visible = 8  # Show 8 teams at a time
        
        # Main button
        self.button = Button(ax, options[0])
        self.button.on_clicked(self.toggle_dropdown)
        
    def toggle_dropdown(self, event):
        if self.visible:
            self.hide_options()
        else:
            self.show_options()
    
    def show_options(self):
        self.visible = True
        fig = self.ax.figure
        
        # Calculate positions
        x, y = self.ax.get_position().x0, self.ax.get_position().y0
        w, h = self.ax.get_position().width, self.ax.get_position().height
        
        # Determine which options to show based on scroll
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.max_visible, len(self.options))
        
        # Add scroll up button if needed
        if self.scroll_offset > 0:
            up_ax = fig.add_axes([x, y + h, w, h*0.6])
            up_ax.set_zorder(1000)
            up_btn = Button(up_ax, '▲ Scroll Up', color='lightgray', hovercolor='gray')
            up_btn.label.set_fontsize(8)
            up_btn.on_clicked(lambda e: self.scroll_up())
            self.option_patches.append(up_ax)
            self.option_texts.append(up_btn)
            y_start = y + h - h*0.6
        else:
            y_start = y + h
        
        # Show options
        for i, option_idx in enumerate(range(start_idx, end_idx)):
            option_ax = fig.add_axes([x, y_start - (i+1)*h*0.8, w, h*0.8])
            option_ax.set_zorder(1000)
            
            btn = Button(option_ax, self.options[option_idx], color='white', hovercolor='lightblue')
            btn.label.set_fontsize(9)
            
            # Closure to capture the index
            def make_callback(idx):
                return lambda event: self.select_option(idx)
            
            btn.on_clicked(make_callback(option_idx))
            
            self.option_patches.append(option_ax)
            self.option_texts.append(btn)
        
        # Add scroll down button if needed
        if end_idx < len(self.options):
            down_y = y_start - (end_idx - start_idx)*h*0.8
            down_ax = fig.add_axes([x, down_y - h*0.6, w, h*0.6])
            down_ax.set_zorder(1000)
            down_btn = Button(down_ax, '▼ Scroll Down', color='lightgray', hovercolor='gray')
            down_btn.label.set_fontsize(8)
            down_btn.on_clicked(lambda e: self.scroll_down())
            self.option_patches.append(down_ax)
            self.option_texts.append(down_btn)
        
        fig.canvas.draw_idle()
    
    def scroll_up(self):
        if self.scroll_offset > 0:
            self.scroll_offset = max(0, self.scroll_offset - self.max_visible)
            self.hide_options()
            self.show_options()
    
    def scroll_down(self):
        if self.scroll_offset + self.max_visible < len(self.options):
            self.scroll_offset = min(len(self.options) - self.max_visible, 
                                    self.scroll_offset + self.max_visible)
            self.hide_options()
            self.show_options()
    
    def hide_options(self):
        self.visible = False
        for patch in self.option_patches:
            patch.remove()
        self.option_patches.clear()
        self.option_texts.clear()
        self.ax.figure.canvas.draw_idle()
    
    def select_option(self, idx):
        self.current_idx = idx
        self.button.label.set_text(self.options[idx])
        self.hide_options()
        self.callback(self.options[idx])


class TeamSelector:
    def __init__(self, df, fig, ax):
        self.df = df
        self.fig = fig
        self.ax = ax

        # Get unique teams and add "All Teams" option
        self.teams = ["All Teams"] + sorted(df["TEAM_NAME"].unique().tolist())

        # Get unique quarters and add "All Quarters" option
        unique_quarters = sorted(df["QUARTER"].dropna().unique().tolist())
        # Store quarter labels as strings for the dropdown
        self.quarters = ["All Quarters"] + [str(q) for q in unique_quarters]
        #get all positions and position groups
        unique_positions = sorted(df["POSITION_GROUP"].unique().tolist()) + sorted(df["POSITION"].unique().tolist())
        self.positions = ["Positions"] + [str(q) for q in unique_positions]
        # Keep track of current selections so the two dropdowns
        # can work together
        self.current_team = "All Teams"
        self.current_quarter = "All Quarters"
        self.current_position = "Positions"
        self.scatter = None
        self.cbar = None
        self.cbar_ax = None

        # Will store position after first colorbar creation
        self.stable_position = None

        # Create dropdowns
        self.create_dropdowns()

        # Initial plot with default selections
        self.update_plot()

    def create_dropdowns(self):
        """Create both the team and quarter dropdown menus."""
        # Team dropdown button position at top
        ax_team = plt.axes([0.05, 0.92, 0.25, 0.04])
        self.team_dropdown = DropdownMenu(
            ax_team,
            self.teams,
            lambda team_name: self.update_plot(team_name=team_name),
        )

        # Quarter dropdown just below the team dropdown
        ax_quarter = plt.axes([0.35, 0.92, 0.25, 0.04])
        self.quarter_dropdown = DropdownMenu(
            ax_quarter,
            self.quarters,
            lambda quarter: self.update_plot(quarter=quarter),
        )
        ax_pos = plt.axes([0.65, 0.92, 0.25, 0.04])
        self.pos_dropdown = DropdownMenu(
            ax_pos,
            self.positions,
            lambda position: self.update_plot(position=position),
        )
    def update_plot(self, team_name=None, quarter=None, position = None):
        """Update the shot chart based on the selected team and quarter.

        Both dropdown menus call this function; whichever dropdown changes
        passes its new value, and we keep the other setting unchanged.
        """
        # Update current selections if new values were provided
        if team_name is not None:
            self.current_team = team_name
        if quarter is not None:
            self.current_quarter = quarter
        if position is not None:
            self.current_position = position
        # Clear the main axis
        self.ax.clear()

        # Restore stable position if we have one (after first colorbar creation)
        if self.stable_position is not None:
            self.ax.set_position(self.stable_position)

        draw_half_court(self.ax)

        # Start from full dataframe and apply filters for both dropdowns
        filtered_df = self.df

        # Filter by team
        if self.current_team != "All Teams":
            filtered_df = filtered_df[filtered_df["TEAM_NAME"] == self.current_team]

        # Filter by quarter
        if self.current_quarter != "All Quarters":
            # Compare as string
            filtered_df = filtered_df[
                filtered_df["QUARTER"].astype(str) == self.current_quarter
            ]
        if self.current_position != "Positions":
            if self.current_position in filtered_df["POSITION_GROUP"].astype(str).unique():
                filtered_df = filtered_df[filtered_df["POSITION_GROUP"].astype(str) == self.current_position]
            else:
                filtered_df = filtered_df[filtered_df["POSITION"].astype(str) == self.current_position]

        # Aggregate shots by (LOC_X, LOC_Y)
        grouped = (
            filtered_df.groupby(["LOC_X", "LOC_Y"])
            .size()
            .reset_index(name="count")
        )

        fg = (
            filtered_df.groupby(["LOC_X", "LOC_Y"])["SHOT_MADE"]
            .mean()
            .reset_index(name="fg")
        )
        grouped = grouped.merge(fg, on=["LOC_X", "LOC_Y"])

        # Scale counts into reasonable bubble sizes
        if len(grouped) > 0:
            max_count = grouped["count"].max()
            min_size = 1
            max_size = 25
            sizes = min_size + (grouped["count"] / max_count) * (max_size - min_size)

            # Bubble chart
            self.scatter = self.ax.scatter(
                grouped["LOC_X"],
                grouped["LOC_Y"],
                s=sizes,
                c=grouped["fg"],
                cmap="viridis",
                alpha=0.7,
                zorder=10,
                vmin=0,
                vmax=1,
            )

            # Create or update colorbar
            if self.cbar is None:
                self.cbar = plt.colorbar(self.scatter, ax=self.ax)
                self.cbar.set_label("Field Goal Percentage (FG%)")
                # Save the position AFTER colorbar creation
                self.stable_position = self.ax.get_position()
            else:
                # Update existing colorbar with new data
                self.cbar.update_normal(self.scatter)

        # Build a descriptive title reflecting both filters
        title_team = self.current_team
        title_quarter = (
            "All Quarters"
            if self.current_quarter == "All Quarters"
            else f"Quarter {self.current_quarter}"
        )
        title_pos = ("Positions" if self.current_position == "Positions" else self.current_position)
        self.ax.set_title(
            f"Shot Chart: {title_team} - {title_pos} - {title_quarter}",
            fontsize=12,
            weight="bold",
            pad=30,
        )
        self.fig.canvas.draw_idle()


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "clean_shots_with_zones.csv")

    # Load cleaned data
    df = pd.read_csv(csv_path)

    # Create figure with extra space for dropdown at top
    fig = plt.figure(figsize=(10, 7))
    ax = plt.axes([0.1, 0.05, 0.8, 0.8])
    
    # Initialize team selector
    selector = TeamSelector(df, fig, ax)
    
    plt.show()


if __name__ == "__main__":
    main()

