# Information-flow labels + explicit declassification (optional lane)

DeriveBSD already treats **authority** and **exports** as first-class, receipted events.
A missing piece in most Unix-like systems: *data flow* is usually implicit.

Greenfield advantage: optionally make “how sensitive data moved” **queryable and gateable**, without requiring a full research-OS kernel.

## The core idea

Introduce a minimal, ecosystem-wide label object:
- `flow.label` = secrecy tags + integrity tags (+ optional provenance hints)

Then make **downgrades** explicit:
- reading higher-labeled data into lower-labeled contexts is allowed only via an explicit, receipted **declassification transform**.

This is not “mandatory full IFC everywhere”. It’s a practical, high-leverage lane:
- apply labels at the edges (imports, portals, exports, backup/replication)
- treat label changes as *derived transforms* with receipts

## Why this matters

- “Where did this file come from?” is not enough; you want:
  - *what sensitivity did it carry?*
  - *what transform reduced it?*
  - *who/what authorized the downgrade?*
- Most leaks happen at boundaries (copy/paste, exports, logs, support bundles).
  Those are already DeriveBSD’s strength: portals and export policies.

## Minimal enforcement points (high ROI)

1) **Content imports**
- Imported bytes get a label (e.g., `secrecy:[external]`, `integrity:[untrusted]`).
- Tie to origin/quarantine metadata.

2) **Portals and brokers**
- Portals produce outputs with labels derived from inputs + transform id.
- Sanitization portal can reduce integrity-taint (by removing active content), but secrecy downgrades require explicit declass approval.

3) **Exports / support bundles / backups**
- Export policies can gate on labels (e.g., “never export `secrecy:[keys]`”).
- Support bundle portal can explain: “bundle contains N objects labeled `external` and M objects labeled `keys`”.

4) **Logging and diagnostics**
- Structured logs/events can carry a label.
- “debug by lease” should be label-aware: replay capsules shouldn’t silently contain downgraded data.

## The objects

- `flow.label` (typed): see `spec/flow.label.schema.json` + example.
- `declass.request` (typed): a request to downgrade (or reclassify) an object’s label.
- `declass.receipt` (typed): policy+consent decision + resulting label.

See schemas + examples:
- `spec/flow.label.schema.json`, `spec/examples/flow.label.json`
- `spec/declass.request.schema.json`, `spec/examples/declass.request.json`
- `spec/declass.receipt.schema.json`, `spec/examples/declass.receipt.json`

## Prior art worth stealing

- Asbestos and HiStar show that labels + explicit declassification are a powerful isolation primitive.
  - HiStar paper: https://www.scs.stanford.edu/~nickolai/papers/zeldovich-histar.pdf
  - Asbestos paper: https://www.scs.stanford.edu/~dm/home/papers/efstathopoulos:asbestos.pdf
- Flume shows a pragmatic approach: DIFC on top of mainstream OS abstractions.
  - Flume paper: https://pdos.csail.mit.edu/papers/flume-sosp07.pdf

DeriveBSD doesn’t need to adopt these kernels wholesale to steal the lessons:
- labels should be composable
- downgrades should be explicit
- boundary crossings are where enforcement pays off

## Related

- Origin labels + quarantine: `docs/280-origin-labels-and-quarantine-attributes.md`
- Export policies + support-bundle portal: `docs/251-export-policies-and-support-bundle-portal.md`
- Sanitization portal: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- Deterministic redaction transforms: `docs/195-deterministic-redaction-transforms.md`
- Consent UX contract: `docs/256-consent-ux-contract.md`

