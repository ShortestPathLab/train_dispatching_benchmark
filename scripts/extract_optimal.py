#!/usr/bin/env python3

import argparse
import pandas as pd
import numpy as np
from pathlib import Path


parser = argparse.ArgumentParser(
    description="Extract optimal solutions from mzn-bench statistics"
)
parser.add_argument(
    "--objective",
    choices=["makespan", "end_sum"],
    required=True,
    help="What objective the statistics optimize",
)
parser.add_argument(
    "--output-missing", help="Path for a file to store the instances that are missing"
)
parser.add_argument("statistics_csv", nargs="*", help="Path to the statistics CSV file")
parser.add_argument("output_csv", help="Path to the output CSV file to update")
parser.add_argument(
    "--use-best-known",
    help="Use best known solution when optimal is missing",
    action="store_true",
)


if __name__ == "__main__":
    args = parser.parse_args()

    files = []
    for file in args.statistics_csv:
        file = pd.read_csv(file)
        files.append(file)

    all = pd.concat(files)
    if args.use_best_known:
        selection = all[(all.status != "ERROR") & (all.status != "UNKNOWN")]
        agg = {"objective": "min"}
    else:
        selection = all[all.status == "OPTIMAL_SOLUTION"]
        agg = {"objective": "mean"}
    optimal = selection.groupby("data_file").agg(agg)
    optimal.objective = optimal.objective.astype(np.int64)
    optimal = optimal.rename(
        columns={
            "objective": "v_makespan" if args.objective == "makespan" else "v_end_sum"
        }
    )

    existing = pd.DataFrame({"data_file": [], "v_makespan": [], "v_end_sum": []})
    if Path(args.output_csv).exists():
        existing = pd.read_csv(
            args.output_csv, dtype={"v_makespan": np.int64, "v_end_sum": np.int64}
        )
        assert list(existing.columns) == ["data_file", "v_makespan", "v_end_sum"]
    existing = existing.set_index("data_file")

    index = existing.index.union(all.data_file.unique())
    data = []
    for i in index:
        point = (-1, -1)
        if i in existing.index:
            point = (existing.loc[i, "v_makespan"], existing.loc[i, "v_end_sum"])
        if i in optimal.index:
            if args.objective == "makespan":
                point = (optimal.loc[i, "v_makespan"], point[1])
            elif args.objective == "end_sum":
                point = (point[0], optimal.loc[i, "v_end_sum"])
        data.append(point)

    out = pd.DataFrame.from_records(
        data, columns=["v_makespan", "v_end_sum"], index=index
    )
    out.to_csv(args.output_csv, index=True)

    if args.output_missing is not None:
        all_data = set(all.data_file)
        missing = all_data.difference(optimal.index)
        model = (
            "../models/solve_makespan.mzn"
            if args.objective == "makespan"
            else "../models/solve_endtimes.mzn"
        )
        data = [f"{file}:{Path(file).parent / 'warmstart.json'}" for file in missing]

        instances = pd.DataFrame(
            {
                "problem": "missing",
                "model": f"{model}:../models/pddl-print.mzn",
                "data_file": data,
            }
        )
        instances.to_csv(args.output_missing, index=False)
