# ADR 0360: Record recovery provenance and witness checkpoint custody

- Status: accepted and implemented
- Date: 2026-09-10

## Context

The trust-graduation frontier now depends less on another synchronization mechanism and more on
operator evidence discipline. A restore drill must name the backup generation it used, and a witness
checkpoint must be retained outside the service store that it is meant to floor. Before this ADR,
IoTox could verify a restored tree and could verify a signed witness checkpoint, but the reports had
no strict place for operator-supplied provenance or custody labels.

A single machine still cannot prove independent administration, independent media, honest storage,
or rollback-resistant retention. The product must therefore record useful evidence without silently
upgrading that evidence into a trust claim.

## Decision

`sync-recovery-verify` now accepts optional all-or-none provenance labels:

```text
backup-system=TEXT
backup-generation=TEXT
backup-failure-domain=TEXT
restore-provenance=TEXT
```

Each label is 1..256 printable bytes. The v1 report now records whether the canonical backup and
restore roots were observed on different device IDs, whether operator provenance was supplied, and
the supplied labels as canonical hex. It still reports:

```text
backup-independence=not-assessed
restore-provenance=not-assessed
```

The new `witness-service-checkpoint-custody` command verifies a signed checkpoint against a pinned
witness-service public key, canonicalizes the service root and checkpoint file, requires the
checkpoint path to be outside the service root, reads the checkpoint through the bounded no-follow
stable file reader, and emits a strict custody report. Optional all-or-none custody labels are:

```text
custody-system=TEXT
custody-generation=TEXT
custody-failure-domain=TEXT
```

The report includes authenticated status, path hex, outside-root status, same/different filesystem
observation, record count, public key, optional custody labels, and:

```text
operational-independence=not-assessed
```

## Consequences

Recovery drills and witness-checkpoint retention can now carry machine-readable operator context in
the same artifact as the verifier result. This makes evidence bundles and later audits less reliant
on prose notes.

The labels are operator assertions, not cryptographic proof. `root-devices-differ=1` or
`checkpoint-root-devices-differ=1` is useful evidence but not sufficient for independence; matching
device IDs are also not a command failure because same-host and VM drills remain valid construction
tests.

This ADR changes no synchronization authority, witness CAS semantics, checkpoint wire format,
storage durability guarantee, or precious-data recommendation.

## Evidence

Accepted local checks:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox iotox_tests && ctest --test-dir build -R "^(iotox\.unit-and-integration|iotox\.client-help)$" --output-on-failure'
nix flake check -L
```
