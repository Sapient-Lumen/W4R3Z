# Backend conformance tests (microVM runtime)

Hypervisor-centric DeriveBSD needs conformance tests so manifests don’t become “works on my machine”.

## What to test (v1)
- manifest digest stability (ADR-0022 (ADR-0005 is superseded))
- bhyve mapping determinism:
  - same manifest → same bhyve_config output
- minimal VM boot + metadata channel presence
- networking modes wired correctly (isolated/nat/bridged)
- audit invariants:
  - artifact_digest + manifest_digest + config_digest recorded

## Golden tests
Store golden manifests + expected configs under `tests/conformance/` (future).

See RFC-0024.
Last updated: 2026-02-23
