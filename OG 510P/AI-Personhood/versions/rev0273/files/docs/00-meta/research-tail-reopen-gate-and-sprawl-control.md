# Research-tail reopen gate and sprawl control

rev0189 compacted RTC-01 through RTC-07. That creates a new risk: after the research tail is finally folded, a future release could reopen it by adding attractive but unowned `research-*.md` notes. rev0190 makes that regression testable.

## Core rule

**No new research-tail surface becomes active without a reopen gate.** A new research note, crosswalk, model-welfare metric, incident variant, namespace edge case, or reserve/accounting scenario must either fold into an existing receiving surface or pass a reopen request that names the affected RTC cluster, the receiving surface, the object hook, the fixture hook, the public summary, and the closure condition.

The reopen request schema is `schemas/research-tail-reopen-gate.schema.json`. The quarantine example is `examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json`.

## What the gate prevents

The gate blocks four bad patterns:

1. **shadow doctrine:** a new research note repeats an already compacted question but avoids the receiving surface;
2. **metric laundering:** a new welfare, incident, namespace, reserve, or proof metric is treated as evidence without object and fixture hooks;
3. **index drift:** the compaction map still says everything is folded while new research surfaces sit outside the clusters;
4. **closure inflation:** a release claims the research tail is compacted while new open questions have no owner or review-by revision.

## Required routing decision

Every proposed research-tail addition must receive one of these decisions:

- `fold-into-existing`: the work extends the receiving surface and updates an existing object family;
- `quarantine`: the work may be useful but cannot become a current surface yet;
- `reopen-approved`: a unique risk requires a new active surface, and the compaction map, registry, fixture suite, and rights-domain map are updated in the same revision;
- `reopen-denied`: the proposal duplicates an existing surface or lacks live evidence;
- `defer`: the change depends on a live drill, external law/protocol change, or materially new research.

## Audit behavior

`tools/audit_research_tail_reopen_and_drill_readiness.py` enforces that every `docs/20-world-design/research-*.md` surface remains assigned exactly once in the active compaction map, that all RTC clusters remain compacted unless a reopen request exists, and that the fixture suite blocks unmapped research-tail additions.

## Closure effect

rev0190 closes the open gate item from rev0189 by adding this surface, the schema, the quarantine example, and the negative fixture. It does not close live welfare, drill, or protocol-backfill work. It prevents the cube from sliding back into scattered notes while those live tasks remain open.


## Machine field note

The reopen-gate object uses `artifact_hooks` to keep object and fixture duties visible. A proposed research-tail addition that lacks object and fixture hooks remains quarantined.

## rev0193 no new research-tail doctrine

rev0193 deliberately does not reopen RTC-01 or create new research-tail surfaces. WRSR receipt progress is handled through operational receipt records, a quorum ledger, and a WRSR exercise outcome. Any future welfare/research addition must still pass the reopen gate rather than arriving as another `research-*.md` note.
