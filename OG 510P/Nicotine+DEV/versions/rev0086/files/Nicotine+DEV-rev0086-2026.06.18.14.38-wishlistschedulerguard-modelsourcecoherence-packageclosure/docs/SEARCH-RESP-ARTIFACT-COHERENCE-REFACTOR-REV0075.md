# SEARCH-RESP artifact coherence refactor — rev0075

## Problem

The active SEARCH-RESP-01A surface consisted of two large modules that each carried their own fixtures, source loader, fake network filter, and policy assumptions. One was called a current reproducer and the other a fixed regression, encouraging readers to equate a green patched suite with a complete disposition.

The wider cube also retains many historical `PRODUCTION-READY`, `PRODUCTION-GATE`, patch-stack, rerun, and handoff copies. Their provenance is useful; their status language is not current authority.

## Refactor

The original active pair was moved byte-for-byte to:

```text
docs/archive/rev0074-active-search-resp-01/
```

Hashes:

```text
d7f98b7fca31085e10df98782ebd824e4d10e950567b5826079a4fa2f6507e6e  test_search_response_scope_and_parse_order_reproducer.py
fc91da0e93f9086f0193e7d2903b56f06e0d5978c730c9295b02989a3966a9c1  test_search_response_user_scope_fixed_regression.py
```

The active surface now has one shared harness and four evidentiary roles:

```text
search_resp_harness.py
  exact-current request, response, network-filter, and wire PeerInit helpers

test_search_resp_current_behavior.py
  observations of unpatched behavior

test_search_resp_rev0039_policy.py
  assertions encoded by the historical guard

test_search_resp_identity_counterexample.py
  wire-level reason the guard is not authentication, plus payload-name compatibility

test_search_resp_token_model.py
  bounded range/sequential-allocation observations, explicitly not exploit proof
```

Adjacent buddy, room, prefix-budget, and result-budget packets remain outside this adjudication.

## Measured change

```text
before: 2 files, 322 lines, 9,898 bytes, 2 lines over 100 characters
after:  5 files, 198 lines, 6,459 bytes, 0 lines over 100 characters
delta:   -124 lines, -3,439 bytes
```

The file count rises because roles are explicit; duplicated fixture mass falls. A test's filename and role now say whether a failure is expected.

## Corrected waste pattern

The important waste was not only duplicate bytes. It was **status duplication**:

```text
historical green regression
  -> copied into a production gate
  -> copied into patch stacks and handoffs
  -> repeatedly revalidated mechanically
  -> still missing identity, reachability, and impact proof
```

Rev0075 prevents that chain from silently remaining authoritative by:

- adding a current disposition row with `selected_patch: null`;
- classifying historical strong-status artifacts in a deterministic inventory;
- checking archived hashes;
- rejecting current landing pages that call SEARCH-RESP-01A production-ready;
- excluding the audit's own outputs and verifying self-reference stability.

## Wider SEARCH-RESP duplication audit

The deterministic inventory found:

```text
SEARCH-RESP-related files: 516
measured bytes: 1,221,199
exact duplicate groups: 80
duplicate bytes beyond one canonical copy: 200,990 (16.5%)
```

The largest groups are not subtle near-duplicates. They are byte-identical tests, patch helpers, rerun transcripts, and patch files copied into active artifacts, rev0048 handoffs, rev0059 bundles, and rev0062 clean-room kits. For example, the room-scope regression is present three times (15,696 redundant bytes), the buddy-scope regression is present three times (13,112 redundant bytes), and a 12,203-byte rev0039 rerun transcript is copied into a handoff unchanged.

`data/rev0075_search_resp_duplicate_groups.csv` ranks every exact group. Rev0075 does not delete historical handoffs because they may be consumed as self-contained snapshots. The corrective direction is now explicit: future handoffs should prefer a content-addressed manifest and one canonical payload over copying the same files into every export.

## Preservation rule

No historical report or evidence file was deleted. Current navigation and active tests are smaller; provenance remains addressable. The machine-readable authority is `data/current_packet_dispositions.json`.
