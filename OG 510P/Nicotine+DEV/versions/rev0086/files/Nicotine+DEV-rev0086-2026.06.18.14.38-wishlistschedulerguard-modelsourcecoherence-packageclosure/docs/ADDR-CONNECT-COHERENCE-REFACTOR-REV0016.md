# ADDR-CONNECT-01 coherence/refactor pass — rev0016

## Merge/prune result

```text
ADDR-CONNECT-01 / U-171:
  canonical audited-backlog lead.

U-145:
  GetPeerAddress pending-request support path under ADDR-CONNECT-01.

U-40:
  older unsafe-address-class wording; alias/support only.

U-205:
  duplicate/support of U-145; alias only.

U-189:
  invalid-port ordering/backport note; not a current master lead.
```

## Why this was not promoted

The source/probe result is real, but the strict lane requires more than “server-controlled address reaches connect.” The issue is server/MITM scoped, and the correct change must account for legitimate private/LAN/VPN peer routes. A standalone strict report would risk encouraging a harmful blanket block.

## Relationship to prior strict candidates

```text
U-123:
  transfer-token/lifecycle orphaning; separate and higher-priority.

PB-01 / U-168+U-176:
  primary peer-connection election and source/generation binding; separate from address-class policy.

SEARCH-RESP-01 / U-163:
  accepted search-response source/scope binding; separate.
```

## Next coherence risk

U-181 is now the better adjacent target. It may reveal whether pending peer-init / GetPeerAddress state can accumulate outbound messages or connection work under server timing. That is a budget/backpressure question, not an address-class policy question.
