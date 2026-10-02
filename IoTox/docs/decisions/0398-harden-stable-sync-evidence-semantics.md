# ADR 0398: Harden stable sync evidence semantics

Date: 2026-09-22

Status: accepted; sync custody terminology superseded by ADR 0405

## Context

ADR 0395 made `iotox ship-check ... stable --evidence-manifest PATH`
hash-bind every required stable receipt. ADR 0396 then made long soaks
first-class stable evidence and added semantic validation for
`terminal.long-soak`.

That still left an avoidable precious-data failure mode: a stable sync manifest
could provide correctly hashed placeholder prose for `sync.storage-readiness`,
`sync.long-soak`, `sync.recovery-custody`, `sync.restore-drill`, or
`sync.recovery-runbook`. The hash check proved only
that the placeholder file was the file named by the manifest. It did not prove
that the file even resembled the receipt class it claimed.

This was too easy to mistake for evidence. The deeper Python verifiers still
own full receipt validation, but the native release brake must catch obvious
wrong-shape sync evidence before a human can talk themselves into trusting
precious data.

## Decision

`iotox ship-check ... stable --evidence-manifest PATH` now performs native
semantic shape checks for every sync stable gate:

- `sync.local-preflight` must be `iotox-sync-doctor-v3` or `v4` with
  `decision=ready`.
- `sync.storage-readiness` must be a content-free
  `iotox.storage-readiness.v1` JSON report with `status=ready`,
  `ready_for_precious_data=true`, and accepted local storage science.
- `sync.long-soak` must be a content-free accepted
  `iotox.sync-three-writer-sandwurm-verification.v1` JSON receipt with
  `soak_campaign=true`, nonzero cycles, and at least the 24-hour stable floor.
- `sync.recovery-custody` must be a passed content-free
  `iotox.sync-backup-custody.v1` JSON receipt with a supported custody class,
  immutable/versioned generation, restore-verified repeatable custody evidence,
  matching recovery comparison, distinct-device metadata, and nonclaims for
  storage-media certification, disk-loss protection, host-compromise
  protection, filesystem-wide corruption protection, and content custody.
- `sync.restore-drill` must be a passed content-free
  `iotox.sync-retained-recovery-drill.v1` JSON receipt with a matching
  decision and satisfied local provenance/device requirements.
- `sync.recovery-runbook` must be a small line-oriented review record with
  `schema=iotox.sync-recovery-runbook-review.v1`, `status=reviewed`,
  `content-free=1`, `operator-runbook=present`, valid reviewer/access/interval
  fields, `dataset-selector-sha256`, `runbook-sha256`, nonzero
  `runbook-bytes`, `accepted-reviewed-runbook=1`, `not-content-custody=1`,
  and stop/restore/verify/retire/rehearse coverage flags. ADR 0404 later
  promoted this from a minimal hand-authored review record to a native
  hash-bound runbook receipt.

These checks are intentionally release-brake sanity checks, not replacements
for the dedicated Python verifiers and operator review. The stable manifest
still hash-binds the exact files, and release owners must still verify the
underlying receipts are real, in scope, and retained with the release dossier.

CTest now also carries the discovered runtime-loaded `libsodium` path into the
owned-registry and human CLI tests when CMake can find it. This keeps the hash
checks testable without depending on the outer shell's library path.

## Consequences

Stable sync can no longer graduate with arbitrary prose files for the receipt
classes most relevant to precious data. A placeholder recovery runbook now
produces `sync-recovery-runbook-invalid`; analogous gate-specific blocker
statuses are used for the other sync receipt classes.

This does not make precious-data readiness true. It only makes the stable
evidence intake harder to fool accidentally. ADR 0400 later removed
storage-media certification from IoTox scope; ADR 0405 later narrowed current
custody language to sync-layer versioned recovery custody. Restore drills and
recovery runbooks still need actual operator evidence.
The native checks deliberately remain content-free
and do not read data paths, file names, secrets, or backup credentials.

## Validation

```sh
nix develop --command bash -lc \
  'cmake -S . -B build/gcc-debug -G Ninja \
     -DCMAKE_MAKE_PROGRAM=$(command -v ninja) \
     -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_COMPILER=g++ \
     -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTING=ON \
     -DIOTOX_WARNINGS_AS_ERRORS=ON &&
   cmake --build build/gcc-debug --parallel --target iotox iotox_tests'

ctest --test-dir build/gcc-debug \
  -R '^(iotox\.unit-and-integration|iotox\.client-help|iotox\.docs-coherence|iotox\.human-cli)$' \
  --output-on-failure

python3 tools/verify-sync-backup-custody.py --self-test
python3 tools/qualify-storage-readiness.py --self-test
```

The focused CTest set passes without an external `IOTOX_SODIUM_LIBRARY`
override after reconfiguration, and `iotox.human-cli` now includes both a
placeholder-sync-receipt rejection fixture and a complete shaped manifest
acceptance fixture.
