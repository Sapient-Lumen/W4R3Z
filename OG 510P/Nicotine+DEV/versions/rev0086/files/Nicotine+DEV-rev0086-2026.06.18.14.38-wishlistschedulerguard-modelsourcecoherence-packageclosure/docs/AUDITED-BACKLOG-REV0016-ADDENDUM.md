# Audited backlog addendum — rev0016

## ADDR-CONNECT-01 verified, retained outside strict lane

rev0016 verified the server-supplied address family across `3.3.10`, `3.3.x`, and `master` with a no-network socket monkeypatch harness.

```text
U-171: canonical lead; unsolicited server ConnectToPeer can drive outbound connection attempts.
U-145: support path; GetPeerAddress pending local request consumes server-supplied address.
U-40:  alias/support only.
U-205: alias/support only.
U-189: branch-specific invalid-port ordering/backport note.
```

## Ranking effect

The family remains useful audited backlog, but no strict promotion was made. The top strict/front lane remains U-123, PB-01, and SEARCH-RESP-01.

## Practical next action

Use the maintainer artifact in `maintainer_artifacts/addr-connect-01/` as a current-behavior witness. A future fixed-behavior test should preserve LAN/private compatibility while rejecting or warning on loopback/link-local/special-use addresses unless explicitly allowed.
