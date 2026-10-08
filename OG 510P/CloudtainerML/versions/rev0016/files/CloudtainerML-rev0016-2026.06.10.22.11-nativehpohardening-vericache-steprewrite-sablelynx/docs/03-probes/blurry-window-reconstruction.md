# Blurry Window / frequency-memory probe

Runnable: `experiments/blurry_window_attention/blurry_window_probe.py`.

Purpose: compare full attention, literal sliding windows, low-frequency reconstruction, and landmark/frequency variants on streams where old smooth structure and sharp old spikes compete for bounded memory.

This is a cheap falsifier for Blurry Window-style claims, not a faithful implementation of the full paper.
