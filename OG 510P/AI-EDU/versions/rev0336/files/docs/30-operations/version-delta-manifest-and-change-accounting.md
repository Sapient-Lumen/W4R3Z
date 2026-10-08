# Version delta manifest and change accounting

A release audit says the package is internally consistent. A version delta manifest says what
changed from the previous revision and what the change is allowed to mean.

This surface is deliberately conservative: a delta can close an internal hardening item, add a
validator, or narrow a claim. It cannot turn readiness work into real pilot evidence.

## Delta states

| Code | Meaning |
|---|---|
| `RDM0` | no delta manifest exists |
| `RDM1` | changed paths listed manually |
| `RDM2` | added/changed/retired paths are checked |
| `RDM3` | validator and queue effects are reconciled |
| `RDM4` | delta is release-reviewed and bounded by forbidden claims |
| `RDMX` | delta overclaims, omits a material path, or hides a queue change |

## Required fields

Each delta manifest should name:

- base revision and current revision;
- added, changed, and retired paths;
- new validators and schemas;
- followthrough items closed by the delta;
- live followthrough items after the delta;
- what the delta changes operationally;
- what it explicitly does not prove.

## Use in rev0222

rev0222 adds audit-plane guardrails: invariants, dependency graph, release delta manifest,
recovery drills, and a closure evidence checklist. These close new internal hardening items, but
`FT-0181` remains live because no real `SRC2+` pilot packet exists.

See `examples/release-deltas/rev0224-delta-manifest.json` and
`tools/check_release_delta_manifest.py`.
