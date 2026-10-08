# Cube deep audit rev0253

## Posture

The cube is still ready-but-not-closed. `FT-0181` remains live because there is
no real `SRC2+` owner-reviewed packet, no accepted import, no live-window readout,
and no closure signoff. Rev0252 fixed the smoke/triage firebreak. Rev0253 focuses
on the next missing field move: preparing the first outbound owner request packet
without adding another broad planning layer.

## Priority change

Rev0253 adds `tools/prepare_ft0181_owner_request_packet.py` and the make target
`make owner-request-packet`. The tool creates the copy-paste email, blank CSV,
send checklist, and manifest for `AIEDU-SR-003` in `scratch/` or an external path.
It blocks archive-controlled output directories and labels the result
`PREPARED_NOT_SENT`, `NO-OWNER-PACKET-YET`, and `not_evidence`.

This is a deliberately boring repair. It turns the highest-risk non-completion
point into one command. The next useful human action is to send or adapt the
packet, not to create more doctrine about why the packet matters.

## Refactor/audit change

Rev0253 also splits the lint plane into lanes:

- `make lint-owner-reply` for the first-contact and owner-reply path.
- `make lint-fast` for changed navigation, registries, owner-reply tooling,
  watchlists, and generated maps.
- `make lint-release-controls` for release-control examples and slow gates.
- `make lint-full` for the complete release gate.

The source of truth remains `CUBE_TOOLCHAIN_REGISTRY.json`; `tools/run_lint_suite.py`
now reads `lint_lanes` rather than hardcoding a second validator list. This should
reduce wasted cloudtainer time during small field-path repairs while preserving the
full release gate.

The audit also found a concrete post-reply command bug in the new first-contact lane:
the seed command pointed at an `owner-reply-intake-bundle.json` filename even though
`tools/seed_owner_packet_workbench.py` expects the intake bundle directory containing
`bundle-manifest.json`. Rev0253 corrects the generated checklist, manifest, root
re-entry examples, and validator so this cannot regress silently.

The owner-reply validators were then made subprocess-free where practical by importing
the receipt, intake, staging, smoke, triage, and workbench-seed functions directly.
`tools/run_lint_suite.py` reads `lint_lanes` from `CUBE_TOOLCHAIN_REGISTRY.json` and
runs selected validators in-process through `runpy`, preserving registry order while
removing the subprocess-per-check fan-out that had made focused cloudtainer loops
feel heavier than the field repair itself.

## Risk crosswalk

Rev0253 adds `docs/20-governance/education-ai-deployment-risk-crosswalk.md` and
refreshes the GenAI education governance watchlist. The crosswalk compresses
external law/guidance signals into deployment lanes: low-risk teacher drafting,
bounded `FT-0181` course operations, tutoring, advising, high-risk assessment or
admission uses, and protected-support/discipline retreat. It is a live decision
surface, not a claim surface.

## What remains

The archive still needs one of two outcomes:

1. a real owner-attested eight-row CSV that survives intake and proceeds to a
   local workbench seed; or
2. a recorded `NO-OWNER-PACKET` after the response clock and one clarification.

Everything else should be subordinated to that field outcome. Branch compression
and doctrine cleanup are useful later, but not before the first-contact lane is
actually exercised.

## Validation intent

Rev0253 should pass `make lint-owner-reply`, `make lint-fast`,
`make lint-release-controls`, and `make lint-full` before packaging. If the
monolithic lane becomes slow again, the lane split lets maintainers isolate the
field-path checks without weakening the final release gate.

## Cloudtainer packaging note

Release packaging now excludes hidden path components so local `.git/` or similar cloudtainer residue cannot leak into the handoff zip.
