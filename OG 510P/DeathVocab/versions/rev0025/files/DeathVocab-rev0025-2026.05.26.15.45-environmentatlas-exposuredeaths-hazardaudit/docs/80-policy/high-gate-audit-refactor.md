# High-gate audit refactor — rev0019

Rev0019 adds `HIGH-GATE-COVERAGE-AUDIT.json` and `tools/high_gate_audit.py`.

The audit detects high-gate domains across record classes, axes, titles, and safety tags, then checks that detected records remain publication-blocked. It does not approve content. It only ensures that the cube can see its own dangerous zones.

The first domain emphasized is `pediatric_and_perinatal`, but the audit also tracks suicide/self-harm, custody/institutional opacity, violent or mass death, restricted tradition, MAID/VSED, and organ/brain-death/DCD records.
