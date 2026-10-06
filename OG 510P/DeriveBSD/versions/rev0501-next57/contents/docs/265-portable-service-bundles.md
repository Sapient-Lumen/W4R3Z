# Portable service bundles (systemd portable services lessons)

MicroVMs are a great default isolation boundary, but there is still a class of “host-adjacent” things where a microVM is heavy:
- metrics exporters
- log forwarders
- device helpers
- emergency/incident tooling

systemd’s **Portable Services** are an interesting distribution pattern:
ship services plus their dependencies as an image/tree, then *attach/detach* them to a host with strong sandboxing defaults.

DeriveBSD can borrow the concept without importing systemd.

## DeriveBSD target

A **portable service bundle** is a signed artifact that contains:
- a root filesystem tree (store-backed or CAS)
- a svcdb fragment (service definitions, placement, dependencies)
- a capability routing fragment (what it is allowed to touch)
- optional health checks and evidence hooks

It can be:
- attached to a host generation (for a timeboxed incident window)
- attached to a workload host/jail (sidecars)
- detached cleanly (no residue)

## Safety invariants

- Attach/detach is an **evidence-producing change-set**
- Bundles never mutate the base generation; they extend via views (`docs/122-system-extensions.md`, `docs/264-mount-namespaces-and-union-views.md`)
- Policy can require:
  - breakglass grants for “ops bundles”
  - maximum attachment duration
  - network egress restrictions

## UX sketch

- `derive bundle build ./bundles/node-exporter`
- `derive bundle attach <bundle-digest> --scope host --until 2h`
- `derive bundle detach <bundle-digest>`
- `derive status` shows attached bundles per deployment

## Why bake this in early

If we don’t provide an official “ops tooling lane”, operators will reinvent one:
- SSHing random binaries onto hosts
- diverging incident playbooks
- growing the base forever “just in case”

A portable bundle lane keeps the base small while still being practical.

## References
- systemd — Portable Services concept: https://systemd.io/PORTABLE_SERVICES/
- man7.org — systemd-portabled.service(8): https://man7.org/linux/man-pages/man8/systemd-portabled.service.8.html
- Debian manpages — portablectl(1): https://manpages.debian.org/experimental/systemd-container/portablectl.1.en.html

Last updated: 2026-02-25
