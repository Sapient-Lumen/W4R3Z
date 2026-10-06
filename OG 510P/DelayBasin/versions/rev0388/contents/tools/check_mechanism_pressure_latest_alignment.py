import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
register_path = ROOT / "docs/10-method/mechanism-pressure-register.md"
text = register_path.read_text(encoding="utf-8")

rev = receipt.get("revision")
if not re.fullmatch(r"rev\d{4}", str(rev)):
    raise SystemExit("receipt revision must be rev####")
expected_mp = f"MP-{int(rev[3:]):04d}"
resolved = receipt.get("resolved_question")
successor = receipt.get("next_open_question")
pressure = receipt.get("current_pressure_id")
transfer = receipt.get("current_import_id")
resolution_surface = receipt.get("resolution_witness", {}).get("witness_surface", "")
_, _, resolution = resolution_surface.partition("#")
method_surface = pathlib.Path(receipt.get("canon_additions", [""])[0]).name

if not resolution:
    raise SystemExit("receipt resolution_witness must point to a resolution id")

rule_idx = text.find("## Register rule")
if rule_idx < 0:
    raise SystemExit("mechanism-pressure register missing Register rule")
pre_rule = text[:rule_idx]
post_rule = text[rule_idx:]
if re.search(r"^\| MP-\d{4} ", post_rule, re.M):
    raise SystemExit("mechanism-pressure rows must stay in the table before Register rule")

rows = []
for raw in pre_rule.splitlines():
    if not raw.startswith("| MP-"):
        continue
    cells = [cell.strip() for cell in raw.strip().strip("|").split("|")]
    if len(cells) != 8:
        raise SystemExit(f"mechanism-pressure row must have 8 cells: {raw}")
    rows.append(cells)
if not rows:
    raise SystemExit("mechanism-pressure register has no MP rows")
ids = [row[0] for row in rows]
if len(ids) != len(set(ids)):
    raise SystemExit("mechanism-pressure register has duplicate MP rows")
if expected_mp not in ids:
    raise SystemExit(f"mechanism-pressure register missing latest {expected_mp}")
if rows[-1][0] != expected_mp:
    raise SystemExit(f"latest mechanism-pressure row must be last table row: {rows[-1][0]} != {expected_mp}")
row = rows[-1]
checks = {
    "revision": (row[1], rev),
    "foreign pressure": (row[3], pressure),
    "transfer": (row[4], transfer),
    "question": (row[5], resolved),
}
for label, (observed, expected) in checks.items():
    if observed != expected:
        raise SystemExit(f"latest mechanism-pressure {label} mismatch: {observed!r} != {expected!r}")
status = row[6]
if resolution not in status or successor not in status:
    raise SystemExit("latest mechanism-pressure status must name current resolution and successor")
if row[7] != method_surface:
    raise SystemExit(f"latest mechanism-pressure method surface mismatch: {row[7]!r} != {method_surface!r}")
print("check_mechanism_pressure_latest_alignment: OK")
