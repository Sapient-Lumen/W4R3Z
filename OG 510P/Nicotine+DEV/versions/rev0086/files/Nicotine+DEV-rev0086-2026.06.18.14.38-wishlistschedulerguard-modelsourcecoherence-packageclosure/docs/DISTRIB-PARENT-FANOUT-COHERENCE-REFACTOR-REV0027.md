# rev0027 coherence refactor — distributed parent/child cluster

The audit goal for this pass was not to inflate the strict document. It was to decide whether the distributed-search cluster contains one coherent root, several unrelated roots, or mostly support/backport material.

## Cluster outcome

```text
DISTRIB-PARENT-FANOUT-01 / U-173:
  canonical audited-backlog lead.

U-187:
  support under DISTRIB-PARENT-FANOUT-01 for child-slot occupancy;
  duplicate claimed-child replacement folds into PB-01, not a new report.

U-216:
  support/regression check for branch-root semantic username validation.

U-214:
  3.3.10 backport/regression note only;
  current/future lanes already changed unsupported EmbeddedMessage fanout.

U-179:
  kept separate and deferred.
```

## Why U-187 is not a standalone strict item

The child-slot evidence is real: distinct claimed usernames can occupy the child budget. But the client does enforce the configured `max_distrib_children` limit and turns off child acceptance at the limit. The better security invariant is PB-01-style identity/generation binding for a claimed D connection, not a separate “every claimed username can occupy a slot” report.

The duplicate-claimed-child check produced a useful surprise: a second direct D `PeerInit` with the same claimed username replaces the existing child connection before duplicate-child preservation can keep the old connection. That is exactly the PB-01 family, so rev0027 records it as support rather than a new finding.

## Why U-214 is a backport note

3.3.10 forwards a server `EmbeddedMessage` wrapper to child peers before local validation. The future lanes changed this behavior: unsupported embedded distributed types are ignored rather than forwarded. Because this is not current/future source-lane behavior, it should not be described as a new report candidate.

## Fix-composition caution

A naive fix could easily break distributed search compatibility. Avoid:

```text
- disabling child acceptance entirely;
- rejecting all multiple parent candidates;
- blocking all D connections not already known through local state;
- treating private/LAN/VPN addresses as inherently invalid in this layer;
- splitting branch-root validation from the shared username validator.
```

Preferred composition:

```text
- cap PossibleParents to the documented max of 10;
- preserve normal parent fallback;
- use PB-01 generation/source-binding for D connection replacement/promotion;
- validate branch-root strings using the same canonical username rules as the rest of the protocol;
- keep current/future EmbeddedMessage validation behavior.
```

## Next target selected by this refactor

The next narrow packet should not remain inside distributed search. The highest-value adjacent target is now:

```text
SEARCH-SEND-POLICY-01 / U-174 + U-247
```

Reason: it is closer to the existing strict SEARCH-RESP-01 lane and may affect policy/confidentiality of returned search metadata, whereas the remaining distributed rows are mostly server/MITM-scoped availability/state hardening.
