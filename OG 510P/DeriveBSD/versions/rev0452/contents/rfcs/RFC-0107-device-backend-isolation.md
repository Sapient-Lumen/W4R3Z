# RFC-0107: Hypervisor device backend isolation

Status: Draft

## Problem

Device emulation is a high-risk surface for VM escapes. If the bhyve process contains both vCPU execution and device emulation, the *impact* of a device bug is large.

## Proposal

Introduce a policy-controlled hardening lane:

* optional per-device-class (or per-device) **backend workers**
* backends run in tight jails / capsicum profiles and receive only pre-opened fds
* VMM worker retains only `/dev/vmm/*` and minimal control plane access

## Compatibility

This is not required for v0. It is designed to be introduced incrementally.

## Evidence

* `vm.device-map`
* `vm.backend-profiles`

## References

See `docs/172-device-backend-isolation-bhyve.md`.
