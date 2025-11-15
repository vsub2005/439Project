import sys
import subprocess
from pathlib import Path


def main():
    # CSV created by data_cleaning.py
    csv_path = Path(__file__).with_name("clean_shots_with_zones.csv")

    try:
        # 1. Run data_cleaning.py
        subprocess.run(
            [sys.executable, "data_cleaning.py"],
            check=True,
        )

        # 2. Run draw_basketball_court.py
        subprocess.run(
            [sys.executable, "draw_basketball_court.py"],
            check=True,
        )

    finally:
        # 3. Delete the resulting CSV file afterward
        if csv_path.exists():
            csv_path.unlink()
            print(f"Deleted CSV: {csv_path}")
        else:
            print(f"No CSV found to delete at: {csv_path}")


if __name__ == "__main__":
    main()
