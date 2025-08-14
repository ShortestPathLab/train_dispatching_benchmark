#!/usr/bin/env python3

import argparse
import pandas as pd

parser = argparse.ArgumentParser(
    description="Small tool to fix the statistics in the train dispatching experiments"
)
parser.add_argument("statistics_csv")

if __name__ == "__main__":
    args = parser.parse_args()

    file = pd.read_csv(args.statistics_csv)

    # Fix solver outputting ALL_SOLUTIONS when should be SATISFIED
    file.loc[file.status == "ALL_SOLUTIONS", "status"] = "SATISFIED"

    # Fix solver outputting UNKNOWN, but not running until timeout (we assume
    # this is an error)
    file.loc[(file.status == "UNKNOWN") & (file.time < 250), "status"] = "ERROR"

    # Remove any additional warm_start data from the data_file column
    file.data_file = file.data_file.apply(lambda files: files.split(":")[0])

    file = file.sort_values(by=["configuration", "data_file"])

    file.to_csv(args.statistics_csv, index=False)
