from datetime import timedelta
from pathlib import Path
import copy

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

# Tried redundant column constraint options
# NOTE: duplicates all configurations for each enabled option.
# - 0: No redundant constraints on columns.
# - 1: Redundant constraints on all columns.
# - 2: Redundant constraints on border and platform columns.
# - 3: Redundant constraints on platform columns.
# - 4: Redundant constraints on border columns.
COLUMN_OPT = [0, 1, 2, 3, 4]

# Time limit for compilation + solving for each instance.
TIME_LIMIT = timedelta(minutes=5)

inst_prefixes = ["all", "icaps21", "cp2025"]
model_prefixes = ["sat", "makespan", "endtimes"]
instance = Path(f"../data/instances_{model_prefixes[MODEL]}_{inst_prefixes[INSTANCES]}.csv")
result = Path(f"../raw_results/{model_prefixes[MODEL]}_{inst_prefixes[INSTANCES]}")

CHUFFED = minizinc.Solver.lookup("org.chuffed.chuffed")
CPOPTIMIZER = minizinc.Solver.lookup("com.ibm.cpo")
CPSAT = minizinc.Solver.lookup("cp-sat")
# CPSAT = minizinc.Solver.load(Path("/opt/easybuild/software/OR-Tools/9.12.4544/share/minizinc/solvers/cp-sat.msc"))
GUROBI = minizinc.Solver.lookup("gurobi")

base_configurations = [
    Configuration(
        name="chuffed_fixed_standard",
        solver=CHUFFED,
        extra_model_files=[Path("../models/search-std.mzn")],
    ),
    Configuration(
        name="chuffed_fixed_standardrestart",
        solver=CHUFFED,
        extra_data={"restart_opt": 1},
        extra_model_files=[Path("../models/search-std.mzn")],
    ),
    Configuration(
        name="chuffed_fixed_priority",
        solver=CHUFFED,
        extra_model_files=[Path("../models/search-prio.mzn")],
    ),
    Configuration(
        name="chuffed_fixed_priorityrestart",
        solver=CHUFFED,
        extra_data={"restart_opt": 1},
        extra_model_files=[Path("../models/search-prio.mzn")],
    ),
    Configuration(
        name="chuffed_fixed_fixedorder",
        solver=CHUFFED,
        extra_model_files=[Path("../models/search-fo-prio.mzn")],
    ),
    Configuration(
        name="chuffed_fixed_fixedorderrestart",
        solver=CHUFFED,
        extra_data={"restart_opt": 1},
        extra_model_files=[Path("../models/search-fo-prio.mzn")],
    ),
    Configuration(
        name="chuffed_free_priority",
        solver=CHUFFED,
        free_search=True,
        extra_model_files=[Path("../models/search-prio.mzn")],
    ),
    Configuration(
        name="cpotimizer_free_fixedorder",
        solver=CPOPTIMIZER,
        free_search=True,
        extra_model_files=[Path("../models/search-fo-prio.mzn")],
    ),
    Configuration(
        name="gurobi_free_fixedorder",
        solver=GUROBI,
        free_search=True,
        extra_model_files=[Path("../models/search-fo-prio.mzn")],
    ),
    Configuration(
        name="cpsat_fixed_standard",
        solver=CPSAT,
        extra_model_files=[Path("../models/search-std.mzn")],
    ),
    Configuration(
        name="cpsat_fixed_fixedorder",
        solver=CPSAT,
        extra_model_files=[Path("../models/search-fo-prio.mzn")],
    ),
    Configuration(
        name="cpsat_free_fixedorder",
        solver=CPSAT,
        free_search=True,
        extra_model_files=[Path("../models/search-fo-prio.mzn")],
    ),
]

configurations = []
for i in COLUMN_OPT:
    for conf in base_configurations:
        x = copy.deepcopy(conf)
        x.name = conf.name + f"_col{i}"
        x.extra_data["col_opt"] = i
        configurations.append(x)

schedule(
    job_name="Train Dispatching",
    instances=instance,
    timeout=TIME_LIMIT,
    configurations=configurations,
    nodelist=["critical001"],
    # nodelist=["extra001"],
    memory=16384,
    output_dir=result,
    debug=False,
)
