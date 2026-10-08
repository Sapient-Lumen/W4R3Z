# 163 — Artifact reference conventions (machine-checkable)

**Track:** Shared


This archive uses a simple reference convention so that claims/hazards can be checked by tools.

## 163.1 Reference tokens
Within CSV fields (e.g., `EvidenceArtifacts`, `DetectionArtifacts`), references SHOULD be written
as a `TYPE:path` token, separated by semicolons.

Allowed `TYPE` values:

- `DOC` — a doc under `docs/`
- `ADR` — an ADR under `adr/`
- `SCHEMA` — a JSON schema under `schemas/`
- `CHECK` — a checklist under `artifacts/checklists/`
- `TOOL` — a tool under `tools/`
- `SCRIPT` — a script under `scripts/`
- `EXAMPLE` — an example under `artifacts/examples/`
- `TEMPLATE` — a template under `artifacts/templates/`
- `PLAY` — a playbook/runbook under `artifacts/playbooks/`
- `REG` — a registry under `artifacts/registries/`

Examples:
- `DOC:docs/04-transparency-log.md`
- `SCHEMA:schemas/InclusionProof.json`
- `CHECK:artifacts/checklists/audience-parity-monitoring-checklist.md`
- `PLAY:artifacts/playbooks/key-compromise-response-playbook.md`

## 163.2 Tombstones
Tombstone docs MAY exist to preserve old references. Tombstones MUST:
- start with a heading that includes the word “Tombstone”
- point to the canonical artifact
- contain no normative content

Tooling MUST treat tombstones as non-normative aliases.

Release gate: `scripts/check_tombstones.py` enforces the minimum tombstone shape.

## 163.3 Why this matters
The most common failure mode in long-lived, security-sensitive archives is **silent incoherence**:
references drift, files move, and the repo becomes unreviewable.

These conventions keep the archive *boring to maintain* and therefore safer.

