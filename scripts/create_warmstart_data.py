from pathlib import Path
import sys
import json
import os

from ruamel.yaml import YAML


yaml = YAML(typ="safe", pure=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: store_warm_start_solns.py <result_dir>")
        sys.exit(1)

    results = Path(sys.argv[1]).absolute()
    assert Path("../data").exists(), "unable to locate data directory"
    os.chdir("../data")
    if not results.exists():
        print(f"Error: {results} does not exist")
        sys.exit(1)
    if not results.is_dir():
        print(f"Error: {results} is not a directory")
        sys.exit(1)

    for file in results.glob("*_chuffed_fixed_fixedorder_col0_sol.yml"):
        with file.open() as fp:
            solns = yaml.load(fp)
            sol = solns[0]

            file = Path(f"{str(Path(sol["data_file"]).with_suffix(""))}-warmstart.json")
            data = {
                "wm_start": sol["solution"]["v_start"],
                "wm_route": sol["solution"]["v_route"],
                "wm_dwell": sol["solution"]["v_dwell"],
            }
            file.write_text(json.dumps(data))
