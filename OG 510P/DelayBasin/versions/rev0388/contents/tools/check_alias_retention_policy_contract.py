import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
policy = json.loads((ROOT / "ALIAS-RETENTION-POLICY.json").read_text(encoding="utf-8"))
ledger = json.loads((ROOT / "PATH-ALIAS-LEDGER.json").read_text(encoding="utf-8"))
if policy.get("project") != "DelayBasin" or policy.get("revision") != receipt.get("revision"):
    raise SystemExit("ALIAS-RETENTION-POLICY project/revision drifted")
if policy.get("surface") != "ALIAS-RETENTION-POLICY.json":
    raise SystemExit("ALIAS-RETENTION-POLICY self surface drifted")
if policy.get("governing_method") != "docs/10-method/alias-retention-toolchain-manifest-witnesses.md":
    raise SystemExit("ALIAS-RETENTION-POLICY governing method drifted")
if policy.get("witness_family") != "alias_retention_state" or policy.get("witness_family_handle") != "WVF-0126":
    raise SystemExit("ALIAS-RETENTION-POLICY family/handle drifted")
if policy.get("source_alias_ledger") != "PATH-ALIAS-LEDGER.json" or ledger.get("entry_count", 0) < 20 or ledger.get("batch_alias_group_count", 0) < 1:
    raise SystemExit("ALIAS-RETENTION-POLICY source alias ledger drifted")
if policy.get("current_decision", {}).get("decision") != "retain":
    raise SystemExit("ALIAS-RETENTION-POLICY must currently retain audit-only provenance")
if "batch alias groups" not in policy.get("batch_alias_retention", "") or "wrapper-regrowth-by-alias" not in policy.get("batch_alias_retention", ""):
    raise SystemExit("ALIAS-RETENTION-POLICY missing batch alias retention boundary")
for bad in ["redirect-authority-board", "path-alias-court", "lint-sovereign", "toolchain-certification-tribunal", "hash-governance-court", "manifest-notary-authority", "old-path-resurrection-registry", "validation-score-sovereign", "wrapper-regrowth-by-alias"]:
    if bad not in policy.get("non_claim", ""):
        raise SystemExit(f"ALIAS-RETENTION-POLICY missing non-claim {bad}")
    if bad.replace("-", " ") not in " ".join(policy.get("forbidden_conclusions", [])) and bad not in " ".join(policy.get("forbidden_conclusions", [])):
        raise SystemExit(f"ALIAS-RETENTION-POLICY missing forbidden conclusion {bad}")
states = {row.get("state") for row in policy.get("retention_states", [])}
if states != {"retain", "compact", "fold", "quarantine"}:
    raise SystemExit("ALIAS-RETENTION-POLICY retention states drifted")
for needle in ["all current references use new_path values directly", "old_path values remain absent on disk", "validation-toolchain manifest is fresh after any admission-wrapper change", "batch alias source counts match exact spec modules"]:
    if needle not in policy.get("retirement_preconditions", []):
        raise SystemExit(f"ALIAS-RETENTION-POLICY missing retirement precondition {needle}")
print("check_alias_retention_policy_contract: OK")
