# Cargo Rebuild Explanation Kit — lane boundaries (2026-03-22)

This note prevents **P-0469** from swallowing every Cargo performance, history, or graph question in the archive.

## P-0469 is for

- one incident-sized rebuild mystery,
- session import/freeze behavior,
- baseline authority,
- exactness labeling,
- reverse-impact honesty,
- and small portable support bundles.

## P-0469 is not for

### 1. Historical warehousing or long-term regression series

That belongs primarily to **P-0035 cargo-build-insights**.
If the main question is “when did this start across many runs?”, do not force it into P-0469.

### 2. Resolver and feature-cause chains

That belongs primarily to **P-0468 Cargo Resolver Explanation Kit**.
If the main question is “why is this version or feature active?”, do not force it into P-0469.

### 3. Tool-only / compile-time-deps parity

That belongs primarily to **P-0494 Cargo Compile-Time-Deps Workflow Kit**.
If the main question is “did editor/tool-only workflow drift make this comparison misleading?”, do not force it into P-0469.

### 4. Waiting and lock contention

That belongs primarily to **P-0490 Cargo Lock Contention Witness Kit**.
If the main question is “what blocked and for how long?”, do not force it into P-0469.

### 5. Proving semantic interface preservation

That belongs to upstream compiler/Cargo work and adjacent analysis lanes.
P-0469 may report **relink_candidate_possible** or **interface_change_unproven**, but it should not pretend to prove semantic equivalence in 0.1.

## Core anti-flattening rule

Do not collapse these distinct claims into one fake “we know why Cargo rebuilt” verdict:

1. **the baseline was chosen coherently**,
2. **the compared runs are compatible enough to discuss together**,
3. **the rebuilt units were observed honestly**,
4. **reverse fanout is separated from proven interface change**,
5. **the exactness class of each claim is visible**.

A bundle can satisfy one or two of those and still mislead another reviewer.

## 6. Not comparison-scope replacement for tool-parity analysis

`comparison-scope.receipt.json` belongs in **P-0469** because a rebuild bundle must say whether two sessions are comparable enough to discuss together.
But if the main question is still “what exactly did the tool-only workflow build, and what should it have built instead?”, that remains primarily **P-0494 Cargo Compile-Time-Deps Workflow Kit**.

## Added anti-flattening rule

Do not collapse these distinct claims into one fake “same build, so same cause” verdict:

1. the baseline was chosen coherently,
2. the sessions are in scope to compare,
3. the artifact routes are close enough that reuse expectations mean the same thing,
4. the rebuilt units were observed honestly,
5. and adjacent tool-only context stayed visibly imported instead of silently becoming proof.
