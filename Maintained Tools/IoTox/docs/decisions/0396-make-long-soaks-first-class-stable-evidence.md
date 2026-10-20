# 0396 — Make long soaks first-class stable evidence

Date: 2026-09-20

Status: accepted

## Context

ADR 0395 created the stable/no-concern evidence manifest, but long-soak
coverage was uneven. Ratox already had a `terminal.long-soak` gate, but no
native receipt grammar around it. Sync had accepted same-host 24-hour
three-writer soak evidence in the roadmap and trust-graduation notes, but the
stable manifest did not name `sync.long-soak` explicitly.

Stable/no-concern should not let long-running behavior hide inside vague review
labels. A release owner should have to show a retained receipt for sync soak
and a retained receipt for terminal soak.

## Decision

Add `sync.long-soak` to the required stable sync gates.

Add native terminal long-soak porch commands:

```sh
iotox terminal soak-plan --root PATH --peer PEER
iotox terminal soak-receipt --root PATH --peer PEER ... > terminal-24h.receipt
iotox terminal soak-verify terminal-24h.receipt
```

The terminal receipt schema is `iotox.terminal-long-soak-receipt.v1`. It is
content-free: it hashes root and peer labels, records route/timing/counts, and
does not record terminal bytes, paths, commands, messages, or keys.

Stable `terminal.long-soak` receipt verification now requires:

- `result=accepted`;
- `required-seconds >= 86400`;
- `observed-seconds >= required-seconds`;
- at least two samples;
- `max-sample-gap-seconds <= 900`; and
- `failures=0`.

`iotox ship-check ... stable --evidence-manifest PATH` verifies both the
receipt file's SHA-256 and the terminal long-soak receipt semantics before
allowing `terminal.long-soak` to pass.

## Consequences

Stable/no-concern is stricter and clearer. A short smoke receipt can still prove
the receipt/verify machinery, but it cannot satisfy stable. Sync stable
graduation now has an explicit long-soak receipt slot, matching the existing
24-hour three-writer soak evidence.

This still does not fabricate evidence. Operators must actually run the elapsed
soak and retain the receipt before placing it in the stable manifest.

## Validation

The human CLI process test now exercises:

- `terminal soak-plan`;
- a short accepted terminal soak receipt;
- `terminal soak-verify` accepting that receipt at a short threshold; and
- `terminal soak-verify` rejecting the same receipt at the 24-hour threshold.

The stable manifest process test now includes `sync.long-soak` and a valid
`terminal.long-soak` receipt file.
