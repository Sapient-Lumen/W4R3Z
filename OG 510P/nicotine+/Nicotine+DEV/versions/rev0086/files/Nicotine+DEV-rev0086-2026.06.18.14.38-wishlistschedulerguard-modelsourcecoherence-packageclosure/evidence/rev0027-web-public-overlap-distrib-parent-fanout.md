# rev0027 public-overlap search — DISTRIB-PARENT-FANOUT-01

Revision: rev0027  
Packet: **DISTRIB-PARENT-FANOUT-01 / U-173 + U-187 + U-216 + U-214**

## Classification

```text
candidate no direct exact public match found / public-adjacent / upstream-adjacent
```

This is not treated as clean novelty. Public project material already explains the distributed parent/child search network, and current release-candidate notes mention distributed-search fixes. The exact rev0027 proof — over-10 `PossibleParents` fanout plus sibling child-slot/branch-root/backport checks — remains useful as a maintainer regression packet, but not as a fourth strict/front-lane item.

## Public material found

### Official protocol documentation

Source:

```text
https://nicotine-plus.org/doc/SLSKPROTOCOL.html
```

Relevant public context:

```text
- HaveNoParent / PossibleParents / parent connection flow is documented.
- ParentSpeedRatio determines the number of distributed child peers the client is willing to accept.
- EmbeddedMessage / DistribEmbeddedMessage / DistribSearch are documented.
- PossibleParents is documented as a list of max 10 possible distributed parents.
```

Impact on novelty:

```text
The maximum-10 invariant is public protocol context, not something discovered only inside the cube.
The rev0027 value is proving that all current archived source lanes still parse and fan out more than 10 entries.
```

### Nicotine+ issue #994

Source:

```text
https://github.com/nicotine-plus/nicotine-plus/issues/994
```

Relevant public context:

```text
Issue #994 publicly explains the distributed search-request delivery model:
server -> PossibleParents -> first successful parent -> parent delivers search requests.
```

Impact on novelty:

```text
Public implementation discussion exists for the distributed parent/child mechanism.
No direct exact public report was found in this pass for over-10 PossibleParents fanout.
```

### Release notes / upstream-adjacent status

Source:

```text
https://nicotine-plus.org/NEWS.html
```

Relevant public context:

```text
The 3.3.11 release-candidate notes include distributed-search fixes and broader network-message hardening.
```

Impact on novelty:

```text
This is enough upstream adjacency to avoid clean novelty language for distributed-search hardening rows.
```

## Exact searches captured

```text
GitHub issues: "PossibleParents"
  - surfaced #994 as public distributed-network implementation context.

GitHub issues: "distributed child peer"
  - surfaced historical implementation PR/issue context, not a direct over-10 fanout report.

GitHub issues: "DistribBranchRoot"
  - no direct issue result found in captured search.

GitHub issues: "EmbeddedMessage" "distributed"
  - no direct issue result found in captured search.
```

## Decision

```text
U-173: verified audited-backlog lead; candidate no direct exact public match found, public/upstream adjacent.
U-187: support/PB-01 overlap; not separate novelty claim.
U-216: branch-root semantic-validation support; not strict.
U-214: 3.3.10 backport/regression note because current/future lanes changed the unsupported EmbeddedMessage fanout shape.
```
