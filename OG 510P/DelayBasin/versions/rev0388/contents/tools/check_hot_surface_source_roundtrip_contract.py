import pathlib
import tempfile

from hot_surface_compaction_lib import restore_originals_to

ROOT = pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="delaybasin-hot-surface-roundtrip-") as tmp:
    records = restore_originals_to(ROOT, pathlib.Path(tmp))
    if len(records) != 4:
        raise SystemExit("hot-surface roundtrip restored the wrong target count")
    for row in records:
        restored = pathlib.Path(tmp) / str(row["path"])
        if not restored.exists():
            raise SystemExit(f"hot-surface roundtrip missing restored path: {row['path']}")
print("check_hot_surface_source_roundtrip_contract: OK")
