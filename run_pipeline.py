import sys
import subprocess
from pathlib import Path


def main():
    # CSV created by data_cleaning.py
    csv_path = Path(__file__).with_name("clean_shots_with_zones.csv")

    try:
        # 1. Only run data_cleaning.py if CSV does NOT already exist
        if csv_path.exists():
            print(f"{csv_path.name} already exists. Skipping data_cleaning.py.")
        else:
            print(f"{csv_path.name} not found. Running data_cleaning.py...")
            subprocess.run(
                [sys.executable, "data_cleaning.py"],
                check=True,
            )

        # 2. Run draw_basketball_court.py
        print("Running draw_basketball_court.py...")
        subprocess.run(
            [sys.executable, "draw_basketball_court.py"],
            check=True,
        )

    except subprocess.CalledProcessError as e:
        # If either script fails, report the error but still go to the prompt below
        print(f"Error while running: {e.cmd}")
        print(e)

    finally:
        # 3. Ask whether to delete the CSV file
        if csv_path.exists():
            answer = input(
                f"\nDo you want to delete {csv_path.name}? (Y/N): "
            ).strip().lower()

            if answer in ("y", "yes"):
                csv_path.unlink()
                print(f"Deleted {csv_path.name}.")
            else:
                print(f"Keeping {csv_path.name}.")
        else:
            print(f"\nNo CSV found at: {csv_path}")


if __name__ == "__main__":
    main()
