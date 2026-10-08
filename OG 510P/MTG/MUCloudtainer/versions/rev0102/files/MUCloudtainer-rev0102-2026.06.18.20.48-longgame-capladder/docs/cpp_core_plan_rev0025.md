# rev0025 C++ core plan

The archive remains C++-forward where valuable, but Python is still the reference authority.

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, batched execution, future rollout core only after differential proof
```

rev0025 does not add a new C++ kernel.  Instead, it routes the new outcome-weighted ranker traffic through the existing batched C++ trace checker:

```text
1,943 events
0 skipped events
0 mismatches
0 Python replay errors
```

## Next C++ target

The next high-value C++ build is a batch-rollout sketch under Python fingerprints:

```text
Python records initial state + chosen legal action indices
C++ applies supported transitions in batch
Python compares SIGv2 checkpoints
only then consider moving more rollout work to C++
```

Do not port the full tournament loop blindly.  The history of this cube says the safe pattern is:

```text
small C++ seam
  -> differential harness
  -> recorded trace checker
  -> promotion/audit gate
  -> only then use for speed
```
