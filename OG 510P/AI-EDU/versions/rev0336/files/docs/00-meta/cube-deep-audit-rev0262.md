# Cube deep audit rev0262

## Posture

The cube remains ready-but-not-closed. `FT-0181` is still live because no real
`SRC2+` owner-reviewed packet has been received, no accepted import exists, no
live-window readout exists, and no closure signoff exists. Rev0253 made the
outbound owner request packet executable. Rev0254 made sent/re-ask/no-owner-packet
status executable. Rev0255 made scratch-state routing executable. Rev0256 made
routed owner-contact commands dated and clock-valid. Rev0257 and rev0258 made
returned-CSV source firebreaks shared across the router and direct tools.
Rev0259 and rev0260 removed fixed local output collisions. Rev0261 changed
scratch artifact selection to manifest-clock-first ordering. Rev0262 fixes the
next quiet stall/regression risk: older intake/workbench artifacts can no longer
outrank newer contact/no-owner outcomes simply because the router checked intake
before contact.

## Priority change

The riskiest remaining failure was a cross-artifact priority bug. Rev0261 made
individual artifact families sort by manifest clocks, but the router still
checked workbench seed and intake branches before contact status. That meant an
older `RE-ASK-ONCE` intake bundle could keep producing clarification commands
even after a later contact-clock or `NO_OWNER_PACKET` status existed.

Rev0262 changes the router to select the latest post-packet artifact across
contact status, intake bundle, and workbench seed candidates before choosing the
branch. Contact status manifests now include `created_at_utc`, and the router
uses that generated clock when present, falling back to `status_date` only for
older scratch artifacts. Every successful field-next docket now records
`latest_artifact_candidates` in addition to observed counts and the selected
artifact key, so the operator can audit why a contact, intake, or seed branch won
without reading raw scratch directories.

## Audit/refactor change

The audit target was still `tools/decide_ft0181_field_next_action.py`, with a
small supporting change in `tools/record_ft0181_owner_contact_status.py`. The
router now treats post-packet artifacts as one manifest-clocked state set before
branching. The contact recorder writes `created_at_utc` so router ordering does
not depend on filesystem mtime or date-only contact fields. The validator adds a
regression test: after an intake bundle requests `RE-ASK-ONCE`, a later
`NO_OWNER_PACKET` contact status must become the selected state and stop the
re-ask loop.

This is intentionally not a new registry or doctrine surface. It is a small
field-path refactor that makes repeated attempts and copied scratch artifacts
less likely to waste a session or reopen a blocked path.

## What changed in tooling

- `tools/decide_ft0181_field_next_action.py` now picks the latest post-packet
  artifact across contact status, intake bundles, and workbench seeds before
  branching.
- `tools/record_ft0181_owner_contact_status.py` now writes `created_at_utc` into
  contact-status manifests so future routing has a generated manifest clock.
- Field-next dockets now include `latest_artifact_candidates`, observed artifact
  counts, and the selected artifact key so operators can see which scratch state
  drove the recommendation.
- `tools/check_ft0181_field_next_action.py` now verifies both copied-stale-status
  protection and the newer-contact-status-over-older-RE-ASK-ONCE-intake case.
- Current local artifact version labels were advanced to `rev0262`.

## Current shortest path

In a clean release extract, ask for the next action:

```bash
make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003
```

Prepare the packet if routed:

```bash
make owner-request-packet OUT=scratch/owner-request-packets/aiedu-sr-003-first-contact
```

After a human sends or adapts the packet, rerun the router and execute the dated
sent-clock command it emits:

```bash
make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003-after-send
```

If a real CSV returns, route it through the router and execute the emitted intake
command:

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/ft0181-field-next-action/returned-owner-reply
```

After intake creates a local bundle, rerun the router. If the latest bundle is
`PROCEED-STAGED`, the emitted workbench-seed command uses the seed tool's
manifest-hash default output path. If the latest bundle is `RE-ASK-ONCE`, the
router emits the one allowed dated clarification-clock command. If the bounded
clarification clock lapses, the router emits the dated `NO_OWNER_PACKET` command
and keeps `FT-0181` live.

## What is still missing

The missing object is still external: one real owner-attested eight-row CSV, or a
recorded `NO_OWNER_PACKET` after a real first-contact attempt and one bounded
follow-up. No rev0262 output is evidence. A field-next docket, packet, contact
status note, receipt, intake bundle, staging note, or workbench seed does not
upgrade source truth, support a public claim, or close `FT-0181`.

## Waste corrected or still visible

Corrected: field-next routing no longer trusts file mtime or branch order as the main state
clock, so copied or touched old scratch state is less likely to regress the next
action. The router now exposes enough state-selection metadata to audit why a
command was recommended without creating a new registry.

Still visible: the archive remains large because branch-history and
release-control surfaces are retained. That is acceptable only while new work
keeps improving the single live field path instead of expanding doctrine. A real
block is progress; a new control surface is justified only if a real owner packet
exposes a failure that the existing router, packet, contact, receipt, intake,
staging, seed, workbench, custody, acceptance, and closeout path cannot represent.

## Validation intent

Rev0262 should pass `make lint-owner-reply`, `make lint-fast`,
`make lint-release-controls`, and `make lint-full` before packaging. The narrow
release claim is this: the cube has a router-first field path whose source,
clock, output-collision, archive-output, and scratch-state selection firebreaks
are enforced by router and direct tools; it still has no real pilot evidence and
no closure basis.
