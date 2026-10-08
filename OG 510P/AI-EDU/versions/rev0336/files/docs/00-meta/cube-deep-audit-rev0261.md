# Cube deep audit rev0261

## Posture

The cube remains ready-but-not-closed. `FT-0181` is still live because no real
`SRC2+` owner-reviewed packet has been received, no accepted import exists, no
live-window readout exists, and no closure signoff exists. Rev0253 made the
outbound owner request packet executable. Rev0254 made sent/re-ask/no-owner-packet
status executable. Rev0255 made scratch-state routing executable. Rev0256 made
routed owner-contact commands dated and clock-valid. Rev0257 and rev0258 made
returned-CSV source firebreaks shared across the router and direct tools.
Rev0259 and rev0260 removed fixed local output collisions. Rev0261 fixes the
next quiet stall/regression risk: scratch artifact selection can no longer be
silently driven by file modification time alone.

## Priority change

The riskiest remaining failure was a copied-stale-state problem. The field router
previously used filesystem mtime to choose the latest local packet, contact
status, intake bundle, or workbench seed. In a long cloudtainer session, a copied
old `SENT_AWAITING_REPLY` status can receive a newer mtime than a later
`NO_OWNER_PACKET` status. That could make the router regress the field state and
recommend waiting or re-asking after the bounded no-owner outcome had already
been recorded.

Rev0261 changes scratch-state selection to manifest-clock-first ordering. Contact
status selection now ranks by embedded `status_date`, `attempt_count`, contact
status rank, and `response_due_date`; mtime is only a final tie-breaker. Intake
bundles and workbench seeds prefer embedded `created_at_utc`; packet manifests
prefer the embedded requested return date. Every successful field-next docket now
records `scratch_selection_rule: manifest-clock-first-file-mtime-tiebreaker-only`,
observed artifact counts, and the selected artifact key.

## Audit/refactor change

The audit target was `tools/decide_ft0181_field_next_action.py`. The router was
already doing useful work, but it mixed decision policy with a brittle `latest()`
helper that hid how scratch state was selected. Rev0261 factors that into
explicit artifact ranking helpers and adds a regression test: after a valid
`NO_OWNER_PACKET` status exists, a newly written but older-date `SENT` status
must not become the selected state.

This is intentionally not a new registry or doctrine surface. It is a small
field-path refactor that makes repeated attempts and copied scratch artifacts
less likely to waste a session or reopen a blocked path.

## What changed in tooling

- `tools/decide_ft0181_field_next_action.py` now ranks scratch artifacts by
  manifest clocks and semantic contact-state rank before using mtime as a
  tie-breaker.
- Field-next dockets now include observed artifact counts and the selected
  artifact key so operators can see which scratch state drove the recommendation.
- `tools/check_ft0181_field_next_action.py` now verifies that a copied stale
  contact-status artifact with newer mtime cannot outrank a recorded
  `NO_OWNER_PACKET` status.
- The duplicate `write_docket(...)` return in the router was removed.
- Current local artifact version labels were advanced to `rev0261`.

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
follow-up. No rev0261 output is evidence. A field-next docket, packet, contact
status note, receipt, intake bundle, staging note, or workbench seed does not
upgrade source truth, support a public claim, or close `FT-0181`.

## Waste corrected or still visible

Corrected: field-next routing no longer trusts file mtime as the main state
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

Rev0261 should pass `make lint-owner-reply`, `make lint-fast`,
`make lint-release-controls`, and `make lint-full` before packaging. The narrow
release claim is this: the cube has a router-first field path whose source,
clock, output-collision, archive-output, and scratch-state selection firebreaks
are enforced by router and direct tools; it still has no real pilot evidence and
no closure basis.
