# Structural audit rev0360

## Main correction

Rev0360 adds a single operator-facing go/no-go command path above the accumulated capture, quarantine, adjudication, release-egress, and claim-kernel controls.

The intended passing result is **capture-ready and claim-frozen**. The package remains unable to make any real-site readiness or unreadiness claim because no real/anonymized June 2026 exercise packets are loaded.

## Integrity notes

- Built from the linked rev0359 package: `Global-Warming-rev0359-2026.06.06.03.21-safeclaim-compiler-cutovergate-refactor.zip`.
- Added one numbered canon file: `567-nuclear-emergency-preparedness-onecommand-gonogo-operatordrill-refactor-compact-canon.md`.
- Added scoped SQLite mirror: `cube/datacube-rev0360-emergency.sqlite`.
- Generated new resource manifest and validation reports for rev0360.

## Remaining highest-risk gap

The next actual risk is execution with a real operator and a first real/anonymized packet. The one-command preflight now exists; it has not been run on live evidence.
