import argparse
import pandas as pd

argparser = argparse.ArgumentParser(
    description="Create a table to compare the different Solver configurations"
)
argparser.add_argument("planner_results")
argparser.add_argument("minizinc_statistics")
argparser.add_argument(
    "--objective", default="end_sum", choices=["makespan", "end_sum"]
)
argparser.add_argument("--solution-file", default=False, action="store_true")
argparser.add_argument("--redundant-pivot", default=False, action="store_true")
argparser.add_argument("--no-latex", default=False, action="store_true")
# argparser.add_argument("--baseline", type=str)


VBS = ["Chuffed", "CP-SAT"]


def opt(series):
    return (series == "OPTIMAL_SOLUTION").sum()


def sat(series):
    return (series == "SATISFIED").sum() + opt(series)


def pretty_slv(name):
    slv = name
    if name == "chuffed":
        slv = "Chuffed"
    elif name == "cpotimizer":
        slv = "CP Optim."
    elif name == "cpsat":
        slv = "CP-SAT"
    elif name == "gurobi":
        slv = "Gurobi"
    return slv


def pretty_search(row):
    free = row["search1"]
    heuristic = row["search2"]
    search = ""
    if heuristic == "fixedorderwarmstart":
        search = "warm start"
    elif free == "free":
        search = "free"
    elif heuristic == "standard":
        search = "standard"
    elif heuristic == "standardrestart":
        search = "standard+"
    elif heuristic == "fixedorder":
        search = "fixed-order"
    elif heuristic == "fixedorderrestart":
        search = "fixed-order+"
    elif heuristic == "priority":
        search = "priority"
    elif heuristic == "priorityrestart":
        search = "priority+"
    return search


def col_number(name):
    if name == "col0" or name == "column0" or name is None:
        col = "none"
    elif name == "col1":
        col = "all"
    elif name == "col2":
        col = "b + p"
    elif name == "col3":
        col = "platform"
    elif name == "col4" or name == "column4":
        col = "border"
    else:
        raise ValueError(f"Unknown column: {name}")
    return col


def sort_val(val):
    name = val.name[0]
    if name == "Planner":
        name = "AAAAAAAAAAAAAAAAAAAAAAAAA"
    search = 0
    str_search = val.name[1]
    if str_search == "standard" or str_search == "":
        search = 1
    elif str_search == "standard+":
        search = 2
    elif str_search == "fixed-order":
        search = 3
    elif str_search == "fixed-order+":
        search = 4
    elif str_search == "priority":
        search = 5
    elif str_search == "priority+":
        search = 6
    elif str_search == "free":
        search = 7
    elif str_search == "warm start":
        search = 8
    elif str_search == "virt. best":
        search = 9
    else:
        raise ValueError(f"Invalid search: {str_search}")

    col = 0
    str_col = val.name[2]
    if str_col == "none":
        col = 0
    elif str_col == "border":
        col = 2
    elif str_col == "platform":
        col = 3
    elif str_col == "b + p":
        col = 4
    elif str_col == "all":
        col = 5
    elif str_col == "virt. best":
        col = 6
    else:
        raise ValueError(f"Invalid column constraint: {str_col}")
    return (name.lower(), search, col)


def sort_col(val):
    str_col = val[0]
    if str_col == "none":
        col = 0
    elif str_col == "border":
        col = 2
    elif str_col == "platform":
        col = 3
    elif str_col == "b + p":
        col = 4
    elif str_col == "all":
        col = 5
    elif str_col == "virt. best":
        col = 6
    else:
        raise ValueError(f"Invalid column constraint: {str_col}")

    str_col = val[1]
    if str_col == "opt":
        x = 1
    elif str_col == "sat":
        x = 2
    elif str_col == "time":
        x = 3
    else:
        raise ValueError(f"Unexpected column in table: {str_col}")
    return (col, x)


def virt_best(rows):
    ok = rows[(rows.status == "OPTIMAL_SOLUTION") | (rows.status == "SATISFIED")]
    if len(ok) > 0:
        if "end_sum" in ok.columns:
            ok = ok[ok.end_sum == ok.end_sum.min()]
        else:
            ok = ok[ok.makespan == ok.makespan.min()]
        row = ok[ok.time == ok.time.min()].iloc[0].to_dict()
    else:
        row = rows.iloc[0].to_dict()
    return row


TIMEOUT = 300

if __name__ == "__main__":
    args = argparser.parse_args()

    planner = pd.read_csv(args.planner_results)
    planner["configuration"] = "Planner"
    planner.loc[planner.status != "SATISFIED", "time"] = TIMEOUT

    # if args.baseline is not None:
    #     baseline = pd.read_csv(args.baseline)
    #     baseline = baseline.rename(
    #         columns={
    #             "v_makespan"
    #             if args.objective == "makespan"
    #             else "v_end_sum": "objective"
    #         }
    #     ).set_index("data_file", drop=True, verify_integrity=True)
    # else:
    #     baseline = planner

    stats = pd.read_csv(args.minizinc_statistics)

    if args.solution_file:
        stats = stats.drop(columns=["objective"])
        stats["status"] = "SATISFIED"
        stats.loc[stats.time > TIMEOUT, "time"] = TIMEOUT
    else:
        stats = stats.rename(
            columns={
                "objective": "v_makespan"
                if args.objective == "makespan"
                else "v_end_sum"
            }
        )
        stats.loc[
            (stats.status != "OPTIMAL_SOLUTION") | (stats.time > TIMEOUT), "time"
        ] = TIMEOUT

    data = {
        "solver": pd.concat([planner.configuration, stats.configuration]),
        "data_file": pd.concat([planner.data_file, stats.data_file]),
        "time": pd.concat([planner.time, stats.time]),
        "status": pd.concat([planner.status, stats.status]),
    }
    if "v_makespan" in stats.columns:
        data["makespan"] = pd.concat([planner.v_makespan, stats.v_makespan])
    if "v_end_sum" in stats.columns:
        data["end_sum"] = pd.concat([planner.v_end_sum, stats.v_end_sum])

    stats = pd.DataFrame(data=data)

    # Extract solver, search, and redundant column constraint from configuration name
    stats[["solver", "search1", "search2", "column"]] = stats.solver.str.split(
        "_", expand=True
    )
    stats.solver = stats.solver.apply(pretty_slv)
    stats["search"] = stats[["search1", "search2"]].apply(pretty_search, axis=1)
    stats = stats.drop(columns=["search1", "search2"])
    stats.column = stats.column.apply(col_number)

    vbs = []
    for slv in VBS:
        cols = stats[stats.solver == slv].column.unique()
        for col in cols:
            for dat in stats.data_file.unique():
                data = stats[
                    (stats.solver == slv)
                    & (stats.column == col)
                    & (stats.data_file == dat)
                ]
                if len(data) > 0:
                    row = virt_best(data)
                    row["search"] = "virt. best"
                    vbs.append(row)
    vbs = pd.DataFrame.from_records(vbs)
    stats = pd.concat([stats, vbs])
    vbs = []
    for slv in VBS:
        searches = stats[stats.solver == slv].search.unique()
        for search in searches:
            for dat in stats.data_file.unique():
                data = stats[
                    (stats.solver == slv)
                    & (stats.search == search)
                    & (stats.data_file == dat)
                ]
                if len(data) > 0:
                    row = virt_best(data)
                    row["column"] = "virt. best"
                    vbs.append(row)
    vbs = pd.DataFrame.from_records(vbs)
    stats = pd.concat([stats, vbs])

    agg = {
        "status": [opt, sat],
        "time": "mean",
    }
    extra_column = []
    if "makespan" in stats.columns:
        agg["makespan"] = "mean"
        extra_column.append("makespan")
    if "end_sum" in stats.columns:
        agg["end_sum"] = "mean"
        extra_column.append("end_sum")
    result = stats.groupby(["solver", "search", "column"]).agg(agg)
    result.time = result.time.round(0)
    result = result.astype(int)

    # Order the different solvers + configurations
    result = result.iloc[result.apply(sort_val, axis=1).argsort()]
    result.columns = ["opt", "sat", "time"] + extra_column

    if args.redundant_pivot:
        pivot = result.pivot_table(
            index=["solver", "search"],
            columns="column",
            values=["opt", "sat", "time"],
            fill_value=0,
        )
        pivot.columns = pivot.columns.swaplevel(0, 1)
        columns = list(pivot.columns)
        columns = sorted(columns, key=sort_col)
        result = pivot[columns].astype(int)

    if args.solution_file:
        result = result.drop(columns=["opt"])

    if args.no_latex:
        print(result.to_string())
    else:
        print(result.to_latex())
