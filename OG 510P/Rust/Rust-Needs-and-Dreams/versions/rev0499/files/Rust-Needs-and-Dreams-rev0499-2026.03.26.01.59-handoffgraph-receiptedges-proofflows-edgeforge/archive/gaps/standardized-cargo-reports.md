# Gap: Standardized Cargo Reports (Authority Paths, Exact Coverage, Quarantine, Projection Receipts, Execution Receipts, Lineage Registers, Currentness, Contract Hygiene, Waiver Ledgers, Review Requests, Decision Witnesses, Review-Separation Receipts, Portable Packs, and Frozen Shared Heads)

## Summary
Cargo now has a real **report family**, but not yet a portable ecosystem contract above it.

That family is already split across two distinct lanes:
- a **stable** `cargo report future-incompat` lane, where Cargo stores and replays future-incompatibility findings;
- an **unstable** `-Zbuild-analysis` lane, where Cargo records JSONL session logs under `$CARGO_HOME/log/` and exposes `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`.

That is meaningful progress.
It means Cargo is no longer only a stream of one-shot terminal output.
But it still leaves a gap for the rest of the ecosystem:
- report identity is still too tied to Cargo’s native storage and unstable formats,
- the same seeming review surface can arrive through replayable report ids, direct native session bytes, copied native bytes, copied HTML renderings, or summary-only derivatives without a shared authority-path story,
- session scope is still too easy to blur across workspace/package/target/profile/feature/toolchain/invocation boundaries,
- one imported session can still too easily widen into a stronger workspace-lane or all-target claim than the native observation actually covered,
- build-analysis capture is intentionally opt-in and still constrained by privacy/performance/stability concerns,
- CI and review systems still lack a small portable bundle for past sessions,
- downstream tools still lack a clean split between **authoritative native basis**, **portable pack**, **shared surface**, **frozen shared example**, and **consumer conclusions**,
- shared packs still lack one compact way to say whether CLI args, env-derived values, local paths, raw payload sections, or whole native attachments were preserved, hashed, coarsened, omitted, or left behind as local-private capture,
- retained imports still lack a quarantine-first posture for bytes that are historically useful but not yet safe to summarize, search, or share normally,
- later summaries/normalizations still lack a clean derived-artifact boundary instead of semantic back-writing onto a risky retained source,
- the archive still lacks a small **schema/example/scenario corpus** that freezes what authority-path, projection, quarantine, currentness, compatibility, and promotion receipts actually mean,
- the archive still lacks a small **machine-checked contract-hygiene surface** that proves those frozen files still agree about class values, scenario coverage, gate references, and example validity,
- and the ecosystem still lacks a compact way to say whether one retained report artifact is merely historical, current only as-of a named observation epoch, explicitly rechecked against a newer native basis, already superseded by a later head, or demoted because that stronger native basis later disappeared,
- while projected packs, derived summaries, and promoted shared heads still lack a durable **execution receipt + lineage register** saying which operation produced them from which parents and which stronger roles remain blocked because that lineage is weaker than the native source.

The missing contribution is therefore **not** another dashboard or another log scraper.
It is a thin report-truth layer above Cargo’s native report lanes and below build/perf/debug consumers, plus a small fixture-backed artifact spine that freezes the portable meanings of its receipts and warning classes. The comparison set also makes one more refinement worth importing here: once fixtures exist, the kit still needs a **taxonomy-backed class register, scenario-coverage index, machine-readable review gates, machine-checked contract hygiene, and expiring waiver ledgers** so those meanings and their temporary exceptions cannot drift through free-form strings, stale fixture files, sticky reviewer memory, or incomplete promotion logic.

## Ecosystem signals
- The Cargo Book documents `cargo report` today and says the stable command currently supports `future-incompat` reports.
  https://doc.rust-lang.org/cargo/commands/cargo-report.html
- The future-incompat chapter says Cargo stores report IDs and lets users replay a full report later with `cargo report future-incompatibilities --id ID`.
  https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
- Cargo’s unstable-features docs now describe `-Zbuild-analysis`: build metrics are persisted on disk, Cargo writes JSONL logs to `$CARGO_HOME/log/`, each invocation gets a unique session ID, and `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds` query those past sessions.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The Cargo 1.94 development-cycle update says the work is actively adding missing `cargo report timings` features, `cargo report rebuild`, `cargo report sessions`, man pages for `cargo report *`, and removing the older unstable `--timings=FMT` because `cargo report timings` supersedes it.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The Cargo build-analysis project goal says the purpose is to record build metadata across invocations, preserve timing and rebuild information, enable external tooling, keep collection opt-in, avoid privacy/performance regressions, and offer **no user-facing stability guarantees during the prototyping phase**.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

## What is still missing
### 1. Stable-vs-unstable lane honesty
A report consumer should be able to tell whether it imported:
- stable future-incompat output,
- unstable build-analysis session output,
- or a mixed pack.

Without that, downstream tools will overclaim compatibility.

### 2. Exact session/report scope and claim coverage
A portable report bundle still needs a disciplined way to say:
- which Cargo invocation or stored report it came from,
- which workspace/package filters/targets/profiles/features/toolchains were actually in scope,
- which command family was run,
- which parts of that scope are known versus absent,
- and whether a later shared artifact is only claiming `single-session` / `selected-slice` truth or trying to say something stronger like `workspace-default-members`, `workspace-all-members`, or `all-targets`.

Without that, later comparisons turn into cargo-folklore archaeology and later promotion turns one narrow observation into a fake lane-wide statement.

### 2.5 Coverage slices and partial-run honesty
A pack also needs one compact way to say:
- what Cargo actually attempted to build or replay,
- what actually completed versus failed/aborted/omitted,
- whether `--keep-going`, package filters, or target-selection flags mean the artifact is only a selected slice,
- and whether a later sentence is merely a local review summary or a promoted shared claim.

Without that, one successful package, one replayable HTML timings surface, or one partial session can silently pose as “the workspace result.”

### 3. Field authorship and trust buckets
Cargo-native report families already mix different kinds of facts:
- Cargo-authored ids and replay metadata,
- rustc- or tool-authored payload carried through Cargo,
- user/workspace-authored invocation context,
- pack-author annotations,
- and downstream summaries.

The ecosystem still lacks one compact way to keep those authorship classes visible inside a portable import layer.

### 4. Authoritative native basis
A pack still needs one explicit answer to:
- which native Cargo surface is the authoritative basis for this import,
- whether the pack was replayed from Cargo-owned storage or reconstructed from copied HTML / copied JSON / issue attachments,
- whether the native basis is still available for re-review,
- and whether promotion should fail closed when the only surviving artifact is a derived rendering.

Without that, later consumers will cite copied renderings and pack summaries as if they were equivalent to Cargo-native evidence.

### 4.5 Authority path, fallback order, and refusal posture
A pack also needs one compact way to say:
- whether the import came from **Cargo-native replay**, **direct native persisted bytes**, **copied native bytes**, **copied renderings**, or **summary-only/manual notes**;
- what fallback order was attempted before the chosen import path was accepted;
- whether a weaker fallback was accepted only for local review, historical retention, or bounded sharing;
- and when promotion/current-active/citation-like reuse must fail closed or hold because the stronger authority path was unavailable.

Without that, a copied timings HTML file or summary note can silently inherit the authority of a replayable native session even when the stronger path was absent.

### 5. Native-capture versus portable-pack versus shared-surface versus frozen-example truth
A tool that imports Cargo-native report data should not pretend that:
- machine-private `$CARGO_HOME/log/` capture,
- a portable review pack,
- a redacted issue/support attachment,
- and a frozen shared example meant to be referenced later

are all the same artifact.
The archive needs a clean distinction between:
- native Cargo storage references,
- copied raw attachments,
- normalized portable summaries,
- declared sharing posture,
- frozen shared examples,
- and later build/perf/debug conclusions.


### 5.5 Projection receipts, omission packets, and share-safe redaction discipline
A portable/shared pack still needs one compact way to say:
- which local-private fields or attachments were preserved verbatim,
- which values were hashed, coarsened, summarized, or replaced with stable placeholders,
- which fields were intentionally omitted for privacy, path sensitivity, or portability reasons,
- whether the shared artifact is a projection of native capture or a full-fidelity retained copy,
- and whether imported distribution labels or downstream sharing context changed what may be shared without silently becoming redaction authority.

Without that, a support bundle, issue attachment, or public example can silently look like "the report" even when it is only one filtered projection of native local capture.

### 5.6 Retained-basis loss posture
A pack also needs one compact way to say:
- whether the stronger replayable/native basis is still present locally,
- whether the pack now depends only on copied projected material because the original native basis was deleted, rotated away, or never retained,
- and which stronger shared/current/citation-like uses must demote once the underlying native basis is gone.

Without that, a historically useful pack can silently keep replay-grade authority long after the native review basis has disappeared.

### 5.7 Quarantine-first retained capture and derived-truth non-laundering
A pack also needs one compact way to say:
- whether some retained bytes are only `capture-only-local` or `quarantined-retained`,
- which conditions caused that posture (privacy-sensitive native capture, decoder-unknown fields, basis-missing weaker copies, projection review pending, or manual hold),
- which uses stay blocked while quarantined (search snippets, summaries, consumer diagnosis imports, frozen-head promotion, citation-like reuse, current-active wording),
- and whether any later OCR/summary/normalization lives on a separate derived artifact rather than semantic back-writing onto the quarantined source.

Without that, the archive is forced into a bad binary: either delete historically useful but risky/unstable bytes, or quietly let them enter normal semantic truth just because a later tool derived a convenient explanation from them.

### 5.8 Omission / decoder-unknown non-inference
A pack also needs one compact way to say:
- that omitted, redacted, decoder-unknown, or quarantine-blocked fields are **not negative evidence**,
- that a shared or derived artifact omitting a field does not imply “absent”, “safe”, “no path”, or “no secret-bearing value”,
- and that later consumer layers must not turn filtered visibility into a stronger claim than the retained source actually justified.

Without that, every privacy filter, schema gap, or review hold quietly turns into fake certainty.

### 6. Promotion gates, currentness classes, and head warnings
Once packs can move, the ecosystem still lacks one compact way to say:
- which imported pack is merely the latest operational head,
- which pack (if any) has been promoted to a frozen shared head,
- whether the frozen head still depends on unstable build-analysis fields,
- whether the pack is only a historical retained artifact, current only as-of a named observation epoch, explicitly rechecked against a newer native basis, or already superseded,
- and which warnings block citation-grade, public-example, or current-active use.

Without that, the latest imported pack will silently masquerade as both the stable shared example and the current workspace story.

### 7. Current-active truth versus retained history
Cargo’s native report surfaces are inherently historical:
- future-incompat reports are stored and replayed later by report id,
- build-analysis sessions are persisted and queried as previous sessions,
- and copied HTML/JSON attachments can outlive the local run that produced them.

A portable report layer therefore still needs one compact way to say:
- what observation epoch was actually captured,
- what changes would invalidate a current-active claim (toolchain, manifest, lockfile, target/profile/feature basis, or later native head),
- whether a newer native basis has been checked,
- and whether this pack is now superseded by a later imported head.

Without that, one old report will keep posing as “current build truth” long after the workspace or toolchain has moved.

### 8. Cross-session diffability
Cargo is beginning to make past sessions queryable, but the ecosystem still lacks a reusable contract for:
- compare two sessions,
- classify missing fields or schema drift,
- preserve unstable-field lossiness,
- and hand the result to build/debug/perf consumers.

### 8.5 Import compatibility and material-change drift discipline
Cargo’s build-analysis goal explicitly leaves room for schema evolution during prototyping, the unstable docs document JSONL session logs and replay commands rather than a frozen external schema, and nearby Cargo work keeps moving report commands and adjacent filesystem/layout behavior. A portable report layer therefore still needs one compact way to say:
- which decoder/importer version interpreted the native evidence,
- which Cargo/toolchain family and native schema family were actually reviewed,
- whether later changes are still compatible, require explicit review, or require re-import from a newer native basis,
- and which promoted/shared/current-active uses are blocked until that drift is handled.

Without that, one unstable-derived pack can silently keep the authority of a newer Cargo nightly, a changed build-analysis storage family, or a changed importer even when the old interpretation is no longer reviewed.



### 8.6 Taxonomy-backed class registers and scenario coverage
The fixture corpus is a big improvement, but it still leaves a gap if key receipt fields remain free-form strings. A portable report layer therefore still needs one compact way to say:
- which class values are actually allowed for lanes, claim classes, authority paths, projection classes, quarantine triggers, currentness classes, compatibility classes, promotion targets, and warning classes;
- which named scenarios cover which classes and which stronger claims they intentionally block;
- and which review gates must clear before a pack may become a support bundle, public example, frozen head, or current-active statement.

Without that, a future revision can quietly mint a new class value or relabel an old one in prose only, and the fixture corpus stops being a reliable semantic guardrail.

### 8.7 Expiring waiver ledgers and stale-waiver demotion
The fixture-backed artifact spine is still incomplete if stronger exceptions remain prose-only. A portable report layer therefore still needs one compact way to say:
- which stronger requested use depended on a waiver (`public-example`, `frozen-public-head`, stronger lane-wide claim, current-active carry, compatibility carry, or other bounded exception);
- what the weaker safe sentence would have been without the waiver;
- who owned and reviewed the exception;
- when the waiver expires, becomes superseded, or is revoked;
- and which demotions or blocked uses automatically reappear once that waiver is no longer active.

Without that, every “explicit waiver required” clause quietly becomes a hidden permanent privilege.

### 8.8 Contradiction packets, arbitration witnesses, and competing-head holds
A portable report layer also still needs one compact way to say:
- that two same-scope artifacts are genuinely in contention rather than one simply superseding the other;
- which contender refs are involved (native import, copied rendering, projected bundle, derived summary, promoted head);
- which precedence or arbitration rule is allowed to choose automatically, if any;
- what unresolved residue remains even after precedence is applied;
- what the review-queue status is (`pending-review`, `reviewed-hold`, or `resolved`);
- and which stronger uses stay blocked while the disagreement remains live.

Without that, the latest, prettiest, or easiest-to-quote artifact will silently become the winner even when the stronger native basis or the actual review state does not justify that collapse.


### 8.9 Machine-checked contract hygiene and drift locks
A portable report layer also still needs one compact way to say:
- which control surfaces (`cargo-report-taxonomy`, `cargo-report-scenario-index`, `cargo-report-review-gates`, `cargo-report-hygiene-checks`) define the frozen portable meanings and completion gates;
- which machine checks verify that schema enums still match the taxonomy, scenario coverage still uses registered class values, review gates still reference real artifact families, and example JSON still validates against the intended schemas;
- which scenario directories and required notes/example files must remain present for the named edge cases the archive depends on;
- and when a revision that changes those surfaces is still incomplete because the contract check has not yet passed.

Without that, fixture-backed semantics still drift in practice: the archive can freeze class meanings in files while letting later revisions quietly rename a value, delete a scenario, point a gate at a nonexistent artifact, or ship an example that no longer validates.

### 9. Bounded consumer handoffs
Build-state review, compile-time perf review, debugger/session triage, issue attachments, and support bundles all want the same Cargo-native report facts.
The report boundary should export them once rather than letting each consumer invent its own half-compatible import layer.

## What “good” looks like
- a CI system can attach one small `cargo-report-pack/v0` bundle instead of preserving Cargo home state forever;
- a maintainer can see exactly which parts of a pack came from stable `future-incompat` reports and which parts came from unstable build-analysis sessions;
- the pack records exact session/report scope and exact coverage slices instead of forcing reviewers to guess workspace/target/profile/feature boundaries from filenames or prose;
- one imported session cannot silently pose as workspace-wide or all-target truth unless the pack can prove that wider coverage or explicitly mark the stronger sentence as out of bounds;
- field authorship stays visible enough that Cargo-authored facts, pack-authored notes, and downstream summaries do not get blurred together;
- every shared or frozen artifact declares both its authoritative native basis and the weaker-or-stronger authority path that actually produced it, or admits that the stronger path is missing;
- every shared or frozen artifact carries a projection receipt when local-private capture was filtered, hashed, coarsened, or omitted rather than pretending the shared bytes are the whole native capture;
- quarantined-retained imports can remain preserved without silently becoming snippet/search/summary/public truth;
- omission, redaction, and decoder-unknown posture remain explicitly non-inferable rather than fake absence claims;
- later summaries or normalized explanations stay on distinct derived artifacts instead of semantic back-writing onto quarantined source bytes;
- basis-loss demotion remains visible when the stronger native path later disappears;
- the latest operational pack can remain distinct from the current frozen shared head;
- historical retained packs, current-as-of packs, rechecked-current packs, and superseded packs remain distinguishable instead of collapsing into one fake “latest” story;
- unstable-lane frozen examples carry explicit warnings instead of silently posing as stable public contracts;
- any stronger exception relies on an explicit waiver ledger with owner/reviewer identity, expiry, and stale-waiver demotion instead of a sticky comment;
- any revision that changes taxonomy/schema/scenario/gate surfaces is incomplete until the contract-hygiene checks pass and prove those files still agree;
- a downstream consumer can admit partial support instead of faking full fidelity;
- same-scope competing artifacts can stay explicit through a contradiction packet instead of being flattened into one silent winner;
- operational heads can branch without automatically becoming frozen/public/current heads;
- hold/review status is visible when consulted disagreement remains unresolved;
- and build/perf/debug layers can import report truth without silently redefining it or treating local-private capture as automatically public-safe.

### 11.5 Execution receipts and lineage registers
The missing shared artifacts should also include:
- `cargo-report-execution-receipt/v0` — compact production receipt for one import/pack/projection/quarantine/promote/diff/explain/derived-summary operation;
- `cargo-report-lineage-register/v0` — compact parent/child/supersession/head-role register linking native imports, projected packs, derived summaries, and promoted shared surfaces.

These are not generic build provenance blobs. They are the narrow review surfaces that keep Cargo Report Kit from losing production truth as soon as artifacts start moving between local-private capture, projected bundles, quarantined source retention, derived summaries, and frozen public heads.



### 8.9 Review requests, decision witnesses, review-separation receipts, and manual-review split truth
The fixture-backed artifact spine is still incomplete if manual-review carries remain folded into one status word. A portable report layer therefore still needs one compact way to say:
- what stronger use is actually being requested (`public-example`, `frozen-public-head`, current-active carry, compatibility carry, contradiction resolution, waiver renewal, or other bounded exception);
- what the safe sentence would be without approval;
- which pack refs, contradiction packets, waiver entries, and basis refs were actually consulted;
- who proposed the stronger carry, who reviewed it, who executed or published it, and whether that review cleared an independent checker or only a weaker same-team/self-review lane;
- which compensating control plus expiry exists when full separation is impractical;
- which exact head the request expected to still be current;
- whether that expected head still matches the lineage tip or has gone stale;
- whether the item is merely queued, intentionally held, resolved, or superseded;
- and what explicit decision witness cleared or refused the requested carry.

Without that, `pending-review`, `resolved`, “approved-with-warning”, or “reviewed” become fake summary states that hide both the request and the basis/head that was actually consulted, while requester-authored approval can still impersonate independent review.
