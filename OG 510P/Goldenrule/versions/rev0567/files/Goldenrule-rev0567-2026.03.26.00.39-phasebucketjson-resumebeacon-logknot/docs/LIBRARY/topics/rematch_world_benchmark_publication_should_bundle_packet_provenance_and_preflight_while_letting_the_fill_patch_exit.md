# Rematch-world benchmark publication should bundle packet, provenance, and preflight while letting the fill patch exit

## Claim

Once a real rematch-world run has been distilled into one retained evidence packet and one retained evidence receipt, publication should flow through one compact bundle receipt that proves the packet compiles into a preflight-ready benchmark artifact. At that point the compiled fill patch is only an intermediate and can stay scratch-only.

## Why this matters

The archive already had all the underlying pieces: packet distillation, packet-to-patch compilation, compile-back onto the seed, a mutation guard, a completion gate, and a consolidated preflight receipt. But that still left one awkward retained object in the middle: the fill patch.

That patch is useful while reviewing a run, but it is not the final artifact and it is not the smallest provenance object either. If the packet and evidence receipt already explain the world-dependent facts, and the preflight-ready candidate can be regenerated deterministically from them, then retaining the patch long-term mostly adds another sidecar for future sessions to reconcile.

## Compactness consequence

Treat the patch as scratch by default. Retain the packet, the evidence receipt, the compiled benchmark artifact, and the preflight receipt. Recompute the patch when needed for debugging or diff review instead of preserving it as permanent archive mass.
