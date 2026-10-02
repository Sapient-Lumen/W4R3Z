# ADR 0299: Add normalized host capabilities to diagnostics

- Status: accepted and implemented
- Date: 2026-09-02

## Context

The explicit `host-capabilities` command already tested pidfds, seccomp, MDWE, Landlock, sudo
mechanism, cgroup v2 delegation, controllers, and resource interfaces. That implementation lived
inside the administrative CLI, and its useful local report intentionally contained paths and raw
controller text. Diagnostics therefore could neither reuse it nor safely share it. Re-running its
fork-based confinement probes inside a multithreaded Agent would also create an avoidable process
safety hazard.

## Decision

Extract one reusable `TerminalHostCapabilities` snapshot and renderer. Explicit
`iotox host-capabilities` retains the live child probes. A running Agent calls the same sampler in
passive/no-fork mode during diagnostics export and explicitly reduces the local snapshot to a closed
`HostCapabilitiesExport` before it reaches the recorder grammar.

Local-control v1.56 keeps no-payload operation 108 and emits `iotox-diagnostics-redacted-v3`.
The v3 appendix contains only closed grades for pidfd, seccomp, MDWE, Landlock and its numeric ABI,
privilege-escalation prerequisites, sudo mechanism, and cgroup-v2 availability/delegation. Known
cgroup controllers and twelve fixed resource interfaces become bounded bitmasks; unknown controller
names become a count. No cgroup root, executable path, controller name, mount data, `/proc` or `/sys`
text, environment, UID, hostname, kernel version, or arbitrary probe error is exported.

Offline inspection accepts v1 flight-only and v2 health-only payloads. New exports use v3. The outer
bundle-v1 framing/digest and its no-authorship boundary remain unchanged. No peer, Ratox, authority,
sync-object, or Tox frame changes.

## Consequences

One support artifact can now say whether the host appears capable of enforcing the intended Ratox
boundary without leaking the coordinates needed to operate that host. `available` from the passive
Agent sampler is weaker than `live-proved` from the explicit administrator command; inspection keeps
those grades distinct. Sudo discovery proves only a privileged executable mechanism, never user
authorization or PAM behavior.

Existing CLI, diagnostics, and live-Agent gates now cross the shared sampler, v3 grammar, invariant
refusal, v1/v2 compatibility, and anonymous health/capability composition. This is a bounded Linux
capability observation, not kernel attestation, final PTY-child enforcement, sudo authorization,
container escape analysis, rollback resistance, or proof that a deployment is safe.
