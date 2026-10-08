# Cargo Rebuild Explanation Kit — frontier note (2026-03-22)

## Product frontier

The frontier for **P-0469 Cargo Rebuild Explanation Kit** is now sharper than “Cargo but nicer”.

Cargo is growing the recorder/query substrate.
What is still missing for downstream users is the **review contract** above that substrate.

The two most important unsolved review questions are now:

1. **baseline authority** — why this baseline was chosen and whether the comparison is compatible enough to support the conclusion;
2. **reverse-impact honesty** — whether reverse dependencies merely rebuilt, whether a relink-only opportunity is plausible, and where interface change is still unproven.

## Why this matters

Without those two layers, a support bundle can still mislead:

- it can compare a build against the nearest prior session even when that earlier session used a different command role or target/profile mix;
- it can report reverse-dependency rebuilds as though they prove public-interface change;
- it can blur observed Cargo facts and downstream judgment into one fake certainty tone.

## The crate should now aim for

- session import/freeze behavior,
- exactness labeling,
- baseline-authority receipts,
- reverse-impact reports,
- and small portable bundles suitable for CI comments, support threads, or issue reports.

## The crate should not aim for

- replacing Cargo’s evolving report/session surfaces,
- solving historical trend analysis by itself,
- proving semantic interface preservation,
- or swallowing resolver, contention, or tool-parity lanes.

## Added frontier note — comparison scope and route honesty

The frontier for **P-0469** is now sharper again than “Cargo but better reports”.

The three review questions that now matter most are:

1. **comparison scope** — should these sessions even be explained together;
2. **artifact-route drift** — did `build-dir`, `target-dir`, or tool-owned route changes alter reuse meaning;
3. **bundle import visibility** — did adjacent tool-only or contention context stay visibly imported.

Without those layers, even a careful rebuild-cause bundle can still over-read what the evidence means.
