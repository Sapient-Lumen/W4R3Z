# Cube deep audit rev0236: end-window evidence readout and claim-laundering risk

Rev0235 made the first live window smaller and more reversible. The remaining high-risk gap was what
happens after that window. A stopped, rolled-back, or completed window can still become wasteful if it
lands as another archive artifact rather than a decision, and it can become dangerous if weak readouts
are laundered into learning, safety, access, workload, compliance, or scale claims.

## Finding 1: the window had controls, but the readout had no hard disposition

The live-window stop/rollback card named scope, stop triggers, rollback steps, evidence readouts, and
claim freeze. It did not force the end of the window to produce a bounded disposition. That left a gap
between operational safety and decision accounting.

Rev0236 adds `docs/30-operations/ft0181-end-of-window-readout-disposition-gate.md` and a machine
readout surface under `examples/live-window-readouts/`. The intended path is now:

```text
owner packet workbench -> first-packet decision board -> post-decision change ticket -> live-window
stop/rollback card -> end-of-window readout and disposition gate -> acceptance / lifecycle / closeout
```

## Finding 2: the highest-probability overclaim is claim-family substitution

The likely bad path is not an explicit false closure. It is a softer drift: usage volume becomes
learning evidence, no incident report becomes safety evidence, satisfaction becomes access evidence,
or faster drafting ignores teacher review and correction time. Rev0236 adds `IFF9` as a negative class
for end-window claim laundering and makes control coverage enumerate it.

## Finding 3: lifecycle should not complete a window without a readout pointer

The lifecycle row already required a decision board, change ticket, and live-window control. Rev0236
adds an `end_window_readout` object so a completed or rolled-back window cannot be represented without
source truth, disposition, claim-family effect, public-language ceiling, and closure boundary.

The example row remains blocked because there is still no real `SRC2+` packet.

## Refactor target

The refactor was intentionally narrow: add one disposition gate, one readout schema/checker, one
negative class, and lifecycle wiring. This avoids expanding doctrine while making the next live-window
result operationally useful.

## Residual risk

`FT-0181` still cannot close. The next real work is still external: obtain a minimized owner-reviewed
`SRC2+` packet, run the first-packet board, write the change ticket, stage the live-window card, and
then use the readout gate to decide stop, rollback, rerun, or bounded continuation.
