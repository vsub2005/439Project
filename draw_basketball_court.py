import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.widgets import Button, Slider, RangeSlider
import numpy as np
import mplcursors


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
        
        # Time settings
        self.regulation_secs = 12 * 60   # 12:00
        self.ot_secs = 5 * 60           # 5:00
        self._current_time_max = self.regulation_secs

        # Get unique teams
        self.teams = sorted(df["TEAM_NAME"].unique().tolist())

        # Get unique quarters and add "All Quarters" option
        unique_quarters = sorted(df["QUARTER"].dropna().unique().tolist())
        self.quarters = ["All Quarters"] + [str(q) for q in unique_quarters]

        # Get all positions and position groups
        unique_positions = sorted(df["POSITION_GROUP"].unique().tolist()) + \
                           sorted(df["POSITION"].unique().tolist())
        self.positions = ["All Positions"] + [str(q) for q in unique_positions]
        
        # Get available seasons
        years = sorted(df["SEASON_1"].dropna().unique().tolist())
        self.min_year = int(min(years))
        self.max_year = int(max(years))
        self.current_year = self.min_year
        
        # Precompute total number of shots per (team, season)
        total_shots_per_team_year = (
            df.groupby(["TEAM_NAME", "SEASON_1"])
            .size()
            .reset_index(name="total_shots")
        )
        self.total_shots_by_team_year = {
            (row["TEAM_NAME"], int(row["SEASON_1"])): int(row["total_shots"])
            for _, row in total_shots_per_team_year.iterrows()
        }

        # Current selections
        self.current_team = self.teams[0]
        self.current_quarter = "All Quarters"
        self.current_position = "All Positions"
        self.scatter = None
        self.cbar = None
        self.cbar_ax = None
        self.size_legend = None 
        
        # Time slider instance (created later)
        self.time_slider = None

        # Will store position after first colorbar creation
        self.stable_position = None

        # Create dropdowns, sliders, and initial plot
        self.create_dropdowns()
        self.create_year_slider()
        self.create_time_slider()
        self.update_plot()
    
    def _format_secs_mmss(self, seconds: float) -> str:
        """Format raw seconds (e.g., SECS_LEFT_UNIFIED) as MM:SS."""
        seconds = max(0, min(self._current_time_max, float(seconds)))
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def _update_time_slider_label(self, val):
        """Update the slider's valtext as 'HIGH_TIME – LOW_TIME'."""
        if self.time_slider is None or self.time_slider.valtext is None:
            return

        lo, hi = sorted(val)
        hi_str = self._format_secs_mmss(hi)
        lo_str = self._format_secs_mmss(lo)
        self.time_slider.valtext.set_text(f"{hi_str} – {lo_str}")

    def create_dropdowns(self):
        """Create team, quarter, and position dropdown menus."""
        ax_team = plt.axes([0.05, 0.92, 0.25, 0.04])
        self.team_dropdown = DropdownMenu(
            ax_team,
            self.teams,
            lambda team_name: self.update_plot(team_name=team_name),
        )

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
    
    def create_year_slider(self):
        """Create a slider to select the season (year)."""
        ax_year = plt.axes([0.1, 0.01, 0.8, 0.03])
        self.year_slider = Slider(
            ax_year,
            "Season",
            self.min_year,
            self.max_year,
            valinit=self.current_year,
            valstep=1,
        )
        self.year_slider.on_changed(self.on_year_change)

    def on_year_change(self, val):
        self.current_year = int(round(val))
        self.update_plot()
        
    # Time Range RangeSlider
    def create_time_slider(self):
        """Create the time-range slider axes once."""
        self.time_ax = plt.axes([0.1, 0.05, 0.8, 0.10])
        self.time_slider = None
        self._rebuild_time_slider(self.regulation_secs)
        self.time_slider.ax.set_visible(False)

    def _rebuild_time_slider(self, max_seconds: float):
        """(Re)build the RangeSlider for a given quarter length."""
        self._current_time_max = max_seconds
        self.time_ax.cla()
        self.time_slider = RangeSlider(
            ax=self.time_ax,
            label="Time Range",
            valmin=0.0,
            valmax=max_seconds,
            valinit=(0.0, max_seconds),
        )
        
        self.time_slider.ax.invert_xaxis()
        self._update_time_slider_label(self.time_slider.val)

        def _on_time_change(val):
            self._update_time_slider_label(val)
            self.update_plot()

        self.time_slider.on_changed(_on_time_change)
    
    def _update_time_slider_for_quarter(self):
        """Ensure the time slider matches the current quarter selection."""
        if self.time_slider is None:
            return

        if self.current_quarter == "OT":
            target_max = self.ot_secs
        else:
            target_max = self.regulation_secs

        if target_max != self._current_time_max:
            self._rebuild_time_slider(target_max)

        show_time = self.current_quarter != "All Quarters"
        self.time_slider.ax.set_visible(show_time)

    
    def update_plot(self, team_name=None, quarter=None, position=None):
        """Update the shot chart based on current filters."""
        if team_name is not None:
            self.current_team = team_name
        if quarter is not None:
            self.current_quarter = quarter
        if position is not None:
            self.current_position = position
        
        if hasattr(self, "time_slider"):
            self._update_time_slider_for_quarter()
            
        if self.time_slider is not None:
            show_time = self.current_quarter != "All Quarters"
            self.time_slider.ax.set_visible(show_time)
        
        # Clear the main axis
        self.ax.clear()

        if self.stable_position is not None:
            self.ax.set_position(self.stable_position)

        draw_half_court(self.ax)

        # Base filter
        filtered_df = self.df
        filtered_df = filtered_df[filtered_df["TEAM_NAME"] == self.current_team]

        # Quarter + time filtering
        if self.current_quarter != "All Quarters":
            filtered_df = filtered_df[
                filtered_df["QUARTER"].astype(str) == self.current_quarter
            ]
            if self.time_slider is not None:
                t_min, t_max = sorted(self.time_slider.val)
                filtered_df = filtered_df[
                    (filtered_df["SECS_LEFT_UNIFIED"] >= t_min)
                    & (filtered_df["SECS_LEFT_UNIFIED"] <= t_max)
                ]

        # Position filtering
        if self.current_position != "All Positions":
            if self.current_position in filtered_df["POSITION_GROUP"].astype(str).unique():
                filtered_df = filtered_df[
                    filtered_df["POSITION_GROUP"].astype(str) == self.current_position
                ]
            else:
                filtered_df = filtered_df[
                    filtered_df["POSITION"].astype(str) == self.current_position
                ]

        # Season filtering
        filtered_df = filtered_df[filtered_df["SEASON_1"] == self.current_year]

        # Aggregate by 2×2 shot zones
        grouped = (
            filtered_df.groupby(["x_bin", "y_bin"])
            .agg(
                count=("SHOT_MADE", "size"),
                fg=("SHOT_MADE", "mean"),
            )
            .reset_index()
        )

        # Player-level stats per zone
        player_groups = (
            filtered_df.groupby(["x_bin", "y_bin", "PLAYER_NAME"])
            .agg(
                player_shots=("SHOT_MADE", "size"),
                player_fg=("SHOT_MADE", "mean"),
            )
            .reset_index()
        )

        # Center of each 2×2 zone in court coordinates
        x_min, y_min = -50, 0
        x_bin_width, y_bin_width = 2, 2
        grouped["x"] = x_min + (grouped["x_bin"] + 0.5) * x_bin_width
        grouped["y"] = y_min + (grouped["y_bin"] + 0.5) * y_bin_width

        # Top players per zone
        best_by_volume = (
            player_groups.sort_values(
                ["x_bin", "y_bin", "player_shots"],
                ascending=[True, True, False],
            )
            .groupby(["x_bin", "y_bin"])
            .first()
        )

        min_shots = 5
        best_by_fg = (
            player_groups[player_groups["player_shots"] >= min_shots]
            .sort_values(
                ["x_bin", "y_bin", "player_fg"],
                ascending=[True, True, False],
            )
            .groupby(["x_bin", "y_bin"])
            .first()
        )

        # Bubble sizes (sqrt scaling)
        min_size = 20
        scale_factor = 40

        if len(grouped) > 0:
            sizes = min_size + np.sqrt(grouped["count"]) * scale_factor
            sizes = np.clip(sizes, min_size, 700)

            self.scatter = self.ax.scatter(
                grouped["x"],
                grouped["y"],
                s=sizes,
                c=grouped["fg"],
                cmap="viridis",
                alpha=0.7,
                zorder=10,
                vmin=0,
                vmax=1,
            )

        # Tooltip with per-zone details
        if hasattr(self, "cursor"):
            self.cursor.remove()

        if len(grouped) > 0:
            self.cursor = mplcursors.cursor(self.scatter, hover=True)

            @self.cursor.connect("add")
            def on_hover(sel):
                idx = sel.index
                row = grouped.iloc[idx]
                x_bin = row["x_bin"]
                y_bin = row["y_bin"]
                total_shots = row["count"]
                fg = row["fg"]

                if (x_bin, y_bin) in best_by_volume.index:
                    bv = best_by_volume.loc[(x_bin, y_bin)]
                    top_vol_player = bv["PLAYER_NAME"]
                    top_vol_shots = int(bv["player_shots"])
                else:
                    top_vol_player = None
                    top_vol_shots = 0

                if (x_bin, y_bin) in best_by_fg.index:
                    ba = best_by_fg.loc[(x_bin, y_bin)]
                    top_acc_player = ba["PLAYER_NAME"]
                    top_acc_fg = float(ba["player_fg"])
                else:
                    top_acc_player = None
                    top_acc_fg = None

                if top_vol_player is not None and top_acc_player is not None:
                    text = (
                        f"Shots: {total_shots}\n"
                        f"FG%: {fg:.2f}\n\n"
                        f"Top Player (Volume): {top_vol_player}\n"
                        f"  Shots: {top_vol_shots}\n\n"
                        f"Top Player (Accuracy): {top_acc_player}\n"
                    )
                elif top_vol_player is not None:
                    text = (
                        f"Shots: {total_shots}\n"
                        f"FG%: {fg:.2f}\n\n"
                        f"Top Player (Volume): {top_vol_player}\n"
                        f"  Shots: {top_vol_shots}\n\n"
                    )
                else:
                    text = (
                        f"Shots: {total_shots}\n"
                        f"FG%: {fg:.2f}\n\n"
                        f"No qualifying players.\n"
                    )

                if top_acc_fg is not None:
                    text += f"  FG%: {top_acc_fg:.2f}"

                sel.annotation.set_text(text)
                sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)

        # Colorbar
        if len(grouped) > 0:
            if self.cbar is None:
                self.cbar = plt.colorbar(self.scatter, ax=self.ax)
                self.cbar.set_label("Field Goal Percentage (FG%)")
                self.stable_position = self.ax.get_position()
            else:
                self.cbar.update_normal(self.scatter)

        # --- Bubble-size legend (shots per zone) ---
        if len(grouped) > 0:
            # Use quantiles instead of min/max so labels are more interpretable
            counts = grouped["count"].values
            if counts.size == 1:
                ref_counts = np.array([int(counts[0])])
            else:
                # 25th, 50th, 90th percentile
                q = np.quantile(counts, [0.25, 0.5, 0.9])
                ref_counts = np.unique(q.round().astype(int))
                ref_counts = ref_counts[ref_counts > 0]  # no zero-shot labels
                if ref_counts.size == 0:
                    ref_counts = np.array([int(counts.max())])

            # Compute legend bubble sizes using the exact same formula
            ref_sizes = min_size + np.sqrt(ref_counts) * scale_factor
            ref_sizes = np.clip(ref_sizes, min_size, 700)

            # Remove previous legend if it exists
            if self.size_legend is not None:
                self.size_legend.remove()
                self.size_legend = None

            # Create dummy scatter handles so legend bubbles use the same 's'
            handles = [
                self.ax.scatter(
                    [], [], s=s, color="gray", alpha=0.7, edgecolor="gray"
                )
                for s in ref_sizes
            ]
            labels = [f"{c} shots" for c in ref_counts]

            self.size_legend = self.ax.legend(
                handles,
                labels,
                title="Shots in Zone",
                loc="upper right",
                bbox_to_anchor=(1.32, 1.00),
                frameon=True,
            )


        self.fig.canvas.draw_idle()


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "clean_shots_with_zones.csv")

    df = pd.read_csv(csv_path)

    fig = plt.figure(figsize=(12, 7))
    ax = plt.axes([0.1, 0.15, 0.8, 0.75])
    
    selector = TeamSelector(df, fig, ax)
    
    plt.show()


if __name__ == "__main__":
    main()
