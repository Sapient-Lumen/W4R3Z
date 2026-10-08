# rev0013 refactor / audit notes

## Real refactor: public payoff helper

rev0013 adds:

```text
src/muc5/public_payoff.py
```

This consolidates the repeated public payoff-row contract:

```text
play public DecisionFrame game
record simulator_revision
record interface
record reward_convention
record terminal/truncation labels
record mulligan policies
```

Older scripts can continue to exist, but new promotion-facing public tables should use this helper.

## Real bug fix: public CHOOSE_FOR_EFFECT scoring

`PublicProfileAgent` had a typo-like mismatch:

```text
action_schema emits: CHOOSE_FOR_EFFECT
public profile checked: CHOOSE
```

That meant public profile agents were not scoring discard/Jace choice actions as intended. rev0013 fixes the check to:

```text
if action.kind == "CHOOSE_FOR_EFFECT":
```

The fix also normalizes the actual engine form (`effect=discard`, `discard=<card>`) and reads Jace +2 seen-card data from `pending_choice_data` rather than non-existent action params. A regression test now checks that public agents prefer discarding Island over Force of Will for an Overlord discard choice.

## Audit additions

`scripts/audit_cube.py` now checks:

```text
rev0013_code_policy_payoff_gate
rev0013_code_policy_lint
rev0013_public_trusted_gap
rev0013_live_code_policy_smoke
required_files_present_through_rev0013
```

## Remaining concern

Readable policy code is inspectable, but not sandboxed. That is acceptable for archive-internal experiments, but if future revisions load arbitrary generated Python from disk, that loader must be treated as unsafe unless explicitly sandboxed.
