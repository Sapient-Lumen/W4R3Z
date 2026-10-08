# ChatGPT proof attempt audit

`proof-attempt-audit` checks the browser-side proof capture sequence before ingest/finalization. It is intentionally narrower than `proof-ingest`: it answers whether the side-panel steps happened in the safe operator order.

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-attempt-audit \
  --input ~/Downloads/GlassTTY-<attempt>-chatgpt-first-proof-capture.json \
  --require-ready-to-download \
  --pretty
```

The required live order is:

1. `prompt.write` with exact checkpoint readback.
2. `fixture.capture` with `proof_live_gate_ok=true`.
3. `proof.surface_screenshot` with a PNG data URL.
4. `prompt.submit` carrying the live-gate verdict/readback.
5. `transcript.latest` with `GLASSTTY-CHECKPOINT` and a matching user-turn witness.
6. Final `proof.operator_readiness` with `proof-attempt-ready-to-download`.

In rev0350+, the side panel's **Download proof JSON** button runs the attempt readiness check before downloading. It blocks incomplete captures and embeds the final readiness envelope, so this audit should pass immediately after download.

A blocked audit means the capture should not be ingested or finalized as live evidence. Re-run the side-panel flow in order and use **Download proof JSON**, not a manual preview copy.
