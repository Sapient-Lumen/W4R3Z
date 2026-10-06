import pathlib
import shutil

from generated_surface_lib import copy_release_tree_for_generation, generated_surface_drift

ROOT = pathlib.Path(__file__).resolve().parents[1]
IGNORED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def tree_snapshot(root: pathlib.Path) -> dict[str, bytes]:
    rows: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in rel.parts) or path.suffix in IGNORED_SUFFIXES:
            continue
        rows[rel.as_posix()] = path.read_bytes()
    return rows


fixture = copy_release_tree_for_generation(ROOT)
try:
    drift_target = fixture / "CURRENT-RECEIPT.json"
    drift_target.write_bytes(drift_target.read_bytes() + b"\n")
    before = tree_snapshot(fixture)
    drifts = generated_surface_drift(fixture)
    after = tree_snapshot(fixture)
    if before != after:
        changed = sorted(set(before) | set(after))
        changed = [rel for rel in changed if before.get(rel) != after.get(rel)]
        raise SystemExit("generated-surface drift validation mutated its target tree: " + ", ".join(changed[:12]))
    if not any(row.surface == "CURRENT-RECEIPT.json" and row.status == "content-drift" for row in drifts):
        raise SystemExit("generated-surface nonmutation canary failed to detect deliberate CURRENT-RECEIPT drift")
finally:
    shutil.rmtree(fixture.parent, ignore_errors=True)

print("check_generated_surface_nonmutation_canary: OK")
