# Design: Cargo Report Pilot Program (`cargo reportpack pilot`, `cargo-report-pilot-pack/v0`)

## Goal
Turn Cargo Report Kit from “good idea near build-state work” into a **ranked execution path**.

The point of this pilot is to prove that Cargo-native reports can be imported, packed, diffed, promoted, and handed off **without flattening**:
- stable `future-incompat` replay,
- unstable build-analysis session logs,
- exact session/report scope,
- observed coverage slices and stronger claim classes,
- observation epochs and currentness classes,
- authorship buckets,
- authoritative native basis,
- authority path / fallback order / refusal posture,
- local-private capture versus portable/shared artifacts,
- projection/redaction/omission receipts plus basis-loss warnings,
- quarantine-first retained-capture posture plus derived-artifact separation,
- latest operational heads versus frozen shared heads,
- produced-by execution receipts versus prose-only production memory,
- parent/child lineage links versus semantic back-write onto source artifacts,
- superseded/stale-head warnings,
- normalized summaries,
- downstream build/perf/debug conclusions,
- and queued manual-review carries versus resolved decision witnesses, review-separation receipts.

## Why now
1. **Cargo already has one stable report lane.** `cargo report` is documented today and the stable surface currently supports future-incompatibility reports.
2. **Cargo also now has a serious unstable report lane.** `-Zbuild-analysis` persists JSONL logs to `$CARGO_HOME/log/`, assigns unique session IDs, and exposes `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds` over past sessions.
3. **The command family is actively evolving.** The 1.94 development-cycle update says Cargo is still adding missing timings features, report man pages, and replay capabilities. That makes this the right moment to harden **import discipline and promotion discipline**, not to pretend the schemas are already final.
4. **Cargo’s own goal text warns against overclaiming.** Build-analysis collection is opt-in, should avoid privacy/performance regressions, and offers no user-facing stability guarantees during prototyping.
5. **Cargo’s own goal text makes projection discipline real.** The build-analysis goal explicitly mentions CLI arguments and invocation metadata while insisting that collection remain privacy-conscious and locally controlled. That means any portable/shared artifact must name how local-private capture was filtered before it moves.
6. **The same sources make quarantine-first retention real.** Some unstable/native-private bytes will still be worth preserving even when they are not yet safe to summarize, search, or share normally. The pilot therefore needs an explicit retained-quarantine lane instead of forcing everything into delete-or-publish.
7. **Multiple nearby stacks already need the same native data.** Build-State Evidence, Perf Labs, and Feedback Loop all want Cargo-native report facts. A pilot should prove the handoff once instead of letting each layer grow its own adapter.

## Source signals
- `cargo report` command docs:
  https://doc.rust-lang.org/cargo/commands/cargo-report.html
- future-incompat report docs:
  https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
- unstable build-analysis docs:
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.94 update:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo build-analysis goal:
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

## Pilot thesis
A serious pilot should prove ten things in order:
1. **stable report import** is honest and portable;
2. **unstable session import** is explicit about drift, scope, and missing fields;
3. **authoritative basis, authority path, and refusal posture** stay machine-readable instead of living in prose;
4. **projection/redaction/omission receipts** stay explicit so shared bytes never pretend to be the full native capture;
5. **quarantine-first retained capture** stays explicit so risky/unknown/native-private bytes can be preserved without silently becoming normal semantic truth;
6. **currentness posture** stays explicit so historical retained artifacts do not silently pose as current-active truth;
7. **field authorship and share posture** stay explicit from local capture through frozen shared head;
8. **execution receipts and lineage links** stay explicit once artifacts become projected, derived, quarantined, promoted, or superseded;
8. **cross-session diffing** is possible without pretending every field is stable;
9. **fixture-backed artifact freeze** exists so schemas/examples/scenarios lock the meaning of receipts and warning classes before broader consumers depend on them;
10. **machine-checked contract hygiene** exists so taxonomy values, review gates, scenario coverage, and example/schema pairs cannot silently drift apart after that freeze;
11. **expiring waiver ledgers** exist so any temporary stronger share/current/frozen exceptions are durable, named, and self-demoting rather than sticky prose;
12. **manual-review split truth** exists so queued requests and the decision that cleared or refused them are not collapsed into one status label;
13. **downstream handoff** works for build/perf/debug/support consumers without silently turning the latest pack into the shared example or the current workspace story.

## Ranked execution lanes
The pilot should also prove one small governance surface: any stronger reuse that only exists because a reviewer temporarily allowed it must move through `cargo-report-waiver-ledger/v0` with owner/reviewer identity, expiry, and stale-waiver demotion rather than living as an inline comment.
### Lane 1 — Stable future-incompat import lane
Goal: prove the baseline import surface.

Use cases:
- a maintainer replays a future-incompat report locally;
- CI exports the report for later review;
- a dependency-review or migration consumer imports it.

Must prove:
- `future-incompat-import/v0` preserves report ID and package filters;
- replay provenance stays visible;
- exact known report scope stays separate from unknown scope;
- textual sections do not silently become machine-guaranteed facts;
- authoritative-basis metadata survives export.

### Lane 2 — Unstable build-analysis session lane
Goal: prove explicit unstable native-session imports.

Use cases:
- import a build-analysis session from `$CARGO_HOME/log/`;
- replay timings without rebuilding;
- inspect rebuild reasons from a past run.

Must prove:
- `cargo-report-session-index/v0` records session ID, unstable posture, and exact known invocation scope;
- `timings-report/v0` and `rebuild-report/v0` preserve native availability and missing-field markers;
- copied artifacts versus replay-only references remain distinct;
- local-private capture posture is visible rather than implied;
- authoritative-basis posture is explicit;
- the chosen authority path is explicit enough to distinguish native replay from direct native bytes, copied native bytes, or weaker renderings.



### Lane 3 — Quarantine-first retained-capture lane
Goal: prove that imported bytes can remain preserved without silently becoming normal semantic/search/share truth.

Use cases:
- keep unstable build-analysis bytes that are decoder-unknown, privacy-sensitive, or basis-missing while stronger interpretation remains unresolved;
- retain copied/native attachments for historical/debug value without letting them surface as frozen-head, citation-like, or current-active truth;
- generate later summaries or normalized explanations without semantic back-writing onto the retained source artifact.

Must prove:
- `cargo-report-quarantine-receipt/v0` records `capture-only-local`, `quarantined-retained`, `review-cleared-local`, or `not-quarantined` posture;
- omitted, decoder-unknown, or quarantine-blocked fields are explicitly non-inferable rather than fake negative evidence;
- later summaries/normalizations carry explicit parent linkage as distinct derived artifacts instead of silently laundering the quarantined source into normal truth;
- promotion/current-active/consumer-import flows fail closed while the relevant bytes remain quarantined.

### Lane 4 — Projection / omission / basis-loss lane
Goal: prove that a portable/shared artifact can admit it is a filtered projection of richer local-native capture.

Use cases:
- strip or hash absolute paths, env-derived values, or raw payload sections before attaching a support bundle;
- keep an issue attachment smaller or safer than the full local pack without hiding the fact that material was removed;
- demote a previously stronger shared artifact once the replayable/local native basis is no longer retained.

Must prove:
- `cargo-report-projection-receipt/v0` records what was kept verbatim, hashed, coarsened, omitted, or summarized;
- projection reasons stay explicit (`privacy`, `path-sensitivity`, `portability`, `size`, `policy`, `unknown`);
- imported share labels do not silently widen or relax local redaction authority;
- basis-loss warnings can demote stronger reuse once only projected/copied material remains.

### Lane 5 — Coverage-slice and claim-exactness lane
Goal: prove that observed native scope and stronger shared claims stay separate.

Use cases:
- distinguish one selected-package or one target/profile slice from whole-workspace language;
- mark partial-failure or aborted sessions as partial evidence rather than “no change” or “workspace green”;
- keep replayed HTML timings from silently becoming all-target performance claims.

Must prove:
- `cargo-report-coverage-slice/v0` records package/target/feature/profile/toolchain coverage honestly enough for later review;
- promotion receipts can carry a declared claim class and block stronger lane-wide wording when coverage is narrower;
- `workspace-default-members`, `workspace-all-members`, and `all-targets` remain explicit proven claim classes instead of convenient guesses.

### Lane 6 — Currentness and recheck lane
Goal: prove that retained historical artifacts do not silently become current-active truth.

Use cases:
- distinguish one historical replay artifact from a pack that is only current as-of a named observation epoch;
- mark a pack superseded once a newer native session/report head exists;
- carry one explicit recheck receipt when a maintainer wants stronger “current build state” wording.

Must prove:
- `cargo-report-currentness/v0` records observation epoch, currentness class, invalidation triggers, and supersession pointers;
- `historical-retained`, `current-as-of-observation`, `rechecked-against-newer-native-basis`, and `superseded` remain explicit classes instead of prose vibes;
- stronger current-active wording fails closed when no recheck basis exists.

### Lane 7 — Import-compatibility and drift-review lane
Goal: prove that retained or promoted artifacts do not silently keep their old authority after Cargo/toolchain/importer change.

Use cases:
- reuse an unstable build-analysis pack after upgrading Cargo nightly;
- distinguish “same bytes, new decoder” from “same reviewed interpretation”;
- block frozen-head or current-active reuse until drift has been reviewed or a newer native import exists.

Must prove:
- `cargo-report-import-compat/v0` records decoder/importer version, reviewed Cargo/toolchain family, and native schema family when known;
- the pilot can classify later changes as `same-reviewed-basis`, `compatible-drift-reviewed`, `material-drift-reimport-required`, `material-drift-rereview-required`, or `basis-missing`;
- promotion/current-active flows fail closed when unstable-derived artifacts cross an unresolved material-change boundary;
- projected, derived, or promoted artifacts always carry produced-by receipt refs and lineage links before they are used outside local review.

### Lane 8 — Authoritative-basis, authority-path, and promotion lane
Goal: prove the pack can say what authorizes later sharing.

Use cases:
- distinguish native replayable basis from copied-native basis;
- distinguish native replay commands from direct native bytes, copied native bytes, copied renderings, and summary-only fallbacks;
- block promotion when only derived renderings remain;
- decide whether a pack is `hold`, `support-bundle`, `issue-attachment`, or `public-example`.

Must prove:
- `cargo-report-authority-basis/v0` is explicit enough for reviewers to tell what still anchors the import;
- that same record carries authority-origin/import-path, fallback-order, and refusal-posture truth;
- `cargo-report-promotion-receipt/v0` records one deliberate promotion decision instead of silent folder motion;
- unresolved unstable/schema/scope/authority-path warnings can block frozen-example promotion.

### Lane 9 — Authorship and head-warning lane
Goal: prove the pack can say who authored what and which head is actually shareable.

Use cases:
- distinguish Cargo-authored ids from pack-authored summaries;
- distinguish rustc/tool passthrough payload from downstream consumer verdicts;
- distinguish the latest operational pack from the current frozen shared head.

Must prove:
- authorship buckets are explicit enough for reviewers to tell native facts from annotations;
- share posture is explicit enough to distinguish local-private capture, portable pack content, shared surface, and frozen shared head;
- `cargo-report-pack-heads/v0` can emit warnings like `not-frozen`, `unstable-fields-present`, and `native-basis-missing`.
- `cargo-report-lineage-register/v0` can show whether a public example is a native-import root, projected child, or derived child, and whether a head-role transition had a produced-by receipt.

### Lane 10 — Cross-session diff lane
Goal: prove a reviewable comparison story.

Use cases:
- compare two sessions from the same repo on different commits;
- compare a no-change rerun against a changed-environment rerun;
- compare timing availability across Cargo versions.

Must prove:
- diff reports can separate semantic changes from missing-data/schema drift;
- absent native fields do not become fake “no change” verdicts;
- changed command/profile/target/share posture remains explicit;
- changed authoritative-basis posture is visible when later review strength changes.

### Lane 10.5 — Fixture corpus / scenario freeze lane
Goal: prove that the artifact vocabulary remains reviewable after semantics evolve.

Use cases:
- a revision changes what `basis-missing`, `quarantined-retained`, or `current-as-of-observation` means;
- promotion/head rules change for projected or unstable-derived packs;
- a new decoder/toolchain drift class appears and must not live only in prose.

Must prove:
- `fixtures/cargo-report-pack-kit/` contains schemas plus example JSON for the core pack/receipt surfaces;
- named scenario folders freeze at least one stable replay case, one projected support-bundle case, one basis-loss demotion case, and one quarantined-derived-summary case;
- changes to trust semantics fail review until the relevant fixture examples move with them;
- and the examples still say what stronger claims remain out of bounds.

### Lane 11 — Build-state / perf / feedback / support imports lane
Goal: prove bounded consumer imports.

Use cases:
- Build-State Evidence imports rebuild reasons;
- Perf Labs imports timing sessions as compile-workflow evidence;
- Feedback Loop imports one session identity alongside debugger/diagnostic evidence;
- issue/support consumers import one shared pack without claiming it is the full native capture.

Must prove:
- consumers can cite the same imported pack;
- consumers do not silently re-own Cargo-native semantics;
- imported report truth remains distinguishable from downstream diagnoses or gates;
- frozen shared examples keep their warnings when they leave local review.

## Deliverables
- new `cargo-report-quarantine-receipt/v0`
- new `cargo-report-projection-receipt/v0`
- new `cargo-report-coverage-slice/v0`
- refreshed `cargo-report-session-index/v0`
- new `cargo-report-authority-basis/v0`
- new `cargo-report-currentness/v0`
- refreshed `future-incompat-import/v0`
- refreshed `timings-report/v0`
- refreshed `rebuild-report/v0`
- refreshed `cargo-report-pack/v0`
- new `cargo-report-promotion-receipt/v0`
- new `cargo-report-pack-heads/v0`
- `cargo-report-diff/v0` review surface
- fixture-backed schema/example/scenario corpus under `fixtures/cargo-report-pack-kit/`
- machine-checked contract-hygiene surfaces under `fixtures/cargo-report-pack-kit/` plus `tools/`
- example import corpus with:
  - stable future-incompat case
  - unstable single-session timings case
  - unstable rebuild-reason case
  - mixed-lane pack with explicit authorship/share posture
  - one quarantined-retained case plus one derived-summary-with-parent-link case
  - one historical-retained case and one rechecked-current case
  - cross-session diff case
  - one `hold` case and one frozen shared-head case
  - support/issue portability case
  - schema/example/scenario freeze for the core receipt vocabulary
  - contract-hygiene checks proving those files still agree

## Success criteria
The pilot is successful when:
- one pack can preserve both stable and unstable Cargo-native report lanes honestly;
- a maintainer can compare sessions without shell-history archaeology;
- every shared artifact says what authoritative native basis still exists and which authority path actually produced the pack;
- quarantined-retained bytes remain preservable without silently becoming snippet/search/summary/public truth;
- no pack can silently claim workspace-wide or all-target truth unless its declared claim class is actually supported by its coverage slice;
- no retained replay/session pack can silently claim current-active truth unless its currentness class and recheck posture justify that wording;
- no manual review request or approval can silently follow a newer operational head unless a new request/witness explicitly reissues on that head;
- the latest operational pack can remain distinct from the frozen shared head;
- unstable-lane frozen examples carry explicit warnings instead of silently posing as stable contracts;
- no pack can silently slide from native replay authority to copied-rendering authority while keeping the same claim strength;
- Build-State Evidence, Perf Labs, Feedback Loop, and support consumers can import the same pack with bounded, explicit lossiness;
- later summaries or normalized explanations cannot semantic back-write onto a quarantined source artifact;
- and future Cargo evolution can still change native formats without breaking the distinction between native imports, portable packs, quarantined-retained capture, shared surfaces, frozen heads, execution receipts, lineage roles, currentness classes, and consumer conclusions.

## Anti-goals
Do not turn this pilot into:
- a universal dashboard product;
- a hidden schema-freeze for Cargo internals;
- a replacement for Build-State Evidence or Perf Labs;
- a claim that all `cargo report` families are equally stable or equally shareable today;
- or a stealth rule that every latest pack is the public example.
- Do not let quarantined-retained bytes silently become search snippets, summary truth, or downstream diagnosis input just because a later tool derived a convenient explanation.
- Do not let one selected package, one target/profile slice, or one partial failed run silently stand in for the whole workspace lane.
- Do not let one copied rendering or summary silently inherit the authority of Cargo-native replay when stronger reuse depends on the missing path.
- Do not let one retained replay or old session silently stand in for the current active workspace state without an explicit as-of or recheck basis.


### Lane 10 — Manual-review request / decision lane
Goal: prove that stronger carry through manual review is explicit rather than status-shaped.

Use cases:
- a projected nightly pack asks to become a public example;
- a contradiction packet asks for one operational head to win while frozen-head carry remains blocked;
- a currentness/compatibility carry asks a reviewer to clear a stronger sentence against named basis refs.

Must prove:
- `cargo-report-review-request/v0` records the stronger requested use, consulted basis refs, `expected_head_ref`, `head_lineage_ref`, safe-without-approval sentence, and gate ids still in play;
- `cargo-report-decision-witness/v0` records who reviewed, what was consulted, `reviewed_head_ref`, `head_guard_status`, which blocks were cleared versus kept, and any winner ref;
- pending, held, resolved, and superseded manual-review carries remain distinct from the pack’s own share/currentness/compatibility classes;
- stale-head review carries fail closed into `reissue-required` rather than silently approving a newer operational head;
- stronger reuse fails closed when prose claims approval but no decision witness exists.
