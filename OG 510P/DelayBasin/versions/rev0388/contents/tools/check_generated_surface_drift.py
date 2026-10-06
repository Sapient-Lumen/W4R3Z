import pathlib

from generated_surface_lib import generated_surface_drift

ROOT = pathlib.Path(__file__).resolve().parents[1]
drifts = generated_surface_drift(ROOT)
if drifts:
    preview = "; ".join(f"{row.surface}:{row.status}" for row in drifts[:12])
    if len(drifts) > 12:
        preview += f"; ... +{len(drifts) - 12} more"
    raise SystemExit(f"generated surfaces drifted before lint; run make context-pack: {preview}")
print("check_generated_surface_drift: OK")
