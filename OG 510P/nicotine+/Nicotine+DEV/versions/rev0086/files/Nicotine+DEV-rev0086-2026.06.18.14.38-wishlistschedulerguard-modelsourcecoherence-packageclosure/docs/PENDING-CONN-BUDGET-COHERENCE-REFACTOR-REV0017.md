# rev0017 coherence refactor: pending connection budget family

## Refactor decision

PENDING-CONN-BUDGET-01 is now a verified audited-backlog family, not a strict/front-lane report.

## Canonical family mapping

```text
PENDING-CONN-BUDGET-01 / U-181:
  canonical row for pending PeerInit/GetPeerAddress/socket-cap outbound-message buffering.

PB-01 / U-168 + U-176:
  remains strict. Different root: primary connection replacement/promotion and source/generation binding.

ADDR-CONNECT-01 / U-171 + U-145:
  remains audited backlog. Different root: server-supplied address policy and special-use destination handling.

U-172:
  backport/regression support about pending peer-connection keying at socket cap.

U-185:
  separate low/medium cancellation-token path (`CantConnectToPeer` by token). Do not merge unless a future harness shows it uses the same budget/generation invariant.

U-146 / U-159 / U-227:
  adjacent future request-budget work. These can reuse budget helpers but should not be presented as the same root unless a source harness proves shared pending-message accumulation.
```

## Combined-fix risk

A naive fix that simply refuses pending peer messages can break legitimate user actions: browse user, user info refresh, folder download, and fallback from direct to indirect connections all rely on holding some work while a peer connection is established.

A coherent fix should therefore bound and fail clearly, not silently drop:

```text
- preserve a small normal queue per user and per connection type;
- account globally across usernames;
- expire or cancel pending state by generation/TTL;
- return main-thread error events with the messages being failed or explicitly cancelled;
- add test coverage for direct-address, GetPeerAddress, indirect, offline, and socket-cap paths.
```

## Strict-lane effect

No strict promotion in rev0017. The strict document remains focused on U-123, PB-01, and SEARCH-RESP-01.
