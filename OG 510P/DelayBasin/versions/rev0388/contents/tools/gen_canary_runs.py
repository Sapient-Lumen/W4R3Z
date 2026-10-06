import pathlib

from canary_runs_lib import write_canary_runs

ROOT = pathlib.Path(__file__).resolve().parents[1]
payload = write_canary_runs(ROOT)
print(f"wrote CANARY-RUNS.json ({payload['scorecard']['observed_score']}/{payload['scorecard']['max_score']})")
