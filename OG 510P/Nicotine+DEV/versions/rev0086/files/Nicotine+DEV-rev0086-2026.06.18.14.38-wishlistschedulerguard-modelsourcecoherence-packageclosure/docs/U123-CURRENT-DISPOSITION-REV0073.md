# U-123 current disposition — rev0073

## Decision

U-123 is a **confirmed peer-triggerable transfer correctness and robustness defect** on the exact supported `3.3.x` branch snapshot at:

```text
98089ac233aa57786e8dbdc48123f6ac1c4767d8
```

Current evidence does not justify a private vulnerability-report route. The defensible cube state is a low-severity public correctness research question, subject to independent human reproduction and authorship under upstream's contribution rules.

This is a severity correction, not a technical retraction. The transfer-session ownership invariant is reproducible, and the selected minimal prototype prevents the demonstrated state.

## Narrow invariant

Nicotine+ stores active transfers in a per-user token map:

```text
active_users[username][token] -> Transfer object
```

The same map routes file initialization, progress, close, and timeout-adjacent state. In the captured current source:

```text
Transfers._activate_transfer()
    assigns active_users[username][token] = transfer without a collision check

Transfers._deactivate_transfer()
    deletes by username+token without checking object identity

Downloads._file_transfer_init()
Downloads._file_download_progress()
Downloads._file_connection_closed()
    recover the transfer through username+token
```

A peer already serving two queued downloads to the local user can reuse one token. The second accepted request replaces the first local owner. A stale timeout for the first transfer can then delete the slot used by the second. Later progress and close callbacks for the second connection no longer find a transfer.

## Exact-current validation

The gate verifies the external source bundle by SHA-256 and confirms the lane head before extracting three independent states:

```text
unpatched
selected-minimal
strict-experiment
```

Final classified results:

```text
focused test expectations: 18/18
burst-state expectations: 3/3
unpatched upstream units: 58 passed, 1 skipped
selected upstream units: 58 passed, 1 skipped
upstream outcome parity: pass
native test-only patch on unpatched source: 2 failed, 7 passed (expected)
native combined patch target: 9 passed
native combined patch full units: 60 passed, 1 skipped
```

The expected matrix is intentionally asymmetric:

```text
current-bad-state witness:
  passes only unpatched

collision, identity-cleanup, burst, and composite fixed behavior:
  fail unpatched; pass selected and strict

same-object reentry experiment:
  fails unpatched and selected; passes strict
```

A nonzero result counts as expected evidence only when the runner executed at least one test. Parse failures and zero-test results fail the gate.

## Selected minimal behavior

The selected research prototype:

1. Resolves the queued or failed download associated with the incoming request.
2. Looks up the current owner of the same username+token.
3. Rejects the request before dequeue or activation when a **different** transfer owns the token.
4. Leaves the colliding transfer queued.
5. Makes deactivation object-identity-aware.
6. Still clears transfer-local timer, socket, token, and bandwidth state for a stale object without deleting another object's map entry.

The cleanup guard is defense in depth. The admission guard prevents the demonstrated replacement; the cleanup guard protects map ownership if a conflicting state arises through another path.

## Why the strict alternative is not selected

The strict experiment rejects every request whose username+token slot is occupied, even when the resolved queued object is the same object already in the slot.

Its extra test deliberately synthesizes one transfer as simultaneously active and queued. Rev0073 did not find a supported runtime transition that creates this overlap. Choosing stricter externally visible behavior without reachability or protocol-compatibility evidence would exceed the demonstrated bug. The strict patch remains an experiment, not the recommended prototype.

## Bounded resource experiment

A focused 32-request burst reuses one username and one token across 32 queued files. The harness records live file handles and transfer objects retaining a socket reference:

```text
unpatched:
  accepted 32, rejected 0
  live file handles 32
  socket-owner references 32
  queued files remaining 0

selected-minimal:
  accepted 1, rejected 31
  live file handles 1
  socket-owner references 1
  queued files remaining 31

strict-experiment:
  same bounded result as selected-minimal for different-object collisions
```

This demonstrates linear transient retention in the bounded harness and a constant live footprint under either guard. It does **not** establish durable operating-system descriptor exhaustion, persistence, remote amplification, or an end-to-end denial-of-service threshold.

## Impact and security ceiling

### Preconditions

The triggering peer must already be the counterparty for at least two local queued downloads under the same resolved username and must reuse a transfer token. The outer map remains scoped by username. The cube has not demonstrated an arbitrary-host primitive, a cross-user collision, or a separate identity-spoofing chain.

### Demonstrated consequences

```text
- active transfer ownership can be replaced;
- stale cleanup can remove the later owner's lookup slot;
- progress and close callbacks can be ignored;
- transfer-local handles and socket references can remain live in the bounded harness;
- affected downloads can stall and require retry or user intervention.
```

### Not demonstrated

```text
- code execution or privilege escalation;
- credential, private-message, or arbitrary-file disclosure;
- writing outside configured download paths;
- cross-user session takeover;
- persistence after restart;
- a measured durable descriptor, memory, disk, or bandwidth exhaustion threshold.
```

A malicious serving peer already controls delivery of its own files. U-123 adds client-side ownership confusion and transient resource growth, but current evidence does not show a qualitatively stronger security-boundary crossing.

## Public-overlap review

Targeted public searches captured on June 17, 2026 found no exact issue for the complete chain:

```text
same username + duplicate peer token
-> active owner replacement
-> stale first timeout
-> later F-connection lookup orphaned
```

Adjacent transfer-lifecycle issues exist, including reports around queued/disallowed responses and connectivity symptoms. They are context, not demonstrated duplicates. The honest statement is:

> No exact direct public match was found in the captured targeted searches; adjacent transfer-lifecycle reports exist.

This is not proof that the behavior has never been discussed or reported.

## Machine-readable evidence

```text
data/rev0073_u123_disposition_summary.json
data/rev0073_u123_test_matrix.csv
data/rev0073_u123_burst_metrics.csv
data/rev0073_u123_source_invariants.csv
data/rev0073_u123_upstream_unit_parity.csv
data/rev0073_u123_refactor_metrics.json
data/rev0073_u123_native_patch_summary.json
data/rev0073_u123_native_patch_matrix.csv
evidence/rev0073-u123-runtime/
evidence/rev0073-u123-public-overlap.md
```

## Final routing

```text
technical status: confirmed on exact captured supported branch
impact class: targeted transfer availability/session integrity
resource evidence: bounded linear transient retention, no durable exhaustion threshold
security confidence: insufficient for private vulnerability routing
public overlap: no exact match found in targeted searches; adjacent reports exist
selected prototype: different-object collision rejection plus identity-aware cleanup
strict prototype: unselected reachability experiment
upstream use: independent human reproduction, implementation, testing, and authorship required
```

A human investigation could change this classification by showing persistent resource exhaustion, a stronger identity boundary crossing, byte redirection to a different local file, protocol incompatibility with rejection, or an existing maintainer-defined preferred behavior. Absent such evidence, low-severity correctness handling is the most supportable conclusion.
