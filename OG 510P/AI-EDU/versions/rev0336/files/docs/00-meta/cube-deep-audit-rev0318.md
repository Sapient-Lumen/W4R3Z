# rev0318 cube deep audit: from runnable plan to one-command pack

## Executive judgment

Rev0317 made the owner-contact and teacher/tutor paths readable. The remaining risk was that the
micro-pilot still required a human to manually assemble an owner plan, coach prompt, session log,
final readout, and stop checklist from several surfaces. That is a classic cube failure mode: the
archive says the next act is simple, but the operator still has to reconstruct the packet from
scattered doctrine.

Rev0318 converts that scattered teacher/tutor path into one scratch-only command:

```bash
make micro-pilot-pack \
  CONCEPT_CODE=equality-one-step \
  CONCEPT="solving one-step equations by preserving equality" \
  SETTING="one teacher-owned practice group selected locally" \
  DATE_RANGE="owner-selected two-session window" \
  TRANSFER_CHECK="one no-AI explanation of why the same operation preserves equality" \
  OVERWRITE=1
```

The command prepares a local packet with `OWNER-PLAN.md`, `SESSION-LOG.csv`, `FINAL-READOUT.csv`,
`COACH-PROMPT.md`, `RUN-CHECKLIST.md`, and `PACK-MANIFEST.json`. It refuses obvious raw/protected
or identifying argument terms, writes only under `scratch/` or outside the repository, and labels the
packet `PREPARED_NOT_RUN` / `NOT_EVIDENCE`.

## What is most at risk of not getting completed

### Owner contact

`FT-0181` still has no real owner contact, route block, returned owner CSV, accepted `SRC2+` packet,
accepted context cycle, closeout, or closure. The owner-contact send pack remains the first field
act. Local tools can prepare and record minimal scratch state, but a human must still send or record a
route block.

### First learning cycle

The teacher/tutor micro-pilot now has a one-command packet generator. The remaining work is not
another template. It is a real owner selecting a concept, using the coach only as a move suggestion
surface, logging aggregate counts, and completing the no-AI transfer or explanation check.

### Burden/deletion

The archive's waste risk is no longer only word count. It is **assembly burden**: a field operator can
lose the run while gathering the pieces. Rev0318 reduces assembly burden without adding a new schema,
validator, or branch family. The next deletion review should target any hot-path surface not used by
the owner send or micro-pilot packet.

## Audit/refactor performed

- Added `tools/prepare_teacher_tutor_micro_pilot_pack.py` as a utility-only scratch packet preparer.
- Added `make micro-pilot-pack` so the micro-pilot can be prepared without manually copying three
  templates and a prompt card.
- Updated the run card, README, START_HERE, AGENTS, re-entry map, startup context, receipt, and
  release examples to make the command path visible.
- Kept the tool out of `lint_order`; it is execution support, not another release-control gate.
- Reclassified the teacher/tutor pack as scratch-only non-evidence in service-record language and
  current release examples.

## What remains blocked

No owner was contacted in this session. No real route block was recorded. No owner CSV or `SRC2+`
packet was accepted. The generated micro-pilot packet is not packaged and is not evidence. No
teacher/tutor micro-pilot was run. No learning, access, safety, workload, compliance, effectiveness,
service authority, custody, public-claim, or closure state changed. `FT-0181` remains queued.
