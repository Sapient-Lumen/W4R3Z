#!/usr/bin/env python3
"""scripts/gen_public_surface_index.py

Generate docs/PUBLIC_SURFACES.md.

Rationale:
The archive has a few small *public surfaces* that external implementers and
observers may depend on. This generator keeps a compact, stable index pointing
to the canonical registries and schemas.

This is intentionally short and non-exhaustive.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "PUBLIC_SURFACES.md"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_row_count(p: Path) -> int:
    with p.open("r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        rows = list(r)
    if not rows:
        return 0
    # Count non-empty, non-comment rows after header.
    n = 0
    for row in rows[1:]:
        if not row:
            continue
        if row[0].strip().startswith("#"):
            continue
        if all((c or "").strip() == "" for c in row):
            continue
        n += 1
    return n


def main() -> int:
    registries = ROOT / "artifacts" / "registries"

    surfaces = [
        {
            "surface": "Envelope kinds (kind → schema)",
            "source": "artifacts/registries/envelope-kinds.csv",
            "human": "docs/EVIDENCE_OBJECT_CATALOG.md (generated), docs/178-envelope-kind-registry.md",
            "notes": "Treat as a stable API surface; add via ADR when semantics change.",
            "count": csv_row_count(registries / "envelope-kinds.csv"),
        },
        {
            "surface": "Required attachments per kind",
            "source": "artifacts/registries/envelope-attachment-requirements.csv",
            "human": "docs/EVIDENCE_OBJECT_CATALOG.md (generated), docs/180-receipts-and-gossip-attachments.md",
            "notes": "Anti-selective-disclosure firewall; changes can be breaking.",
            "count": csv_row_count(registries / "envelope-attachment-requirements.csv"),
        },
        {
            "surface": "Receipt profiles",
            "source": "artifacts/registries/receipt-profiles.csv",
            "human": "docs/182-receipt-profiles-and-mappings.md, docs/185-receipt-semantics-tiers.md",
            "notes": "Profile IDs are public strings; keep small and stable.",
            "count": csv_row_count(registries / "receipt-profiles.csv"),
        },
        {
            "surface": "Publishable verifier problem codes",
            "source": "artifacts/registries/verifier-problem-codes.csv",
            "human": "docs/VERIFIER_PROBLEM_CODES.md (generated), docs/193-publishable-verifier-reports.md",
            "notes": "Designed for cross-verifier comparability; registry is strict + sorted.",
            "count": csv_row_count(registries / "verifier-problem-codes.csv"),
        },
        {
            "surface": "Publishable public-surface anomaly codes",
            "source": "artifacts/registries/surface-anomaly-codes.csv",
            "human": "docs/SURFACE_ANOMALY_CODES.md (generated), docs/201-public-surface-parity-snapshots.md, docs/210-liveness-beacons-and-missingness-surface.md",
            "notes": "Designed for cross-monitor comparability when using notes fields in bounded monitoring payloads; registry is strict + sorted.",
            "count": csv_row_count(registries / "surface-anomaly-codes.csv"),
        },
        {
            "surface": "Verifier profiles (capability claims)",
            "source": "artifacts/registries/verifier-profiles.csv",
            "human": "docs/VERIFIER_PROFILES.md (generated), docs/179-evidence-api-surface.md",
            "notes": "Small profile IDs for cross-verifier capability comparability; registry is strict + sorted.",
            "count": csv_row_count(registries / "verifier-profiles.csv"),
        },
        {
            "surface": "Tool maturity + evidence-safety registry",
            "source": "artifacts/registries/tool-maturity.csv",
            "human": "docs/212-tooling-maturity-and-evidence-safety.md, tools/README.md",
            "notes": "Non-normative intent surface to prevent confusing research/skeleton tools with evidence outputs; keep sorted.",
            "count": csv_row_count(registries / "tool-maturity.csv"),
        },
        {
            "surface": "Official communication channel IDs",
            "source": "artifacts/registries/official-channels.csv",
            "human": "docs/186-incident-communications-as-evidence.md, artifacts/checklists/official-communications-channels-hardening-checklist.md",
            "notes": "Channel IDs appear in PublicNotice payloads; changes require migrations.",
            "count": csv_row_count(registries / "official-channels.csv"),
        },
        {
            "surface": "Publication trigger vocabulary",
            "source": "artifacts/registries/publication-triggers.csv",
            "human": "docs/184-publication-trigger-vocabulary.md",
            "notes": "Used for incident comms + compliance coverage; keep IDs stable.",
            "count": csv_row_count(registries / "publication-triggers.csv"),
        },
        {
            "surface": "EvidenceEnvelope schema",
            "source": "schemas/EvidenceEnvelope.json",
            "human": "docs/173-canonical-evidence-envelopes-and-packets.md, docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md",
            "notes": "Envelope header semantics; versioned by envelope_version.",
            "count": None,
        },
        {
            "surface": "PacketVerificationReport schema",
            "source": "schemas/PacketVerificationReport.json",
            "human": "docs/193-publishable-verifier-reports.md",
            "notes": "Packet-scoped publishable verifier output.",
            "count": None,
        },
        {
            "surface": "VerifierReport schema",
            "source": "schemas/VerifierReport.json",
            "human": "docs/193-publishable-verifier-reports.md",
            "notes": "Implementation-scoped verifier identity + conformance claims.",
            "count": None,
        },
        {
            "surface": "EvidenceBundleManifest schema",
            "source": "schemas/EvidenceBundleManifest.json",
            "human": "docs/173-canonical-evidence-envelopes-and-packets.md, docs/179-evidence-api-surface.md",
            "notes": "Bundle manifest contract; used by offline verifiers.",
            "count": None,
        },
        {
            "surface": "PublicNotice schema",
            "source": "schemas/PublicNotice.json",
            "human": "docs/186-incident-communications-as-evidence.md",
            "notes": "Canonical official communication payload.",
            "count": None,
        },
        {
            "surface": "PublicNoticeFeed schema",
            "source": "schemas/PublicNoticeFeed.json",
            "human": "docs/200-publicnotice-feeds-and-mirror-index.md",
            "notes": "Bounded notice discovery surface (rollback-detectable).",
            "count": None,
        },
        {
            "surface": "PublicNoticeSigningKeyset schema",
            "source": "schemas/PublicNoticeSigningKeyset.json",
            "human": "docs/208-publicnotice-signing-keys-and-channel-identity.md",
            "notes": "Allow-list of keys authorized to sign PublicNotices for a scope.",
            "count": None,
        },
        {
            "surface": "OfficialChannelDirectory schema",
            "source": "schemas/OfficialChannelDirectory.json",
            "human": "docs/203-official-channel-directory-as-evidence.md",
            "notes": "Declared official channel directory (discovery anchor).",
            "count": None,
        },
        {
            "surface": "WellKnownElectionStackDiscovery schema",
            "source": "schemas/WellKnownElectionStackDiscovery.json",
            "human": "docs/204-well-known-election-stack-discovery.md",
            "notes": "Domain-first bootstrap pointer object for comms discovery.",
            "count": None,
        },
        {
            "surface": "PublicSurfaceParitySnapshot schema",
            "source": "schemas/PublicSurfaceParitySnapshot.json",
            "human": "docs/201-public-surface-parity-snapshots.md",
            "notes": "Portable split-view/parity evidence across official channels.",
            "count": None,
        },
        {
            "surface": "OfficialSurfaceSecuritySnapshot schema",
            "source": "schemas/OfficialSurfaceSecuritySnapshot.json",
            "human": "docs/199-official-surface-security-snapshots.md",
            "notes": "Auditable snapshot of official-surface hardening posture.",
            "count": None,
        },
        {
            "surface": "LivenessBeacon schema",
            "source": "schemas/LivenessBeacon.json",
            "human": "docs/210-liveness-beacons-and-missingness-surface.md",
            "notes": "Independent watcher heartbeat for reachability + observed pointer digests.",
            "count": None,
        },
        {
            "surface": "External source lockfile IDs",
            "source": "evidence/lock/external-sources.toml",
            "human": "docs/191-external-source-lockfile-playbook.md",
            "notes": "Cite, don’t bloat; pinned sources are treated as normative references.",
            "count": None,
        },
    ]

    for s in surfaces:
        try:
            s["sha256"] = sha256_file(ROOT / s["source"])
        except Exception:
            s["sha256"] = None

    lines: list[str] = []
    lines.append("# Public surfaces index\n")
    lines.append(
        "This document is a compact index of the archive’s **public surfaces**: small identifiers and schemas that external implementers may depend on.\n"
    )
    lines.append(
        "If you change any of these in a way that could break consumers, prefer an ADR + a migration story.\n\n"
    )

    lines.append("| Surface | Canonical source | Digest | Human view | Notes |\n")
    lines.append("|---|---|---|---|---|\n")
    for s in surfaces:
        src = f"`{s['source']}`"
        digest = "(missing)"
        if isinstance(s.get("sha256"), str):
            digest = f"`sha256:{s['sha256'][:12]}…`"
        human = s["human"].replace(" ", " ")
        notes = s["notes"]
        if isinstance(s.get("count"), int):
            notes = f"{notes} ({s['count']} entries.)"
        lines.append(f"| {s['surface']} | {src} | {digest} | {human} | {notes} |\n")

    lines.append("\n## Full digests\n\n")
    lines.append(
        "Full sha256 digests for canonical sources listed above (computed from file bytes at generation time; also present in `MANIFEST.sha256`).\n\n"
    )
    for s in surfaces:
        if isinstance(s.get("sha256"), str):
            lines.append(f"- `{s['source']}` — `sha256:{s['sha256']}`\n")

    content = "".join(lines)
    OUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
