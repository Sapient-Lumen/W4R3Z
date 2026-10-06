# Minimal privilege escalation (doas-style) for the DeriveBSD control plane

DeriveBSD’s core stance is “limit authority” and “minimize TCB”.
Operator and automation workflows need a privilege-escalation tool, but that tool should make it easy to be:
- explicit
- auditable
- deny-by-default

OpenBSD’s **doas** is a small, policy-file-driven alternative to sudo.
FreeBSD also ships doas via ports, with compatible `doas.conf` semantics.

References:
- doas(1): https://man.openbsd.org/doas.1
- doas.conf(5): https://man.openbsd.org/doas.conf
- FreeBSD doas.conf(5) (ports manpage): https://man.freebsd.org/cgi/man.cgi?manpath=FreeBSD+12.1-RELEASE+and+Ports&query=doas.conf&sektion=5

## Lesson to steal

### 1) “Permit rules” are easier to review than sprawling sudoers

doas rules are short:
- `permit|deny ... identity [as target] [cmd command [args ...]]`

That structure aligns with DeriveBSD’s desire for *diffable* authority.

### 2) Treat escalation rules as a derived artifact

Instead of hand-editing host policy forever, DeriveBSD can **derive** a doas-style rule file:
- input: Spec + policy decisions
- output: `privilege.escalation.rules` (content-addressed, signed)

This mirrors how pf config is derived from anchors, and how capability grants are derived from routing manifests.

## DeriveBSD mapping

### Recommended posture

- Prefer running long-lived control-plane daemons with **only the capabilities they need** (Capsicum/MAC/devfs/pf scoping)
- Use doas-style escalation only for:
  - one-shot administrative actions
  - controlled maintenance workflows

### Integration sketch

- `derive activate`:
  - produces a *generation-bound* escalation rules artifact
  - installs it into the active boot environment
  - emits `escalation.rules.digest` into the explainability trail

- `derive explain --authority <proc|jail|vm>`:
  - includes the relevant derived escalation rules and why they exist

### Audit hooks

- require OpenBSM/audit events for doas invocation (where available)
- forbid “NOPASS” except for tightly scoped automation identities

Candidate RFC: *Derived escalation rules and minimal operator TCB*.

Last updated: 2026-02-23
