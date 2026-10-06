# Measured launch (DRTM) and late-launch integrity (optional TrenchBoot-shaped lane)

DeriveBSD already has a **measured boot** posture:

- unified boot capsules + measured boot receipts
- boot event log digesting
- attestation receipts as reusable evidence

Measured boot assumes the firmware/boot chain is trustworthy enough to begin measurement.
Some deployments want a stronger story: a **Dynamic Root of Trust for Measurement (DRTM)** (a “late launch”), which establishes a measured environment *after* reset using CPU features (e.g., Intel TXT / AMD SKINIT / related approaches).

TrenchBoot is an open-source project aimed at making DRTM measurable launch less bespoke.

## The stance

- **Optional lane:** DRTM is not required for most users.
- Treat it as a *platform-mode choice*:
  - static measured boot (default)
  - measured launch / late launch (DRTM)

## Why this matters in DeriveBSD terms

- It is another way of producing **boot evidence**.
- It changes threat assumptions for:
  - early boot malware,
  - “evil maid” scenarios,
  - firmware trust boundaries.

The greenfield win is not that we ship DRTM everywhere, but that if we support it:

- it becomes an explicit lane,
- and its evidence flows into the same receipt model.

## Integration sketch

### 1) Boot capsules advertise launch mode

A boot capsule can declare a `launch_mode`:

- `static-measured-boot`
- `late-launch-drtm`

This becomes a fact referenced by:
- attestation requirements (some policies may require DRTM),
- admission policies (some actions may be gated on it).

### 2) DRTM evidence is just another evidence digest

Treat DRTM event logs / PCR usage as:
- an evidence object stored in the CAS,
- and referenced by `attestation.receipt.evidence.*`.

### 3) Parser registry applies

DRTM and boot logs are *parsers*.
If we ingest vendor/firmware measurement logs, those formats should show up in `parser.registry`.

## Ergonomics

- Provide a “posture explain” command that can say:
  - which launch mode was used,
  - which measurements were verified,
  - and what policies depended on them.

- Keep it modular:
  - DRTM tooling can live in a privileged compartment, invoked by plans.

## Non-goals

- Treating DRTM as a universal fix for firmware risk.
- Supporting every platform feature on day one.

## References

- TrenchBoot late-launch overview (DRTM background):
  - https://trenchboot.org/dev-docs/Late_Launch_Overview/
- TrenchBoot project docs (quickstart / context):
  - https://github.com/TrenchBoot/documentation/blob/master/QUICKSTART.md
- Qubes OS: TrenchBoot Anti Evil Maid (illustrates a real deployment motivation):
  - https://www.qubes-os.org/news/2023/01/31/trenchboot-aem-for-qubes-os/

Last updated: 2026-02-27r110
