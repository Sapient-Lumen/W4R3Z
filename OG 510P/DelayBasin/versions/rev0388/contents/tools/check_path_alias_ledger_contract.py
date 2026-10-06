import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
ledger = json.loads((ROOT / "PATH-ALIAS-LEDGER.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))


def load_symbol(rel: str, symbol: str):
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"batch alias spec path missing: {rel}")
    spec = importlib.util.spec_from_file_location("_alias_spec_" + pathlib.Path(rel).stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return getattr(module, symbol)

if ledger.get("project") != "DelayBasin" or ledger.get("revision") != receipt.get("revision"):
    raise SystemExit("PATH-ALIAS-LEDGER project/revision drifted")
if ledger.get("surface") != "PATH-ALIAS-LEDGER.json":
    raise SystemExit("PATH-ALIAS-LEDGER self id drifted")
if "not a review court" not in ledger.get("non_claim", "") or "old_path is retained only as audit" not in ledger.get("alias_rule", ""):
    raise SystemExit("PATH-ALIAS-LEDGER missing non-authority/audit-only warning")
if "wrapper-regrowth-by-alias" not in ledger.get("non_claim", "") or "must not recreate wrapper files" not in ledger.get("batch_alias_rule", ""):
    raise SystemExit("PATH-ALIAS-LEDGER missing batch-alias non-regrowth warning")
entries = ledger.get("entries")
if not isinstance(entries, list) or len(entries) < 20:
    raise SystemExit("PATH-ALIAS-LEDGER must record the path refactor entries")
if ledger.get("entry_count") != len(entries):
    raise SystemExit("PATH-ALIAS-LEDGER entry_count drifted")

handle_rows = {row.get("handle"): row for row in handles.get("families", [])}
seen_new = set()
seen_old = set()
for entry in entries:
    for key in ["handle", "kind", "old_path", "new_path", "rationale", "authority"]:
        if key not in entry:
            raise SystemExit(f"PATH-ALIAS-LEDGER entry missing {key}")
    old = entry["old_path"]
    new = entry["new_path"]
    if old == new:
        raise SystemExit("alias entry old_path equals new_path")
    if old in seen_old or new in seen_new:
        raise SystemExit("duplicate path in method alias ledger")
    seen_old.add(old); seen_new.add(new)
    if (ROOT / old).exists():
        raise SystemExit(f"old path still exists on disk: {old}")
    if not (ROOT / new).exists():
        raise SystemExit(f"new path missing on disk: {new}")
    row = handle_rows.get(entry["handle"])
    if row is None:
        raise SystemExit(f"alias handle missing from WITNESS-FAMILY-HANDLES: {entry['handle']}")
    if entry["kind"] != "method-doc":
        raise SystemExit(f"per-entry alias ledger should retain method-doc entries only after batch alias compaction: {entry}")
    if new not in row.get("surfaces", []):
        raise SystemExit(f"method alias not reflected in handle row: {new}")

groups = ledger.get("batch_alias_groups")
if ledger.get("batch_alias_group_count") != len(groups or []):
    raise SystemExit("PATH-ALIAS-LEDGER batch_alias_group_count drifted")
if not isinstance(groups, list) or len(groups) < 3:
    raise SystemExit("PATH-ALIAS-LEDGER must retain compact batch alias groups for GPU, GPustorming, and method-doc batches")
source_total = 0
for group in groups:
    for key in ["group_id", "kind", "target_path", "spec_path", "spec_symbol", "source_count", "authority", "non_claim"]:
        if key not in group:
            raise SystemExit(f"batch alias group missing {key}: {group}")
    if group["kind"] != "contract-tool-batch":
        raise SystemExit(f"unexpected batch alias group kind: {group['kind']}")
    if not (ROOT / group["target_path"]).exists():
        raise SystemExit(f"batch alias target missing: {group['target_path']}")
    rows = load_symbol(group["spec_path"], group["spec_symbol"])
    if group["source_count"] != len(rows):
        raise SystemExit(f"batch alias source count drift for {group['group_id']}: {group['source_count']} != {len(rows)}")
    source_names = [row.get("source_checker") for row in rows]
    if len(source_names) != len(set(source_names)):
        raise SystemExit(f"duplicate source checker in batch alias group {group['group_id']}")
    for name in source_names:
        if not isinstance(name, str) or not name.startswith("check_"):
            raise SystemExit(f"bad source checker in batch alias group {group['group_id']}: {name!r}")
        if (ROOT / "tools" / name).exists():
            raise SystemExit(f"former wrapper path still exists on disk: tools/{name}")
    if "not-canonical-method-content" not in group.get("authority", "") and "not-canonical-method-content" not in group.get("non_claim", ""):
        raise SystemExit(f"batch alias group lacks non-authority marker: {group['group_id']}")
    source_total += len(rows)
if source_total < 110:
    raise SystemExit("batch alias groups should cover GPU, standard GPustorming, and method-doc retired checker paths")

path_budget = ledger.get("path_budget", {})
limit_rel = int(path_budget.get("fail_relative_path_over", 180))
limit_component = int(path_budget.get("fail_component_over", 170))
max_rel = 0
max_component = 0
for path in ROOT.rglob("*"):
    if not path.is_file() or any(part.startswith(".") for part in path.relative_to(ROOT).parts):
        continue
    rel = path.relative_to(ROOT).as_posix()
    max_rel = max(max_rel, len(rel))
    max_component = max(max_component, *(len(part) for part in path.relative_to(ROOT).parts))
    if len(rel) > limit_rel:
        raise SystemExit(f"archive-relative path exceeds alias budget ({len(rel)}>{limit_rel}): {rel}")
    for part in path.relative_to(ROOT).parts:
        if len(part) > limit_component:
            raise SystemExit(f"path component exceeds alias budget ({len(part)}>{limit_component}): {rel} :: {part}")
if path_budget.get("max_archive_relative_path") != max_rel or path_budget.get("max_component") != max_component:
    raise SystemExit("PATH-ALIAS-LEDGER path budget drifted")
print("check_path_alias_ledger_contract: OK")
