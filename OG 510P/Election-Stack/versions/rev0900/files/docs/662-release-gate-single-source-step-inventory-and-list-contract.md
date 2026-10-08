# 662 — Release-gate single-source step inventory and list contract

**Track:** Shared / Release engineering

This document records a v789 release-gate maintainability hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

Before v789, the authoritative release-gate child-step order lived inline inside `scripts/release_gate.py`. The human checklist drift firewall, `scripts/check_release_gate_doc_coverage.py`, had to recover that list by regex-parsing the runner source.

That was workable, but it created a brittle maintenance seam: the release gate, the documentation coverage check, and the operator `--list` surface were coupled by source formatting rather than by a small explicit inventory.

## Reconstruction rule

`scripts/release_gate_steps.py` is now the single source of truth for ordered child-step names. The runner imports that inventory to build subprocess commands, and documentation coverage imports the same inventory instead of parsing runner source.

The final `MANIFEST.sha256` check/write remains separate from the child-step inventory because it has different release semantics:

1. a normal full gate checks the manifest after all child steps pass;
2. `--write-manifest` may only run on a full, unsliced gate;
3. diagnostic slices do not check or write the manifest as a release verdict.

## Inventory self-check

`scripts/check_release_gate_step_inventory.py` now gates the inventory itself. It verifies that:

- child-step names are unique bare Python filenames;
- every child step exists under `scripts/`;
- `build_manifest.py` remains the final manifest step rather than an ordinary child check;
- critical release-control checks remain present;
- `scripts/release_gate.py` no longer carries an inline `check_steps` list;
- the runner suppresses bytecode-cache creation before importing the local inventory, so merely starting the gate or asking for `--list` does not create a `__pycache__` artifact before cache hygiene runs;
- `python3 scripts/release_gate.py --list` reports the same child order as `scripts/release_gate_steps.py`.

This turns the operator-visible list contract into a checked release surface.

## Operator effect

Maintainers still use the same commands:

```bash
python3 scripts/release_gate.py --list
python3 scripts/release_gate.py --from-step 56 --to-step 58 --profile --progress
python3 scripts/release_gate.py --write-manifest
```

The difference is that adding, removing, or moving a child step is now a one-inventory edit plus the required `docs/162-*` checklist update. The checker fails if a formatter change or manual source edit would make the runner and the documentation coverage check disagree about the child-step set.

## Compression posture

This revision adds one small inventory module, one small inventory self-check, and one compact maintainer-control document. It does not add schemas, registries, downloaded external bodies, or a new public-answer surface.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/657-release-gate-resumability-profiled-diagnostics-and-process-group-timeouts.md`
- `docs/661-release-gate-file-backed-child-capture-and-daemonization-firewall.md`
- `scripts/release_gate_steps.py`
- `scripts/release_gate.py`
- `scripts/check_release_gate_doc_coverage.py`
- `scripts/check_release_gate_step_inventory.py`
