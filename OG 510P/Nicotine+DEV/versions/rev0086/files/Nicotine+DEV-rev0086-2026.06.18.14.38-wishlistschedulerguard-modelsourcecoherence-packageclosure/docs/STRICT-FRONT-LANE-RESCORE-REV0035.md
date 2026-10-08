# Strict/front lane rescore — rev0035

## Purpose

Rev0034 deliberately stopped the local media-parser sweep and queued a strict/front-lane re-score. Rev0035 performs that re-score across the three existing report-candidates:

```text
U-123          duplicate transfer token / stale timeout / F-session orphan
PB-01          U-168 + U-176 peer primary-election and secondary promotion
SEARCH-RESP-01 U-163 search response token/source/scope and parse order
```

## Rerun summary

```text
U-123:
  github-tag-3.3.10:   1 unittest OK
  github-branch-3.3.x: 1 unittest OK
  github-branch-master: 1 unittest OK

PB-01:
  github-tag-3.3.10:   10 passed
  github-branch-3.3.x: 10 passed
  github-branch-master: 10 passed

SEARCH-RESP-01:
  github-tag-3.3.10:   6 passed
  github-branch-3.3.x: 6 passed
  github-branch-master: 6 passed
```

These are current-behavior witnesses. They remain useful because they keep the report-candidates reproducible, but they are not fixed-behavior regressions.

## Rescore outcome

| Rank | Packet | Report-readiness score | Decision |
|---:|---|---:|---|
| 1 | U-123 | 86 | Next production-draft target, still not production-ready. |
| 2 | PB-01 | 82 | Retain as architectural strict candidate; compatibility model still blocks production text. |
| 3 | SEARCH-RESP-01 | 78 | Retain; split source/scope binding from parser-budget text before production use. |

## Why U-123 leads the next pass

U-123 has the narrowest identity invariant and the lowest compatibility risk. The active map is keyed by `username + token`; duplicate activation overwrites the key; stale deactivation deletes by the same key without checking that the timer belongs to the current transfer object; later F-connection progress/close callbacks depend on that map. A fixed-behavior regression can be stated compactly: firing the first transfer's stale timeout must not remove the active mapping for the later transfer/session.

## Why PB-01 remains second

PB-01 is broader and likely more architectural. The witness still proves incoming direct `PeerInit` replacement and secondary post-init promotion across P/D/F connection types. The problem is report readiness: a safe fix must preserve legitimate direct/indirect connection races, PierceFireWall fallback, file transfer F sockets, and distributed transitions. A naive "never accept secondary" or "never replace" patch would be risky.

## Why SEARCH-RESP-01 remains third

SEARCH-RESP-01 still reproduces and remains a strict candidate, but production text must not overclaim token guessing or break global/wishlist search behavior. The report should separate two sections: source/scope binding for user/room/buddy search modes, and pre-materialization parser budgets/privacy-display order for result rows.

## Production-readiness decision

```text
strict/front lane: 3 report-candidates retained
production-ready disclosure texts: 0
next action: U-123 production-draft hardening pass
```
