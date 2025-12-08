# NBA Shot Data Cleaning & Court Visualization  
CS439 — Team Project

This repository contains three main Python scripts that work together to download NBA shot data, clean it, generate shot zones, and visualize the resulting dataset on a basketball half-court.

---

## Project Files

### **1. `data_cleaning.py`**
This script:
- Downloads the NBA Shots dataset using `kagglehub` (`mexwell/nba-shots`).
- Loads all season CSV files.
- Keeps only relevant columns.
- Removes rows with missing values in the `POSITION` column.
- Filters out any shots whose coordinates fall outside the half-court range.
- Makes quarter values above 4 "OT" (overtime).
- Combines minutes and seconds together into unified second values.
- Computes:
  - `X_ABS` — absolute x-coordinate.
  - `x_bin` and `y_bin` — 2×2 grid zone bins.
  - `zone_id` — unique ID from 1–625.
- Saves the final processed dataset as **`clean_shots_with_zones.csv`** in the project root.

### **2. `draw_basketball_court.py`**
This script:
- Loads `clean_shots_with_zones.csv`.
- Draws a basketball half-court using Matplotlib patches (hoop, paint, restricted area, 3-pt line, half-court line).
- Uses the same coordinate system as the dataset:
  - `LOC_X` ranges from **-50 to 50** (left → right)
  - `LOC_Y` ranges from **0 to 50** (baseline → half-court line)
- Creates a bubble plot, bubbles sized based on shot frequency within each zone, colored based on FG (Field Goal) Percentage.
- Provides scales for bubble size and bubble color.
- Creates dropdown menus for team, quarter, and position selection.
- Creates sliders for season and time values (12:00-0:00 for regular quarters, 5:00-0:00 for overtime).
- Creates a tooltip for each point, showing the top player for volume and accuracy (after a threshold is reached). 

### **3. `run_pipeline.py`**
This script:
- Runs both `data_cleaning.py` and `draw_basketball_court.py` in succession.
- If `clean_shots_with_zones.csv` exists, `data_cleaning.py` is not run.
- Asks in the command line, after the pre-set graph is closed, whether `clean_shots_with_zones.csv` should be deleted or not.

---

## Requirements

Install dependencies:

```bash
pip install kagglehub pandas matplotlib mplcursors
```

---

## How to Run the Project

### Step 1 — Run `run_pipeline.py`

This script **must be run first**.

From the project root, run:

```bash
python run_pipeline.py
```
The script will run the files `data_cleaning.py` and `draw_basketball_court.py` in sucession.
It will generate a graph as outlined in `draw_basketball_court.py`.
The process may take a few minutes.

If `clean_shots_with_zones.csv` already exists, `data_cleaning.py` is not run. Additionally, the program
will ask in the command line, after the pre-set graph is closed, whether `clean_shots_with_zones.csv` should
be deleted or not.

---