# Cube deep audit rev0264

Date: 2026-06-13
Revision: rev0264
Status: terminal no-owner-packet and packet-integrity repair; `FT-0181` remains live and unclosed.

## What was most at risk

The riskiest remaining failure was not another missing doctrine surface. It was a
same-session state regression in the live field path. Rev0263 already stopped
malformed selected contact/intake/seed artifacts from driving commands, but a
later local `SENT_AWAITING_REPLY` or `REASK_AWAITING_REPLY` status in the same
scratch root could still outrank an already recorded `NO_OWNER_PACKET` status and
silently reopen a bounded no-packet session.

That is dangerous because `NO_OWNER_PACKET` is not success, evidence, or closure.
It is a terminal local outcome for that bounded first-contact attempt. Reopening
the same scratch state with another sent/reask note would create motion without
new owner context and would invite the cube's old vice: more local artifacts
instead of a real owner packet.

A second quiet risk sat one step earlier. The router trusted a local packet
manifest enough to emit a sent-clock command as long as a `packet_state` key
existed. A hand-edited packet manifest could claim sent/evidence/closure and
still look like the latest packet candidate. That is now blocked before routing.

## Concrete forward motion

The live path still starts with one router command:

```bash
make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003
```

The router now has two extra field-session stops:

- `OWNER-REQUEST-PACKET-INTEGRITY-BLOCKED` when the selected packet manifest no
  longer says exactly `FT-0181`, `PREPARED_NOT_SENT`, `NO-OWNER-PACKET-YET`,
  `not_evidence`, `does_not_close_ft0181`, and `public_claim_effect: none`.
- `CONTACT-STATUS-TERMINAL-REGRESSION-BLOCKED` when a same-scratch-root
  sent/reask contact status appears after a recorded `NO_OWNER_PACKET` status.

Those stops are progress because they keep the operator on the real field path:
regenerate the local packet through `make owner-request-packet`, use a new routed
scratch/session path only for genuinely new owner context, or leave `FT-0181`
live as blocked by missing owner evidence.

## Audit/refactor result

`tools/ft0181_field_guards.py` now centralizes packet-manifest integrity alongside
local output and returned-CSV source guards. `tools/decide_ft0181_field_next_action.py`
uses that shared guard before it can emit a sent-clock command.

`tools/check_ft0181_field_next_action.py` now includes regression fixtures for:

- locally edited packet manifests that claim sent, evidence, closure, or public
  claim support;
- same-scratch-root post-`NO_OWNER_PACKET` sent/reask regression;
- malformed contact status artifacts;
- malformed/non-live intake bundles;
- locally edited `ACCEPTED`/closed workbench seeds;
- previous cross-artifact manifest-clock, source/smoke, digest-output, and
  router-first cases.

The refactor is deliberately small. It adds no new registry family and no new
policy surface; it turns two field-session failure modes into checked command
stops.

## Still missing

`FT-0181` still lacks the only thing that would materially advance the pilot: a
real `SRC2+` owner-reviewed packet, a returned eight-row owner CSV, accepted
workbench content, a live-window readout, and a closure signoff. No rev0264
artifact changes that.

The next external move remains the same: run the router, send or adapt the
prepared owner packet outside the archive, record the sent clock through the
router-emitted command, and then either route a plausible returned owner CSV
through intake or record `NO_OWNER_PACKET` after the bounded follow-up path.

## Anti-waste note

Do not add another registry, broad request, evidence abstraction, or branch-tail
explanation to compensate for a missing owner packet. The cube's useful work now
is field execution and bounded local-state hygiene, not more policy prose.
