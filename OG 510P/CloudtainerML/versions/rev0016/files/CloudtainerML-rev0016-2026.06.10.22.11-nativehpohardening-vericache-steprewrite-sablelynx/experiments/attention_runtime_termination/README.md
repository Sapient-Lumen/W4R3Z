# Attention run-time termination probe

Tiny ART-style block traversal test. It accumulates blockwise attention outputs and stops when direction and magnitude stabilize, then compares to full attention.

```bash
python experiments/attention_runtime_termination/art_probe.py
```
