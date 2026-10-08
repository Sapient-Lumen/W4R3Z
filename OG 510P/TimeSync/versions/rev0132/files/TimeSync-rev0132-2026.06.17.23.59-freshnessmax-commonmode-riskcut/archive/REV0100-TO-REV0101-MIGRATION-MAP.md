# rev0100 to rev0101 migration map

## Summary

rev0101 is a backward-compatible validation tightening for replay transparency. Valid fixtures that already had coherent replay, anchor, freshness, checkpoint, and witness times continue to validate. Invalid fixtures that rely on evidence after the anchor evaluation, or that cite `logged_at` freshness without binding `basis_time` to `transparency_anchor.logged_at`, now fail semantic validation.

## New helper

```text
tools/replay_transparency_temporal.py
```

The helper owns replay-transparency timestamp ordering and is invoked from `check_replay_transparency_audit`.

## New negative fixtures

```text
examples/negative/replay-transparency-replay-event-after-evaluation-invalid.json
examples/negative/replay-transparency-anchor-logged-after-evaluation-invalid.json
examples/negative/replay-transparency-anchor-freshness-basis-mismatch-invalid.json
```

## New semantic vectors

```text
TV-N270
TV-N271
TV-N272
```

## New derivations

```text
DF-0101-001
DF-0101-002
DF-0101-003
```

All three derive from:

```text
examples/evaluator/replay-transparency-receipt-p3-witnessed.json
```

## Validator movement

`tools/validate_archive.py` no longer owns replay-transparency anchor freshness arithmetic or checkpoint/witness observation timestamp ordering inline. Those checks are delegated to `tools/replay_transparency_temporal.py`.
