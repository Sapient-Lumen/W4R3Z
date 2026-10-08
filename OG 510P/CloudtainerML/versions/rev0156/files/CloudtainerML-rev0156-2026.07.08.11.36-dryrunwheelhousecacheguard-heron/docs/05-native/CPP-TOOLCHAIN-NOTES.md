# C/C++ toolchain notes

The cloudtainer has `gcc` and `g++`, so CloudtainerML can include small native probes as source + Makefile rather than only Python.

Why this matters:

- high-volume Monte Carlo sweeps can move from Python loops to native loops;
- cache/attention approximations can be tested with predictable CPU performance;
- algorithmic probes from data-structures papers can be implemented without needing GPU libraries;
- compiled probes can serve as future kernels under Python orchestration.

Current native probe:

```text
experiments/express_streaming_coreset/express_coreset.cpp
```

The native audit compiles it in a temporary directory and writes a smoke JSON artifact. The zip should not rely on a prebuilt binary.
