import argparse
import csv
import os
from pathlib import Path

argparser = argparse.ArgumentParser(
    description="Create instance files for MiniZinc benchmarks."
)
argparser.add_argument("--warm-start", action="store_true")

if __name__ == "__main__":
    args = argparser.parse_args()

    goals = (
        ["sat", "makespan", "endtimes"]
        if not args.warm_start
        else ["makespan", "endtimes"]
    )
    ws_str = "_warmstart" if args.warm_start else ""

    fieldnames = ["problem", "model", "data_file"]

    assert Path("../data/").exists()
    os.chdir("../data/")
    for goal in goals:
        assert Path(f"../models/solve_{goal}.mzn").exists()

        with open(f"instances_{goal}{ws_str}_all.csv", "w", newline="") as csvfile:
            writer_all = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer_all.writeheader()

            for dataset in ["icaps21", "cp2025"]:
                data_dir = Path(f"./{dataset}")
                assert data_dir.exists(), f"Data directory {data_dir} does not exist"

                with open(
                    f"instances_{goal}{ws_str}_{dataset}.csv", "w", newline=""
                ) as csvfile:
                    writer_single = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer_single.writeheader()

                    for data in data_dir.glob("*.dzn"):
                        warmstart = (
                            f":{str(data.with_suffix(''))}-warmstart.json"
                            if args.warm_start
                            else ""
                        )
                        row = {
                            "problem": dataset,
                            "model": f"../models/solve_{goal}.mzn:../models/pddl-print.mzn",
                            "data_file": f"{str(data)}{warmstart}",
                        }
                        writer_single.writerow(row)
                        writer_all.writerow(row)
