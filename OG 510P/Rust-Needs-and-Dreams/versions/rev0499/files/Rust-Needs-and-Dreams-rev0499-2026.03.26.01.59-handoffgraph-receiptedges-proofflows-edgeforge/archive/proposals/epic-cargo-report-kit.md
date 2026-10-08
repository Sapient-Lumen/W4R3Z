# Epic Proposal: Cargo Report Kit

## One-sentence pitch
Make Cargo’s native report families portable and reviewable through one thin import-and-pack layer that preserves **authoritative native basis**, **authority-origin/import-path truth**, **fallback-order/refusal-posture truth**, **stable versus unstable posture**, **exact session/report scope**, **observed coverage slices**, **lane-wide claim-class honesty**, **projection/redaction/omission receipts**, **execution-receipt truth**, **derivation-lineage truth**, **quarantine-first retained-capture truth**, **derived-artifact non-laundering**, **observation-epoch/currentness truth**, **import-compatibility/drift-review truth**, **expiring waiver-ledger truth**, **contradiction/arbitration truth for same-scope competing artifacts**, **review-request/decision-witness truth plus review-separation truth for manual carries**, **field authorship**, **private-capture versus shared-surface versus frozen-head truth**, and **native-versus-normalized truth** for downstream build, perf, and debug consumers.

## Deliverables
- refreshed schemas:
  - `cargo-report-coverage-slice/v0`
  - `cargo-report-session-index/v0`
  - `cargo-report-authority-basis/v0`
  - `future-incompat-import/v0`
  - `cargo-report-projection-receipt/v0`
  - `cargo-report-quarantine-receipt/v0`
  - `cargo-report-currentness/v0`
  - `cargo-report-import-compat/v0`
  - `timings-report/v0`
  - `rebuild-report/v0`
  - `cargo-report-pack/v0`
  - `cargo-report-promotion-receipt/v0`
  - `cargo-report-waiver-ledger/v0`
  - `cargo-report-pack-heads/v0`
  - `cargo-report-execution-receipt/v0`
  - `cargo-report-lineage-register/v0`
  - `cargo-report-contradiction-packet/v0`
  - `cargo-report-review-request/v0`
  - `cargo-report-decision-witness/v0`
  - `cargo-report-diff/v0`
- tooling:
  - `cargo reportpack import-future-incompat`
  - `cargo reportpack import-session`
  - `cargo reportpack pack`
  - `cargo reportpack diff`
  - `cargo reportpack promote`
  - `cargo reportpack heads`
  - `cargo reportpack receipt`
  - `cargo reportpack lineage`
  - `cargo reportpack basis`
  - `cargo reportpack projection`
  - `cargo reportpack quarantine`
  - `cargo reportpack currentness`
  - `cargo reportpack compat`
  - `cargo reportpack waiver-ledger`
  - `cargo reportpack request-review`
  - `cargo reportpack decision-witness`
  - `cargo reportpack explain`
  - `cargo reportpack contradict`
- fixture-backed schema/example/scenario corpus under `fixtures/cargo-report-pack-kit/`
- machine-readable class register / scenario index / review-gate / contract-hygiene surfaces:
  - `fixtures/cargo-report-pack-kit/cargo-report-taxonomy.json`
  - `fixtures/cargo-report-pack-kit/cargo-report-scenario-index.json`
  - `fixtures/cargo-report-pack-kit/cargo-report-review-gates.json`
  - `fixtures/cargo-report-pack-kit/cargo-report-hygiene-checks.json`
- archive hygiene tooling:
  - `tools/check_cargo_report_pack_contract.py`
  - `tools/hygiene.py`
- example import corpus and CI / issue / support attachment workflow
- build/perf/debug consumer examples using the same pack

## Why now
- The Cargo Book documents a stable `cargo report` lane today for future-incompatibility reports.
  https://doc.rust-lang.org/cargo/commands/cargo-report.html
  https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
- Cargo’s unstable-features docs now define `-Zbuild-analysis`, persistent JSONL session logs, unique session IDs, and native `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds` commands.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The Cargo 1.94 update shows the family is actively growing: more timings parity, new rebuild/session commands, man pages, and replay-oriented cleanup.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The Cargo build-analysis goal explicitly wants external tools to analyze historical trends and explain build behavior over time while keeping collection opt-in, privacy/performance-conscious, and free of user-facing stability guarantees during prototyping.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

## Strategic value
This kit is high leverage because it solves a **shared substrate** problem rather than a point-tool problem:
- Build-State Evidence gets first-party rebuild/timing imports instead of raw-log scraping.
- Perf Labs gets compile-workflow timing imports without pretending they are benchmark-native results.
- Feedback Loop gets native session identity for iterative build/debug review.
- Support/issue workflows get a bounded way to share report truth without pretending local Cargo-home logs are automatically public-safe.
- Shared examples get an explicit way to say what was preserved, hashed, coarsened, omitted, or later lost from the stronger native basis instead of hiding projection choices inside prose.
- Projected bundles, derived summaries, and promoted heads get a compact produced-by and parentage story instead of relying on CI logs, shell history, or reviewer memory.
- Risky/unknown/native-private imports can be preserved in a quarantined-retained posture instead of forcing everything into delete-or-publish semantics.
- Cross-project example corpora get a disciplined way to distinguish the latest operational pack from the current frozen shared head.
- Same-scope competing artifacts can remain explicitly unresolved through contradiction packets and hold posture instead of forcing one summary or later import to win silently.
- Manual-review carries become explicit request and decision artifacts instead of sticky queue labels or prose-only approvals.
- Build/perf/debug/support consumers get one honest way to distinguish historical retained packs from current-as-of, rechecked-current, and superseded packs.
- Cargo itself remains free to evolve native unstable schemas, because the portable layer records stability, scope, currentness, compatibility/drift posture, authorship, authoritative basis, authority path, fallback/refusal posture, and visibility explicitly.

## Milestones
1. **v0 import baseline**
   - stable future-incompat imports
   - unstable build-analysis session imports
   - exact scope fields
   - observed coverage slices
   - pack/explain commands
2. **v0.2 claim exactness**
   - coverage-slice records
   - declared claim classes in promotion receipts
   - fail-closed rule for workspace/target/feature/toolchain-wide claims that outrun the observed slice
3. **v0.3 projection receipts and share-safe packaging**
   - `cargo-report-projection-receipt/v0`
   - explicit projection/redaction/omission reasons
   - fail-closed rule when shared bytes are only a filtered projection of richer native capture
   - basis-loss demotion when the stronger native basis later disappears
3.5 **v0.25 fixture-backed artifact spine**
   - freeze `cargo-report-pack` and the core receipts into schemas/examples/scenario folders
   - treat trust-semantic changes as incomplete until fixture examples move with them
   - keep at least one stable replay case, one projected support-bundle case, one basis-loss demotion case, and one quarantined-derived-summary case in the corpus
3.6 **v0.26 taxonomy-backed class register and review gates**
   - freeze the allowed class vocabulary for claim/currentness/projection/quarantine/compatibility/promotion fields
   - add a machine-readable scenario coverage index so named scenarios prove which classes and blocked stronger claims are already covered
   - add fail-closed review gates for stronger share/current/frozen-head reuse
3.65 **v0.265 execution receipts and lineage spine**
   - add `cargo-report-execution-receipt/v0`
   - add `cargo-report-lineage-register/v0`
   - require produced-by receipt refs and parent/child links for projected, derived, quarantined, promoted, or superseded artifacts
   - block stronger head/public/citation-like reuse when that production story is missing
3.68 **v0.268 contradiction packets and competing-head holds**
   - add `cargo-report-contradiction-packet/v0`
   - freeze conflict-scope, precedence/arbitration, and review-queue-status classes
   - require contradiction packets when same-scope native/projection/summary/head artifacts compete without one automatic winner
   - block stronger current/public/frozen-head reuse until contradiction state is `resolved` or an allowed precedence rule actually settles the winner
3.69 **v0.269 machine-checked contract hygiene**
   - add `cargo-report-hygiene-checks.json` plus `tools/check_cargo_report_pack_contract.py` and `tools/hygiene.py`
   - fail closed when taxonomy/schema/scenario/gate surfaces drift apart
   - require example JSON validation and scenario-directory coverage before Cargo-report revisions touching the fixture spine are treated as complete
3.695 **v0.2695 manual-review split truth**
   - add `cargo-report-review-request/v0` and `cargo-report-decision-witness/v0`
   - require stronger review-cleared carries to cite both the request and the resulting decision witness
   - require review requests to name the expected reviewed head and lineage, and decision witnesses to fail closed into `reissue-required` when that head has gone stale
   - keep queue state, requested carry, safe-without-approval sentence, and reviewed basis distinct from artifact status fields

3.697 **v0.2697 review-separation receipts**
   - add `cargo-report-review-separation-receipt/v0`
   - require review requests and decision witnesses to cite a separation receipt naming proposer/reviewer/executor identity, review-separation class, and compensating control / expiry when independence is weak
   - block stronger public/current/frozen/contradiction carry when self-review lacks an explicit fallback control
3.7 **v0.27 expiring waiver ledgers**
   - add `cargo-report-waiver-ledger/v0`
   - require owner/reviewer identity, stronger requested use, weaker safe sentence, expiry, and stale-waiver demotion
   - make promotion/currentness/compat carry refs explicit when a waiver is involved
4. **v0.35 quarantine-first retained capture**
   - `cargo-report-quarantine-receipt/v0`
   - quarantine classes for risky/unknown/native-private retained bytes
   - explicit non-inference rule for omitted / decoder-unknown / quarantine-blocked fields
   - derived-summary parent-link rule so later normalization cannot semantic back-write onto the source
5. **v0.4 authoritative basis, authority path, and promotion**
   - authority-basis records
   - authority-origin / import-path / fallback-order / refusal-posture truth
   - promotion receipts (`hold` / `support-bundle` / `issue-attachment` / `public-example`)
   - fail-closed rule for derived-only or weaker-path basis when stronger claims are attempted
6. **v0.5 currentness and supersession**
   - observation-epoch records
   - historical/as-of/rechecked/superseded classes
   - fail-closed rule for current-active wording without recheck basis
7. **v0.6 import compatibility and drift gates**
   - `cargo-report-import-compat/v0`
   - decoder/importer version + reviewed Cargo/toolchain/schema family
   - fail-closed drift classes for unstable-derived reuse
   - reimport/re-review triggers for material change
8. **v0.7 authorship and heads**
   - field-authorship markers
   - local-private versus shared-surface posture
   - copied-attachment versus replay-reference distinctions
   - operational-head versus frozen-head register and warnings
9. **v0.8 diff and portability**
   - cross-session diffs
   - CI / issue / support artifact examples
   - omission/redaction notes where needed
10. **v0.9 downstream consumers**
   - Build-State Evidence imports
   - Perf Labs timing imports
   - Feedback Loop session imports
11. **v1 convergence**
   - align with Cargo-native evolution where useful
   - preserve honest stable/unstable, basis, and frozen-head boundaries
   - reduce ad hoc importer duplication across the archive’s build/debug bands

## Non-goals
- replacing Cargo’s own report commands;
- turning Cargo Report Kit into a diagnosis or performance-policy layer;
- promising stability for all build-analysis fields before Cargo does;
- silently reusing an unstable-derived frozen/shared/current-active artifact after Cargo/toolchain/importer drift without a compatibility receipt or explicit fail-closed hold;
- silently letting a copied rendering or summary inherit the authority of a missing replay/native-byte path;
- treating local-private raw capture as automatically portable or public-safe;
- letting a projected/shared bundle hide which fields were hashed, coarsened, omitted, or later lost from the stronger native basis;
- silently letting quarantined-retained bytes become search/snippet/summary/public truth because a later tool derived a convenient explanation;
- or treating omitted / decoder-unknown / quarantine-blocked fields as fake evidence of absence or safety;
- inventing another standalone dashboard product;
- or letting the latest imported pack silently stand in for the archive’s citeable shared example.
- treating one retained replay artifact as the current active workspace story without an explicit as-of or recheck basis.
- or relying on prose-only waivers for stronger share/current/frozen/compatibility reuse without an explicit expiring waiver ledger.
- letting projected exports, derived summaries, or promoted heads exist without an explicit produced-by receipt and lineage link.
- letting same-scope competing artifacts silently collapse into one winner without an explicit contradiction packet, precedence rule, and blocked stronger-use posture.
- letting requester-authored or same-actor review silently impersonate independent checker approval for stronger public/current/frozen/contradiction carry.
- letting artifact meanings drift only in prose after schemas/examples/scenarios already exist.
- letting taxonomy/schema/scenario/gate surfaces drift apart without a machine-checked contract failure.
