# rev0294 returned-reply workbench seed refactor

## What changed

`rev0294` compresses the next risky local seam in `FT-0181`: what happens after
an actual returned owner CSV/source packet exists. The prior path was safe but
brittle: run the router with `CSV=...`, copy the emitted intake command, inspect
the intake outcome, and then manually run the workbench seed only when the
triage result was `PROCEED-STAGED`.

The new bounded helper is:

```bash
make owner-returned-reply-work CSV=/path/to/returned-owner-reply.csv \
  SOURCE_CONTACT_STATUS=scratch/.../contact-status.json
```

For post-readout new context, the same helper is sourced from the context
receipt instead:

```bash
make owner-returned-reply-work CSV=/path/to/actual-returned-owner-context.csv \
  SOURCE_POST_READOUT_CONTEXT_RECEIPT=scratch/.../post-readout-context-receipt.json
```

The helper runs local intake and creates a workbench seed only if the intake
bundle is `PROCEED-STAGED`. Non-proceed outcomes stop at the generated intake
note. Blocked or protected/security/overbroad material does not seed the
workbench.

## Why this is the riskiest next seam

The archive had already shortened the pre-send and post-send local paths:
`owner-field-work` prepares the packet, and `owner-after-human-send` records the
send log plus active clock after a real human send. The remaining avoidable
friction was reply handling. A real returned CSV could still stall because the
operator had to chain intake and seed commands by hand.

This is a substance risk, not a registry risk. The cube is most wasteful when it
answers missing field progress with another explanatory surface. The corrective
move is to make the real returned packet easier to route without weakening the
source and claim boundaries.

## Boundaries preserved

This refactor does not:

- contact an owner;
- infer a recipient or owner route;
- accept owner answers as `SRC2+`;
- copy raw owner answers into release surfaces;
- run the human workbench review;
- create custody or acceptance;
- edit service records or public summaries;
- activate a live window;
- change lifecycle state; or
- close `FT-0181`.

The new session artifact is local non-evidence. It records source hashes,
provenance references, intake outcome, seed path when applicable, and the human
review boundary.

## Operator rule

After a real owner CSV returns, do not run direct intake first. Rerun the router:

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv \
  OUT=scratch/ft0181-field-next-action/returned-owner-reply
```

Then execute only the emitted `owner-returned-reply-work` command. If it creates
a workbench seed, a human must still review the minimized proceed-staged fields
before any workbench review record, decision board, activation receipt, change
ticket, live-window card, readout, post-readout action, custody step, public
claim, or closure action.
