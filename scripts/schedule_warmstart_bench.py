from datetime import timedelta
from pathlib import Path

import minizinc

from mzn_bench import Configuration, schedule

# The chosen instance set.
# - 0: ALL
# - 1: ICAPS21
# - 2: CP2025
INSTANCES = 0

# The solution goal.
# - 0: Find a solution (aka satisfaction problem).
# - 1: Minimize the makespan.
# - 2: Minimize the sum of end times.
MODEL = 2
assert MODEL != 0, "Satisfiability is not interesting when warmstarting"

# Time limit for compilation + solving for each instance.
TIME_LIMIT = timedelta(minutes=5)

inst_prefixes = ["all", "icaps21", "cp2025"]
model_prefixes = ["sat", "makespan", "endtimes"]
instance = Path(
    f"../data/instances_{model_prefixes[MODEL]}_warmstart_{inst_prefixes[INSTANCES]}.csv"
)
result = Path(
    f"../raw_results/{model_prefixes[MODEL]}_{inst_prefixes[INSTANCES]}_warmstart"
)

with_column_0 = {"col_opt": 0}
with_column_4 = {"col_opt": 4}

CHUFFED = minizinc.Solver.lookup("org.chuffed.chuffed")
CPSAT = minizinc.Solver.lookup("cp-sat")
# CPSAT = minizinc.Solver.load(Path("/opt/easybuild/software/OR-Tools/9.12.4544/share/minizinc/solvers/cp-sat.msc"))
GUROBI = minizinc.Solver.lookup("gurobi")

schedule(
    job_name="Train Dispatching",
    instances=instance,
    timeout=TIME_LIMIT,
    configurations=[
        Configuration(
            name="gurobi_free_fixedorderwarmstart_column0",
            solver=GUROBI,
            free_search=True,
            extra_model_files=[Path("../models/search-fo-prio-warmstart.mzn")],
            extra_data=with_column_0,
        ),
        Configuration(
            name="gurobi_free_fixedorderwarmstart_column4",
            solver=GUROBI,
            free_search=True,
            extra_model_files=[Path("../models/search-fo-prio-warmstart.mzn")],
            extra_data=with_column_4,
        ),
        Configuration(
            name="cpsat_free_fixedorderwarmstart_column0",
            solver=CPSAT,
            free_search=True,
            extra_model_files=[Path("../models/search-fo-prio-warmstart.mzn")],
            extra_data=with_column_0,
        ),
    ],
    nodelist=["critical001"],
    # nodelist=["extra001"],
    memory=16384,
    output_dir=result,
    debug=False,
)
