# rev0300 terminal live-window readout brief refactor

## What changed

`rev0300` compresses the next risky seam in `FT-0181`: after a human records a
terminal live-window card, the archive previously emitted a dense aggregate
readout command directly. That was safe, but it remained a drop-off point exactly
where the operator must distinguish terminal window state from end-of-window
readout, post-readout dispatch, service-record mutation, public language, and
closure.

New helper:

```bash
make owner-live-window-readout-brief \
  CARD=scratch/.../live-window-card.json
```

`make owner-field-work` may now safely prepare this brief when the router selects
`PREPARE-LIVE-WINDOW-READOUT-BRIEF`. It reruns the router and stops at the
human-owned aggregate-readout boundary.

## What the brief does

The brief validates only a scratch-local terminal live-window card in one of
these states:

- `paused`
- `rolled_back`
- `completed_no_closure`
- `quarantined`

It writes a one-screen handoff with state-matched `owner-live-window-readout`
command skeletons. The primary command preserves the source card hash,
source-truth class, evidence-readout count, reviewer-role minimum, no-public-claim
flags, no-service-record-edit flags, no-lifecycle-change flags, and
no-closure-from-readout confirmation.

## Boundary

The brief is not a readout. It is not post-readout dispatch. It is not evidence,
SRC2+ acceptance, custody evidence, public-summary support, lifecycle movement,
service-record mutation, or closure.

The refactor reduces operator drop-off at the point where a real bounded terminal
card must become an aggregate readout before any post-readout action dispatch can
happen.
