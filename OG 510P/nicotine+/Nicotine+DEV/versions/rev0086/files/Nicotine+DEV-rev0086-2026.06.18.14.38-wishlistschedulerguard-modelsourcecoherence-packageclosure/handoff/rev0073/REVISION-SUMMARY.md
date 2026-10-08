# rev0073 revision summary

## Problem resolved

Rev0073 performs an exact-current disposition of U-123, a same-user duplicate transfer-token ownership collision in the download state machine.

The demonstrated chain is:

```text
peer has multiple local queued downloads
-> first request activates token T for transfer A
-> peer reuses T for transfer B
-> B replaces A in active_users[username][T]
-> stale cleanup for A can delete B's slot
-> later B progress/close callbacks cannot recover their transfer
```

## Selected and rejected designs

The selected minimal experiment rejects admission when a **different** transfer already owns the same username+token and makes deactivation identity-aware. A stricter experiment rejects every occupied slot, including a synthetic same-object reentry state. Because rev0073 did not show that extra state is reachable, the strict design remains unselected.

## Results

```text
exact supported 3.3.x ref: 98089ac233aa57786e8dbdc48123f6ac1c4767d8
focused classified expectations: 18/18
bounded burst expectations: 3/3
baseline upstream units: 58 passed, 1 skipped
selected upstream units: 58 passed, 1 skipped
native test-only negative control: 2 failed, 7 passed
native selected targeted tests: 9 passed
native selected full units: 60 passed, 1 skipped
```

The 32-request bounded experiment retained 32 file handles and 32 socket-owner references in the unpatched state, versus one of each under the selected guard. This is evidence of linear transient retention in the harness, not proof of durable descriptor exhaustion or end-to-end denial of service.

## Severity and routing correction

Current evidence supports a low-severity transfer correctness and robustness classification. It does not demonstrate cross-user takeover, arbitrary-file access, path escape, persistence, or a durable resource-exhaustion threshold. The private vulnerability route is therefore retired for U-123 on current evidence.

Targeted public searches found adjacent transfer-lifecycle issues but no exact direct match for the complete collision-and-stale-cleanup chain. This is a bounded search result, not proof of novelty.

## Cube audit and refactor

Rev0073 also corrects five cube problems:

```text
1. conflicting U-123 policy generations on one active artifact surface;
2. copied test fixtures and misleading compression-based line reductions;
3. shared temporary roots and clobbering result namespaces in validation tools;
4. readiness language incompatible with Nicotine+'s current AI contribution policy;
5. a self-referential boundary inventory that counted its own generated reports.
```

The rev0072 U-123 packet is preserved byte-for-byte under `docs/archive/rev0072-active-u123/`. The active set uses one readable shared harness, six explicit test roles, independent source/runtime roots, non-overlapping data namespaces, and a package-level coherence gate.

## Use boundary

Every generated patch, test, report, and sentence in this revision is research-only. Nicotine+'s current contribution policy excludes generative-AI-produced contribution content. Any upstream investigation must be independently reproduced, understood, implemented, tested, and written by a human.
