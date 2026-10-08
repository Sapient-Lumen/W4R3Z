# rev0060 trace-packet dispatch replay

Creates a replayable NPZ attention-trace packet from a locally trained tiny transformer, evaluates it through the existing trace gate, and applies dispatch policies over the resulting learned traces.

This is **not** public/pretrained evidence and not GPU/fused-kernel timing. It closes the narrower blocker that the dispatch gate had not been exercised on a learned trace packet.
