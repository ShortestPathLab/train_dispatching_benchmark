import argparse
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

argparser = argparse.ArgumentParser(
    description="Create a plot of the difference between the planner and various MiniZinc configurations"
)
argparser.add_argument("planner_results")
argparser.add_argument("minizinc_statistics", nargs="*")
argparser.add_argument("output_file")
argparser.add_argument(
    "--objective", default="end_sum", choices=["makespan", "end_sum"]
)
argparser.add_argument("--solution-file", default=False, action="store_true")
argparser.add_argument("--baseline", type=str)
argparser.add_argument("--keep", type=str, nargs="*")
argparser.add_argument("--rename", type=str, nargs="*")
argparser.add_argument("--output-solver-total", default=False, action="store_true")
argparser.add_argument("--splitx-at", type=int, default=None)


def create_diff_line(baseline, conf_stats, name):
    diffs = []
    instances = conf_stats[
        (conf_stats.status != "UNKNOWN") & (conf_stats.status != "ERROR")
    ].index
    for inst in instances:
        assert inst in baseline.index, f"Instance {inst} not found in baseline"
        base = (
            baseline.objective.loc[inst] if baseline.objective.loc[inst] > 0 else None
        )
        obj = conf_stats.objective.loc[inst]
        assert obj is not None

        if base is None:
            diffs.append(-obj)
        else:
            diffs.append(obj - base)

    diffs = sorted(diffs)
    sum = 0
    points = []
    for d in diffs:
        sum += d
        points.append(sum)

    t = pd.DataFrame({"diff": points})
    t["instances"] = list(range(1, 1 + len(points)))
    t["configuration"] = name
    return t


if __name__ == "__main__":
    args = argparser.parse_args()

    if args.output_file.endswith(".pgf"):
        matplotlib.use("pgf")
        matplotlib.rcParams.update(
            {
                "pgf.texsystem": "pdflatex",
                "font.family": "serif",
                "font.size": 15,
                "legend.fontsize": 12,
                "text.usetex": True,
                "pgf.rcfonts": False,
            }
        )

    planner = pd.read_csv(args.planner_results)
    planner = planner.rename(
        columns={
            "v_makespan" if args.objective == "makespan" else "v_end_sum": "objective"
        }
    ).set_index("data_file", drop=True, verify_integrity=True)
    if args.baseline is not None:
        baseline = pd.read_csv(args.baseline)
        baseline = baseline.rename(
            columns={
                "v_makespan"
                if args.objective == "makespan"
                else "v_end_sum": "objective"
            }
        ).set_index("data_file", drop=True, verify_integrity=True)
    else:
        baseline = planner

    frames = []
    for file in args.minizinc_statistics:
        frames.append(pd.read_csv(file))
    stats = pd.concat(frames)

    if args.solution_file:
        stats = stats.drop(columns=["objective"]).rename(
            columns={
                "v_makespan"
                if args.objective == "makespan"
                else "v_end_sum": "objective"
            }
        )
        stats["status"] = "SATISFIED"

    configurations = stats.configuration.unique()
    frames = []
    for conf in configurations:
        conf_stats = stats[stats.configuration == conf].set_index(
            "data_file", drop=True, verify_integrity=True
        )
        frames.append(create_diff_line(baseline, conf_stats, conf))

    if args.baseline is not None:
        frames.append(create_diff_line(baseline, planner, "Planner"))

    data = pd.concat(frames, ignore_index=True)

    if args.output_solver_total:
        total_idxs = data.groupby("configuration")["instances"].idxmax().values
        totals = data.loc[total_idxs]
        totals.set_index("configuration", inplace=True, verify_integrity=True)
        print("### Solver Totals ###\n", totals.to_string(), "\n")

    if args.keep is not None:
        rename = args.keep if len(args.rename) is None else args.rename
        assert len(args.keep) == len(args.rename), (
            "The number of `--keep` arguments must match the number of `--rename` arguments."
        )

        frames = [data[data.configuration == "Planner"]]
        for i in range(len(rename)):
            f = data[data.configuration == args.keep[i]]
            f.loc[:, "configuration"] = rename[i]
            frames.append(f)
        data = pd.concat(frames)

    max = data["diff"].max()

    if args.splitx_at is None:
        fig, ax = plt.subplots()
        sns.lineplot(
            ax=ax,
            data=data,
            y="diff",
            x="instances",
            hue="configuration",
            style="configuration",
            markers=True,
            markevery=[-1],
            markersize=10,
            dashes=False,
            clip_on=False,
        )
        ax.set(ylabel="", xlabel="", yscale="symlog")
        ax.set_xlim(left=0, right=len(baseline.index))
        ax.set_ylim(bottom=0, top=max * 1.5)
        ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(base=25))
        ax.get_legend().set(loc="upper left")
    else:
        fig, (ax_before, ax) = plt.subplots(
            1, 2, sharey=True, gridspec_kw={"width_ratios": [1, 6]}
        )
        fig.subplots_adjust(wspace=0.05)

        sns.lineplot(
            ax=ax_before,
            data=data,
            y="diff",
            x="instances",
            hue="configuration",
            style="configuration",
            markers=False,
            dashes=False,
        )

        sns.lineplot(
            ax=ax,
            data=data[data.instances >= args.splitx_at],
            y="diff",
            x="instances",
            hue="configuration",
            style="configuration",
            markers=True,
            markevery=[-1],
            markersize=10,
            dashes=False,
            clip_on=False,
        )

        ax_before.set(ylabel="", xlabel="", yscale="symlog")
        ax.set(ylabel="", xlabel="")
        ax.set_ylim(bottom=0, top=max * 1.5)
        ax_before.set_xlim(left=0, right=13)
        ax.set_xlim(left=args.splitx_at, right=len(baseline.index))
        ax_before.spines.right.set_visible(False)
        ax.spines.left.set_visible(False)
        ax_before.yaxis.tick_left()
        ax.yaxis.tick_right()
        ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(base=25))
        ax_before.set_xticks([0])
        d = 0.5  # proportion of vertical to horizontal extent of the slanted line
        kwargs = dict(
            marker=[(-d, -1), (d, 1)],
            markersize=12,
            linestyle="none",
            color="k",
            mec="k",
            mew=1,
            clip_on=False,
        )
        ax_before.plot([1, 1], [1, 0], transform=ax_before.transAxes, **kwargs)
        ax.plot([0, 0], [0, 1], transform=ax.transAxes, **kwargs)
        ax_before.get_legend().remove()
        ax.get_legend().set(bbox_to_anchor=(-0.19, 0.98), loc="upper left")

    ax.get_legend().set_title("Solver")
    # fig.tight_layout()
    fig.subplots_adjust(left=0.07, right=0.97, bottom=0.06, top=0.97)
    fig.savefig(args.output_file)
