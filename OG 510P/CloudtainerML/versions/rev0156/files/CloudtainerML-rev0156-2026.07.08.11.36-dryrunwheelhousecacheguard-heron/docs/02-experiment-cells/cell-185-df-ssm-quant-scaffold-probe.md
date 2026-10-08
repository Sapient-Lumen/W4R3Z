# CELL-185: DF-SSM Quant Scaffold Probe

Priority: P0

Status: runnable

Idea: IDEA-0184

Source: SRC-0137

Cheap first run: C++ recurrent transition compression toy; output REV0015_DFSSM_QUANT_SCAFFOLD_SMOKE.json.

Metrics:
- mean relative state error
- sign agreement
- bytes proxy

Baselines:
- fp32 teacher
- int8 full
- binary scaffold
- binary plus low-rank correction

Stop condition: If low-rank correction fails rare-direction regimes, mark as representation-specific.
