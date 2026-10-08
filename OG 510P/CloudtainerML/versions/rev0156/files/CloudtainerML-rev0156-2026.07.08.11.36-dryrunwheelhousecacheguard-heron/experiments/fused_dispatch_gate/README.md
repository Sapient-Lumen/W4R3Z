# Fused dispatch gate

This experiment is a claim gate over measured native CPU schedule rows from rev0058. It does not run a GPU kernel and does not claim public/pretrained traces.

Run:

```bash
python experiments/fused_dispatch_gate/fused_dispatch_gate.py
python tools/fused_dispatch_gate_audit.py
```

The strict materialization-free gate promotes a sparse schedule only if it passes quality, speed, score-storage, selected-fraction, and QK-schedule constraints. In rev0059 no sparse schedule passes that strict gate.
