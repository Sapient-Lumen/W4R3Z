# RFC-0091: Declarative image pipelines (apko/melange/Wolfi lessons)

Status: Draft

Decision note: `ADR-0289` and `docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md` now fix the language boundary around this RFC. This page remains the place for follow-on implementation detail about the exact restricted typed pipeline lane; it no longer reopens whether DeriveBSD should grow an in-tree general-purpose recipe evaluator.

## Summary

Introduce an optional “restricted recipe” lane where builds are expressed as typed, structured
pipelines instead of freeform shell scripts.

This is inspired by apko/melange’s declarative posture and reproducibility-by-default.

References:
- apko: https://github.com/chainguard-dev/apko
- apko file format: https://github.com/chainguard-dev/apko/blob/main/docs/apko_file.md
- melange: https://github.com/chainguard-dev/melange
- Wolfi overview: https://edu.chainguard.dev/open-source/wolfi/overview/

## Goals

- Make high-assurance builds easier to lint, diff, and policy-check.
- Keep network denied by default; fetching becomes a separate capability.
- Encourage minimal runtime images with explicit debug extensions.

## Non-goals

- Replacing full-power builders immediately.
- Locking DeriveBSD to apk-based packaging.
- Reopening a general-purpose in-tree recipe evaluator.

## Design sketch

- New derivation kind: `pipeline`
  - step graph recorded in the Plan
  - authoritative steps identify a registry-backed `step_kind`
  - no generic authoritative `run` / `script` / opaque command-array step in the native lane
  - imperative power may still exist inside bounded tool capsules/backends, but not as reviewed recipe authority
- Optional adapter lane: import/export of apko/melange outputs as foreign artifacts.

See: `docs/134-declarative-image-pipelines-apko-melange.md`, `docs/699-package-recipe-surface-stays-evaluator-free-and-restricted-pipeline-first.md`, `docs/700-native-restricted-pipelines-reject-generic-run-steps-and-stay-registry-backed.md`.
