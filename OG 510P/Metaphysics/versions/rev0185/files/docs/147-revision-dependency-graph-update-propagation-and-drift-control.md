# Revision Dependency Graph, Update Propagation, and Drift Control

## Why this file exists

The archive entered this control layer with a mature local diagnostic sequence:

1. `144-operator-family-map-and-triage-grid.md` routes a candidate case.
2. `145-adversarial-stress-tests-and-revision-protocol.md` attacks the routed diagnosis.
3. `146-diagnostic-case-ledger-calibration-set-and-benchmark-protocol.md` records hard cases when they become reusable calibration instruments.

That sequence still leaves a larger danger. A revision can be locally excellent and globally incomplete. It can add a careful operator, a good demotion, a strong calibration case, or a justified synthesis adjustment while leaving the archive's front door, method rules, open questions, family map, source note, index, or manifest stale.

This is not a clerical worry. In a large metaphysical archive, stale integration files become theory. Readers enter through `README.md`, `00-start-here.md`, `01-working-synthesis-layered-process-realism.md`, `03-method-selection-and-compression-rules.md`, and `04-open-questions-and-discriminating-tests.md`. If those files do not register an accepted change, the archive silently has two doctrines: the detailed file's doctrine and the control layer's older doctrine.

This file therefore turns the **update footprint** mentioned in `145` and `146` into an explicit dependency graph and propagation protocol. In `rev0142`, `148-terminology-register-synonym-control-and-crosswalk-protocol.md` adds a further vocabulary-audit layer after propagation, so accepted changes do not leave uncontrolled terminology behind. In `rev0143`, `149-claim-status-register-maturity-levels-and-commitment-governance.md` adds a commitment-status layer after terminology audit, so propagated and well-named changes do not become stronger doctrine than intended. In `rev0144`, `150-application-dossier-decision-record-and-verdict-report-protocol.md` adds an application-record layer after status assignment, so accepted and status-assigned verdicts can travel without losing their limits. In `rev0145`, `151-precedent-reuse-appeal-transfer-and-review-governance.md` adds a post-dossier reuse-and-appeal layer, so traveled verdicts do not become unbounded precedents. In `rev0146`, `152-transmission-excerpt-compression-and-pedagogical-governance.md` adds an output-transmission layer, so licensed verdicts do not become stronger, flatter, or more current-sounding when summarized, excerpted, taught, diagrammed, or exported.

## Compressed default

The archive should now say:

> **A revision is not complete when the new analysis is written; it is complete when the downstream commitments have been propagated, explicitly declined, or ledgered as open debt.**

In shorter form:

> **No accepted change without an update footprint.**

And more carefully:

> **Every revision should state what changed, which control files must reflect the change, which neighboring files are affected, which source anchors are implicated, which regression cases must be preserved, and which non-updates are intentional.**

## Place in the control sequence

The revised control sequence is:

1. **Route** the case or proposal with `144`.
2. **Stress-test** the routed verdict with `145`.
3. **Ledger** reusable, precedent-setting, or regression-sensitive cases with `146`.
4. **Propagate** the accepted change through the archive with this file.
5. **Register or audit terminology** with `148` when the accepted change introduces, stabilizes, renames, aliases, deprecates, quarantines, or overloads durable terms.
6. **Assign commitment status** with `149` when the accepted change could be mistaken for a stronger or weaker commitment than intended.
7. **Write an application dossier** with `150` when the accepted change or verdict will be reused, taught, source-bound, cited as precedent, or used to guide later revision.
8. **Govern precedent reuse and appeal** with `151` when a dossiered result will be reused, transferred, taught, challenged, narrowed, superseded, or marked do-not-reuse.
9. **Govern transmission and compression** with `152` when a result will leave the archive as a summary, excerpt, table, diagram, teaching example, prompt answer, paper section, rubric, or derivative artifact.

The fourth step matters because a stable archive is not just a set of correct files. It is a network of files whose front door, synthesis, methods, tests, family map, adversarial protocol, ledger, source notes, and package metadata agree about what has been accepted. The fifth step matters because a stable archive also needs its vocabulary to agree with its verdicts: terms should not become stronger, broader, or more canonical than the accepted change permits. The sixth step matters because a stable archive also needs its commitment strengths to agree with its verdicts: provisional probes, live rivals, domain-local rules, calibrated precedents, working defaults, kernel commitments, deprecated items, and open debts should not be confused. The seventh step matters because a stable archive also needs portable verdicts: a status-assigned conclusion should not travel without its target, route, rivals, basis, grain, non-verdict, future-use permission, open debts, and review trigger. The eighth step matters because portable verdicts still need travel rules: a dossiered result should not become teaching precedent, calibration, source-bound interpretation, or synthesis support unless target, basis, grain, family, source role, term status, commitment status, non-verdict, transfer conditions, and appeal triggers still hold.

## The dependency graph

### 1. Package-integrity nodes

These files establish what the package is.

- `VERSION` — current revision marker.
- `ARCHIVE_INDEX.md` — package table of contents and high-level navigation.
- `README.md` — public front door, revision note, file map, and summary of what changed.
- `MANIFEST.sha256` — integrity check for every packaged file.

Default rule: every packaged revision changes `VERSION`, `README.md`, `ARCHIVE_INDEX.md`, and `MANIFEST.sha256`. If a new file is added, the index and file map must include it. If a file is renamed, removed, demoted, or superseded, the package-integrity nodes must make that visible.

### 2. Front-door doctrine nodes

These files tell a reader what the archive currently believes.

- `docs/00-start-here.md` — present-answer sequence, main bets, and file map.
- `docs/01-working-synthesis-layered-process-realism.md` — current best theory and synthesis-level commitments.

Default rule: do not update these files merely because a local example is interesting. Do update them when a revision changes the default theory, adds a durable control layer, changes the interpretation of a family, introduces a major operator, demotes a once-central distinction, or changes how future revisions should proceed.

### 3. Method and frontier nodes

These files tell future work how to continue.

- `docs/03-method-selection-and-compression-rules.md` — admissibility, compression, and expansion rules.
- `docs/04-open-questions-and-discriminating-tests.md` — open problems and discriminating tests.

Default rule: any change that alters how future distinctions should be added, compressed, demoted, consolidated, or tested must propagate to `03` and usually to `04`. A revision that only adds a local analysis may not need a synthesis amendment, but it often needs a method or test amendment if it changes the archive's future behavior.

### 4. Source-anchor nodes

These files tell the archive what external anchors support a claim.

- `docs/05-source-citations.md` — source ledger and revision-integration notes.

Default rule: if a revision adds no source-dependent claim, say so explicitly. If it depends on a historical, legal, scientific, engineering, clinical, textual, or empirical example, add a source anchor. Do not smuggle source-dependent cases into the archive as if they were generic contrast patterns.

### 5. Local operator nodes

These are the first-order diagnostic files, roughly `06` through `143`.

Default rule: a local operator file can be changed without rewriting the entire archive, but not without checking its nearest rivals, method rule, frontier test, and family-map placement. If the local change shifts a family boundary, update `144`. If it creates a new hostile variant, update `145`. If it becomes a precedent, update `146`.

### 6. Control-layer nodes

These files govern how the whole archive grows.

- `docs/144-operator-family-map-and-triage-grid.md` — routing and family placement.
- `docs/145-adversarial-stress-tests-and-revision-protocol.md` — hostile-variation and revision-safety tests.
- `docs/146-diagnostic-case-ledger-calibration-set-and-benchmark-protocol.md` — reusable cases, negative controls, regression cases, and benchmarks.
- `docs/147-revision-dependency-graph-update-propagation-and-drift-control.md` — downstream update propagation and drift control.
- `docs/148-terminology-register-synonym-control-and-crosswalk-protocol.md` — terminology registration, synonym control, metaphor quarantine, and crosswalk discipline.
- `docs/149-claim-status-register-maturity-levels-and-commitment-governance.md` — claim-status registration, maturity levels, commitment scope, and open-debt discipline.

Default rule: a revision should state which of these control files it uses and which it changes. The control layer is not ornamental; it is the archive's self-correction mechanism. If a revision changes which words may safely carry doctrine, it should treat that as a control-layer change rather than as mere prose.

## Revision types and required propagation

### Type A: Editorial cleanup

A purely editorial cleanup corrects typos, wording, formatting, numbering, broken links, duplicated headings, or stale labels without changing doctrine.

Minimum update footprint:

- `VERSION`
- `README.md` revision note
- `ARCHIVE_INDEX.md` if file inventory changes
- `MANIFEST.sha256`

Usually no update needed:

- `00`
- `01`
- `03`
- `04`
- `144` through `148`

Exception: if the cleanup corrects a misleading doctrine summary or file map, update the relevant front-door node.

### Type B: Local operator clarification

A local clarification improves one operator without changing its family boundary.

Minimum update footprint:

- the local file
- `03` if the admissibility or compression rule changes
- `04` if the discriminating test changes
- `MANIFEST.sha256`
- `README.md` and `VERSION` for the packaged revision

Check but do not automatically change:

- `00` and `01` unless the clarification becomes synthesis-level
- `144` unless neighbor placement changes
- `145` unless a new hostile variant is introduced
- `146` unless a calibration case is added or altered
- `148` if the clarification introduces a durable term, alias, forbidden inference, or deprecation

### Type C: Neighbor-boundary adjustment

A boundary adjustment changes how two or more existing files should be distinguished: for example, sealing versus valving, support versus hosting, substitution versus turnover, or meshing versus gripping.

Minimum update footprint:

- all affected local files or a clear note explaining why not
- `03` method rule
- `04` discriminating test
- `144` adjacency rule
- `145` hostile-rival test if the boundary is tempting or unstable
- `146` if the boundary is calibrated by a reusable case
- `148` if the boundary depends on canonical terms, aliases, neighboring rivals, or unsafe shortcuts
- package-integrity nodes

Default warning: a boundary adjustment is not just a local wording change. It changes the archive's routing behavior.

### Type D: New first-order operator

A new operator adds a new diagnostic file to the first-order sequence.

Minimum update footprint:

- new local file
- `README.md` file map and revision note
- `ARCHIVE_INDEX.md`
- `00` present-answer sequence, main bets if appropriate, and file list
- `01` if the operator affects the synthesis-level default
- `03` method and compression rule
- `04` open question and discriminating test
- `05` source note, if any new source anchor is needed
- `144` family placement and nearest-rival rules
- `145` hostile variants, if the operator introduces new failure patterns
- `146` calibration cases, if any case becomes precedential
- `147` only if the operator changes the propagation protocol itself
- `148` term record or crosswalk if the operator introduces durable vocabulary, aliases, metaphors, or high-risk shortcuts
- `VERSION`
- `MANIFEST.sha256`

Default warning: a new operator without `03`, `04`, and `144` updates is under-integrated. A new operator without `00` and `README` updates is hard to find. A new operator without `145` or `146` may be acceptable only if it is not yet precedential.

### Type E: Control-layer addition

A control-layer addition changes how the archive governs itself rather than adding a new first-order operator.

Minimum update footprint:

- new or changed control file
- `README.md`
- `ARCHIVE_INDEX.md`
- `00` present-answer sequence, main bets, file list, and use instructions
- `01` synthesis-level control-layer section
- `03` method rule
- `04` open question or test for the new control layer
- `05` source note
- adjacent control files that must know about the new layer
- `148` if the addition introduces, renames, aliases, deprecates, or quarantines control-layer vocabulary
- `VERSION`
- `MANIFEST.sha256`

Default warning: a control-layer file that is not wired into `00`, `01`, `03`, `04`, and adjacent control files is merely an appendix, not a governance rule.

### Type F: Family consolidation

A family consolidation groups existing files under a clearer higher-level grammar without necessarily removing files.

Minimum update footprint:

- `144` family map
- `03` compression rule
- `04` discriminating tests
- affected local files if their interpretation changes
- `00` and `01` if the consolidation changes the current default
- `146` if calibration cases define the consolidation
- package-integrity nodes

Default warning: consolidation should reduce confusion, not hide unresolved rivalry. If several operators remain distinct but are grouped together, say which distinctions survive.

### Type G: Demotion, quarantine, or deprecation

A demotion says a file, rule, example, or candidate distinction has been weakened, quarantined, retired, or superseded.

Minimum update footprint:

- the demoted file or candidate note
- `03` if the demotion changes admission rules
- `04` if the demotion changes frontier tests
- `144` if routing changes
- `145` if a hostile variant caused the demotion
- `146` if a regression case records the demotion
- `148` if the demotion changes term status, deprecates vocabulary, or quarantines a metaphor
- `README.md` and `ARCHIVE_INDEX.md` if the file remains but changes status
- `00` and `01` if the default theory changes
- package-integrity nodes

Default warning: deletion is not the only way to demote. Some files should remain as live warnings, historical contrasts, or negative controls.

### Type H: Source-dependent enrichment

A source-dependent enrichment adds or revises claims that depend on specific external examples, scholarship, data, engineering cases, legal structures, clinical facts, or textual interpretations.

Minimum update footprint:

- affected local or control file
- `05-source-citations.md`
- `146` if the source-dependent case becomes a calibration or regression case
- `145` if source ambiguity creates artifact risk
- `148` if a source-specific term is imported, translated, quarantined, or prevented from becoming generic doctrine
- package-integrity nodes

Default warning: generic contrast patterns can be source-light. Specific empirical or historical claims should not be.

### Type I: Terminology registration, alias control, or deprecation

A terminology revision changes how words should be used, translated, aliased, quarantined, deprecated, or allowed to carry operator-work.

Minimum update footprint:

- `148` term record, crosswalk, alias rule, quarantine rule, deprecation note, or terminology audit
- `03` method rule if future revisions must behave differently
- `04` frontier test if a live term boundary needs discriminating tests
- `144` if the term changes family routing or nearest-rival behavior
- `145` if the term creates a same-word / changed-basis or same-basis / changed-word stress test
- `146` if a calibration case licenses or defeats the term
- `05` if the term depends on a source-specific anchor
- front-door and synthesis nodes if the term affects public doctrine
- package-integrity nodes

Default warning: terminology changes are not cosmetic when they alter which inferences readers are allowed to draw. Renaming, aliasing, deprecating, or quarantining a term can change routing behavior as much as a local operator edit.

## The update-footprint worksheet

Every future revision should be able to answer the following before the archive is packaged:

1. **What changed?** New file, local clarification, boundary adjustment, consolidation, demotion, ledger case, source enrichment, front-door cleanup, or package repair?
2. **What did not change?** Which adjacent files were checked and intentionally left alone?
3. **Which files must know?** `README`, `ARCHIVE_INDEX`, `VERSION`, `MANIFEST`, `00`, `01`, `03`, `04`, `05`, local operators, `144`, `145`, `146`, `147`, `148`?
4. **What is the nearest-rival dependency?** Which files could now be stale because a boundary moved?
5. **What is the synthesis dependency?** Does the current best theory have to say anything different?
6. **What is the method dependency?** Does future admission, compression, or demotion behavior change?
7. **What is the frontier dependency?** Does future testing need a new question or revised comparison class?
8. **What is the source dependency?** Are new anchors required, or is this source-neutral methodology?
9. **What is the calibration dependency?** Does a case need a positive control, negative control, hard positive, hard negative, boundary case, or regression instruction?
10. **What is the package dependency?** Do file maps, index entries, version marker, folder name, ZIP name, and manifest agree?
11. **What is the terminology dependency?** Did any term become canonical, aliased, deprecated, quarantined, source-specific, or unsafe enough to require `148`?

## Drift-control tests

### 1. Front-door drift test

Ask whether a reader who reads only `README.md` and `00-start-here.md` would know the revision exists and understand its role. If not, the archive has front-door drift.

### 2. Synthesis drift test

Ask whether `01-working-synthesis-layered-process-realism.md` still states the best current doctrine after the revision. If a new control layer changes how metaphysical verdicts are earned, the synthesis should say so.

### 3. Method drift test

Ask whether `03-method-selection-and-compression-rules.md` tells future revisions to follow the new rule. If not, the archive has method drift: it says one thing in a new file and trains future work to do another.

### 4. Frontier drift test

Ask whether `04-open-questions-and-discriminating-tests.md` poses the questions that would reveal success or failure of the new distinction. If not, the archive has frontier drift.

### 5. Family-map drift test

Ask whether `144` routes future cases to the right family after the revision. If a new distinction or demotion changes family placement and `144` does not know it, the archive has routing drift.

### 6. Adversarial drift test

Ask whether `145` contains the right hostile variants for the revised claim. If the revision introduces a new way for the archive to fool itself and `145` does not mention it, the archive has red-team drift. Vocabulary-based hostile variants should also be checked against `148` so the failed word, alias, metaphor, or shortcut remains visible.

### 7. Ledger drift test

Ask whether `146` preserves the cases future revisions must not forget. If a hard case is used repeatedly but never ledgered, the archive has calibration drift.

### 8. Source drift test

Ask whether `05` records the anchors needed to support source-dependent claims. If a revision quietly relies on a concrete example without an anchor, the archive has source drift.

### 9. Package drift test

Ask whether the file list, version marker, archive index, folder name, ZIP name, and manifest all agree. If not, the archive has package drift.

### 10. Negative-space drift test

Ask whether the revision makes clear which nearby files were intentionally not changed. If not, future work may mistake omission for oversight or, worse, mistake oversight for doctrine.

### 11. Terminology drift test

Ask whether the revision introduced, stabilized, renamed, aliased, deprecated, quarantined, or overloaded any durable term. If `148` does not record the relevant status, the archive may have terminology drift: words begin doing more work than the accepted verdict licensed.

## Non-update notes

Not every related file must be changed every time. The archive should permit explicit non-update notes.

Good non-update notes look like this:

- **No synthesis update required**: the revision clarifies a local example but does not change the default theory.
- **No source update required**: the revision is methodological and adds no new source-dependent claim.
- **No ledger update required yet**: the case is illustrative, not precedential.
- **No family-map update required**: the case stays within an existing family boundary.
- **No adversarial-protocol update required**: the existing hostile variants already cover the risk.
- **No terminology update required**: the revision uses no new durable term, alias, source-specific vocabulary, metaphor, deprecation, or high-risk shortcut beyond what `148` already controls.

Bad non-update notes look like this:

- **No update needed** with no reason.
- **Already covered somewhere** with no file named.
- **Minor change** when the revision changes admission, routing, or synthesis behavior.
- **Future work** when the change is already accepted and affects current navigation.

The point is not to maximize edited files. The point is to make the update footprint intentional.

## Propagation table

| Change accepted | Must check | Usually update | Ledger/source trigger |
|---|---|---|---|
| New operator | `00`, `01`, `03`, `04`, `144`, `145`, `146`, `05` | `README`, `ARCHIVE_INDEX`, `VERSION`, `MANIFEST` | Ledger if precedential; source if example-specific |
| Boundary adjustment | affected local files, `03`, `04`, `144` | `145`, `146` if unstable | Ledger if a hard case calibrates the boundary |
| Family consolidation | `144`, `03`, `04` | `00`, `01`, affected local files | Ledger if consolidation is case-driven |
| Demotion or quarantine | `03`, `04`, `144`, `145`, `146` | `00`, `01` if default changes | Ledger as negative control or regression case |
| Control-layer addition | `00`, `01`, `03`, `04`, adjacent control files | `05`, package nodes | Source note if source-neutral; anchors if not |
| Source-dependent case | `05`, target file, `146` | `145`, `148` if artifact-prone or term-specific | Always source-check before packaging |
| Terminology registration | `148`, `03`, `04`, `144`, `145`, `146`, `05` if source-specific | `00`, `01` if public doctrine changes | Ledger if a hard case licenses or defeats the term |
| Editorial cleanup | package nodes | affected file only | Usually none |

This table is a floor, not a ceiling. The stronger question is always: **which files would become misleading if left unchanged?**

## Relation to previous control files

### Relation to `144`

`144` asks where a case belongs. This file asks where the consequences of that placement must be reflected. A case can be routed correctly and still leave the archive under-updated.

### Relation to `145`

`145` asks what would break a preferred verdict. This file asks what must change if the verdict survives. The **update footprint** from `145` is not a final checkbox; it is the input to the propagation audit here.

### Relation to `146`

`146` records reusable hard cases. This file asks which other files must recognize that a ledgered case has become precedent, regression test, negative control, or calibration standard.

### Relation to `148`

`148` records terminology discipline. This file asks which other files must recognize that a term has become canonical, aliased, narrowed, deprecated, quarantined, source-specific, or unsafe. A terminology change can require propagation just as much as a new operator, boundary adjustment, or demotion.

## Anti-patterns

### 1. Orphaned file addition

A new file is added and listed in the manifest, but the front door, method rules, family map, and open questions do not know what it does. This produces file-count growth without navigational growth.

### 2. Synthesis overreach

A local improvement is inflated into a synthesis-level commitment. This produces a front door that overstates the doctrine.

### 3. Synthesis silence

A global control change is treated as merely local. This produces a synthesis that trains readers to ignore the new discipline.

### 4. Index-only integration

A new file is added to `ARCHIVE_INDEX.md` but not to `00`, `03`, `04`, or the relevant control file. This makes the file findable but not operative.

### 5. Source laundering

A concrete historical, scientific, engineering, legal, clinical, or textual example is used as if it were merely generic. This hides evidential debt.

### 6. Manifest theater

The manifest is recomputed even though the conceptual dependencies were not checked. Integrity hashing cannot substitute for theoretical integration.

### 7. Everything-update bloat

Every file is touched to signal diligence, even where no dependency exists. This creates noise and makes meaningful changes harder to see.

### 8. Non-update ambiguity

A neighboring file is left alone without any record of whether it was checked. Future revisions cannot tell whether silence means irrelevance, oversight, or unresolved debt.

### 9. Terminology invisibility

A revision changes which words may safely carry doctrine, but the term status is not recorded in `148`. This lets aliases, metaphors, source terms, or unsafe shortcuts reappear later as if the archive had licensed them.

## Packaging checklist

Before releasing a ZIP, verify:

1. `VERSION` matches the revision string.
2. `README.md` matches the revision string, date, codename, file map, and revision note.
3. `ARCHIVE_INDEX.md` includes every file intended for release.
4. `docs/00-start-here.md` includes new durable control layers in the present-answer sequence, main bets if appropriate, file list, and use instructions.
5. `docs/01-working-synthesis-layered-process-realism.md` reflects any synthesis-level change.
6. `docs/03-method-selection-and-compression-rules.md` includes the method rule required by the revision.
7. `docs/04-open-questions-and-discriminating-tests.md` includes the relevant test or explicitly leaves the issue outside the frontier.
8. `docs/05-source-citations.md` records new anchors or states that none were added.
9. `docs/144`, `145`, `146`, `147`, `148`, `149`, `150`, `151`, and `152` agree about the control, application, reuse, appeal, and transmission sequence.
10. No file map stops one file early.
11. No revision note describes a previous revision.
12. `MANIFEST.sha256` is recomputed after all edits.
13. A fresh extraction of the ZIP validates against the manifest.

## Default verdict

The default verdict of this file is procedural but substantive:

> **A large metaphysical archive survives by propagating accepted distinctions through its own dependency graph, keeping the words that express those distinctions under control, assigning their commitment status, and recording reusable verdicts in auditable form.**

A revision that adds insight without propagation creates drift. A revision that propagates without insight creates bureaucracy. A revision that updates files while leaving terms uncontrolled creates vocabulary drift. A revision that assigns status without a portable application record creates verdict evaporation. The aim is neither bloat nor bureaucracy. The aim is disciplined growth: local analysis, hostile testing, reusable calibration, explicit downstream update control, terminology registration, commitment-status assignment, and application-dossier reporting.


## Revision-integration note: propagation and commitment status

`149-claim-status-register-maturity-levels-and-commitment-governance.md` adds a status assignment after propagation. This matters because propagation can spread overcommitment if the accepted change is not labeled. A front-door update should not make a provisional probe sound like a working default, a domain-local rule sound archive-wide, or an open debt sound resolved.

Future update-footprint worksheets should therefore include **status result** and **maturity result**. A propagated change is complete only when the archive knows whether it is kernel, default, diagnostic, calibrated, local, rival, provisional, quarantined, source-dependent, deprecated, or open debt.


## Revision-integration note: propagation records and application dossiers

`150-application-dossier-decision-record-and-verdict-report-protocol.md` adds a case-level record of what propagation did or did not change. This matters because a reader of an application verdict should know whether the verdict merely applied the archive locally or created downstream obligations in the front door, synthesis, method rules, frontier tests, source ledger, family map, adversarial protocol, case ledger, terminology register, status register, index, version marker, manifest, or package name.

Future update-footprint worksheets should therefore include **application record needed?** and **future-use permission**. A propagated change is easier to audit when the final dossier records not just that files changed, but why the case is allowed to travel as illustration, precedent, calibration, source-bound example, live rival, or open pressure.


## Revision-integration note: propagation after appeal

`151-precedent-reuse-appeal-transfer-and-review-governance.md` adds a post-propagation review loop. If an appeal affirms, narrows, splits, demotes, quarantines, supersedes, absorbs, deprecates, or reopens a precedent, the result may need propagation through the same dependency graph as a new revision. Future propagation worksheets should therefore include one additional field: **precedent consequence** — no precedent effect, safe reuse, teaching-only use, calibration update, source-bound narrowing, appeal pending, superseded precedent, deprecated caution, do-not-reuse, or open debt.


## Revision-integration note: public-output drift

`152-transmission-excerpt-compression-and-pedagogical-governance.md` adds a new propagation target: reader-facing outputs. A revision is not fully safe if the archive files have been updated but the summary, teaching packet, public memo, diagram, table, or derivative framework still transmits an older or stronger claim. Future propagation worksheets should therefore include one additional field: **transmission consequence** — no output effect, front-door summary update, teaching warning update, table/diagram relabeling, source-bound warning, status warning, appeal warning, derivative artifact update, or do-not-transmit.

## Revision-integration note: correction-loop propagation

`153-reception-feedback-errata-and-correction-loop-governance.md` adds reception-driven propagation. A correction may start as a reader question or erratum notice but still require updates to front-door prose, synthesis, method rules, frontier tests, source notes, terminology records, status labels, dossiers, precedent packets, transmission packets, index entries, and package metadata. Future propagation worksheets should therefore include **reception consequence**: no action, local reply, wording repair, warning repair, return-path repair, erratum, packet revision, appeal, ledger entry, output quarantine, package correction, or doctrinal reopening.

## Revision-integration note: propagation as a release gate

`154-release-gates-maintenance-ledgers-deprecation-and-rollback-governance.md` turns propagation into an explicit release gate. Accepted changes should be propagated, explicitly declined, or ledgered as open debt before publication. Otherwise the release may be package-valid while still front-door-stale, synthesis-stale, method-stale, source-stale, or control-sequence-stale.

## Revision-integration note: version lineage and compatibility

Propagation controls drift inside a package; `155` adds the corresponding cross-package rule by requiring lineage packets, compatibility classes, migration actions, and forbidden reuse when material crosses versions or forks.

## Revision-integration note: provenance, custody, and reproducibility

`rev0150` adds `156-provenance-custody-build-evidence-and-reproducibility-governance.md`. Propagation now has a provenance consequence: the archive should record not only that accepted changes reached the front door, synthesis, method rules, frontier tests, source note, and control files, but also what evidence shows those files were actually touched, checked, packaged, and validated.


## Revision-integration note: review authority and claim warrant

`rev0151` adds `157-review-authority-audit-certification-and-claim-warrant-governance.md`. Propagation audits can now be review targets. A revision should not say that propagation was reviewed unless touched files, declined updates, open debts, evidence inspected, and review limits are recorded.

## Revision-integration note: public reliance after review

`rev0152` adds `158-public-reliance-citation-dispute-withdrawal-and-retraction-governance.md`. The control stack now distinguishes review warrant from public reliance. A result that is correctly routed, stress-tested, ledgered, propagated, named, status-assigned, dossiered, transmission-safe, reception-audited, release-gated, lineage-governed, provenance-audited, and reviewed still needs public-use status before it may circulate as something others can rely on. Future use should therefore ask whether the item is U0 private scratch, U1 orientation, U2 historical citation, U3 public summary with limits, U4 controlled public citation, U5 teaching/derivative reuse, U6 source-bound use, U7 advisory decision support, U8 release-warranted reliance, or U9 unsafe to cite.

## Revision-integration note: stewardship obligations and accountability

`rev0153` adds `159-stewardship-obligations-delegated-authority-and-accountability-governance.md`. Propagation audits should now check whether public-use, teaching, fork, source-bound, or derivative changes create stewardship duties that must be updated, declined, delegated, handed off, or ledgered as open debt.


## Revision-integration note: continuity registers after stewardship

`rev0154` adds `160-operational-registers-watch-queues-and-continuity-memory-governance.md`. Future uses of this file should distinguish a duty, status, packet, or verdict that is conceptually stated from one that is operationally registered. When a routed verdict, stress test, ledger case, propagation debt, terminology entry, commitment status, application dossier, precedent packet, transmission packet, reception event, release packet, lineage packet, provenance packet, review packet, public-reliance packet, or stewardship packet creates an ongoing watch, notice, correction, migration, source-refresh, derivative-maintenance, or successor duty, route the operational memory through `160`.

## Revision-integration note: validation harnesses after continuity registers

`rev0155` adds `161-validation-harness-invariant-checks-and-machine-readable-governance.md`. Future uses of this file should distinguish a rule, verdict, packet, register, or duty that is merely stated from one whose fields and invariants have actually been checked. Validation can confirm package identity, file continuity, manifest integrity, packet presence, local schema shape, and declared exceptions; it does not by itself certify metaphysical truth, source currency, public reliance, domain authority, independent review, or operational monitoring.

## Revision integration note: rev0156 workflow governance

`rev0156` adds `162-release-workflow-runbooks-execution-traces-and-handoff-governance.md` and local workflow artifacts after the validation layer. This file should now treat workflow-control claims as downstream of its own verdicts: a routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, and validation-checked item still needs a runbook stage trace before it is described as workflow-controlled, handoff-ready, or repeatably produced. Local workflow records do not create independent review, public CI, public issue tracking, source currency, or philosophical authority.

## Revision integration note: rev0157 automation-boundary governance

`rev0157` adds `163-automation-boundaries-agent-delegation-scheduled-execution-and-tool-permission-governance.md` plus local automation-boundary artifacts after workflow governance. This file should now treat automation, tool assistance, generated drafts, scheduled checks, validators, packaging commands, search tools, and delegated agents as bounded execution aids rather than sources of authority. A routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, and workflow-traced item still needs automation status, tool-permission class, scheduled-execution class, authorized scope, human-review gate, evidence record, allowed claim language, forbidden claim language, and stop triggers before it is described as automated, monitored, source-current, independently re-executed, or tool-certified. Local tool use does not create public CI, source-watch automation, external audit, independent review, domain authority, or philosophical truth.

## Rev0158 integration note: semantic fidelity after automation

`164-semantic-fidelity-generated-output-audit-and-warning-retention-governance.md` adds the next control layer after automation. This file should now be read with the following boundary in mind: an output may be routed, stress-tested, registered, validated, workflow-executed, and automation-bounded while still failing to preserve target, basis, status, warning, non-verdict, source, version, or public-use limits. When a result is summarized, diagrammed, taught, generated, excerpted, migrated, or handed off, route the transfer through `164` before calling it faithful, teaching-safe, derivative-ready, source-preserving, or public-use appropriate.


## Rev0159 integration note: operational reliance after semantic fidelity

`165-operational-reliance-deployment-boundaries-and-action-use-governance.md` adds the next control layer after semantic fidelity. This file should now be read with the following boundary in mind: a result may be routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, workflow-traced, automation-bounded, and semantically faithful while still being unauthorized for action. When archive material is proposed as policy, procedure, classifier, recommendation, decision support, automated trigger, institutional workflow, teaching practice, public guidance, or high-stakes domain advice, route the use through `165` before calling it operationally permitted.

## Rev0160 integration note: incident response after deployment

`166-incident-response-harm-review-near-miss-and-recovery-governance.md` adds the next control layer after deployment-boundary governance. This file should now be read with the following boundary in mind: a result may be routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, workflow-traced, automation-bounded, semantically faithful, and deployment-classified while still producing an incident, near miss, warning failure, unauthorized escalation, evidence-loss risk, rollback failure, derivative misuse, public reliance failure, or domain-sensitive recovery debt. When something goes wrong after action-use or attempted action-use, route the event through `166` before calling it ordinary feedback, ordinary errata, closed recovery, harmless misuse, or solved rollback.


## Rev0161 integration note: post-incident learning after incident response

`167-post-incident-learning-root-cause-capa-and-recurrence-risk-governance.md` adds the next control layer after incident response. This file should now be read with the following boundary in mind: an event can be routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, workflow-traced, automation-bounded, semantically faithful, deployment-classified, and incident-recovered while still being unlearned. When a recovered incident, near miss, warning failure, deployment-boundary failure, derivative misuse, validation misclaim, or recovery dispute may recur, route it through `167` before calling the pattern fixed, prevented, verified, or safe to forget.

## Rev0162 integration note

`rev0162` adds `168-longitudinal-monitoring-effectiveness-review-sunset-and-residual-risk-governance.md`. This does not replace this protocol. It adds a later check on whether controls, warnings, review duties, release gates, deployment limits, incident lessons, or post-incident preventive actions remain effective across future releases and uses. Any result produced by this file that is meant to persist, travel, govern derivatives, guide operational use, or close a recurrence risk should now be eligible for a `168` monitoring packet stating monitoring status, effectiveness class, residual-risk trend, review trigger, and sunset/renewal condition.

## Revision-integration note: risk portfolio governance

`169-cross-case-risk-portfolio-systemic-exposure-and-prioritization-governance.md` adds a control above single-record review. This file's verdicts, packets, registers, duties, warnings, release gates, review claims, public-use permissions, deployment boundaries, incidents, learning controls, or monitoring items should not be treated as collectively manageable merely because they are locally acceptable one by one. When several such items accumulate, future revisions should use `169` to classify portfolio status, exposure aggregation, correlation/common-cause class, cumulative burden, priority/treatment class, accepted residual risks, blocked or escalated items, allowed wording, forbidden wording, and next review trigger.

## Rev0164 capacity-allocation update

`170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md` adds a layer after portfolio prioritization. Any result from this file that becomes a priority item, release debt, source-refresh need, public-use restriction, derivative duty, deployment-boundary review, incident lesson, monitoring trigger, validation gap, or stewardship obligation should not be described as assigned, scheduled, manageable, monitored, safe to defer, or handled until a capacity packet states CAP/BL/WIP/DEF classes, resource basis, scarce dependency, owner or declined responsibility, next action, WIP limit, stop condition, allowed wording, forbidden wording, and open capacity debt.
