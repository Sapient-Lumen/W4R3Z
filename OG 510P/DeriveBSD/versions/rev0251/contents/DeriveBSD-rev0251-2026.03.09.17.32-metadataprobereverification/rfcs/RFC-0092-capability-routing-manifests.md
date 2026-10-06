# RFC-0092: Capability routing manifests

Status: draft

## Motivation

DeriveBSD needs an authority model that is:
- **reviewable** (diffable)
- **enforceable** (maps to jails/pf/Capsicum/microVM wiring)
- **derived** (not hand-maintained)

Fuchsia’s Component Framework treats capability routing as the primary access-control mechanism.
We want the lesson, not the runtime: explicit grants as a graph.

Primary references:
- https://fuchsia.dev/fuchsia-src/concepts/components/v2/capabilities
- https://fuchsia.dev/fuchsia-src/contribute/contributing-to-cf/original_principles

## Proposal

Introduce a derived artifact: `caproute.json`.

Properties:
- Canonical JSON (JCS) → digestable
- Produced during Plan evaluation + activation planning
- Included by digest in the Policy Decision Record

### Minimal schema sketch

```json
{
  "version": 1,
  "subjects": {
    "fetcher": {
      "kind": "jail",
      "caps": {
        "fs_ro": ["/derive/store/..."],
        "net": [{"pf_anchor": "derive/fetcher", "mode": "egress-only"}],
        "rpc": [{"service": "derive.cache", "via": "vsock"}],
        "dev": ["null", "random"],
        "secrets": []
      }
    }
  }
}
```

The initial version must stay small; it is a *grant summary*, not a full policy engine.

## Enforcement mapping

- `fs_*` → jail mounts / microVM disks (read-only datasets)
- `net` → pf anchors + NAT/bridge wiring
- `rpc` → qrexec-like mediation layer (policy decides)
- `dev` → devfs rulesets (jails) / device wiring (microVM)
- `secrets` → sealed secret IDs + delivery mechanism references

## Open questions

- How to represent “capability inheritance” (templates / base components) without making diffs noisy?
- Which subjects are first-class (service jails, microVMs, host daemons)?
