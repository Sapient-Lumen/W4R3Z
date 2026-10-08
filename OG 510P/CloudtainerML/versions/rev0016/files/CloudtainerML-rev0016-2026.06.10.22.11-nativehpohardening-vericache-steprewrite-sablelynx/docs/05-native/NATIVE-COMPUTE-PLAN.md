# Native compute plan

Native code should be used when the probe is mostly tight loops over generated arrays, not when rapid model iteration matters.

Good C++ candidates:

1. streaming coreset / thinning tests;
2. quantization frontier sweeps;
3. cache eviction Monte Carlo;
4. tree-search and rollout allocation simulators;
5. pointer-chasing / finite-state world tests;
6. CPU kernels that Python can call later through subprocess or a small extension.

Keep Python for:

1. model training;
2. JSON/dashboard/report generation;
3. exploratory glue;
4. small probes where readability matters more than speed.

Rule of thumb: prototype in Python, freeze the kernel in C++ only after the cell survives the falsifier.
