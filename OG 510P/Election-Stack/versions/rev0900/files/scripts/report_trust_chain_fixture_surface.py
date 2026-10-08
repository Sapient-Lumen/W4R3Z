#!/usr/bin/env python3
"""Audit the synthetic verifier trust-chain fixture surface.

This is not a production trust-root audit. It is a maintainer check that the
bounded local verifier examples keep trust-root, governance, receipt, status, authorization, and policy artifacts
external to the packet and byte-pinned by sidecars.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
VERSION = VERSION_FILE.read_text(encoding="utf-8").strip()
VERSION_NUM = VERSION.removeprefix("v").zfill(4)

FIXTURES = [
    ("trust_keyset", "artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.json", "required_external_public_keyset"),
    ("trust_keyset_publication_receipt", "artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.publication-receipt.json", "required_external_publication_receipt"),
    ("trust_governance_bundle", "artifacts/examples/trust_keysets/trust-key-governance-bundle-ed25519-threshold2-rev0845.json", "required_external_governance_bundle"),
    ("trust_governance_bundle_publication_receipt", "artifacts/examples/trust_keysets/trust-key-governance-bundle-ed25519-threshold2-rev0845.publication-receipt.json", "required_external_governance_receipt"),
    ("trust_status_snapshot", "artifacts/examples/trust_keysets/trust-status-snapshot-ed25519-threshold2-rev0847.json", "required_external_status_snapshot"),
    ("trust_status_snapshot_publication_receipt", "artifacts/examples/trust_keysets/trust-status-snapshot-ed25519-threshold2-rev0853.publication-receipt.json", "required_external_status_receipt"),
    ("signer_authorization_roster", "artifacts/examples/trust_keysets/signer-authorization-roster-ed25519-threshold2-rev0852.json", "required_external_signer_authorization_roster"),
    ("signer_authorization_roster_publication_receipt", "artifacts/examples/trust_keysets/signer-authorization-roster-ed25519-threshold2-rev0853.publication-receipt.json", "required_external_signer_authorization_roster_receipt"),
    ("verification_policy_lockfile", f"artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev{VERSION_NUM}.json", "required_external_policy_lockfile"),
    ("verification_policy_lockfile_publication_receipt", f"artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev{VERSION_NUM}.publication-receipt.json", "required_external_policy_lockfile_publication_receipt"),
]

BOUNDARY = (
    "Synthetic fixture-surface audit only. Passing this report proves sidecar byte-pin coherence and packet-external fixture placement; "
    "it does not prove production key ceremony, real signer authority, employment, online revocation freshness, independent governance, certification, live-pilot readiness, current voter instruction, or legal reliance."
)


def sha256_uri(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sidecar_for(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".sha256")


def read_sidecar(path: Path) -> str:
    sidecar = sidecar_for(path)
    if not sidecar.exists():
        return ""
    return sidecar.read_text(encoding="utf-8").split()[0].strip()


def build_report() -> tuple[list[dict], dict]:
    rows: list[dict] = []
    for role, rel, requirement in FIXTURES:
        path = ROOT / rel
        exists = path.exists()
        digest = sha256_uri(path) if exists else ""
        sidecar = read_sidecar(path) if exists else ""
        obj = {}
        if exists:
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                obj = {}
        inside_packet = "/evidence_packet_" in rel or rel.startswith("artifacts/examples/evidence_packet_")
        rows.append({
            "role": role,
            "requirement": requirement,
            "path": rel,
            "exists": str(exists).lower(),
            "packet_external": str(not inside_packet).lower(),
            "profile": str(obj.get("profile") or ""),
            "id": str(obj.get("keyset_id") or obj.get("receipt_id") or obj.get("governance_bundle_id") or obj.get("bundle_id") or obj.get("snapshot_id") or obj.get("roster_id") or obj.get("policy_id") or ""),
            "sha256": digest,
            "sidecar_sha256": sidecar,
            "sidecar_matches": str(bool(digest and sidecar == digest)).lower(),
        })
    failures = [r for r in rows if r["exists"] != "true" or r["packet_external"] != "true" or r["sidecar_matches"] != "true" or not r["id"]]
    version = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else "unknown"
    summary = {
        "archive_version": version,
        "fixture_count": len(rows),
        "failure_count": len(failures),
        "all_sidecars_match": not failures,
        "all_fixtures_packet_external": all(r["packet_external"] == "true" for r in rows),
        "roles": [r["role"] for r in rows],
        "boundary": BOUNDARY,
        "recommended_next_move": "Keep the strongest synthetic verifier path assembled from these ten packet-external byte-pinned fixtures; do not move any trust root, governance, receipt, status, signer-authorization, or policy fixture into the packet under test. Prefer the current packet-fingerprint-bound scoped policy lockfile with signer-authorization receipt gating and policy-id/selector/fingerprint-bound policy-publication receipt checks over hand-assembling long trust-chain CLI flag sets, and keep trust-input paths child-bounded under the declared base directory, packet_selector-bound to packet scope, and bounded by policy validity windows.",
    }
    return rows, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=f"artifacts/reports/trust-chain-fixture-surface-rev{VERSION_NUM}.csv")
    ap.add_argument("--json", default=f"artifacts/reports/trust-chain-fixture-surface-rev{VERSION_NUM}.json")
    args = ap.parse_args()
    rows, summary = build_report()
    csv_path = ROOT / args.csv
    json_path = ROOT / args.json
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["role", "requirement", "path", "exists", "packet_external", "profile", "id", "sha256", "sidecar_sha256", "sidecar_matches"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE {csv_path.relative_to(ROOT)}")
    print(f"WROTE {json_path.relative_to(ROOT)}")
    print(f"fixtures={summary['fixture_count']} failures={summary['failure_count']}")
    return 0 if summary["failure_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
