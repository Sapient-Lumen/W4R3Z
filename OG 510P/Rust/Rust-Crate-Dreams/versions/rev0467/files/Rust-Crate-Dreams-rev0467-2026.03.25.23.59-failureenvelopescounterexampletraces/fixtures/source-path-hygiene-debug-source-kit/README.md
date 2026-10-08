# Source Path Hygiene & Debug Source Kit fixtures

Fixture ideas:
- developer profile with no path sanitization and full workspace/std source lookup
- release profile with `trim-paths` and remapped workspace paths
- sysroot source lookup requiring `rust-src`
- compiler-source lookup requiring `rustc-dev`


Suggested starter schemas:
- `source-hygiene.schema.json` — coarse source-path posture receipt
- `virtual-source.manifest.schema.json` — virtual path prefixes plus source-class/component hints
- `source-availability.report.schema.json` — conservative debugger-source verdicts
