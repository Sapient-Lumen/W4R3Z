# Dual-Use Policy (Draft) + Public Export Semantics

Concord is a “defense-first” lab for stress-testing cooperation/reciprocity strategies. This has **dual-use risk**: robustness testing can encode exploit recipes.

This doc turns the spec-pack intent (`Original-Starting-Place/06_Red_Team_and_Adversaries.md`) into concrete operator rules.

## Principles

- **Goal:** improve defensive robustness and failure understanding, not build the “best exploit strategy”.
- **Public by default:** assume outputs may be shared; only include details that are safe under that assumption.
- **No recipe leakage:** keep exploit triggers, adversary implementations, and parameters that enable exploitation out of public artifacts unless explicitly approved.

## Current implementation (today)

`grlab export --public` currently produces a tarball that includes:
- a redacted `manifest.json` (task ids + artifact filenames only),
- a redacted `report.json` (experiment details removed),
- redacted `artifacts/*.json` where `trace` is removed,
- and an `attestation.json` binding hashes of the exported bytes (`grlab/attest.py`, `grlab/verify.py`).

It also supports an executable denylist that blocks public export by default when matching task/strategy ids are present:
- denylist file: `policy/public_export_denylist.json`
- override: pass `--allow-sensitive` (explicit, intentional)

Code: `grlab/exporter.py` (`redact_run_public`, `export_run_public_tar`).

## What is still missing (big-ticket)

- A richer notion of **SENSITIVE** beyond “drop traces” + denylist regexes (e.g., redacting recipe-level parameter fields for strategy families that encode them outside tasks).
- Redaction of recipe-level strategy parameters (when those exist outside tasks).
- A “public narrative summary” format that explains failures without enabling them.

## Operator rules (practical)

- Keep adversary implementations in **private registries** (do not put them in public `examples/`).
- Prefer publishing:
  - probe ids and high-level descriptions,
  - failure envelopes (what class of weakness exists),
  - mitigations and defensive patterns,
  - and **trace-free** summary metrics.
- If you need to share something ambiguous, share a **public export** bundle and treat internal run dirs as sensitive by default.
