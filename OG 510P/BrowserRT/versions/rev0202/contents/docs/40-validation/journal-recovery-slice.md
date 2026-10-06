# Journal recovery testing slice

Revision: rev0028

## Manifest id

`storage:journal-recovery-proof`

## Why this slice exists

The storage lane needs recovery semantics before browser durability tests grow expensive. This slice proves the shape of journal/manifest evidence in a fake provider.

## What it proves

The slice runs `tools/journal_recovery_probe.mjs` and writes `artifacts/validation/REV0044-JOURNAL-RECOVERY-PROBE.json`.

It proves:

- manifest checkpoints capture accepted fake block state;
- an older checkpoint replays more journal records than a newer checkpoint;
- committed deletes are preserved through recovery;
- a torn/corrupt journal tail is ignored once;
- a corrupt manifest checksum is rejected;
- repeating recovery from the same image is deterministic;
- trace events include journal append, manifest checkpoint, replay apply, ignored tail, and recovery result.

## What it intentionally does not prove

- OPFS persistence.
- Browser restart or reload recovery.
- `FileSystemSyncAccessHandle.flush` durability.
- Quota pressure behavior.
- Eviction behavior.
- Compaction.
- Multi-tab safety.
- Real performance.

## Why this belongs in the release tier

It is cheap, deterministic, and expands the storage contract without launching Chromium. This is exactly the kind of slice the cloudtainer testing strategy wants before a future browser recovery rung.
