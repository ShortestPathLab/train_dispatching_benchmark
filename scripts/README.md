# Scripts

## Running Experiments

To run the experiments, follow these steps:

1. Start in the root directory of the repository.
2. Run `source bench_env.sh` to set up the environment.
   This uses `uv` to setup a virtual environment and install all Python dependencies, download the right version of MiniZinc, and will use `module load` to load installed modules from a cluster environment.
3. Navigate to the `scripts` directory: `cd scripts`
4. Run `python schedule_bench.py` or `python schedule_warmstart_bench.py` to run the normal solvers or the warmstarted solvers respectively.
   This will schedule individual MiniZinc runs using SLURM.

This will create seperate files for each individual MiniZinc run combined in a folder for the experiment in the `<root>/raw_results` directory.

## Processing Results

The results in `raw_results` are processed using `mzn-bench` to create CSV files that collects all statistical information reported by MiniZinc and the solvers.

For each type of objective, a command such as the following is used to create the `<root>/results/statistics_*.csv` files:

```
uv run mzn-bench collect-statistics raw_results/results_endtimes_all raw_results/results_endtimes_all_warmstart  results/statistics_endtimes_all.csv
```

For satisfaction runs, the statistical information does not contain an `objective` value.
Instead the following command can be used to extract the different makespan and sum of end times as part of the `<root>/results/solution_sat_all.csv` file:

```
uv run mzn-bench collect-objectives --param v_makespan --param v_end_sum results_sat_all/ solutions_sat_all.csv
```

## Other Scripts

The following other helper scripts are contained in this directory:

- `create_instance_files.py`: This script generated the instance CSV files in the `<root>/data` directory used by the `schedule_bench.py` and `schedule_warmstart_bench.py` scripts to determine which files belong to each instance.
- `create_table.py`: This script generated the (LaTeX) table that summarizes the results for the paper.
- `create_warmstart_data.py`: This script generates the files containing the solutions that are used to warmstart the solvers when using `schedule_warmstart_bench.py`.
- `extract_optimal.py`: This script extracts the optimal/best known solutions from the aggregated CSV results, to be used as a baseline by other scripts.
- `fix_statistics.py`: This script fixes the statistics of OR-Tools in the aggregated CSV results. (The solver incorrectly reports OPTIMAL when it is SATISFIED, and UNKNOWN when it is ERROR).
- `plot_cumulative_diff.py`: This script creates the cumulative line plots, like the ones shown in the paper.
- `plot_single_conf_per_solver.sh`: This creates the specific cumulative line plots used in the paper, choosing the best configuration for each solver (calling `plot_cumulative_diff.py`).

Note that most of these scripts have some additional `--help` information about their accepted arguments.
