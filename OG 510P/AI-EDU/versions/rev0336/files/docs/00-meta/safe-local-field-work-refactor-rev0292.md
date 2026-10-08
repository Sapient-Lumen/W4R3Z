# rev0292 safe local field-work refactor

## Problem found

The highest-risk unfinished work was not another missing rule. It was the
operator seam between the router and the first real owner contact. In a clean
extract, the archive correctly emitted:

```bash
make owner-request-packet OUT=scratch/owner-request-packets/aiedu-sr-003-first-contact
```

That was safe, but it still required a maintainer to copy the command, prepare
the packet, rerun the router, and then locate the human-send or route-block
fork. This friction encouraged the cube's recurring failure mode: adding more
local doctrine because the actual field step still felt awkward.

## Refactor made

`tools/decide_ft0181_field_next_action.py` now supports `--execute-safe-local`.
The new mode does exactly one automatable thing:

1. run the same router and write the normal field-next docket;
2. if and only if the outcome is `PREPARE-FIRST-CONTACT-PACKET`, prepare the
   bounded first-contact packet locally;
3. rerun the router and write a post-prep docket;
4. write `SAFE-LOCAL-FIELD-SESSION.md` and `safe-local-field-session.json` with
   the human-action boundary.

The Makefile exposes this as:

```bash
make owner-field-work OUT=scratch/ft0181-field-work/aiedu-sr-003
```

The target is intentionally not a new evidence gate. It is a local execution aid
that stops before every action requiring a human field decision.

## Explicit non-automation boundary

The safe local mode must not automate or infer:

- who the accountable owner is;
- whether the route is valid;
- whether a request was sent or adapted;
- whether silence means anything;
- whether a returned packet is real;
- whether candidate evidence is accepted;
- whether a live window may start;
- whether a public claim, service record, lifecycle state, custody state, or
  closure state may change.

Those remain owner/human actions routed through the existing gates.

## Audit/refactor result

The actionable surface is now smaller. The maintainer can run one target and get
from clean scratch to a prepared packet plus the exact post-prep fork. The
archive still cannot send mail, invent a recipient, record a send, create a
contact clock, intake a CSV, accept evidence, or close `FT-0181`.

This is real forward movement because it consumes the safe local work that was
blocking the field rail, while preserving the hard boundary that only owner
return and human action can advance evidence state.
