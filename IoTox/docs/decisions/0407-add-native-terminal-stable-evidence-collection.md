# 0407 — Add native terminal stable evidence collection

## Status

Accepted.

## Context

Stable sync evidence already had a native porch: `iotox evidence collect sync`
copies shape-checked receipts into a manifest directory and writes
`stable-evidence.manifest` when the sync gates are complete. Ratox had
`terminal graduation-check` and `terminal soak-verify`, but not the matching
native intake step for stable release evidence. Operators had to hand-author
the 11 non-soak terminal manifest receipts and place the 24-hour
`terminal.long-soak` receipt correctly.

That was too easy to do loosely, and previous stable manifests could satisfy
non-soak terminal gates with arbitrary placeholder prose as long as the hashes
matched.

## Decision

Add `iotox evidence collect terminal`.

The command accepts:

- `--root PATH` and `--peer PEER` to scope the host/route evidence;
- `--long-soak PATH` for the native `iotox.terminal-long-soak-receipt.v1`
  receipt;
- 11 `--evidence NAME=LABEL` entries for daily-control, profile freshness,
  service supervision, reconnect continuity, cgroup delegation, route loss,
  Tor route loss, I2P route loss, sudo policy, security review, and activation
  decision; and
- `--out DIR` for the evidence directory.

For the 11 operator-attested gates, IoTox now writes
`iotox.terminal-stable-evidence.v1` receipts containing the full stable gate
name, safe label, hashed root/peer labels, `content-free=1`, and
`repo-certified=0`. For `terminal.long-soak`, the collector copies only a
receipt that passes the existing stable 86,400-second semantic checker. Short
smoke receipts are rejected for stable collection.

`iotox evidence manifest DIR --out PATH` now supports
`--scope auto|sync|terminal|all`. Auto scope emits a sync, terminal, or combined
manifest based on the complete receipt sets present in the directory.

## Consequences

- Terminal stable evidence is ordinary and native like sync evidence.
- `ship-check terminal stable --evidence-manifest PATH` can now pass from a
  collected terminal evidence directory when a real 24-hour terminal soak
  receipt exists.
- `ship-check all stable` still cannot pass from sync evidence alone; it needs
  both sync and terminal receipt sets in the manifest.
- The 11 operator labels remain operator evidence, not cryptographic proof.
  The command makes the content-free receipt boundary explicit rather than
  pretending labels are stronger than they are.

