from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_accel import PROBE_COLUMNS, cpp_toolchain_status, probe_table_cpp
from src.muc5.deckspace import DeckVector
from src.muc5.payoff import write_csv
from src.muc5.probability import deck_probe

COLS = ["deck_size", "Island", "Counterspell", "ForceOfWill", "JaceTheMindSculptor", "OverlordOfTheFloodpits"]


def main() -> None:
    data = ROOT / "data"
    status = cpp_toolchain_status(try_build=True).as_dict()
    df = pd.read_csv(data / "deck_space_all.csv.gz", usecols=COLS, nrows=50000)
    arr = df.to_numpy(dtype=np.int32, copy=True)

    t0 = time.perf_counter()
    cpp_out = probe_table_cpp(arr)
    t_cpp = time.perf_counter() - t0

    sample_n = min(2000, len(arr))
    t1 = time.perf_counter()
    py_rows = []
    for row in arr[:sample_n]:
        p = deck_probe(DeckVector(int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5])))
        py_rows.append([
            p.p_keepable_2_to_5_islands,
            p.p_force_plus_pitch_open7,
            p.p_counterspell_online_turn2_play,
            p.p_overlord_impending_turn3_play,
            p.p_jace_turn4_play,
            p.p_overlord_full_turn5_play,
            p.crude_probe_score,
        ])
    t_py = time.perf_counter() - t1
    py_out = np.array(py_rows, dtype=np.float64)
    max_abs_diff = float(np.max(np.abs(py_out - cpp_out[:sample_n]))) if sample_n else 0.0

    rate_cpp = float(len(arr) / t_cpp) if t_cpp > 0 else 0.0
    rate_py = float(sample_n / t_py) if t_py > 0 else 0.0
    speedup_est = rate_cpp / rate_py if rate_py > 0 else None
    top_idx = np.argsort(-cpp_out[:, -1])[:10]
    top_rows = []
    for rank, i in enumerate(top_idx, 1):
        base = {k: int(v) for k, v in zip(COLS, arr[i])}
        base.update({name: float(cpp_out[i, j]) for j, name in enumerate(PROBE_COLUMNS)})
        base["rank"] = rank
        top_rows.append(base)
    write_csv(data / "rev0015_cpp_probe_top10.csv", top_rows)

    summary = {
        "revision": "rev0015",
        "toolchain_status": status,
        "rows_cpp": int(len(arr)),
        "rows_python_sample": int(sample_n),
        "cpp_seconds": t_cpp,
        "python_seconds_sample": t_py,
        "cpp_rows_per_second": rate_cpp,
        "python_rows_per_second_sample": rate_py,
        "speedup_estimate_vs_python_sample": speedup_est,
        "max_abs_diff_vs_python_sample": max_abs_diff,
        "probe_columns": list(PROBE_COLUMNS),
        "note": "C++ accelerates exact deck probes only; it is the first measured bridge, not the core game referee yet.",
    }
    (data / "rev0015_cpp_probe_benchmark.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
