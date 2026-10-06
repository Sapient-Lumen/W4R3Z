# Ports adapter lane: impurity taxonomy & containment

FreeBSD ports were not designed for hermetic, reproducible builds. DeriveBSD’s ports adapter lane must treat this honestly.

## Taxonomy

### Class A: deterministic with pinning

- fixed distfiles + fixed patches
- no runtime feature probing
- stable toolchain

### Class B: deterministic with controlled probes

- configure probes exist but can be normalized by:
  - fixed PATH/tool versions
  - fixed sysroot
  - declared probe inputs

### Class C: environment-sensitive

- uses system state (installed libs, uname, sysctl)
- links against “whatever is present”

### Class D: network or time dependence

- downloads during build
- embeds timestamps

## Containment rules

- Class A/B can graduate toward “verifiable lane”.
- Class C/D remain in “best-effort lane” unless patched.

Plan MUST record:

- impurity class
- detected impurity signals (time, uname, fs scanning)
- whether outputs are eligible for promotion to signed caches

## Why keep this lane?

- migration path
- fast access to ecosystem packages

But DeriveBSD must avoid pretending these outputs have the same guarantees as fully derived artifacts.
