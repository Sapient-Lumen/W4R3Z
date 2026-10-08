# rev0286 cube deep audit

## Finding

The cube's practical center is now a field-execution rail, not the large body of
background governance. The rail had been hardened through packet prep, route
block, send log, reask log, source-clock intake, candidate review, first-packet
decision, activation receipt, active-change ticket, and live-window card. The
next weak seam was the first step after a terminal live-window card.

A terminal card was already bounded and non-evidence, but the router's next step
was a manual prose gate. That created a familiar waste pattern: a maintainer
could either over-interpret the card or create another explanatory surface to
avoid making the next action concrete.

## Refactor performed

Rev0286 converts the terminal readout step into executable scratch tooling:

```bash
make owner-live-window-readout CARD=scratch/.../live-window-card.json \
  WINDOW_DISPOSITION=continue-bounded SOURCE_TRUTH_CLASS=SRC2 \
  AGGREGATE_EVIDENCE_READ_COUNT=3 CLAIM_FAMILY_EFFECT_COUNT=2 \
  DECISION_DELTA_COUNT=1 FIELD_TRIM_COUNT=0 REVIEWER_ROLE_COUNT=2 \
  NO_PUBLIC_CLAIM_UPGRADE=1 NO_SERVICE_RECORD_EDIT=1 \
  NO_LIFECYCLE_CHANGE=1 NO_CLOSURE_FROM_READOUT=1 \
  CONFIRM=human-recorded-aggregate-readout-no-closure
```

The resulting readout is local, minimized, and hash-tied to the source terminal
card. It is an action dispatch source only, not evidence or closure.

## Waste reduced

The change removes one manual interpretation gap without adding a new policy
family. It also gives future maintainers a testable path for the terminal card
case, which is the kind of path most likely to be skipped when the archive feels
large.

## Residual waste

The cube still has a broad control plane. The useful discipline is to keep the
control plane behind the router. Re-entry should point to the router and current
mission kernel, not reproduce the whole archive.
