# Sync loopback custody prerequisite drill — 2026-09-17

Status: accepted local prerequisite; not independent backup evidence.

## Command

```sh
nix develop -c tools/iotox-repo.sh sync-loopback-custody-drill --iotox build/iotox
```

The helper creates two temporary ext4 loopback filesystems, writes one selected backup generation,
remounts that backup filesystem read-only, restores the generation onto a second loopback filesystem,
and then runs the retained recovery drill with both local requirements enabled:

- operator provenance labels must be present and bound into the verifier report; and
- `root-devices-differ=1` must be observed by `sync-recovery-verify`.

Raw loop images were unmounted, detached, and removed after the receipt was written.

## Accepted receipt

```text
run-id:                       run.9xP4yW5T
receipt:                      .sandwurm/exports/sync-recovery-custody/run.9xP4yW5T/retained-recovery-drill.json
receipt-sha256:               f747c34cb23cde72f6e144fa30c99949a11c153a5d0bd5fd9931ef88e3786907
status:                       passed
decision:                     match
root-devices-differ:          1
operator-provenance-bound:    true
local-requirements-satisfied: true
backup-files:                 3
backup-entries:               6
backup-bytes:                 32848
backup-manifest:              d4b3318a0947f3e464a8eed3929e14f74281fc0a5d579f09a8f2e1c05e3bbce1
restored-manifest:            d4b3318a0947f3e464a8eed3929e14f74281fc0a5d579f09a8f2e1c05e3bbce1
report-sha256:                aac587244e84dbc42a8d4a825650e376d9b99b010076fbd97a13e0a4ef0d9d0d
iotox-binary-sha256:          e0a97478380374951e8c28e3f7ef42f26a5be454fb2083f29a08e07193e8789d
contains-secrets:             false
```

## Boundary

This is stronger than the earlier same-directory retained drill because the accepted receipt requires
different filesystem device observations and a read-only selected generation. It is still same-host
loopback evidence. It does not prove off-machine custody, append-only retention, backup software
correctness, snapshot provenance, storage honesty, administrative independence, or suitability as the
sole recovery path for precious data.

The useful result is that the exact operator command and content-free receipt path now exist. A real
backup promotion should reuse the same retained drill shape against an actual immutable/versioned
backup generation in a different failure domain.
