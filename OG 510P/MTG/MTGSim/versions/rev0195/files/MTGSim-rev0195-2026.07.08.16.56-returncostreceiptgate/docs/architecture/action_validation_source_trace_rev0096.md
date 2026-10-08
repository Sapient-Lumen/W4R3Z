# rev0096 action validation source trace

## Why this was the next risky seam

rev0095 fixed the false claim that a bounded legal-action vector was necessarily exhaustive. The remaining replay risk was subtler: once an action was accepted, evidence still mostly said `legal=true`. It did not durably say whether the action was actually present in the offered choice surface or accepted by direct domain validation because the frontier was known incomplete.

That difference is consensus-critical for agents, replay, and debugging. A listed prefix choice and an omitted-but-legal combat declaration are both legal, but they prove different things about the choice surface.

## New contract

`validate_legal_action(...)` returns `LegalActionValidation` instead of forcing callers to collapse legality to a bool. The result carries:

- the choice kind and whether a choice was required;
- frontier completeness and generation limit;
- listed action count;
- choice request hash;
- `LegalActionValidationSource`.

The source is currently one of:

- `None` for rejected actions;
- `OfferedAction` for membership in the materialized choice surface;
- `DirectDomainValidation` for supported combat declarations/orders accepted outside an incomplete bounded prefix.

## Evidence path

`ActionReceiptRecord::choice_validation_source` is now hashed into transition evidence. `ActionTrace.v2` serializes it as `choice_source=...`. Replay checks the expected source before applying a step and returns `ChoiceValidationSourceMismatch` if the current engine derives a different source.

`ActionTrace.v1` remains parseable, but older rows are treated as wildcarded for source because that evidence did not exist yet. The parser does not invent provenance retroactively.

## Refactor boundary

This change deliberately avoids a new registry. It removes the stale membership-only validation helper, routes legality through one typed validation result, and makes the receipt/trace/replay spine carry the fact that mattered.

## Still missing

The bounded vector is still only a prefix. The next larger legal-choice protocol should provide authoritative `validate(action)`, paged enumeration, stable cursors, count/bound queries, and structured combat declaration variables rather than forcing every consumer through a flat vector.
