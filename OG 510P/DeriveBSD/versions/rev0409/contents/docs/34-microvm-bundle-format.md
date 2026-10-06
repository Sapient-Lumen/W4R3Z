# MicroVM bundle format (directory bundle)

The microVM artifact is a **directory bundle** whose integrity is verifiable and whose parts are addressable.

## Bundle layout (v1 proposal)

```
bundle/
  bundle.json
  runtime.manifest.json
  image/
    rootfs.raw   (or: zfs-ref.txt)
  meta/
    build-info.json          (non-authoritative; for humans/tools)
  attestations/
    provenance.dsse.json
    sbom.dsse.json           (optional)
```

## bundle.json (the integrity root)

`bundle.json` lists files and their digests (sha256), plus a format version.

Define:
- `bundle_digest = sha256( bytes(bundle.json) )`

The bundle is valid only if:
- `bundle.json` digest matches,
- listed file digests match,
- required attestations verify.

## Signing and attestations

Bind the runtime and image together via an in-toto Statement:
- subject = digests of `runtime.manifest.json` and image payload
- envelope = DSSE

- provenance attestation MUST exist for distributable artifacts
- SBOM attestation MAY exist (policy-controlled)

See RFC-0014 and RFC-0016.

Last updated: 2026-02-23
