# SEARCH-RESP buddy artifact and orchestration refactor — rev0076

## Why refactor

The active buddy packet used one 212-line regression file to encode current behavior, proposed behavior, compatibility defaults, and implied disposition. That structure made a green patched run look more conclusive than it was.

The file is now archived byte-for-byte at:

```text
docs/archive/rev0075-active-search-resp-buddy/test_search_response_buddy_scope_fixed_regression.py
SHA-256 6b4d9ae5e246e70bcbce34790938ba252fbdd970f0f06382279bb3e328935c86
```

## New role-classified surface

```text
buddy_search_harness.py
  shared buddy-list, sender, and request construction

test_search_resp_buddy_current_behavior.py
  exact-current supported-branch witnesses

test_search_resp_buddy_rev0040_policy.py
  mechanics of the historical snapshot/claimed-name policy

test_search_resp_buddy_identity_counterexample.py
  PeerInit claim and response-body compatibility boundary

test_search_resp_buddy_snapshot_presence.py
  absent versus present-empty snapshot behavior

test_search_resp_buddy_master_resend_epoch.py
  Search Again counterexample after buddy-list mutation
```

Measured result:

```text
before: 1 file / 212 lines / 6,556 bytes / 2 lines over 100 characters
after:  6 files / 167 lines / 6,504 bytes / 0 lines over 100 characters
delta:             -45 lines / -52 bytes
```

The important gain is not the small byte reduction. Each test now has one evidentiary role, so expected failures are meaningful and no one suite silently chooses policy.

## Probe refactor

`tools/probe_rev0076_search_resp_buddy_disposition.py` also corrects two orchestration hazards:

- each run extracts source into a unique temporary root and gives nested pytest lanes isolated HOME/XDG/TMP/working directories;
- baseline and patched upstream parity compares semantic passed/failed/skipped counts, not pytest summary strings containing variable elapsed times.

The matrix is executed deterministically rather than sharing a mutable staging checkout. Runtime logs are stored by state and role under `evidence/rev0076-search-resp-buddy-runtime/`.

## Patch attribution refactor

The historical rev0040 helper stacked the rev0039 direct-user guard with the buddy components. The new helper applies only the buddy snapshot, sender, and claimed-name guard. That prevents a result from being credited to the wrong packet.

The helper remains a research experiment and is explicitly not selected.

## Wider historical inventory

The self-stable status audit found:

```text
SEARCH-RESP-01B-related files: 80
related bytes: 230,248
exact duplicate groups: 13
redundant exact-copy bytes: 36,901
historical strong-name files retained: 13
```

These copies are not deleted in rev0076 because many are signed-off historical handoff or replay evidence. The corrective refactor is to demote their status authority, preserve hashes, and keep only the role-classified suite active. A later compaction revision can replace exact duplicate exports with a content-addressed index after proving that downstream references remain recoverable.
