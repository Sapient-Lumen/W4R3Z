# rev0060 — trace packet dispatch replay

rev0059 correctly blocked materialization-free/fused promotion on the native CPU schedule proxy, but the dispatch gate had not yet been exercised on a replayable learned trace packet.

rev0060 creates `REV0060_TINY_TRAINED_TRACE_PACKET.npz` from a locally trained tiny transformer and replays the dispatch gate over that external-NPZ packet. The packet is explicitly not public/pretrained evidence.

## Result

- trace packet rows: 256
- strict materialization-free sparse rows promoted: 0
- score-storage-allowed sparse row rate: about 0.789
- public/pretrained trace loaded: false
- oracle leakage rows: 0

The useful finding is conditional: materialized score-histogram sparsity still has a learned-trace opportunity, but the strict no-score-storage path does not. Therefore the cube now has a concrete learned-trace replay gate without closing the public/pretrained or fused-kernel blockers.

## What changed structurally

The stale current-artifact surface is also refactored: rev0060 status, current-run audit, evidence-integrity audit, and smoke validation point at rev0060 artifacts rather than carrying rev0058/rev0059 lanes forward as current evidence.

## Remaining blockers

- actual public/pretrained trace bundle missing
- GPU/fused attention kernel timing missing
- strict materialization-free sparse schedule has no learned-trace speed win
- materialized sparse CPU path still requires global score storage
- value-norm sidecar kernel path missing
