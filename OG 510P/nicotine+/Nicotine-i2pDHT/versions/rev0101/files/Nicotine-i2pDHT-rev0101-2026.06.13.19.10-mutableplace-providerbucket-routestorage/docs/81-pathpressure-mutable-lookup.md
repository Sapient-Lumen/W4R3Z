# Path-pressure mutable lookup

`pathpressure.py` tests the lookup acceptance problem before real I2P latency hides it.

## Risk

A captured or merely unlucky path family can answer first. If clients accept the fastest quorum, the DHT becomes easy to bias. The subtle failure is a valid stale record that arrives before the newer record. A normal local monotonic memory system may accept the old sequence first and then accept the new sequence later without ever marking the earlier reply as stale pressure.

rev0010 adds **post-hoc stale detection**:

```text
observe all returned signed heads
find highest valid sequence
mark lower valid sequences in the same lookup as stale pressure
```

That is not proof of attack. It is a reason to keep asking more independent paths or preserve evidence.

## Decision ladder

`PathPressureDecisionKind` currently includes:

```text
accept_highest
continue_low_diversity
continue_empty_cluster
continue_stale_pressure
continue_fork_pressure
continue_invalid_pressure
continue_no_valid_head
```

The important default is conservative: a lookup can be cryptographically valid and still remain open.

## Tests

The tests cover:

```text
fast single-family empty replies must not satisfy early acceptance
later diverse clean replies can accept the highest head
stale head arriving first is still detected post-hoc
same-sequence fork keeps lookup open and produces witness receipts
```

## Guess

Future live lookup should maintain several independent-ish path queues. It should not merge all candidates into one soup and stop after the first provider-looking or head-looking result.
