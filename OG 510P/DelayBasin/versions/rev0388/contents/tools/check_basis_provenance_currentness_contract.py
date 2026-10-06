import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
innovation = json.loads((ROOT / "innovation-packet.json").read_text(encoding="utf-8"))
audit = json.loads((ROOT / "BASIS-PROVENANCE-AUDIT.json").read_text(encoding="utf-8"))
basis = receipt.get("basis_witness", {})
previous = receipt.get("previous_revision")
violations = []
if basis.get("expected_head") != previous:
    violations.append(f"basis_witness.expected_head={basis.get('expected_head')} expected {previous}")
if basis.get("observed_head") != previous:
    violations.append(f"basis_witness.observed_head={basis.get('observed_head')} expected {previous}")
if innovation.get("anchor", {}).get("expected_head") != previous:
    violations.append("innovation-packet anchor expected_head stale")
if innovation.get("anchor", {}).get("observed_head") != previous:
    violations.append("innovation-packet anchor observed_head stale")
if audit.get("counts", {}).get("failures") != 0:
    violations.append("basis provenance audit reports failures")
prov = basis.get("session_provenance", "")
if previous not in prov:
    violations.append("basis session_provenance must name the immediate previous revision")
if receipt.get("revision", "") >= "rev0333":
    for stale in ("rev0328", "rev0330", "rev0331"):
        if stale in prov:
            violations.append(f"basis session_provenance carries stale source revision {stale}")
if violations:
    raise SystemExit("basis provenance currentness violations: " + "; ".join(violations))
print("check_basis_provenance_currentness_contract: OK")
