# Benchmark and stress policy

Revision: rev0005.

Benchmarks and stress tests are useful for regression detection inside the
cloudtainer, but they are not product performance claims.

## Rules

- Run a dry plan before stress execution.
- Shard stress tests whenever possible.
- Record environment, selected tasks, and timing.
- Keep benchmark inputs synthetic and deterministic.
- Treat GPU/browser timings as cloudtainer-specific.
- Never block release packaging on a broad stress suite by default.

## Future tiers

The `stress` tier is reserved for expensive probes. Each probe still needs a
manifest id, timeout, isolation mode, and artifact path.
