# Seeded RNG but system clock still leaks nondeterminism

Focus: a crate exposes a seeded RNG seam and therefore *looks* deterministic, but timeout, expiry, or retry logic still reads the system clock.
This fixture exists to keep `seed_injectable` distinct from fully deterministic profiles and to force the witness report to record fixed-clock requirements explicitly.
