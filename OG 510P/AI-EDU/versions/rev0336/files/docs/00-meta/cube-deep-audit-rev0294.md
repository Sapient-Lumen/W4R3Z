# rev0294 cube deep audit

## Finding

The highest-risk incomplete seam after `rev0293` was returned-reply handling.
The cube could now prepare a packet and record the post-send clock, but a real
returned owner CSV still required a fragile manual command chain before reaching
a reviewer-ready seed.

## Change made

`rev0294` adds `tools/run_ft0181_returned_reply_work.py` and the Make target:

```bash
make owner-returned-reply-work CSV=/path/to/returned-owner-reply.csv \
  SOURCE_CONTACT_STATUS=scratch/.../contact-status.json
```

The helper runs:

1. source-provenance-gated local intake;
2. receipt and triage;
3. proceed-staged note creation only for `PROCEED-STAGED`; and
4. workbench seed creation only for `PROCEED-STAGED`.

For all other intake outcomes, it stops at the local intake outcome note.

## Waste corrected

The old path encouraged avoidable operator drift:

- router command copied by hand;
- direct intake run separately;
- seed command run separately;
- risk of seeding a non-proceed bundle by habit; and
- temptation to answer friction with more explanatory controls.

The refactor removes that command choreography while keeping the evidence wall
intact.

## What remains risky

The riskiest remaining gap is human review after a seed exists. The cube should
not automate that review. The next useful improvement, if needed, should be a
review-prep checklist or a tighter router handoff only after a real seed exposes
operator confusion.

## Closure boundary

No real owner was contacted by this release. No real returned CSV is included.
No `SRC2+` packet was accepted. No custody, public claim, live-window movement,
lifecycle action, or closure occurred. `FT-0181` remains live.
