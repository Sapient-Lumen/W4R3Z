# rev0336 source-result hashlink fresh-packet refactor

## Risk found

rev0335 made a `repeat-narrower` or `continue-bounded` decision require a local follow-through seed, but the actual fresh packet could still be produced by a generic `make micro-pilot-pack` command. That left an execution gap: the prior owner-reviewed result could say "fresh packet required," while the next packet carried no machine-readable link to the specific local result that authorized the repeat/continue path.

That gap is high-risk because it can create fake momentum. The operator may generate another broad packet, lose the prior decision boundary, or accidentally treat the previous local result as cumulative evidence rather than as non-evidence routing context.

## Change made

The packet generator now accepts a prior `MICRO-PILOT-RESULT.json` through `--source-result`, with the confirmation token `source-result-read-for-local-followthrough-not-evidence`.

When used, the generator validates that the source result:

- is `LOCAL_MICRO_PILOT_RESULT_RECORDED_NOT_EVIDENCE`;
- has decision `repeat-narrower` or `continue-bounded`;
- has no evidence, custody, service-authority, public-claim, or closure effect;
- recorded the owner follow-through seed without copying seed values;
- requires a fresh packet and forbids evidence escalation.

The new packet writes `FOLLOWTHROUGH-SOURCE-RESULT.json` and `.md`, which include only the source result path, SHA-256, revision, dates, source decision, and non-evidence boundary. They do **not** copy owner seed text, learner counts, protected facts, local observations, or prior result details.

The readiness scorer now checks the optional source link. If the linked source result is missing, changed, not a repeat/continue result, or not marked non-evidence, readiness fails before field use.

The router now emits `make micro-pilot-followthrough-pack SOURCE_RESULT=... CONFIRM=source-result-read-for-local-followthrough-not-evidence ...` for repeat/continue results rather than a generic fresh-packet command.

## Boundary

The source link is a continuity firebreak, not evidence import. It lets the operator make exactly one fresh local packet from human-supplied new arguments while preventing pooling, trend claims, service-record updates, public claims, or `FT-0181` closure from the prior result.
