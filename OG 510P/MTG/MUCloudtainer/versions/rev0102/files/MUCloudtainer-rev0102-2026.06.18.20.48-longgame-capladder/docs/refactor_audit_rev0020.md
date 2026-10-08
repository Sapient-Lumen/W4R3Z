# rev0020 refactor/audit notes

## Refactor: random transition transport

rev0020 changes the C++ transition bridge from a purely deterministic one-action transport into a deterministic-plus-transcript transport. The only transcript currently implemented is Jace ultimate's shuffled new library.

This avoids a bad long-term path:

```text
bad: C++ must clone Python RNG internals exactly before it can check random transitions
better: Python records random outcomes explicitly for differential checking
```

The agent still sees only legal actions and public observations. The explicit shuffle CSV is created after Python applies the action and is used only by the checker.

## Refactor: code-policy catalog

A new built-in public code policy was added:

```text
code_jace_ultimator_rev0020
```

It is a coverage/test policy, not a claimed strong player. It ramps Jace loyalty and creates ultimate events so C++ shuffle transport stays exercised in ordinary replay checks.

## Refactor: imitation feature seam

`src/muc5/imitation.py` separates public context features from action features. This keeps the future action-ranker path from ad hoc parsing of action strings.

## Audit checks added

The rev0020 audit checks:

```text
C++ trace checker has 0 skipped transitions
C++ trace checker has 0 mismatches
Jace ultimate events were present and C++-supported
action-ranker dataset rows/decision counts are present
action-ranker feature count matches code
action-ranker smoke accuracy beats random-slot baseline
new docs/scripts/tests exist
```

## Remaining concern

The C++ transition microkernel is now broad enough to follow sampled public traffic, but it is still a microkernel. It is not yet responsible for full game rollout, legal-menu generation, or tournament scoring.
