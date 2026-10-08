# ADR 0141 — router harness before bundled i2pd side effects

Status: accepted for the design cube.

The bundle-first router path must be checked before live side effects: persistent destination, persistent datadir, loopback/default endpoint, disabled accidental proxies, and transit contribution rather than a default `notransit` island.

External SAM remains supported but explicit.
