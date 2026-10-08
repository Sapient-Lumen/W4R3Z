# F-CONN-FRAME coherence/refactor note — rev0015

## Canonical family

```text
U-164 = canonical F-CONN-FRAME-01 row
U-188 = duplicate/alias only; keep as archive continuity/back-reference
```

## Why U-164 should not be merged into U-123

U-123 and U-164 both touch F-connection lifecycle, but they are not the same root cause.

```text
U-123:
  duplicate peer-supplied transfer token
  stale timeout deletes the newer active mapping
  later F-socket callbacks are ignored
  fix family: transfer identity / generation / timer binding

U-164:
  incomplete fixed-width FileTransferInit/FileOffset prefix consumed
  complete frame cannot be reconstructed or can resynchronize into a wrong value
  fix family: frame accumulator / minimum-buffer check
```

A coherent maintainer packet should not ask for a broad transfer rewrite when a small minimum-buffer guard plus regression tests addresses U-164.

## Other separations

```text
U-169: token/source/socket binding for FileTransferInit; keep separate.
U-170: unknown-token close/backport note; keep paired with U-169.
U-269: completed-upload socket lifetime; keep separate.
```

## Next risk family

The next highest-value frontier is **ADDR-CONNECT-01 / U-145 + U-171**, with U-40 and U-205 treated as aliases/back-references where appropriate. That family concerns server-supplied peer addresses driving outbound connection attempts and should be kept separate from PB-01 primary-election/source-binding work.
