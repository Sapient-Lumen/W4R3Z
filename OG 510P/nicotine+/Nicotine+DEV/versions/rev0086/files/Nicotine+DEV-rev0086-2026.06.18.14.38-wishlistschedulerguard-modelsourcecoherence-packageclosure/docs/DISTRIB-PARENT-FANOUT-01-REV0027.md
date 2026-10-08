# DISTRIB-PARENT-FANOUT-01 — distributed parent/child fanout and branch metadata

Revision: rev0027  
Canonical lead: **U-173**  
Support rows: **U-187**, **U-216**, **U-214**  
Deferred sibling: **U-179**

## Decision

**Verified across 3.3.10, 3.3.x, and master; not promoted to the strict document.**

This packet is useful, but it is not a fourth high-priority report candidate. The boundary is malicious Soulseek server, active MITM, compromised server stream, or distributed-parent/child state manipulation. The main consequence is connection fanout, child-slot/backpressure, and distributed-search state hardening. It is not peer-only file disclosure, code execution, or a stronger source-binding result than PB-01.

## What the rev0027 witness proves

Maintainer-style witness:

```text
maintainer_artifacts/distrib-parent-fanout-01/test_distributed_parent_fanout_reproducer.py
```

Run results:

```text
github-tag-3.3.10:   5 passed
github-branch-3.3.x: 5 passed
github-branch-master: 5 passed
```

Observed behavior:

```text
U-173:
  PossibleParents with 25 distinct entries is parsed into 25 potential parents.
  The server handler initiates 25 distributed parent connection attempts.

U-187:
  max_distrib_children=3 can be filled by three distinct claimed D PeerInit usernames.
  The client then emits AcceptChildren(False).
  A fourth distinct claimed child is rejected by the max-child limit.

PB-01 support found while checking U-187:
  a duplicate claimed D child username can replace the existing distributed child connection.
  This is not a new standalone row; it belongs to PB-01's primary-election/source-binding family.

U-216:
  the current distributed parent can send a 4096-byte DistribBranchRoot root string.
  The client accepts it as _branch_root and propagates BranchRoot / DistribBranchRoot.

U-214:
  3.3.10 forwards an unsupported server EmbeddedMessage wrapper to child peers before validation.
  3.3.x and master do not forward that unsupported embedded message shape.
```

## Source shape summary

The external rev0003 source bundle remains outside the cube. Compact source traces are recorded in:

```text
evidence/rev0027-distrib-parent-fanout-source-trace.md
```

Relevant source patterns:

- `PossibleParents.parse_network_message()` parses the declared count without enforcing the protocol-documented maximum of 10.
- The server `PossibleParents` handler assigns the full list to potential parents and initiates one distributed connection per entry when no current parent is active.
- Distributed child acceptance enforces `max_distrib_children`, but the identities occupying that budget are claimed usernames from peer-init state.
- A parent `DistribBranchRoot` update is accepted as the local branch root and propagated without a shared semantic username cap.
- 3.3.10 server `EmbeddedMessage` handling distributes the wrapper before local validation; 3.3.x/master changed the shape to unpack/validate only supported distributed search content before child fanout.

## Public-overlap status

**Classification:** public-adjacent / not clean novelty.

Hard searching found public distributed-network implementation context, but not a direct issue report for the exact over-10 `PossibleParents` fanout invariant. The project protocol documentation states that `PossibleParents` is a list of **max 10** possible distributed parents, and issue #994 publicly explains the distributed parent/child search-request implementation path.

There is also current/future upstream adjacency: 3.3.11 RC notes mention “some fixes for incorrect behavior in the distributed search network.” That makes this unsuitable for clean novelty language even though the exact U-173 over-10 connection-fanout test remains useful.

Searches captured in `evidence/rev0027-web-public-overlap-distrib-parent-fanout.md` included:

```text
"PossibleParents"
"distributed child peer"
"DistribBranchRoot"
"EmbeddedMessage" "distributed"
```

## Coherent fix shape

A coherent patch should not treat U-173, U-187, U-216, and U-214 as four unrelated one-off changes.

Recommended hardening shape:

```text
1. At the PossibleParents parser/handler boundary, cap entries at the documented max of 10.
   Prefer reject/log or truncate-with-audit; do not initiate more than 10 D parent attempts from one frame.

2. De-duplicate and normalize parent candidates before connection fanout.
   Preserve legitimate direct/indirect distributed parent fallback.

3. Keep distributed child-slot logic compatible, but do not let a duplicate D PeerInit silently replace an existing child without the PB-01 generation/source-binding invariant.

4. Apply the shared username semantic validator to BranchRoot / DistribBranchRoot values.
   Cap bytes, reject empty values where unsupported, reject control/bidi characters, and avoid propagating over-budget roots.

5. Keep the 3.3.x/master EmbeddedMessage rule: only unpack/forward supported distributed search payloads.
   Treat 3.3.10 unsupported-message fanout as a backport/regression test, not a new current-lane issue.
```

## Strict-document decision

Not promoted. Reasons:

```text
- server/MITM/distributed-parent scoped;
- availability/fanout/state hardening rather than file integrity/confidentiality;
- public/upstream distributed-search adjacency;
- U-187 duplicate replacement is already covered better by PB-01;
- U-214 is branch-changed in current/future lanes.
```

## Files added in rev0027

```text
maintainer_artifacts/distrib-parent-fanout-01/test_distributed_parent_fanout_reproducer.py
maintainer_artifacts/distrib-parent-fanout-01/README.md
tools/probe_rev0027_distrib_parent_fanout.py

evidence/rev0027-distrib-parent-fanout-pytest-run.txt
evidence/rev0027-distrib-parent-fanout-source-trace.md
evidence/rev0027-web-public-overlap-distrib-parent-fanout.md

data/rev0027_distrib_parent_fanout_probe_summary.csv
data/rev0027_public_overlap_distrib_parent_fanout.csv
data/rev0027_distrib_parent_fanout_coherence_refactor.csv
```
