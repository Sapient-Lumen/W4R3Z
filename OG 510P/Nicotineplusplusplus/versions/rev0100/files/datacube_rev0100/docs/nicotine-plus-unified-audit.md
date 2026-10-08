# Nicotine+ cumulative audit — rev0100

## Latest round summary

Rev0100 audits the retry-admission side of the lifecycle bridge introduced by the accepted-work hardening stream. Rev0099 fixed retry ordering by placing tiny cleanup/rollback events ahead of ordinary preserved payloads. Rev0100 fixes the complementary admission problem: priority cleanup events must be admitted even when the retry shelf is full of ordinary preserved events.

## Highest-value rev0100 finding

**Priority lifecycle cleanup can still be dropped when the retry shelf is full of ordinary preserved payloads.** A full retry shelf containing ordinary events such as preserved private messages or request-intent objects can reject a later `file-connection-closed`, `peer-message-unsent`, `peer-response-unsent`, or `server-message-unsent` event before the priority insertion logic ever runs. Those tiny events are exactly the cleanup signals that keep transfer state, peer-init state, grants, and request ledgers honest.

## Implementation

- Added a single lifecycle-retry admission predicate.
- Added safe removal/release accounting for queued retry entries.
- Added priority-admission room-making that evicts only nonpriority retries.
- Preserved relative order among existing priority events.
- Kept the same count and byte budgets.
- Added regression coverage for both ordinary-payload eviction and priority-only non-eviction.

## Reportability

This is mostly a cube/hardening-layer correctness fix because current upstream still uses an unbounded main-thread bridge. It belongs in the new/unmentioned lane as a precise mechanism and design invariant: a bounded bridge must not allow ordinary preserved payloads to crowd out cleanup/rollback events.

## Validation observed

```text
compileall: OK
new rev0100 targeted regressions: 2 tests OK
NetworkThreadUnitTest + EventsTest: 287 tests OK
all unit modules except test_i18n.py: 1042 tests OK, 1 skipped
```

Not claimed: GTK runtime coverage, i18n/`msgfmt` coverage, live-network behavior, every possible mixed global-state ordering, or proof nobody noticed this privately.
