# RFC-0091: Declarative image pipelines (apko/melange/Wolfi lessons)

Status: Draft

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

## Design sketch

- New derivation kind: `pipeline`
  - step graph recorded in the Plan
  - step types are restricted + toolcapsule-backed
- Optional adapter lane: import/export of apko/melange outputs as foreign artifacts.

See: `docs/134-declarative-image-pipelines-apko-melange.md`.
