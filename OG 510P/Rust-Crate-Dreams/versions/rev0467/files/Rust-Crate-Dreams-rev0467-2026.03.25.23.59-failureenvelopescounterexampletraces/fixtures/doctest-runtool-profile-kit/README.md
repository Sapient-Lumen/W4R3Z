# Doctest Runtool Profile Kit fixtures

This fixture family is for `P-0481 Doctest Runtool Profile Kit`.

Core schemas in this fixture family now include:
- `runner-route.receipt.schema.json`
- `execution-basis.receipt.schema.json`
- `doctest-runtool-support-bundle.manifest.schema.json`
- the older `doctest-runtool.schema.json` umbrella placeholder

Suggested fixture cases:
- host-only docs examples with no custom runner
- target-specific ignore annotations
- QEMU or VM-backed runner profile
- Cargo target-runner config applying without explicit rustdoc `--test-runtool`
- working-directory-sensitive wrapper scripts or assets
- changed runner arguments producing route/basis drift
