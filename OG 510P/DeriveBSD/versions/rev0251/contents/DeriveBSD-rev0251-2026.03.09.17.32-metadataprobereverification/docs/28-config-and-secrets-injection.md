# Config and secrets injection (microVM contract)

Standardize how instances receive configuration and secrets across hypervisor backends.
Goal: no ad-hoc boot hacks, no secrets baked into images, predictable reproducibility.

## Definitions

- **Config**: non-secret instance parameters (identity, endpoints, feature flags).
- **Secrets**: secret bytes (keys, tokens, cert material) with rotation requirements.
- **Injection channel**: host→guest delivery mechanism with a defined schema.

## Constraints

- Images are immutable; config/secrets are delivered at instance start.
- Guest must be able to boot **without network**.
- Config that changes image content influences Plan identity; secrets never do.

## Baseline channels (v1)

### A) Read-only metadata disk (baseline)
Attach an extra read-only disk (ISO9660 or VFAT) containing:
- `meta.json` (instance identity, digests, nonces)
- `config.json` (non-secret)

Foreign guests may optionally consume a cloud-init NoCloud compatible layout; DeriveBSD defines a native schema and can generate adapters if needed.

### B) Read-only shared folder (virtio-9p) (optional)
Attach a host directory read-only for non-secret config *only* when backend+guest support is stable.
On FreeBSD guests, mounting requires 9P filesystem support (see p9fs(4)) and may not be available on older releases.

### C) Host/guest control channel for secrets (vsock preferred when available; virtio-console fallback)

Note: AF_VSOCK support varies by platform; treat vsock as an optimization and keep virtio-console as the baseline.
Secrets are delivered via a dedicated control channel:
- prefer AF_VSOCK where supported
- otherwise use virtio-console ports connected to host UNIX sockets

A tiny guest agent authenticates and fetches secrets; secrets land in tmpfs and get strict perms.

## Metadata schema (v1)

### meta.json
- `instance_id` (UUID)
- `artifact_digest` (bundle/store digest)
- `manifest_digest`
- `boot_nonce` (fresh random)
- `issued_at` (timestamp)
- `derive_version` (compat)

### config.json
- `service_name`
- `roles`
- `network` (attachments)
- `logging` (sink)
- `feature_flags`

## Secrets contract (v1)

Runtime manifest declares:
- `secrets.required`
- `secrets.optional`
- `secrets.rotation` hints (`ttl`, `reload_method`)

Host secrets agent enforces allowlists keyed by:
- artifact signing key / namespace
- target kind
- instance identity

### Optional identity-gated lane (preferred at scale)

Instead of long-lived secrets, workloads can obtain a short-lived identity (SVID-style) and then fetch scoped tokens/operations via brokers.
This keeps static credentials out of images while preserving tight auditability.

See: `docs/181-workload-identity-and-secretless-deploys.md`.

## Minimal handshake

- Host generates `boot_nonce`; writes it to metadata disk.
- Guest agent connects and presents: `instance_id`, `boot_nonce`, `artifact_digest`.
- Host verifies artifact trust + policy + nonce freshness.
- Host streams secrets; guest applies and acknowledges.

See RFC-0012 and ADR-0003.

## Notes on platform reality

- `virtio-console` is the baseline control channel because bhyve supports it widely (see bhyve(8): https://man.freebsd.org/bhyve).
- AF_VSOCK is desirable (host/guest comms without network) but treat it as optional until it’s solid everywhere (see FreeBSD status report: https://www.freebsd.org/status/report-2024-07-2024-09/vsock/).
- virtio-9p / shared folders are optional and not required for correctness; guest support varies (bhyve(8) lists virtio-9p, but FreeBSD guest support depends on p9fs/virtio_p9fs):
  - bhyve(8): https://man.freebsd.org/bhyve%288%29
  - p9fs(4): https://cocalc.com/github/freebsd/freebsd-src/blob/main/share/man/man4/p9fs.4
  - vm-bhyve issue notes: https://github.com/churchers/vm-bhyve/issues/552

## First-boot provisioning vs per-boot injection

Some state should be written exactly once (disk layout, non-secret config files) and then remain immutable.
Borrow the Ignition pattern: provision once, inject always.
See: `docs/123-ignition-style-firstboot.md`.

## Sealed secrets

See `docs/63-secrets-sealing-and-delivery.md` (RFC-0039) for sealing/delivery design.


Last updated: 2026-02-24
