# Release audit trace and reproducibility manifest

This surface adds a narrow audit layer for late-stage AI-EDU releases.
It does not prove that any AI service works. It proves only that the
archive's stated release posture, live queue, generated surfaces, and
selected file digests agree at packaging time.

Use it when a release is allowed to ship with an externally gated item,
especially `FT-0181`. The release may be handoff-safe while still being
substantively incomplete.

## RA states

| State | Meaning | May ship? |
|---|---|---|
| `RA0` | no release audit record | no |
| `RA1` | lint listed but not run | no |
| `RA2` | lint run, generated surfaces refreshed | maybe |
| `RA3` | selected source hashes verified | maybe |
| `RA4` | package verified after unpacking | yes, if the release candidate permits it |
| `RAX` | audit invalidated by queue, hash, or claim mismatch | no |

## Required manifest fields

A release audit manifest must name:

- the current revision and base revision;
- the live followthrough ids;
- whether all followthrough is claimed closed;
- the command path used to lint and package;
- the generated artifacts that were refreshed;
- selected file hashes;
- excluded files whose bytes are expected to change during packaging;
- the exact limits of the audit claim.

The manifest should hash enough files to catch accidental drift in the
release posture. It should not claim bit-for-bit reproducible zip archives
unless the packaging tool also controls timestamps, file ordering, and
compression metadata. The current package tool does not make that claim.

## Hash target default

Hash these at minimum:

- `REVISION_RECEIPT.json`;
- `FOLLOWTHROUGH_QUEUE.json`;
- `ASSUMPTION_LEDGER.json`;
- `SURFACES.json`;
- `context-pack.json`;
- `tools/run_lint_suite.py`;
- every new validator added in the release;
- every new schema and example record that affects release posture;
- every new human-facing surface that explains the release posture.

Do not hash `RELEASE-MANIFEST.json` inside this audit, because packaging
writes that file after lint has passed. The package can still be checked
after unpacking by running `python3 tools/run_lint_suite.py`.

## Stop rules

Set the audit state to `RAX` if any of these occur:

- the manifest claims all work is closed while `FOLLOWTHROUGH_QUEUE.json`
  still has a queued item;
- a selected hash fails;
- a release candidate permits shipping with an ungated open item;
- a synthetic example is missing from the source-status declaration;
- a policy exception bypasses `SRC2+`, protected-route separation, or
  public-summary evidence limits;
- a closeout record permits `FT-0181` closure without a real source packet.

## Relationship to existing gates

This surface sits after the ordinary lint suite and before packaging. It
is weaker than a real pilot import and stronger than an informal release
note. It complements, but does not replace, the release-candidate state,
operator handoff, closeout-board record, no-fake-real-import guard, and
assurance case.

## Current posture

rev0222 uses `RA4` for a ready-but-not-closed release. The audit verifies
repository consistency and selected digests while preserving `FT-0181` as
live because no `SRC2+` real pilot packet is present. The new coverage,
refresh, and quorum records are audit targets, not substitutes for real pilot evidence.


rev0222 also hashes the new invariant, dependency-graph, delta, drill, and closure-checklist controls as release-control artifacts. Hash success does not close `FT-0181`.
