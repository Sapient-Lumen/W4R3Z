# CELL-150 — Native Probe Lane / C++ Microkernels

Priority: **P0**  
Status: **candidate-with-runnable-probe**

## Question

Does compiled code change CloudtainerML by making larger synthetic sweeps cheap enough to matter?

## Cheap first run

experiments/express_streaming_coreset/express_coreset.cpp plus tools/native_probe_audit.py compile/run path.

## Metrics

- runtime
- compile status
- output JSON presence
- audit pass/fail

## Stop condition

If native probes are hard to audit, slow to compile, or produce no new feasible cells, keep C++ optional only.
