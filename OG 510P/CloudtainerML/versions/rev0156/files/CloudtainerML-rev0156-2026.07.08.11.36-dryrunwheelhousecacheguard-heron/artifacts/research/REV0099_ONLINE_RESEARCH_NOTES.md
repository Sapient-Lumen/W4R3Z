# Online research notes — REV0099

Purpose: keep the next move operational and reduce waste before a large public model download.

## Findings used

1. Hugging Face Hub documentation says `snapshot_download()` downloads an entire repository at a given revision and caches downloads locally; it also supports `allow_patterns` for filtering files. Observed via web.run: `turn377661view0` lines 123-145 and 168-176.
2. The current `huggingface_hub` source exposes `snapshot_download(..., dry_run=True)` and returns `DryRunFileInfo` objects, which lets the cube estimate/validate a snapshot plan before downloading. Observed via web.run: `turn815091view0` lines 1418-1464 and 1665-1676.
3. Transformers installation docs state Transformers is tested with Python 3.10+ and PyTorch 2.4+. Observed via web.run: `turn377661view2` lines 107-145.
4. Transformers attention docs state SDPA chooses fast implementations automatically on CUDA and that attention implementations are selected by `attn_implementation`; custom attention also requires matching mask handling. Observed via web.run: `turn377661view3` lines 156-160 and 212-216.
5. The locked TinyLlama tree shows the selected `fe8a4ea` revision, Apache-2.0 license, 2.2 GB model size, and required config/tokenizer/safetensors files. Observed via web.run: `turn597299view0` lines 53-60 and 180-249.

## Consequence for this cube

The riskiest unfinished work is not another acceptance doctrine. It is the actual public trace run. The best pre-run change is therefore a fail-fast chain:

`dependency lock -> source lock -> runtime surface -> backend identity -> no-download snapshot dry-run -> materialize exact snapshot -> capture`

If the dry-run fails, the full materializer should not be attempted. That avoids wasting bandwidth/time and produces a specific network/token/revision blocker.
