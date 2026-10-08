# Strict/front lane coherence refactor — rev0035

## Refactor goal

The strict/front lane had three candidates that could be accidentally blended because they all use tokens, peer connections, or parser gates. Rev0035 separates them by the invariant that must be fixed.

## Family split

### TR-01 / U-123 — transfer-token active-map lifetime

Core invariant:

```text
active_users[username][token] -> transfer
```

The row is about duplicate peer-supplied transfer tokens, stale request timers, and F-connection callbacks becoming unindexed. It is not a general peer-primary election bug, a file-size provenance bug, or an upload completion lifetime bug.

### PB-01 / U-168 + U-176 — peer primary-election generation binding

Core invariant:

```text
which P/D/F connection has the right to become init.sock for a claimed user/type
```

This family should stay merged. U-168 and U-176 are two symptoms of a missing generation/election model; U-165 remains PierceFireWall context, not a separate first report.

### SEARCH-RESP-01 / U-163 — search response token/source/scope and parse order

Core invariant:

```text
whether a FileSearchResponse is accepted and materialized before source/scope and display-budget policy are enforced
```

This is not outbound search policy, folder-browse response parsing, or generic file attribute parsing. Production text should separate source/scope matching from parser-budget/private-result materialization.

## Resulting queue decision

- U-123 becomes the next production-draft target.
- PB-01 stays second because it has broader impact but higher compatibility risk.
- SEARCH-RESP-01 stays third because it needs scope-specific wording to preserve global/wishlist behavior.
- U-138 and the media-parser backlog are deferred until at least one strict/front candidate gets a production-draft pass.
