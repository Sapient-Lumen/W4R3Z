# bhyve IO channels and “what actually works” (notes)

Moved to attic in favor of the canonical doc:
- `docs/72-bhyve-io-channels.md`

This older note is kept only for historical context.

## Console / control
- `virtio-console` is a supported bhyve device and is the baseline “control channel”. (See `docs/32-curated-references.md`.)

## AF_VSOCK
- AF_VSOCK support has been under active development in FreeBSD; treat it as “preferred when available, optional in v1”.

## Shared folders
- virtio-9p is useful for development, but guest support and performance vary.
- For DeriveBSD v1, do not require 9p for correctness; metadata disk remains baseline.

Last updated: 2026-02-23
