# Shared cube runtime refactor — rev0078

## Problem

The cube's append-only tool history repeatedly implements hashing, canonical JSON, CSV writing, isolated HOME/XDG/TMP setup, archive extraction, path validation, JUnit parsing, and bounded subprocess handling. Similar names conceal many structural variants. Earlier revisions already found two consequences of this drift: generated outputs counted themselves, and descendant processes kept inherited capture pipes open after pytest exited.

Historical scripts are evidence and remain untouched. The correction is prospective and contract-driven.

## Shared mechanism

```text
tools/cube_runtime.py
  canonical JSON
  SHA-256 path, byte, and stream helpers
  CSV/JSON writers
  portable package-relative path validation
  revision derivation
  isolated runtime environment
  process-group timeout with regular-file capture
  safe nested tar.gz extraction
  JUnit normalization
  file inventory

data/current_runtime_adoption_contract.json
  names current entrypoints and forbidden helper redefinitions

tools/audit_cube_runtime_adoption.py
  measures historical duplication and fails current-tool drift
```

Current manifest, delta, package, packet-authority, and rev0078 probe entrypoints all use the shared runtime. The package auditor derives its current Python compile set and packet assertions from data contracts rather than embedding revision policy in code.

## Measured surface

```text
tool files:                                  119
top-level functions:                        759
helper-name families measured:               21
helper definitions:                         159
helper definition bytes:                 67,393
exact duplicate function groups:             59
redundant exact-function bytes, lower bound: 39,423
current contracted scripts:                   6
contract checks:                          23/23 pass
```

These numbers describe accumulated history; they are not a deletion target. Rewriting old probes would destroy reproducibility and create large review noise. New revisions should update the current contracts and shared runtime instead of forking another helper family.

Evidence:

```text
data/rev0078_runtime_helper_audit.json
data/rev0078_runtime_helper_inventory.csv
evidence/rev0078-runtime-helper-audit.md
```
