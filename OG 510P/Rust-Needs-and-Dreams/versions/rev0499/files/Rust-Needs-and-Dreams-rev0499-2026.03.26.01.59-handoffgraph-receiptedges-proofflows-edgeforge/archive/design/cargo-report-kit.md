# Design: Cargo Report Kit (`cargo reportpack`, `cargo-report-pack/v0`)

## Goal
Define the missing **portable import, quarantine, authority-path, contradiction/arbitration, review-request/decision, projection, execution/lineage, claim, currentness, promotion, and handoff layer** for Cargo-native reports.

Cargo Report Kit should sit:
- **above** Cargo’s native report storage and replay surfaces,
- **below** Build-State Evidence, Perf Labs, Feedback Loop, and other consumer layers,
- and **beside** native Cargo evolution rather than trying to freeze Cargo internals prematurely.

The point is not to replace Cargo’s own `cargo report` work.
The point is to make native report lanes:
- portable across CI, issue trackers, and local review,
- explicit about stability, visibility, lossiness, and currentness,
- explicit about **authoritative native basis**,
- explicit about **authority path / fallback order / refusal posture**,
- explicit about **projection / redaction / omission receipts** when local-private capture becomes a portable/shared artifact,
- explicit about **quarantine-first retained capture** when imported bytes are historically worth keeping but not yet safe to summarize, search, or share normally,
- and reusable by multiple downstream consumers without letting the latest imported pack silently masquerade as either a frozen shared example or the current active workspace story.
- The kit must also preserve a compact production story once artifacts become projected, derived, or promoted: which operation ran, which parents it consumed, which outputs it produced, and which head/supersession roles that lineage now justifies.

## Why this seam matters now
Cargo’s reporting surface is no longer hypothetical.
It now has two real families with different maturity and semantics:
- stable future-incompat report replay;
- unstable build-analysis sessions with persisted logs, replayed timings, and rebuild explanations.

That combination creates exactly the kind of boundary the archive should elevate:
- there is enough real native surface to import,
- there is still enough instability that consumer honesty matters,
- multiple nearby stacks already want the same data,
- and Cargo’s own build-analysis goal explicitly says collection must remain opt-in, privacy/performance-conscious, and free of premature user-facing stability promises.

## References (signals)
- Cargo Book: `cargo report` currently supports the stable `future-incompat` report lane.
  https://doc.rust-lang.org/cargo/commands/cargo-report.html
- Future-incompat report chapter: Cargo stores report IDs and replays full reports later.
  https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
- Cargo unstable features: `-Zbuild-analysis` persists JSONL logs in `$CARGO_HOME/log/`, gives each invocation a unique session ID, and enables `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.94 dev cycle: `cargo report timings` is gaining features, `cargo report rebuild` and `cargo report sessions` were added, man pages now exist for `cargo report *`, and unstable `--timings=FMT` is being removed in favor of report replay.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo build-analysis goal: Cargo wants to record build metadata across invocations, expose it through report-style tooling, enable external analysis, avoid privacy/performance regressions, and keep prototyping free of user-facing stability guarantees.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

## Working thesis
A worthy contribution here should make it possible to answer all of these cleanly:
1. Which native Cargo report lane was imported?
2. Was it stable, unstable, or mixed?
3. Which session/report IDs anchor the data, what exact workspace/package/target/profile/feature/toolchain/invocation scope did they cover, and which stronger workspace-lane claim classes are still out of bounds?
4. Which fields were Cargo-authored, rustc/tool-authored passthrough, user/workspace-authored context, pack-authored annotation, or downstream-derived summary?
5. Which parts came from local-private native capture, which were copied into the pack, which are actually intended to be shared, which are frozen shared examples, and which shared bytes are only a projected/redacted view of richer native capture?
6. What **authoritative native basis** justifies the pack or shared example, and is that stronger basis still present?
7. Which **authority path** actually produced the pack (native replay, direct native bytes, copied native bytes, copied rendering, or summary-only), what fallback order was attempted, and what refusal posture blocks stronger reuse?
8. Can two sessions be diffed without pretending their schemas were identical?
9. Is this pack merely a historical retained artifact, current only as-of a named observation epoch, explicitly rechecked against a newer native basis, or already superseded?
10. If fields are omitted, decoder-unknown, privacy-sensitive, or basis-missing, can the pack retain them in a quarantine-first posture without laundering them into normal semantic truth?
11. Which pack is merely the latest operational head, which pack is the frozen shared head, and what warnings block a safe citation/public-example/current-active story?
12. Which execution receipt and lineage register explain how this artifact was produced from native imports or prior artifacts?
13. If two same-scope artifacts compete, can the kit preserve the contender set, precedence rule, unresolved residue, and blocked stronger-use posture without silently picking a winner?
14. Can downstream consumers import the pack without re-owning Cargo-native semantics?

If the kit cannot answer those questions, it is not yet doing its job.

## Fixture-backed artifact vocabulary and scenario corpus
The kit now has enough receipts, warning classes, and promotion gates that prose alone is no longer a safe review surface.

A serious `v0` should therefore freeze a small **fixture corpus** under `fixtures/cargo-report-pack-kit/` with:
- minimal schemas for the core receipts/pack surfaces;
- example JSON for each artifact family;
- named scenario folders for edge cases that repeatedly threaten to blur the seam back into prose;
- and review notes saying what each scenario does **not** justify.

The point is not to promise that Cargo’s unstable native bytes are already final.
The point is to freeze **our portable artifact meanings** so later revisions cannot quietly mutate trust semantics without touching examples.
That now also means freezing the **allowed class vocabulary** and the **review gates** that govern stronger reuse, not just the example bytes, and adding a small machine-check surface so those files cannot silently drift apart.

Initial scenario families should include at least:
- stable future-incompat imported from native replay with basis preserved;
- nightly build-analysis imported from direct native bytes but only promotable as a projected support bundle;
- basis-lost demotion where only projected/copied material remains;
- quarantined decoder-unknown or privacy-sensitive bytes where any later explanation stays on a distinct derived artifact;
- same-scope competing artifacts where native import and weaker summary/projection disagree and the kit must preserve a contradiction packet plus hold posture rather than mint a silent winner.

Review-completion rule:
if a Cargo Report Kit revision changes claim classes, authority-path classes, projection rules, quarantine classes, currentness classes, compatibility/drift classes, or frozen-head promotion rules, the matching schema/example/scenario files should change in the fixture corpus before the prose revision is treated as complete.



## Taxonomy-backed class register, scenario index, and review gates
The fixture corpus is necessary but not sufficient.
If `claim_class`, `authority_path`, `currentness_class`, `projection_class`, `quarantine_class`, `compatibility_class`, `target_posture`, and warning classes remain free-form strings, a later revision can still mutate the seam without touching the right examples.

The kit should therefore carry four small machine-readable control surfaces under `fixtures/cargo-report-pack-kit/`:
- `cargo-report-taxonomy.json` — the allowed class values for core receipt/pack fields;
- `cargo-report-scenario-index.json` — which named scenarios cover which classes and which stronger claims they intentionally block;
- `cargo-report-review-gates.json` — the fail-closed lifecycle gates for stronger share/current/frozen-head reuse;
- `cargo-report-hygiene-checks.json` — the machine-checked contract expectations that keep taxonomy, scenarios, gates, and example/schema pairs synchronized.

That is the key import from Goldenrule, Radical Governance, and GlassTTY: fixture-backed semantics need a **class register and gate surface**, not just example files, or future revisions quietly relabel trust semantics through new strings and half-updated examples.

Practical review rule:
if a revision adds a new class value or warning class, it is incomplete until the taxonomy, the affected schema enums, the matching examples, and the scenario index all move together.

## Machine-checked contract hygiene
The comparison set also made one more thing hard to ignore after the fixture/taxonomy pass: once portable meanings live in several JSON control surfaces, a future revision can still break the seam by changing one file and forgetting the rest.

The kit should therefore carry a tiny machine-check surface alongside the fixtures:
- `fixtures/cargo-report-pack-kit/cargo-report-hygiene-checks.json` — declares the contract checks, known control surfaces, required scenario directories, and any explicit example-to-schema overrides;
- `tools/check_cargo_report_pack_contract.py` — validates taxonomy/class usage, scenario-directory coverage, review-gate artifact refs, and example JSON against schemas;
- `tools/hygiene.py` — one entrypoint that runs the Cargo-report contract check as part of archive hygiene.

Suggested checks:
- revision-stamp coherence across the machine-readable control surfaces;
- scenario coverage values must exist in the taxonomy;
- review gates may only reference real schema-backed artifacts or declared control surfaces;
- every named scenario directory must exist and carry `notes.md`;
- every `*.example.json` file must validate against its declared schema before a revision touching Cargo Report Kit is treated as complete.

This is not busywork. It is the import from SlopOS, DeriveBSD, TriKEM, and Radical Governance that turns “frozen portable semantics” into **fail-closed archive hygiene** instead of a promise that still depends on reviewer memory.

Additional review rule:
if a revision allows two same-scope artifacts to coexist without one automatic winner, it is incomplete until the contradiction/arbitration classes, the blocked stronger-use gates, and at least one named competing-head scenario move in the same revision.

## Contradiction packets, arbitration witnesses, and competing heads
The comparison set exposed one more missing cut after basis/projection/quarantine/currentness/compatibility/waiver/lineage work:
**the kit still needed a first-class answer for same-scope competing report stories.**

Once the archive can retain:
- stable future-incompat replay imports,
- unstable build-analysis session/native-byte imports,
- copied native bytes or copied HTML renderings,
- projected support bundles,
- derived summaries,
- and promoted public/frozen heads,

reviewers still need one compact answer when two of those artifacts compete over the same package/session/coverage slice:
- which artifacts are actually in contention;
- whether the disagreement is source-versus-summary, competing operational heads, same-scope lane disagreement, or stronger current/public carry disagreement;
- which precedence or arbitration rule is allowed to choose automatically, if any;
- what unresolved residue remains even after precedence is applied;
- and which stronger uses stay blocked until manual review settles the conflict.

Without that, the archive has every ingredient for honest raw-evidence handling except one:
it still lets the prettier, later, or easier-to-quote artifact silently inherit winner status.

Suggested artifact:
- `cargo-report-contradiction-packet/v0` — compact record of contender refs, conflict scope, precedence/arbitration rule, unresolved residue, review-queue hold status, optional resolved winner ref, and blocked stronger-use surfaces.

Suggested precedence/arbitration classes:
- **native-basis-first** — native replay/direct-native import beats weaker copies or summaries when scope and epoch are otherwise aligned;
- **same-scope-native-over-derived** — same-scope summaries/explanations cannot outrank retained native evidence on their own;
- **newer-rechecked-over-historical** — only when the newer artifact actually names recheck/currentness basis;
- **manual-review-required** — when no automatic winner is justified;
- **no-automatic-winner** — when the archive must remain conflict-transparent and branch/hold rather than collapse.

Suggested hold/review posture:
- **pending-review** — disagreement preserved, no winner yet;
- **reviewed-hold** — a reviewer has examined the conflict and intentionally kept stronger reuse blocked;
- **resolved** — one winner or merge outcome is now justified by an explicit witness.

This is the clearest import from DelayBasin, Goldenrule, EvidenceVault, and VHK:
once several same-scope artifacts survive the earlier gates, the next durable seam is not “pick one.”
It is **preserve the contradiction, preserve the allowed arbitration rule, and fail closed on stronger head/current/public uses until the contradiction is actually settled.**


## Review requests, decision witnesses, review-separation receipts, and manual-review split truth
The comparison set exposed one more seam that still mattered after contradiction packets, waiver ledgers, and execution receipts:
**manual review should not collapse into a queue label or a later “approved” adjective.**

Once the archive can say that a pack is blocked by contradiction, waiver expiry, frozen-head carry, currentness carry, or compatibility drift, reviewers still need one compact answer to:
- what stronger use is actually being requested;
- what the safe sentence would be without that approval;
- which basis refs and gate ids were consulted;
- whether the request is still pending, held, resolved, or superseded;
- and what explicit decision witness cleared or refused the carry.

Without that split, `pending-review`, `resolved`, `approved-with-warning`, or “reviewed” become overloaded status words that hide the actual request and the actual basis consulted.

Suggested artifacts:
- `cargo-report-review-request/v0` — request id, request kind, subject refs, requested stronger use, consulted basis refs, required gate ids, safe-without-approval sentence, and current review-queue status.
- `cargo-report-decision-witness/v0` — witness id, request ref, reviewer, consulted basis refs, decision class, cleared blocks, remaining blocks, optional winning artifact ref, and expiry when the decision itself ages out.

Suggested request kinds:
- **promotion-carry** — asking to move from support bundle to stronger shared/public posture;
- **frozen-head-carry** — asking to let one artifact become the frozen shared head;
- **currentness-carry** — asking to let a retained artifact speak as current/rechecked-current;
- **compatibility-carry** — asking to let an unstable-derived artifact keep reviewed compatibility authority after drift;
- **contradiction-resolution** — asking to clear same-scope competing-head or source-versus-summary holds;
- **waiver-renewal** — asking to continue a previously temporary stronger exception.

Review-separation rule:
manual-review carry should also preserve one `cargo-report-review-separation-receipt/v0` saying who proposed the stronger use, who reviewed it, who executed or published it, whether that review cleared an independent checker, and what compensating control plus expiry applies when the same actor or same team carried too much of the flow.

Suggested review-separation classes:
- **independent-checker** — reviewer is meaningfully separate from requester and executor for this stronger carry;
- **cross-team-checker** — reviewer is on a different team/unit even if not fully external;
- **same-team-second-look** — a second look exists but independence is weaker and should not silently impersonate an independent checker;
- **self-review** — requester/reviewer/executor overlap enough that stronger carry should hold unless a compensating control is named explicitly.

Decision rule:
if stronger reuse depends on manual review, the archive should be able to point to one review request and one decision witness rather than treating `pending-review`, `resolved`, or `approved` as self-explaining state.

Head-guard rule:
manual-review carry must also stay bound to the exact head that was reviewed. A request should name an `expected_head_ref` plus `head_lineage_ref`; a decision witness should name the `reviewed_head_ref` and `head_guard_status`. If the lineage’s operational head changes before or after review, the old request/witness should surface `stale-head` / `reissue-required` rather than silently clearing the newer head.

Suggested head-guard statuses:
- **matched-head** — the reviewed head still matches the expected lineage tip for the requested carry;
- **stale-head** — the request or witness names a head that is no longer the current tip;
- **reissue-required** — stronger carry remains blocked until a new request or rereview is issued on the current head;
- **superseded-request** — the older request is retained historically but replaced by a newer head-scoped request.

This is the clearest import from pyCausalWeave, Goldenrule, VHK, EvidenceVault, Radical Governance, and DelayBasin:
**queue state, requested carry, approved basis, and exact reviewed head must remain distinct truths.**

## Execution receipts and derivation lineage
The comparison set exposed one more missing cut after authority/projection/quarantine/currentness/compatibility/waiver work:
**the kit needs a production-story spine, not just semantic classes.**

Once a nightly session becomes a projected support bundle, a quarantined-retained source, a derived summary, or a promoted shared head, reviewers still need one compact answer to:
- which operation produced the artifact,
- which tool / decoder / reviewer lane ran it,
- which parents were consumed,
- which outputs were emitted,
- and which head/supersession roles now follow from that lineage.

Without that, the archive can freeze the *meaning* of a pack while still leaving its production story in shell history, CI logs, or reviewer memory.

Suggested operation classes:
- **import-future-incompat** — stable report replay import;
- **import-session** — unstable build-analysis session/native-byte import;
- **pack** — bundle/import-index assembly;
- **projection** — local-private capture becomes a bounded portable/shared artifact;
- **quarantine** — retained source bytes are moved into or cleared from a quarantine posture;
- **promote** — a pack is moved toward support-bundle / issue-attachment / public-example / frozen-head use;
- **diff** — two packs are compared into a derived difference artifact;
- **explain** — human-readable review surface emitted from machine receipts;
- **derived-summary** — later prose/aggregate/normalized artifact emitted from prior source artifacts.

Suggested lineage roles:
- **native-import-root** — direct child of a Cargo-native replay or direct native bytes;
- **projected-child** — share-safe projection of richer native/local capture;
- **quarantined-source** — retained source artifact still blocked from stronger semantic/share reuse;
- **derived-child** — summary/normalization/explanation artifact that must not semantic back-write onto its parent;
- **promotion-surface** — artifact currently proposed or approved for stronger sharing;
- **superseded-head** — artifact replaced by a later operational/shared head for the same subject family.

Review rule:
if an artifact is projected, derived, quarantined, promoted, or used as a head, the kit should be able to point to one compact execution receipt and one lineage register entry rather than relying on prose to reconstruct how it came to exist.

## Core UX: `cargo reportpack`
### `cargo reportpack import-future-incompat`
Import stable future-incompat report output.

Should record:
- Cargo report ID;
- package filters, if any;
- Cargo/toolchain context when known;
- exact known scope versus unknown scope;
- coverage-slice posture (`single-report`, `selected-package-slice`, `workspace-default-members`, or `unknown` only when actually justified);
- whether the report was replayed from native storage or copied from prior export;
- fidelity notes for package scoping or textual sections;
- authoritative-basis metadata saying whether the replayed native report id is still available;
- authority-path metadata saying whether the import used native replay, copied-native bytes, or weaker fallback surfaces;
- quarantine posture saying whether any captured bytes are `capture-only` / `quarantined-retained` pending later review or projection;
- observation-epoch metadata and whether any current-active claim is out of bounds until rechecked.

### `cargo reportpack import-session --id <session>`
Import one unstable build-analysis session.

Should record:
- session ID;
- exact invocation scope when known (workspace root / selected packages / targets / profile / features / host-target tuple / command family);
- explicit coverage-slice posture describing what the session actually covered and what it definitely did not;
- native command family availability (`sessions`, `timings`, `rebuilds`);
- whether raw JSONL logs were present, copied, omitted, or only referenced;
- explicit unstable-lane marker;
- explicit local-private capture posture for paths, CLI args, env-derived values, or raw attachments that should not automatically become public artifacts;
- projection markers saying which fields stayed verbatim, which were hashed/coarsened, and which were omitted entirely;
- authoritative-basis metadata saying whether the pack still points back to the original Cargo log session or only to copied derivatives;
- authority-path metadata saying whether the import came from native replay, direct native bytes, copied native bytes, copied renderings, or summaries;
- quarantine posture saying whether risky/unknown/native-private bytes remain retained but blocked from normal summaries or sharing;
- observation-epoch metadata plus any known invalidation triggers for current-active claims.

### `cargo reportpack pack`
Bundle imported report truth for review.

Should include:
- session index;
- imported future-incompat reports;
- coverage-slice records and any partial-run warnings;
- imported timings and rebuild reports when available;
- native storage references or copied attachments;
- schema/version/lossiness markers;
- declared sharing posture (`local-review`, `support-bundle`, `issue-attachment`, `public-example`) plus a projection receipt covering omissions/redactions/hashing/coarsening when applicable;
- quarantine records describing whether some captured bytes remain `capture-only` / `quarantined-retained`;
- authoritative-basis records for each imported lane;
- authority-path / fallback-order / refusal-posture records for each imported lane;
- currentness records describing whether the bundle is historical-only, current-as-of, rechecked-current, or superseded.

### `cargo reportpack diff <packA> <packB>`
Compare two imported packs without hiding drift.

Should report:
- added/removed sessions;
- changed timing availability and changed rebuild explanations;
- changed field coverage, scope coverage, coverage-slice posture, or schema versions;
- missing-native-data versus actual semantic changes;
- changed share posture, projection receipt, copied-attachment posture, or quarantine posture when that affects what reviewers can see;
- changed authoritative-basis posture when later review depends on replay versus copied evidence;
- changed currentness posture when one pack becomes superseded, current-only-as-of, or freshly rechecked.

### `cargo reportpack promote <pack>`
Promote one portable pack into a bounded shared surface.

Should require:
- declared target posture (`support-bundle`, `issue-attachment`, `public-example`, or `hold` / `no-share`);
- declared claim class (`single-session`, `selected-slice`, `workspace-default-members`, `workspace-all-members`, `all-targets`, or stronger custom wording that must then justify itself explicitly);
- explicit authoritative-basis record;
- explicit authority-path / fallback-order / refusal-posture record;
- explicit currentness class (`historical-retained`, `current-as-of-observation`, `rechecked-against-newer-native-basis`, or `superseded`) with any stronger “current active” sentence failing closed unless justified;
- explicit unstable-field warnings when build-analysis data survives into the shared artifact;
- explicit quarantine clearance or retained-quarantine note when some native bytes must stay capture-only;
- projection / redaction / omission receipt when local-private capture is intentionally left behind or coarsened for sharing;
- a concise promotion receipt rather than silent folder motion.

### `cargo reportpack heads`
Render the small review surface that distinguishes:
- latest operational heads,
- quarantined-retained heads,
- frozen shared heads,
- superseded historical heads,
- and warnings that block one from standing in for another or from making stronger lane-wide/current-active claims than the native observation allows.

This is the smallest durable fix for the common failure mode where the latest imported pack gets treated as both the citeable example and the current workspace story even though it still depends on unstable fields, unknown scope, missing native basis, or an observation epoch that has not been rechecked.

### `cargo reportpack receipt <artifact>`
Render or emit one compact execution receipt.

Should explain:
- which operation class produced the artifact;
- which tool / decoder / reviewer lane performed it;
- which input refs and parent artifact refs were consumed;
- which outputs were emitted;
- whether the artifact is a native import, projected export, quarantined source, derived explanation, or promoted surface;
- and whether the receipt blocks stronger frozen/current/citation-like reuse because the artifact is only derived from weaker parents.

### `cargo reportpack lineage <artifact>`
Render or emit one compact lineage register slice.

Should explain:
- the artifact family / subject family;
- parent refs, child refs, and superseded/superseding refs;
- which artifacts are native-import roots versus projected children versus derived children;
- which artifact currently holds operational-head versus frozen-head role;
- and whether any later derived artifact is explicitly blocked from semantic back-writing onto its source.

### `cargo reportpack basis <pack>`
Render or emit one compact authority-path receipt.

Should explain:
- which native Cargo lane the artifact ultimately depends on;
- whether the chosen basis came from Cargo-native replay, direct native persisted bytes, copied native bytes, copied renderings, or summary-only/manual notes;
- what fallback order was attempted before the chosen path was accepted;
- whether the weaker path is acceptable only for local review, historical retention, bounded sharing, or stronger frozen/current/citation-like reuse;
- and when the tool must hold or fail closed instead of silently degrading the authority class.

### `cargo reportpack projection <pack>`
Render or emit one compact projection receipt.

Should explain:
- which native/local-private fields or attachments were preserved verbatim;
- which values were hashed, coarsened, normalized, summarized, or omitted;
- why each projection class was chosen (`privacy`, `path-sensitivity`, `portability`, `size`, `policy`, or `unknown`);
- whether the shared artifact is a full-fidelity copy, a bounded projection, or a summary-only derivative;
- whether omitted or decoder-unknown fields are explicitly non-inferable rather than negative evidence;
- and whether stronger frozen/current/citation-like reuse is blocked because the remaining bytes no longer match the richer native basis.

### `cargo reportpack quarantine <pack>`
Render or emit one compact quarantine receipt.

Should explain:
- whether any retained bytes are classified as `capture-only-local`, `quarantined-retained`, `review-cleared-local`, or `not-quarantined`;
- which conditions caused quarantine (`privacy-sensitive-native`, `decoder-unknown`, `basis-missing`, `projection-review-pending`, `unstable-meaning-review-pending`, or `manual-hold`);
- which uses stay blocked while quarantined (search snippets, summary-only explanations, frozen-head promotion, citation-like reuse, current-active wording, or downstream diagnosis imports);
- whether any later summary/normalization lives on a distinct derived artifact with explicit parent linkage;
- and what explicit review or clearance step is required before the source can leave quarantine.

### `cargo reportpack currentness <pack>`
Render or emit one compact currentness receipt.

Should explain:
- the observation epoch actually captured by the native basis when known;
- whether the pack is only **historical-retained**, **current-as-of-observation**, **rechecked-against-newer-native-basis**, or **superseded**;
- which changes would invalidate a stronger current-active claim (manifest/lockfile/toolchain/target/profile/feature basis changes, schema drift, or a newer native head);
- whether a later pack/head supersedes this one;
- and which warnings block “current workspace build truth” language even when the pack is still a valid historical artifact.

### `cargo reportpack compat <pack>`
Render or emit one compact import-compatibility receipt.

Should explain:
- which decoder/importer version interpreted each native lane;
- which Cargo/toolchain family and native schema family the import was reviewed against;
- whether later changes are classified as `same-reviewed-basis`, `compatible-drift-reviewed`, `material-drift-reimport-required`, `material-drift-rereview-required`, or `basis-missing`;
- which frozen/shared/current-active uses are still allowed under that class;
- and which warnings block stronger reuse until a newer native import or explicit review occurs.

### `cargo reportpack explain <pack>`
Render a human review surface that still preserves machine import facts.

Should explain:
- which native Cargo lane each report came from;
- which parts are stable versus unstable;
- which exact coverage slice was observed and which stronger claim classes remain out of bounds;
- which parts are local-private capture versus copied pack content versus declared shared surface versus frozen shared head;
- which parts are summaries rather than native payloads;
- which authoritative native basis still exists;
- which authority path actually produced the pack, what fallback order was attempted, and what refusal posture now limits stronger reuse;
- which bytes remain quarantined-retained or capture-only and therefore must not silently become normal semantic truth;
- which later summaries or normalized explanations are distinct derived artifacts rather than semantic back-writes onto the source;
- which observation epoch was actually captured and which currentness class now applies;
- which downstream consumer lanes are likely safe imports;
- and which warnings block public-example, citation-like, or current-active use.



## Execution receipts versus semantic classes
The kit should make one more discipline painfully explicit:
**an artifact class is not the same thing as a production story.**

A pack can be perfectly honest about authority path, projection, quarantine, currentness, compatibility, and waiver state and still leave reviewers unable to answer the simpler question “what exactly produced this artifact from which parents?”

Suggested fail-closed rule:
if a projected bundle, derived summary, or promoted head lacks an execution receipt and lineage link, then stronger frozen/current/citation-like reuse should hold even if the artifact’s semantic classes look otherwise plausible.

## Import compatibility versus upstream drift
The kit should make one third discipline painfully explicit:
**retained native evidence is not automatically the same thing as evidence whose interpretation is still reviewed after Cargo, the toolchain, or the importer changes.**

Suggested compatibility classes:
- **same-reviewed-basis** — same native lane family, same reviewed decoder/importer line, and no material Cargo/toolchain/schema drift relevant to the intended reuse;
- **compatible-drift-reviewed** — something changed, but the change was reviewed and the stronger reuse still remains justified at the requested claim/promotion level;
- **material-drift-reimport-required** — upstream/native change means the safer move is to regenerate the pack from a newer native basis before stronger reuse;
- **material-drift-rereview-required** — old bytes may still matter historically, but any frozen-head/current-active/citation-like reuse must stop until a reviewer checks the drift explicitly;
- **basis-missing** — the pack can no longer show enough native/decoder basis to justify compatibility claims.

Suggested material-change triggers:
- Cargo or toolchain version change that affects report commands, native field sets, or rendering posture;
- build-analysis storage/schema family change or changed command-family availability;
- importer/decoder normalization change that reclassifies fields, omissions, or lossiness;
- native-path/layout changes that break assumptions about replayable attachments or local references;
- any later finding that the old pack depended on unstable fields whose meaning was revised.

Suggested fail-closed rule:
if a frozen/shared/current-active artifact still depends on unstable build-analysis interpretation, then later Cargo/toolchain/importer drift should demote it to historical-only or drift-review-needed until an explicit compatibility receipt says the stronger reuse remains safe.

## Quarantine-first retained capture versus derived semantics
The kit should make one more discipline painfully explicit:
**retaining native bytes is not automatically the same thing as admitting those bytes into normal semantic/search/share truth.**

Suggested quarantine classes:
- **capture-only-local** — native bytes are retained only as local capture with no portable/share/search summary role yet;
- **quarantined-retained** — the pack may travel as a retained artifact, but stronger summary/search/current/public reuse stays blocked;
- **review-cleared-local** — a reviewer cleared local use, but the source still is not automatically a shared/frozen artifact;
- **not-quarantined** — no special quarantine posture remains on the retained source bytes.

Suggested quarantine triggers:
- privacy-sensitive local-native capture that has not yet been projected or redacted for sharing;
- decoder-unknown or schema-ambiguous fields whose meaning is not yet reviewed;
- basis-missing artifacts where only weaker copied/projected bytes remain;
- imported summaries or renderings whose stronger native parent is unavailable for review;
- manual hold decisions where the bytes should remain preserved but stronger interpretation or sharing would be misleading.

Suggested non-laundering rule:
if later tooling summarizes, OCRs, classifies, normalizes, or otherwise derives semantics from quarantined source bytes, the result should live on a distinct derived artifact with explicit parent linkage; it must not semantic back-write onto the quarantined source object or silently clear the source for stronger reuse.

Suggested non-inference rule:
omitted, redacted, decoder-unknown, or quarantine-blocked fields are not negative evidence. A later consumer should not infer “absent”, “safe”, “no path”, or “no secret-bearing value” merely because the shared or derived artifact omitted that field.

## Expiring waiver ledgers and stale-waiver demotion
The kit should make one additional discipline painfully explicit:
**temporary stronger exceptions are not normal semantics and should not live only in prose.**

Suggested waiver scope classes:
- **coverage-overclaim** — a reviewer allows a stronger lane-wide sentence than the observed coverage slice would normally permit;
- **projection-share** — a reviewer allows a projected/shared artifact to move to a stronger share posture than the default gates allow;
- **currentness-carry** — a reviewer temporarily carries current-active wording forward without a full recheck;
- **compatibility-carry** — a reviewer temporarily allows reuse across reviewed drift boundaries;
- **frozen-head-exception** — a reviewer temporarily allows a stronger shared-head role that would otherwise hold.

Suggested waiver status classes:
- **active** — still valid for the named stronger use until its expiry or supersession;
- **expired** — no longer valid; the stronger use should demote automatically;
- **superseded** — replaced by a newer waiver or a stronger real basis;
- **revoked** — explicitly cancelled before expiry.

Suggested fail-closed rule:
if a promotion/currentness/compatibility decision depends on a waiver, that waiver should live in a `cargo-report-waiver-ledger/v0` artifact with owner, reviewer, stronger requested use, weaker safe sentence, expiry, and status. Once the waiver is not `active`, the stronger use should demote rather than lingering by habit.

## Historical observation versus current active truth
The kit should make one second discipline painfully explicit:
**retained historical report identity is not automatically the same thing as current active build truth.**

Suggested currentness classes:
- **historical-retained** — the pack is a valid retained observation, but it makes no current-active claim beyond what was captured then;
- **current-as-of-observation** — the pack is being used as current only relative to its named observation epoch, with no claim about later workspace/toolchain change;
- **rechecked-against-newer-native-basis** — a later native replay/session/import was examined closely enough to justify carrying a current-active sentence forward;
- **superseded** — a later operational or shared head replaces this one for current review, even if this artifact still matters historically.

Suggested invalidation triggers:
- workspace manifest or lockfile changes;
- target/profile/feature-basis changes;
- toolchain or Cargo-version changes;
- later native report/session heads that materially overlap the same claim surface;
- schema or attachment loss that drops the basis below the requested claim strength.

Suggested fail-closed rule:
if a consumer wants to say “this is the current build state” or “this is the current compile-time posture,” a mere retained replay artifact should stop at **historical-retained** or **current-as-of-observation** unless a recheck receipt or explicitly bounded as-of sentence exists.

## Observed scope versus claimed coverage
The kit should make one discipline painfully explicit:
**what Cargo observed is not automatically the same thing as what a later pack, issue attachment, or shared example is allowed to claim.**

Suggested claim classes:
- **single-report** — only this stored report or replayed artifact is being claimed;
- **single-session** — only this exact build-analysis invocation is being claimed;
- **selected-package-slice** — only the explicitly selected packages / targets / features are being claimed;
- **workspace-default-members** — only justified when the pack can show that coverage really matches that Cargo selection basis;
- **workspace-all-members** — only justified when the pack can show that full workspace coverage really occurred;
- **all-targets** — only justified when the pack can show that target-family coverage really occurred;
- **manual-summary-only** — a review summary exists, but it must not pose as native lane-wide truth.

Suggested fail-closed rule:
if a shared artifact wants to say something stronger than the observed coverage slice proves, promotion should stop at `hold` unless a reviewer adds an explicit waiver that names the missing coverage and the weaker sentence that is still safe.

## Authorship buckets and visibility posture
The kit should make **field authorship**, **authoritative basis**, and **capture/share/promotion posture** first-class instead of implicit.

Suggested authorship buckets:
- **Cargo-authored** — report ids, replay metadata, session ids, command-family availability, Cargo-side storage references.
- **Tool-authored passthrough** — rustc/build-tool payload carried through Cargo-native logs or reports.
- **User/workspace-authored context** — package filters, target/profile selection, workspace path hints, command intent, operator-supplied notes.
- **Pack-authored annotations** — lossiness notes, projection/redaction notes, copied-versus-referenced markers, share-posture declarations, authoritative-basis notes, head warnings.
- **Consumer-derived** — build diagnoses, perf verdicts, issue summaries, support conclusions.

Suggested visibility posture:
- **local-private capture** — native `$CARGO_HOME/log/` state, raw paths, or copied raw attachments intended only for local/restricted review;
- **portable pack** — the bounded artifact meant to move between machines or CI systems;
- **shared surface** — the subset intentionally safe for issue/support circulation;
- **frozen shared head** — the specific shared artifact that is intentionally held up as the current reviewable example;
- **consumer conclusion** — later interpretations built on top of the pack.

Suggested authoritative-basis postures:
- **native-replayable** — the pack can still point to a Cargo-native report id or session log basis;
- **copied-native** — the pack copied the relevant native payload into itself and can still justify the import basis from those bytes;
- **derived-only** — only a rendering, projected subset, or summary survives; promotion should fail closed for stronger claims unless explicitly waived.

Suggested authority-path classes:
- **native-replay-command** — the import was produced by replaying a Cargo-native report/session handle through Cargo’s own command surface;
- **direct-native-bytes** — the import was produced from persisted native bytes/logs without requiring a copied derivative to stand in for them;
- **copied-native-bytes** — the pack copied the native payload into itself and now relies on those copied bytes;
- **copied-rendering** — the pack only has a generated HTML/JSON/text rendering rather than the stronger native basis;
- **summary-only** — only a summary/manual note survives.

Suggested fallback-order rule:
- prefer **native-replay-command** when available;
- otherwise prefer **direct-native-bytes**;
- otherwise allow **copied-native-bytes** for bounded historical/share uses;
- treat **copied-rendering** and **summary-only** as weaker classes that must not silently inherit replayable authority.

Suggested refusal-posture classes:
- **hard-hold** — no stronger share/current/citation-like reuse is allowed from this authority path;
- **historical-only** — retainable and explainable, but not promotable to stronger active/public roles;
- **local-review-only** — enough for local/operator inspection but not for portable sharing;
- **bounded-share-with-warning** — allowed for support/issue circulation with explicit warnings;
- **explicit-waiver-required** — stronger reuse needs a named reviewer waiver that acknowledges the weaker path.

Suggested fail-closed rule:
if a consumer asks for frozen-head, citation-like, or current-active reuse and the strongest reviewed authority path is missing, the tool should emit a hold/refusal posture rather than silently falling back from native replay to copied renderings or summaries.


## Projection receipts and basis-loss discipline
The kit should make one additional discipline painfully explicit:
**a portable/shared artifact is often only a projection of richer native local capture, and later basis loss should demote authority instead of being silently ignored.**

Suggested projection classes:
- **verbatim-kept** — native/local value or attachment is preserved as-is in the pack;
- **hashed-or-tokenized** — the value is retained only through a stable digest/token placeholder;
- **coarsened** — the value remains but with less precision or less identifying detail;
- **omitted** — the field/attachment was intentionally left out;
- **summary-derived** — only a prose or aggregate summary remains.

Suggested projection reasons:
- **privacy** — field could expose operator-local or sensitive information;
- **path-sensitivity** — absolute/local paths or host-specific identifiers should not circulate unchanged;
- **portability** — field is too machine-local to pretend it moves cleanly;
- **size** — raw attachment is too large for the chosen shared posture;
- **policy** — local policy forbids carrying the raw value forward;
- **unknown** — projection exists but the reason was not recorded.

Suggested fail-closed rules:
- if a shared artifact drops or coarsens fields that materially affect later review, the pack should carry a projection receipt instead of pretending the visible bytes are the whole native capture;
- imported distribution labels or issue-tracker context must not silently widen or relax local redaction policy;
- if the stronger replayable/native basis later disappears, a previously stronger artifact should demote to copied-native / projected / historical-only posture rather than quietly keeping replay-grade authority.

## Shared artifacts

### `cargo-report-coverage-slice/v0`
Compact statement of what native observation actually covered.

Fields should include:
- source lane (`future-incompat`, `build-analysis-session`, `timings-replay`, `rebuilds-replay`);
- selected package basis (`current-package`, `default-members`, `workspace`, explicit package list, or unknown);
- target basis (`default-targets`, explicit target flags, `all-targets`, or unknown);
- feature basis (`default-features`, explicit feature list, `all-features`, `no-default-features`, or unknown);
- profile / command family / host-target tuple when known;
- completion posture (`completed`, `partial-failure`, `aborted`, `replay-only`, or `unknown`);
- known omissions and unresolved coverage gaps;
- whether stronger workspace-lane claims are blocked.

### `cargo-report-projection-receipt/v0`
Compact record of how richer native capture became a portable/shared artifact.

Fields should include:
- linked pack/head id;
- source lane and authority-path linkage;
- per-field or per-attachment projection class (`verbatim-kept`, `hashed-or-tokenized`, `coarsened`, `omitted`, `summary-derived`);
- projection reason (`privacy`, `path-sensitivity`, `portability`, `size`, `policy`, `unknown`);
- whether the stronger native/local basis still exists;
- whether the projection blocks stronger frozen/current/citation-like reuse;
- notes when imported share labels did not change local redaction authority.

### `cargo-report-currentness/v0`
Compact record of what kind of presentness a pack is honestly allowed to claim.

Fields should include:
- linked pack/head id;
- observation epoch (`captured-at`, `replayed-at`, or `unknown-but-not-current`);
- currentness class (`historical-retained`, `current-as-of-observation`, `rechecked-against-newer-native-basis`, `superseded`);
- invalidation triggers still in force;
- linked newer pack/head when superseded;
- warnings that block current-active wording;
- whether the currentness judgment depends on replayable native basis, copied-native basis, or derived-only material.

### `cargo-report-import-compat/v0`
Compact record of whether an imported pack is still reviewed against current Cargo/importer reality.

Fields should include:
- linked pack/head id;
- source lane family and whether it was stable or unstable;
- decoder/importer id and version;
- reviewed Cargo/toolchain family and native schema family when known;
- compatibility class (`same-reviewed-basis`, `compatible-drift-reviewed`, `material-drift-reimport-required`, `material-drift-rereview-required`, `basis-missing`);
- material-change triggers that were checked or are still unresolved;
- strongest still-allowed reuse posture (`historical-only`, `shared-with-warning`, `frozen-head-allowed`, `current-active-blocked`, etc.);
- review receipt / waiver refs when drift was explicitly reviewed.

### `cargo-report-waiver-ledger/v0`
Compact ledger of temporary stronger-use exceptions.

Fields should include:
- linked pack / promotion / currentness / compat artifact refs;
- waiver entries with `waiver_id`, `scope_class`, `stronger_requested_use`, and `weaker_safe_sentence`;
- owner / reviewer identity and decision timestamp;
- `status` (`active`, `expired`, `superseded`, `revoked`);
- expiry timestamp or superseding waiver ref;
- automatic blocked/demoted uses once the waiver is no longer active.


### `cargo-report-execution-receipt/v0`
Compact record of how one Cargo Report Kit artifact was produced.

Fields should include:
- `receipt_id` and operation class;
- producer tool / decoder / reviewer identity and version when known;
- input refs and parent artifact refs;
- output refs;
- lane family and whether the result is native import, projected child, quarantined source, derived child, or promotion surface;
- notes when the production story depends on copied/projected/weaker parents;
- and warnings that block stronger reuse.

### `cargo-report-lineage-register/v0`
Compact register of artifact parentage, supersession, and head roles.

Fields should include:
- subject family / lineage id;
- artifact refs with role (`native-import-root`, `projected-child`, `quarantined-source`, `derived-child`, `promotion-surface`, `superseded-head`);
- parent / child refs;
- produced-by execution receipt refs;
- superseded / superseding refs when present;
- operational-head ref and frozen-head ref when present;
- no-semantic-backwrite flags for derived children.

### `cargo-report-session-index/v0`
Index of imported native report sessions.

Fields should include:
- imported lane family (`future-incompat`, `build-analysis`);
- stable/unstable posture;
- session ID or report ID;
- Cargo version / rustc version when known;
- exact invocation/report scope when known;
- linked coverage-slice id;
- native storage provenance;
- capture visibility (`local-private`, `copied-into-pack`, `reference-only`);
- available attachments and missing pieces;
- authoritative-basis posture.

### `cargo-report-authority-basis/v0`
Compact record of what native evidence authorizes an import or shared artifact.

Fields should include:
- linked report/session ids;
- native source family (`future-incompat-replay`, `build-analysis-jsonl`, `timings-replay`, `rebuilds-replay`);
- whether the basis is replayable, copied, or derived-only;
- authority path (`native-replay-command`, `direct-native-bytes`, `copied-native-bytes`, `copied-rendering`, `summary-only`);
- fallback-order trace and refusal posture for stronger reuse;
- whether the native basis is still locally available;
- lossiness notes when only copied or derived material survives;
- promotion-blocking flags when the basis is insufficient for a frozen shared example.

### `future-incompat-import/v0`
Portable import of stable future-incompat report data.

Fields should include:
- native report ID;
- package scope and any omitted/unknown scope notes;
- Cargo-authored findings and report metadata;
- replay provenance;
- lossiness notes for textual or omitted sections;
- authorship markers distinguishing Cargo replay facts from pack-authored summaries;
- authoritative-basis linkage;
- authority-path linkage when the import relied on copied or weaker fallback material.

### `timings-report/v0`
Normalized import of timing data from a build-analysis session.

Fields should include:
- session linkage;
- exact known invocation scope;
- native timings availability;
- per-unit timing data when available;
- totals / critical-path-like summaries when available;
- replay/copy posture;
- field-authorship markers for Cargo/native payload versus pack-authored summaries;
- missing-field markers;
- authoritative-basis linkage;
- authority-path linkage when the import relied on copied or weaker fallback material.

### `rebuild-report/v0`
Normalized import of rebuild reasons from a build-analysis session.

Fields should include:
- session linkage;
- exact known invocation scope;
- rebuilt/fresh unit identity;
- reason codes or native dirty reasons;
- dependency-chain or upstream-cause linkage when available;
- explanation-fidelity notes;
- field-authorship markers;
- authority-path linkage when the import relied on replay versus copied renderings or summaries;
- authoritative-basis linkage.

### `cargo-report-pack/v0`
Portable bundle combining the above, including linked currentness records when present.

Should include:
- manifest metadata;
- session index;
- imported report files;
- copied native attachments when needed;
- checksums;
- stability, visibility, and lossiness declarations;
- declared share posture and any required redactions/omissions;
- authoritative-basis records;
- execution-receipt and lineage-register refs;
- consumer-support notes describing which downstream lanes were intentionally kept out of scope.

### `cargo-report-promotion-receipt/v0`
Written decision about how one pack is allowed to move.

Should include:
- target posture (`hold`, `support-bundle`, `issue-attachment`, `public-example`);
- linked pack id;
- declared claim class and whether it exceeds the observed coverage slice;
- authoritative-basis status;
- unstable-lane warnings;
- required redactions/omissions;
- decision owner and rationale;
- produced-by execution receipt ref;
- lineage-register ref when the result changes head roles;
- whether the result becomes a frozen shared head.

### `cargo-report-pack-heads/v0`
Tiny register of current operational heads versus frozen shared heads.

Should include:
- lineage id or subject family;
- latest operational pack id;
- frozen shared head id, if any;
- warnings such as `unstable-fields-present`, `native-basis-missing`, `scope-partial`, `coverage-claim-exceeds-observation`, `workspace-lane-unproven`, `target-family-unproven`, `not-frozen`, or `branch-ambiguous`;
- whether the shared head is safe for support-only or public-example use.

## Design principles
1. **Native import comes before normalization.** Preserve Cargo-native semantics before adding summaries.
2. **Stable and unstable lanes must stay explicit.** Do not let build-analysis imports masquerade as stable Cargo contracts.
3. **Projected shared bytes are not the same thing as full native capture.** Do not let omitted, hashed, coarsened, or summarized fields quietly disappear from the review story.
3. **Subject scope must stay exact.** Do not infer package/target/profile/feature/workspace scope from filenames, html titles, or downstream guesses when the import does not actually know.
4. **Observed scope and claimed coverage are different facts.** A pack can be useful locally before it is allowed to say “workspace-wide” or “all-target” anything.
5. **Field authorship matters.** Cargo-authored facts, tool-authored passthrough, user/workspace context, pack-authored notes, and consumer conclusions must not silently collapse into one fake canonical record.
6. **Private capture, portable pack, shared surface, and frozen shared head are different facts.** Local build-analysis logs are not automatically portable or public-safe just because they were imported once.
7. **Replay and copy are different facts.** Re-rendering from native storage is not the same thing as copying raw attachments into a pack.
8. **Authoritative basis comes before promotion.** A frozen shared example should say exactly which native basis authorizes it, or fail closed.
9. **Operational heads and citation-like heads must stay distinct.** The latest imported pack can be operationally useful before it is the right shared example.
10. **Production story is first-class.** Projected bundles, derived summaries, and promoted heads should carry compact execution receipts and lineage links instead of relying on shell history or reviewer memory.
11. **Warnings are first-class review output.** `unstable`, `scope-partial`, `basis-derived-only`, `not-frozen`, and `lineage-missing` should be visible states, not embarrassing footnotes.
12. **Downstream consumers import, they do not overwrite.** Build, perf, debug, and support layers can summarize imported report truth, but they must not silently redefine it.

## Success bar
- one pack can preserve stable and unstable Cargo report lanes honestly;
- the pack can keep exact session/report scope and observed coverage slices visible enough to avoid folklore comparisons;
- no single imported session or replayed report can silently widen into workspace-wide or all-target truth without an explicit proven claim class;
- every shared artifact carries an explicit authoritative-basis posture;
- CI can diff packs without requiring access to the original `$CARGO_HOME/log/` state;
- issue/support sharing can admit omissions instead of silently leaking or silently inventing coverage;
- frozen shared examples can carry explicit unstable/head warnings instead of pretending to be stable contracts;
- downstream build/perf/debug layers can import the pack without redefining Cargo-native truth;
- projected or derived artifacts can always point to a compact produced-by receipt and lineage chain before they are used as support bundles, public examples, or frozen heads.

## Non-goals
- replacing Cargo’s own report commands;
- turning report packs into one giant dashboard format;
- silently stabilizing Cargo-internal schemas by accident;
- treating local-private build-analysis capture as automatically public-safe;
- letting the latest imported pack silently become the citeable public example;
- or letting one narrow observation silently masquerade as workspace-wide, all-target, or all-feature truth;
- absorbing diagnosis, benchmarking, or debugger semantics into the report layer.
