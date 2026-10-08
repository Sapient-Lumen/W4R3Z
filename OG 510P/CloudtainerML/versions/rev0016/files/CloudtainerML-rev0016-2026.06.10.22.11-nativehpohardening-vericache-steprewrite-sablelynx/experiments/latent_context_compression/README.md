# Latent context compression probe

Toy long-context compression probe: generated key-value fact chunks are compressed
into latent summaries, then either answered from compressed summaries alone or used
to select raw chunks for expansion.

Run:

```bash
python experiments/latent_context_compression/lclm_probe.py
```

This is the cheap local analogue of the question: should compressed context be a
replacement for raw context, or a router that skims and selectively expands?
