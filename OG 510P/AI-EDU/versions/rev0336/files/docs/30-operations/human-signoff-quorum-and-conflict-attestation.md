# Human signoff quorum and conflict attestation

The schema and validators can catch shape, traceability, and obvious overclaiming. They cannot
substitute for accountable human judgment when a real pilot import is used to change archive claims.
This surface defines the minimum quorum before `FT-0181` can close.

## SQ states

| State | Meaning |
|---|---|
| `SQ0` | no signoff record |
| `SQ1` | pre-import quorum defined but not closure-ready |
| `SQ2` | reviewers named and conflicts checked |
| `SQ3` | closure-ready after `SRC2+` evidence and decision deltas |
| `SQX` | conflict, missing role, or non-waivable-control bypass |

## Required roles for FT-0181 closure

At minimum, closure requires separable roles:

| Role | Why it is needed |
|---|---|
| record owner | verifies provenance and local meaning of the source export |
| educational evaluator | judges learning/workload/access claims without relying on vendor summary alone |
| protected-route reviewer | confirms protected support facts are minimized or kept local |
| security reviewer | checks prompt/tool/security payload handling and excessive agency risks |
| public-summary reviewer | confirms public language is evidence-bounded and audience-safe |
| archive maintainer | updates queue, receipt, surface map, release audit, and assurance case |

One person may hold more than one role only when the signoff record explains why independence is not
materially weakened. Vendor or tool-operator claims may inform review, but they cannot be the only
basis for closure.

## Conflict controls

A signoff record should disclose:

- vendor or procurement relationships;
- operational responsibility for the service under review;
- pressure to publish a positive result;
- involvement in writing the public summary;
- whether a reviewer helped construct the evidence they are judging.

A disclosed conflict does not always block review, but an unresolved conflict blocks closure.

## Non-waivable rule

No quorum can waive the need for real `SRC2+` source evidence, protected-route separation,
source-status labeling, action-authority ceilings, or public-summary evidence limits. A quorum can
only decide whether the evidence received satisfies those controls.
