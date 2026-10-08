# rev0009 Cloudtainer Office Note

This archive is intended to be opened and continued inside a constrained cloudtainer, not treated as a normal long-lived local research repo.

## Why this matters

The project is deliberately cloudtainer-bound:

- Work happens in the Python runtime available to the assistant/operator.
- The execution container may not have outbound internet from Python, even when the assistant can browse separately for research.
- The environment may be recreated later with similar but not identical packages.
- Artifacts, docs, smoke data, audits, and checksums must travel with the zip.
- Future sandpeople should be able to understand the state of the office without relying on private conversation context.

That is inefficient compared with a normal dev machine. It is also part of the design constraint: small exact systems, lots of logs, cheap audits, and interpretable baselines.

## Tool inventory policy

rev0009 adds:

```text
scripts/inspect_cloudtainer_tools.py
```

It writes:

```text
data/rev0009_cloudtainer_tools.json
```

The script records Python/Node availability, CPU count, memory from `/proc/meminfo`, and selected Python package versions. It does not assume that a package is a good idea merely because it is installed.

## Current engineering stance

Use this order of escalation:

1. Pure Python correctness.
2. Structural speedups that avoid repeated work.
3. NumPy/vectorized probes for bulk deck-space or probability work.
4. PyTorch/JAX/scikit-learn only when a learning method needs them.
5. Numba only after a measured hotspot is stable and pure-Python behavior has tests.
6. Cython/compiled extensions only as a last resort; they add archive fragility.

The simulator is still small enough that the best speedups are probably not exotic compilers. The rev0008/rev0009 profile points at repeated observation/legal-action construction and baseline-agent scoring, so the current target is interface design and caching, not Cython/Rust.

## What belongs in the zip

Each revision should include:

- source code
- tests
- scripts used to generate new data
- generated smoke/audit data
- docs explaining why the revision changed
- a manifest
- checksums

The zip is the lab notebook.
