# rev0226 — Late-change remedy resolution and recompute lock

## Why this revision exists

rev0225 made late-change notice dispatch explicit. That closed silent freeze and silent continuation after a retained revocation, supersession, correction, authority withdrawal, hash mismatch, challenge, or rollback signal.

The next risky seam is subtler: notice can be delivered and a remedy window can be opened, but the archive could still treat the matter as administratively handled before the remedy/appeal window is closed, submissions are retained, authority is scoped, a decision is recorded, and recompute/publication rollback is rerun.

rev0226 therefore adds a separate `live-receipt-late-change-remedy-resolution-record`.

## Boundary enforced

A remedy resolution record is not a publication continuation object. It cannot:

- continue a published snapshot;
- continue reliance;
- upgrade reliance;
- increment the live floor;
- treat silence as waiver;
- publish private-vault material; or
- substitute for a fresh floor recompute receipt or publication rollback adjudication.

Its only successful live-signal result is `resolution-ready-publication-stayed`: the remedy window has been closed and decided, but publication remains stayed until the floor engine and publication rollback adjudicator replay the outcome.

## Path after this revision

The live-evidence path is now:

`evidence drop → pilot → LEAP candidate → challenge/replay → custody authority gate → custody record → response verification gate → response record → intake conversion gate → intake record → import readiness gate → actual import gate → floor activation record → quorum participation record → computed floor → floor recompute receipt → publication rollback adjudication → late-change ingress → late-change notice dispatch → late-change remedy resolution`

## What this avoids

This closes three practical failure modes:

1. **Open-window laundering** — treating a still-open remedy/appeal window as resolved.
2. **Silence-as-waiver laundering** — treating no affected-party response as acceptance of continued publication.
3. **Resolution privacy breach** — publishing private-vault locators or sealed remedy submissions in public release outputs.

## Current status

The current example is no-signal monitoring only. No genuine late signal, live notice dispatch, or live remedy resolution exists. The computed live receipt floor remains zero and reliance stays stayed.
