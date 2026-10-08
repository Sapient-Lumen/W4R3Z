# Raw evidence intake page — source, role, path, and artifact class interface spec

## Purpose

Give the operator one durable page that answers:

- what raw artifacts were actually discovered or imported
- where each raw artifact came from
- which witness / participant / platform / capture row produced it
- what artifact class each raw file most likely belongs to
- what provenance is already strong, weak, or missing before cleanup starts

This page exists so `I found some logs in a hidden folder` and `I copied the NAS var directory` become typed product truth instead of temporary file-manager memory.

## Inputs

- incident identifier
- witness set and participant roles if any
- evidence plan and capture matrix rows if any
- imported raw files / folders / dumps / measurements
- source-path metadata
- original filename / extension / size / timestamps
- import route (`local-harvest`, `scp-copy`, `public-download`, `mobile-export`, `manual-drop`, `other`)
- current sensitivity heuristics

## Primary questions this page must answer

1. What raw sources now exist for this incident?
2. What witness, platform, or capture row does each source belong to?
3. What artifact family does each source appear to represent?
4. Is the source original, copied, moved, extracted, compressed, or already derived?
5. Which provenance gaps must be resolved before normalization or assembly?

## Layout

### A. Intake strip

Fields:

- incident headline
- intake batch label
- source count
- provenance posture (`strong`, `mixed`, `weak`, `unknown`)
- normalization readiness

### B. Raw sources table

Columns:

- raw source id
- original filename / folder name
- artifact-family guess (`debug-log`, `rotated-log`, `journal`, `crash-report`, `mini-dump`, `core-dump`, `profiler`, `mixed-folder`, `unknown`)
- witness / participant
- platform / runtime
- source path class (`desktop-storage`, `service-storage`, `hidden-mobile`, `nas-var`, `public-download`, `manual-import`, `other`)
- origin state (`original`, `copied`, `moved`, `compressed`, `extracted`, `unknown`)
- current intake verdict (`typed`, `needs-review`, `duplicate-candidate`, `overscoped-folder`, `blocked`)

### C. Provenance card

Show:

- strongest known source claim for the selected raw item
- witness/participant binding
- capture-row binding if known
- missing lineage warnings
- whether the item was already detached from its original path

### D. Overscope and sensitivity card

Show:

- whether a whole folder was imported instead of a narrow member set
- likely unrelated internals present
- path/privacy exposure warnings
- whether normalization should prune or split before assembly

### E. Next-step card

Show the smallest honest next move:

- `type remaining unknown members`
- `bind source to witness`
- `prune overscoped folder`
- `extract compressed member`
- `open normalization review`
- `hold because provenance is too weak`

## Required interactions

- `Bind raw source to witness`
- `Bind raw source to capture row`
- `Retype artifact family`
- `Mark source as copied / extracted / moved`
- `Open artifact normalization review`
- `Block intake batch`
- `Issue intake receipt draft`

## Guardrails

- Never flatten a whole imported folder into one vague `logs` member.
- Never hide whether the file came from a hidden path, service path, or public-download staging path.
- Never present a raw source as original if it has already been moved, copied, or extracted.
- Never let witness/platform provenance vanish during drag-drop or upload.
- Never mark intake `ready` while artifact class or witness binding is still materially ambiguous.

## Output

A reviewed raw-intake object that preserves original source identity, witness/platform provenance, artifact-family typing, and initial sensitivity warnings before normalization begins.

