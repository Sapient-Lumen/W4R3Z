# rev0297 post-decision change-ticket brief refactor

## What changed

`rev0297` compresses the next risky seam in `FT-0181`: after a human records the
five-slice first-packet decision, the next post-decision change-ticket command is
still dense and easy to misuse. The dangerous failure is jumping from a decision
record to active change, live-window authority, service-record mutation, or
public language before a real SRC2+ packet and activation receipt exist.

New helper:

```bash
make owner-post-decision-change-ticket-brief \
  DECISION=scratch/.../first-packet-decision.json
```

`make owner-field-work` may now safely prepare this brief when the router selects
`PREPARE-POST-DECISION-CHANGE-TICKET-BRIEF`. It then reruns the router and stops
at a human-owned ticket-recording command.

## What the brief does

The brief validates a scratch-local first-packet decision, writes a one-screen
change-ticket handoff, and emits bounded command skeletons for:

- ready-for-real-packet sandbox adjustment;
- ready-for-real-packet trim;
- blocked no-real-packet;
- quarantine;
- active change only after an already-created activation receipt.

The default router command after the brief is the pre-activation
`ready-for-real-packet` path. The active-change template exists only to make the
activation boundary explicit; it requires a valid `owner-activation-receipt`
artifact and is not emitted as the normal next step.

## Boundary

The brief is not a post-decision change ticket. It is not evidence, not SRC2+
acceptance, not custody, not a public claim source, not a live-window card, not a
service-record edit, not lifecycle movement, and not closure.

The only valid next human-owned step after the brief is to choose one bounded
route and run `make owner-post-decision-change-ticket ...` with the confirmation
token `human-recorded-bounded-post-decision-change-ticket`.

## Waste corrected

The refactor removes a command-heavy local stall without adding a new governance
family. It also forces the operator to distinguish two materially different
modes: pre-real-packet readiness versus active change after activation receipt.
That distinction is the current high-risk laundering point.
