# Risk register index (generated)

**Tier:** A (Core)  
**Profiles:** A, B, C, D  
**Pillars:** operability

This is a compact, deterministic index for the canonical long-form register: `docs/266-open-questions-and-risk-register.md`.

- Machine-readable index: `docs/_generated/risk_register.json`

## How to refresh
- `python3 tools/gen_risk_register_index.py --write`
- `python3 tools/check_generated_docs.py` (fails if this doc or the JSON index is stale)

## Items
| # | Topic | Risk |
|---:|---|---|
| 1 | Package recipe surface: how much language is allowed? | Risk: a rich language becomes the real product; the typed Spec becomes a veneer. |
| 2 | Cross compilation and multi-arch closures | Risk: subtle non-reproducible builds and broken caches. |
| 18 | Formal methods lane: models become stale or theatre | Risk: models drift from implementation/intent and become diagramware; the lane becomes theatre instead of a safety tool. |
| 25 | Queryable metadata: privacy, laundering, and index integrity | Risk: either metadata is too hard to use (people ignore it), or it becomes ambient surveillance/exfiltration. |
| 30 | Snapshot UX vs security: revocation, secret retention, and ambient exposure | Risk: snapshots become a silent data-exfil path and undermine least-authority promises. |
| 31 | P2P distribution: poisoning, identity confusion, and privacy leakage | Risk: operators deploy P2P daemons outside the Derive trust/evidence model, or P2P becomes a stealthy exfil surface. |
| 33 | Flight recorders: overhead, covert channels, and “debug mode” bypasses | Risk: performance regressions, covert channels, or an ecosystem split where the real debugging happens outside the Derive evidence model. |
| 37 | Trustworthy time: quorum failures, expiry safety, and operational response | Risk: expiry-based security becomes a bypass (“clock was wrong”), or operators add ad-hoc time tooling outside the Derive evidence model. |
| 40 | Measured boot in practice: event-log replay ergonomics, attester lifecycle, and variance policy | Risk: the lane exists “on paper” but is too painful to adopt, so secrets/update gates drift into bespoke vendor tooling outside the Deriv… |
| 49 | Desktop viability implementation details (even if desktop is not v0) | Risk: B becomes infeasible in practice, forcing forks or abandoning the workstation story despite the high-level boundary being correct. |
| 50 | Removable-media implementation details on imperfect hardware | Risk: the baseline stays correct on paper, but fallback mechanics turn into ad-hoc convenience paths that recreate ambient device authority. |
| 55 | Remote assistance implementation details after the profile default | Risk: the product boundary stays correct on paper, but implementation details drift into stealthy persistence, privacy-toxic recording, o… |
| 56 | Crypto-operation implementation details after the profile default | Risk: the product boundary stays correct on paper, but implementations drift into opaque prompt spam, privacy-toxic receipts, or classic … |
| 57 | Human identity / home-state implementation details after the profile default | Risk: the product boundary stays correct on paper, but implementations drift into always-mounted homes, folklore compatibility hacks, or … |
| 58 | Backup / restore implementation details after the profile default | Risk: the archive agrees on posture but still ships a recovery lane that is too awkward, too privacy-toxic, or too expensive to run often… |
| 59 | Data-at-rest implementation details after the profile default | Risk: the archive agrees on posture but still ships unlock/recovery workflows that are too brittle, too opaque, or too convenience-biased… |
| 60 | Export-boundary implementation details after the profile default | Risk: the archive agrees on posture but still ships an export lane that is too permissive, too noisy, or too adapter-fragmented to keep e… |
| 61 | Operator-access implementation details after the profile default | Risk: the archive agrees on posture but still ships an operator-access lane that is too brittle, too privacy-toxic, or too awkward to rep… |
| 62 | Trustworthy-time implementation details after the profile default | Risk: the archive agrees on posture but still ships a trustworthy-time lane that is either too brittle for real operations or too weak/no… |
| 63 | Platform-provenance implementation details after the profile default | Risk: the product default is sound but the implementation lane still drifts into opaque verifier stacks, broad exceptions, or brittle PCR… |
| 64 | Workload-identity implementation details after the profile default | Risk: the product boundary stays correct on paper, but implementations drift into opaque mesh sprawl, selector folklore, or compatibility… |

## Notes
- Treat missing `Risk:` lines as a hygiene failure; each item should state the failure mode explicitly.
- The index intentionally does not copy full sections; use `docs/266-...` for details and mitigation.

Last updated: 2026-03-19r307
