import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
MAP_PATH = ROOT / "examples" / f"rights-domain-coverage-map-{REV}.json"
SCHEMA_PATH = ROOT / "schemas" / "rights-domain-coverage-map.schema.json"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

mp = load(MAP_PATH)
if Draft202012Validator is not None:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(mp), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{MAP_PATH.relative_to(ROOT)} fails rights-domain-coverage-map.schema.json: {errors[0].message}")

seen = set()
covered = set()
for domain in mp.get("domains", []):
    did = domain.get("domain_id")
    if did in seen:
        raise SystemExit(f"duplicate rights-domain id: {did}")
    seen.add(did)
    owner = domain.get("owner_surface")
    if not (ROOT / owner).exists():
        raise SystemExit(f"rights-domain owner surface missing: {owner}")
    if domain.get("coverage_state") == "missing":
        raise SystemExit(f"rights-domain is marked missing in current release: {did}")
    for rel in domain.get("covered_surfaces", []):
        if not (ROOT / rel).exists():
            raise SystemExit(f"rights-domain {did} references missing covered surface: {rel}")
        covered.add(rel)

required_domains = {
    "expression-reputation",
    "persona-communication-provenance",
    "social-graph-portability",
    "audit-refactor",
    "federated-namespace-continuity",
    "research-welfare-safeguards",
    "protocol-wrsr-backfill",
    "external-receipt-simulation",
    "external-receipt-intake",
    "wrsr-live-exercise-outcome",
    "external-receipt-response-reconciliation",
    "response-to-intake-conversion",
    "actual-receipt-import-gate",
    "failed-gate-public-summary",
    "live-counterparty-import-attempt",
    "quorum-recomputation-report",
    "nonhost-response-artifact-envelope",
    "live-import-replay-report",
    "live-class-local-import-replay",
    "counterparty-artifact-custody",
    "receipt-import-challenge-rollback",
    "computed-live-floor-engine",
    "computed-floor-positive-controls",
    "live-artifact-import-fieldkit",
    "live-evidence-drop-quarantine",
    "private-evidence-vault",
    "live-artifact-candidate-challenge",
    "external-receipt-import-readiness-gate",
    "live-receipt-quorum-participation",
    "live-receipt-floor-recompute-publication",
    "live-receipt-publication-rollback-adjudication",
    "live-receipt-late-change-ingress",
    "live-receipt-late-change-notice-dispatch",
    "live-receipt-late-change-remedy-resolution",
    "live-receipt-late-change-remedy-execution",
}
missing = sorted(required_domains - seen)
if missing:
    raise SystemExit(f"rights-domain coverage map missing current domains: {missing}")

status = load(ROOT / "SURFACE-STATUS.json")
current_markdown = [p for p in status.get("new_surfaces", []) if p.endswith(".md")]
uncovered = [p for p in current_markdown if p not in covered]
if uncovered:
    raise SystemExit(f"current-release markdown surfaces not covered by rights-domain map: {uncovered}")

print("audit_rights_domain_coverage: OK")
