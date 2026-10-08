#!/usr/bin/env python3
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV_NUM = int(REV.replace("rev", ""))

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def rev_num(path_or_value):
    m = re.search(r"rev(\d{4})", str(path_or_value))
    return int(m.group(1)) if m else -1


def latest_example(pattern):
    candidates = [p for p in (ROOT / "examples").glob(pattern) if rev_num(p) <= REV_NUM]
    if not candidates:
        raise SystemExit(f"no example found for {pattern} at or before {REV}")
    return sorted(candidates, key=rev_num)[-1]

# These are stable guard surfaces. They must not be copied forward merely to chase
# the active revision; the audit intentionally resolves the latest valid example
# at or before the active release.
POLICY = latest_example("private-evidence-vault-policy-rev*.json")
SHELL = latest_example("evidence-vault-public-shell-rev*-ready-no-live-artifact.json")
POLICY_REV = f"rev{rev_num(POLICY):04d}"
SHELL_REV = f"rev{rev_num(SHELL):04d}"


def load(rel_or_path):
    path = Path(rel_or_path)
    if not path.is_absolute():
        path = ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_rel, data_path):
    if Draft202012Validator is None:
        return
    schema = load(schema_rel)
    data = load(data_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{Path(data_path).relative_to(ROOT)} fails {schema_rel}: {errors[0].message}")

validate("schemas/private-evidence-vault-policy.schema.json", POLICY)
validate("schemas/evidence-vault-public-shell.schema.json", SHELL)

policy = load(POLICY)
shell = load(SHELL)
if policy.get("revision") != POLICY_REV or shell.get("revision") != SHELL_REV:
    raise SystemExit("private vault policy/shell revision mismatch")
if rev_num(POLICY) > REV_NUM or rev_num(SHELL) > REV_NUM:
    raise SystemExit("private vault audit resolved a future example")
if policy.get("raw_vault", {}).get("root_policy") != "outside-release-tree":
    raise SystemExit("private vault root policy must be outside-release-tree")
if policy.get("raw_vault", {}).get("raw_payload_may_enter_examples_artifacts") is not False:
    raise SystemExit("policy must block live raw payloads from examples/artifacts")
if shell.get("public_disclosure", {}).get("no_raw_bytes") is not True:
    raise SystemExit("public shell must exclude raw bytes")
if shell.get("no_live_floor_effect") is not True:
    raise SystemExit("public shell must have no live-floor effect")

from tools.vault_release_guard import guard_release_tree  # noqa: E402
guard_release_tree(ROOT)
package_src = (ROOT / "tools" / "package_release.py").read_text(encoding="utf-8")
if "guard_release_tree(ROOT)" not in package_src:
    raise SystemExit("package_release.py does not call private evidence vault release guard")

with tempfile.TemporaryDirectory(prefix="ai-personhood-vault-audit-") as td:
    tmp = Path(td)
    source = tmp / "synthetic-private-counterparty.txt"
    secret = "SYNTHETIC_PRIVATE_COUNTERPARTY_BYTES_REV0212_DO_NOT_PACKAGE"
    source.write_text(secret, encoding="utf-8")
    vault = tmp / "external-vault"
    out = tmp / "ledger.json"
    subprocess.run([
        sys.executable,
        str(ROOT / "tools" / "stage_live_evidence_drop.py"),
        "--input", str(source),
        "--output", str(out),
        "--drop-id", "rev0228-synthetic-private-vault-audit",
        "--created-at", policy["created_at"],
        "--source-kind", "file-upload",
        "--collection-context", "live-counterparty",
        "--vault-root", str(vault),
    ], check=True, capture_output=True, text=True)
    ledger = load(out)
    staged = ledger["staged_payload"]
    source_payload = ledger["source_payload"]
    if ledger.get("intake_mode") != "live-candidate-drop":
        raise SystemExit("synthetic private vault staging did not create live-candidate-drop")
    if not staged.get("quarantine_locator", "").startswith("private-vault://"):
        raise SystemExit("synthetic private vault staging did not emit private-vault URI")
    if not source_payload.get("original_locator", "").startswith("private-source-redacted:sha256:"):
        raise SystemExit("synthetic private vault staging leaked the source locator")
    copied = list(vault.rglob("*.txt"))
    if len(copied) != 1 or copied[0].read_text(encoding="utf-8") != secret:
        raise SystemExit("synthetic private vault payload was not copied into external vault")
    if secret in "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in ROOT.rglob("*.txt") if "__pycache__" not in p.parts):
        raise SystemExit("synthetic private vault bytes appeared in archive tree")

for rel in [
    "fixtures/negative-tests/private-vault-live-payload-in-release-tree.json",
    "fixtures/negative-tests/private-vault-public-shell-missing-hash.json",
]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing private vault negative fixture: {rel}")

print(f"audit_private_evidence_vault_split: OK using {POLICY.relative_to(ROOT)} and {SHELL.relative_to(ROOT)}")
