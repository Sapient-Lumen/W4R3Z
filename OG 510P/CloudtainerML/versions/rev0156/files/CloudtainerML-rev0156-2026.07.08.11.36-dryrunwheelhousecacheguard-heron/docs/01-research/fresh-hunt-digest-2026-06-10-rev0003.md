# Fresh hunt digest — rev0003

## What got added

rev0003 expanded the hunt around six especially actionable themes.

### 1. Region-aware KV compression

Adaptive Mass-Segmented KV Compression argues that global token-level top-k retention can cause **region wipe-out**: contiguous reasoning blocks are evicted, damaging coherence even when some high-score tokens survive. The cloudtainer version is synthetic and cheap: generate traces where each proof block has to survive as a block, not as isolated tokens.

### 2. Depth-cache tradeoffs

Depth-cache theory frames reasoning as a memory-budget problem, especially in pointer chasing. This turns into a beautiful toy battery: cache slots × hops × loop depth × precision. The question is not whether a large model performs well; it is where the heatmap breaks.

### 3. Dormant tokens and semantic sponsorship

Transactional Attention emphasizes tokens that are essential later but statistically invisible earlier. This is worth testing because it attacks the core assumption behind attention-mass and reconstruction-loss retention: important tokens should leave a signal before they are queried.

### 4. Memory tokens as recursive scratchpad

Universal Transformers Need Memory reports a sharp memory-token threshold and an ACT halt-bias trap on a recursive reasoning task. The small-scale test is to see whether simplified recursive tasks show similar threshold/dilution curves.

### 5. Looped models versus explicit scratchpads

The looped-transformer line asks whether test-time compute in latent state is equivalent to chain-of-thought tokens. The emerging answer seems to be: only if the state budget is large enough. This is exactly the kind of claim we can test with pointer chasing and associative recall.

### 6. RASP/CRASP and grokking diagnostics

RASP decompilation and C-RASP verification suggest a stricter standard for tiny transformer claims: can we recover a compact program, or did we merely fit the validation set? Meanwhile, cheap grokking diagnostics offer a way to watch circuits form before performance jumps.

## New code posture

Two probe scaffolds were added under `experiments/`:

- `kv_wind_tunnel`: pseudo-decode divergence under cache quantization variants.
- `spectral_assoc_recall`: associative memory geometry under noise, key collision, rank, and online updates.

These are not final experiments. They are calibration instruments for deciding which cells deserve more code.
