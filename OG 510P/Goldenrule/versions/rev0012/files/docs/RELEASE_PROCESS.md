# Release Process

## Pre-release

1. `make gate`
2. `make gate-strict` (if strict tooling is installed)
3. `make test-release-manifest-schema`
4. `make test-release-checksums RELEASE_VERSION=<version>`
5. `make test-release-hygiene RELEASE_VERSION=<version>`

## Manifest

Generate release manifest and checksums:

```bash
make release-manifest RELEASE_VERSION=<version>
```

Outputs are written under `artifacts/release/<version>/`.

Validate manifest structure and checksums:

```bash
make test-release-manifest-schema
make test-release-checksums RELEASE_VERSION=<version>
```

## Notes

- Strict security tools may be optional in some dev environments.
- Release candidates should run in environments where strict tools are installed.
