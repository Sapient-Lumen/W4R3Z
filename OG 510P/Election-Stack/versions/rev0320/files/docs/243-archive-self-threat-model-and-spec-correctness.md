# 243. Archive self-threat model and spec-correctness response

**Track:** Shared

This archive is itself a **critical dependency** for deployments and reviews.
If the spec is wrong, or the reference tooling is misleading, the archive can create false confidence or false disputes.

This document defines the archive’s **self-threat model** and the **minimum response loop** when the archive (or its tools) are wrong.

## 243.1 Scope and non-goals

**In scope**
- Spec/schema errors (missing/incorrect requirements; ambiguous semantics).
- Tooling errors (reference verifier bugs; example packet drift; registry incoherence).
- Maintainer compromise or “legibility theater” edits that preserve form while weakening substance.
- Supply-chain compromise affecting the shipped archive zip (tampered files; dependency sabotage).

**Non-goals**
- This does not promise the archive is “correct.” It defines **how we detect, disclose, and repair** correctness failures.

## 243.2 Archive-level hazards (ARCH-*)

ARCH-1 **Spec correctness bug**  
A schema/protocol requirement is wrong or incomplete; a proof obligation is missing; a hazard is misclassified.

ARCH-2 **Verifier/tool mismatch**  
Two honest verifiers disagree, or a verifier passes invalid artifacts / rejects valid artifacts.

ARCH-3 **Drift and silent incoherence**  
Docs, schemas, examples, and tools diverge (e.g., example packets no longer validate; registries reference missing items).

ARCH-4 **Maintainer compromise / rhetorical drift**  
A change subtly expands claims, obscures boundaries, or “passes the checks” while undermining deployment honesty.

ARCH-5 **Release tampering / supply-chain compromise**  
The distributed archive is modified (zip replacement, manifest mismatch, compromised build tools).

## 243.3 Existing defenses (what already exists in this repo)

This archive already carries several “drift firewalls” and integrity anchors:

- **Release gates:** `scripts/release_gate.py` (runs the coherence checks).
- **Content manifest:** `MANIFEST.sha256` (tamper-evident inventory for the shipped archive).
- **Schema + example validation:** example packets + schema checks (see `docs/213` and `scripts/check_example_packets.py`).
- **External citations without bundling:** lockfile + pinning workflow (`docs/151`, `docs/233`, `evidence/lock/external-sources.toml`).
- **Known-issues registry:** `artifacts/registries/known-issues.csv` (explicitly recorded breaks/risks).
- **Spec error response playbook:** `artifacts/playbooks/spec-error-response-playbook.md` (bounded incident-style loop).

## 243.4 Minimum response loop when the archive is wrong

When a credible ARCH-* issue is reported:

1) **Capture a bounded reproducer**  
Use `artifacts/templates/external-challenge-report.md` (or equivalent): version, claim, reproducer, expected vs observed behavior.

2) **Triage severity and freeze if needed**  
- If the issue could change outcomes or create non-recoverable ambiguity, treat as **high severity** and freeze promotion of affected material (see `docs/153`, `docs/229`).

3) **Publish a repair note and record the break**  
- Add/extend a row in `artifacts/registries/known-issues.csv` and ship a short repair note (template: `artifacts/templates/spec-error-response-note.md`).

4) **Patch with drift-proofing**  
A fix is incomplete unless it also adds at least one of:
- a schema constraint,
- an interop/test vector,
- an example packet,
- or a release-gate check that would have caught the failure.

## 243.5 External challenge interface (how outsiders should critique)

To prevent “read-the-whole-archive” review failure modes, external critiques should be submitted as:

- **A bounded challenge report** (`artifacts/templates/external-challenge-report.md`)
- Referencing a **specific claim card / proof obligation / hazard**, not “the whole system”
- Including a minimal reproducer whenever possible (packet, manifest digest, tool pin)

This is not bureaucracy; it is the smallest format that makes critique **actionable**.

## 243.6 Minimum external review process (small, repeatable)

Internal coherence checks do not detect mistaken assumptions. Minimum posture:

- Run **surface-focused external reviews** (one surface per session) using `artifacts/checklists/external-review-session-checklist.md`.
- Record each session (who/when/what surface + bounded challenge-report pointer) in `artifacts/registries/external-review-log.csv` so “external review happened” is auditable without bundling large appendices.
- Require critiques to be **bounded** (challenge report + reproducer when possible), so review does not degrade into “read the whole archive.”
- Publish a bounded response note and add a regression vector or gate check for any correctness-relevant issue.

This is a recommendation for all work and a practical requirement before promoting new claims into Track A.

## 243.7 Relationship to Track A deployment claims

Track A deployments must assume:
- the archive might have bugs,
- verifiers may disagree,
- and institutions may exploit ambiguity.

Operationally, this means Track A pilots should plan for:
- verifier diversity (`docs/30`, `docs/241`),
- rapid correction + refutation pathways (`docs/219`, `docs/240`),
- and explicit non-claims discipline (`docs/166`, `docs/167`).
