import kagglehub
import pandas as pd
import os

# load in data
path = kagglehub.dataset_download("mexwell/nba-shots")

print("Dataset folder:", path)
print("Files in folder:", os.listdir(path))
all_files = [f for f in os.listdir(path) if f.endswith(".csv")]

df_list = []
for file in all_files:
    file_path = os.path.join(path, file)
    print(f"Loading {file}...")
    temp_df = pd.read_csv(file_path)
    df_list.append(temp_df)

# Combine all season files into a single dataset
df = pd.concat(df_list, ignore_index=True)

print(df.shape)
print(df.head())
print(df.info())

# keeping only relevant columns
keep_cols = [
    "SEASON_1", "TEAM_ID", "TEAM_NAME", "PLAYER_ID", "POSITION", "POSITION_GROUP",
    "HOME_TEAM", "AWAY_TEAM", "SHOT_MADE", "ACTION_TYPE", "SHOT_TYPE",
    "BASIC_ZONE", "ZONE_NAME", "ZONE_ABB", "ZONE_RANGE", "LOC_X", "LOC_Y",
    "QUARTER", "MINS_LEFT", "SECS_LEFT"
]
df_cleaned = df[keep_cols].copy()

# 7930 missing values - all in POSITION column
df_cleaned = df_cleaned.dropna()

# Make QUARTER values greater than 4 into value "OT"
df_cleaned["QUARTER"] = df_cleaned["QUARTER"].apply(lambda x: x if x <= 4 else "OT")

# Unify minutes and seconds left into single column SECS_LEFT_UNIFIED
df_cleaned['SECS_LEFT_UNIFIED'] = df_cleaned['MINS_LEFT'] * 60 + df_cleaned['SECS_LEFT']

# Drop the old columns
df_cleaned = df_cleaned.drop(columns=['MINS_LEFT', 'SECS_LEFT'])

# removed all rows with x or y values outside 0-50 range (mainly back court shots)
df_cleaned = df_cleaned[
    ~(
        (df_cleaned["LOC_X"].abs() > 50) | 
        (df_cleaned["LOC_Y"] > 50) | 
        (df_cleaned["LOC_X"].abs() < 0) | 
        (df_cleaned["LOC_Y"].abs() < 0)
    )
]
print("Cleaned dataset shape:", df_cleaned.shape)
print(df_cleaned.head())
print(df_cleaned.info())

df_cleaned["X_ABS"] = df_cleaned["LOC_X"].abs()

# Each interval of 2 in [0, 50] --- bin 0 to bin 24 in each direction
df_cleaned["x_bin"] = (df_cleaned["X_ABS"] // 2).astype(int)
df_cleaned["y_bin"] = (df_cleaned["LOC_Y"] // 2).astype(int)

# ID each zone from 1 to 625
df_cleaned["zone_id"] = (df_cleaned["x_bin"] * 25 + df_cleaned["y_bin"] + 1).astype(int)

print("Cleaned + zoned dataset shape:", df_cleaned.shape)
print(df_cleaned[["LOC_X", "LOC_Y", "X_ABS", "x_bin", "y_bin", "zone_id"]].head())

# Save final dataset with zones as CSV in repo root
output_path = "clean_shots_with_zones.csv"
df_cleaned.to_csv(output_path, index=False)
