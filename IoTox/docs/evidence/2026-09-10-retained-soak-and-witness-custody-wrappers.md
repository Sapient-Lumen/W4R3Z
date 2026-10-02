# Retained soak and witness custody wrappers — 2026-09-10

## Scope

This note records the repository-side validation for ADR 0364 and ADR 0365.

The work improves evidence retention for two existing roadmap frontiers:

- interrupted three-writer writable soaks; and
- witness checkpoint custody drills.

It does not claim a completed 24-hour soak, backup independence, operational witness independence,
immutability, off-machine custody, or precious-data suitability.

## Validated commands

```sh
bash -n tools/iotox-repo.sh tools/iotox-monsternix-adapter.sh \
  tools/iotox-sandwurm-lab.sh tools/make-repository-datacube.sh tools/test.sh

python3 -m py_compile \
  tools/run-sync-three-writer.py \
  tools/verify-sync-three-writer-sandwurm.py \
  tools/run-witness-checkpoint-custody-drill.py \
  tools/run-sync-retained-recovery-drill.py \
  tools/clean-workspace.py \
  tools/run-sync-recovery-rehearsal.py

python3 tools/verify-sync-three-writer-sandwurm.py --self-test
python3 tools/run-witness-checkpoint-custody-drill.py --self-test
tools/iotox-repo.sh witness-custody --self-test
git diff --check
tools/iotox-repo.sh test quick
nix flake check --no-build --override-input sandwurm git+file:../sandwurm
```

The raw shell cannot run linked `build/iotox` commands that load libsodium because `libsodium.so.23`
is not on the ambient loader path. The linked-runtime command surface was therefore validated
through `nix develop`, which is this repository's normal runtime environment for the source-linked
binary.

One additional real-binary negative drill ran under `nix develop`: a temporary owner-private witness
service root and fake checkpoint were passed through
`tools/run-witness-checkpoint-custody-drill.py --iotox build/iotox`. The production C++ custody
command rejected the fake checkpoint, and the wrapper wrote a JSON receipt with:

- `status=rejected`;
- `failure_kind=iotox-command-rejected`;
- nonzero `return_code`;
- stdout/stderr byte counts;
- failure, binary, and checkpoint hashes; and
- `contains_secrets=false`.

The receipt intentionally retained no raw stderr/stdout text.

## Result

All listed validation commands passed. The C++ quick gate and real-binary negative custody drill ran
through the Nix-backed environment.

The witness wrapper success path is covered by its self-test with a fake IoTox-compatible custody
report. The underlying production C++ custody success path remains covered by the default
`iotox.unit-and-integration` quick gate.
