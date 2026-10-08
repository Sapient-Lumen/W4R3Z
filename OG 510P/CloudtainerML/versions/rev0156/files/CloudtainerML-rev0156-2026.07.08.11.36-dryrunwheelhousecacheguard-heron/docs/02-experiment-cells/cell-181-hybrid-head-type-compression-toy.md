# CELL-181: Hybrid Head-Type Compression Toy

Priority: P1

Status: candidate

Idea: IDEA-0180

Source: SRC-0216

Cheap first run: No runnable probe yet; static/dynamic head compression policy split.

Metrics:
- head-type assignment accuracy
- output error
- budget use

Baselines:
- one-size top-k
- text-prior pruning
- chunk retrieval
- oracle head policy

Stop condition: If head classes are unstable, defer.
