# SECOND-SEMANTIC-TEST

This note asks whether Lane A now forces a second promoted semantic beyond `rate_error_bound`.

## Question

After the rev0019 break attempt, do the hardest Lane A cases still fit inside:
- `rate_error_bound`
- `freshness`
- `regime`
- `holdover_class`

or do they force another first-class semantic such as explicit stability or holdover confidence?

## Current result

**No decisive second semantic is forced yet.**

The archive still sees real pressure around:
- stability
- holdover behavior
- recovery after loss of reference

But the current evidence does not yet show that these must be promoted into a second first-class field.

## Why the current stack still holds

### 1. Holdover pressure already has neighboring semantics
The archive already exposes:
- `freshness`
- `regime`
- `holdover_class`

That means the field candidate does not need to encode the whole holdover story internally.

### 2. Stability matters, but not yet as an independent promoted semantic
The source base keeps stability important, but the current pressure still looks like support for the trustworthiness of the bound rather than clear evidence for a second externalized field.

### 3. Recovery behavior looks regime-shaped before it looks field-shaped
Loss of traceable path, holdover entry, and recovery after backup-path selection still look more like regime and control-surface transitions than like a second Lane A field.

## Why this is only provisional

The archive has **not** proved that a second semantic will never be needed.
It has only failed to find the decisive counterexample so far.

## Current archive posture

Keep:
- `rate_error_bound`
- `freshness`
- `regime`
- `holdover_class`

Do **not** yet promote:
- explicit stability field
- explicit holdover-confidence field

## What would overturn this result

The archive should reverse this note if it finds a Lane A case where:
- `rate_error_bound` remains honest,
- the neighboring semantics remain present,
- and users still cannot act correctly without a second promoted semantic.
