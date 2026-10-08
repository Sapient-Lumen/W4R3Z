# rev0027 worklog

Focus: **DISTRIB-PARENT-FANOUT-01 / U-173 + U-187**, with **U-216** and **U-214** as support checks.

## Work performed

- Built a cross-lane pytest witness for distributed parent/child fanout behavior.
- Ran the witness against 3.3.10, 3.3.x, and master from the external rev0003 source bundle.
- Captured source traces for parser/handler paths without embedding source trees.
- Rechecked public overlap around `PossibleParents`, distributed child peers, `DistribBranchRoot`, and embedded distributed messages.
- Refactored the cluster to avoid duplicating PB-01 or turning 3.3.10-only behavior into a current/future report.

## Test result

```text
github-tag-3.3.10:   5 passed
github-branch-3.3.x: 5 passed
github-branch-master: 5 passed
```

## Audit decision

No strict promotion in rev0027.

The verified behavior is important enough for the audited backlog and useful maintainer hardening, but not strict/front-lane quality. The strongest row, U-173, is server/MITM-scoped distributed parent fanout. U-187 is partly PB-01 support. U-216 is branch-root semantic validation. U-214 is a backport note.

## Cube refactor

```text
U-173 = canonical lead.
U-187 = support/PB-01 overlap.
U-216 = support username-validation check.
U-214 = 3.3.10 backport note.
U-179 = separate/deferred.
```

## Next target

```text
SEARCH-SEND-POLICY-01 / U-174 + U-247
```

This is higher value than continuing to split distributed-network rows because it may connect to the existing strict search-response lane and policy/confidentiality boundaries.
