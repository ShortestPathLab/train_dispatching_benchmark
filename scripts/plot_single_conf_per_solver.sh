PICEXT="pgf"

uv run ./plot_cumulative_diff.py --baseline best_all.csv --objective end_sum \
../results/planner_all.csv ../results/statistics_endtimes_all.csv ../results/plot_solver1_endtimes_all.${PICEXT} \
--keep chuffed_fixed_priorityrestart_col4 cpotimizer_free_fixedorder_col0 gurobi_free_fixedorder_col0 cpsat_free_fixedorder_col0 gurobi_free_fixedorderwarmstart_column4 \
--rename "Chuffed" "CP Optimizer" "Gurobi" "CP-SAT" "Gurobi Warm Start" \
--splitx-at 85

uv run ./plot_cumulative_diff.py --baseline best_all.csv --objective makespan \
../results/planner_all.csv ../results/statistics_makespan_all.csv ../results/plot_solver1_makespan_all.${PICEXT} \
--keep chuffed_fixed_fixedorder_col0 cpotimizer_free_fixedorder_col0 gurobi_free_fixedorder_col0 cpsat_free_fixedorder_col0 gurobi_free_fixedorderwarmstart_column4 \
--rename "Chuffed" "CP Optimizer" "Gurobi" "CP-SAT" "Gurobi Warm Start" \
--splitx-at 118

uv run ./plot_cumulative_diff.py --solution-file --baseline best_all.csv --objective end_sum \
../results/planner_all.csv ../results/solutions_sat_all.csv ../results/plot_solver1_satendsum_all.${PICEXT} \
--keep chuffed_fixed_priorityrestart_col0 cpotimizer_free_fixedorder_col0 gurobi_free_fixedorder_col0 cpsat_fixed_fixedorder_col0 \
--rename "Chuffed" "CP Optimizer" "Gurobi" "CP-SAT"

uv run ./plot_cumulative_diff.py --solution-file --baseline best_all.csv --objective makespan \
../results/planner_all.csv ../results/solutions_sat_all.csv ../results/plot_solver1_satmakespan_all.${PICEXT} \
--keep chuffed_fixed_fixedorder_col0 cpotimizer_free_fixedorder_col0 gurobi_free_fixedorder_col0 cpsat_fixed_fixedorder_col0 \
--rename "Chuffed" "CP Optimizer" "Gurobi" "CP-SAT"
