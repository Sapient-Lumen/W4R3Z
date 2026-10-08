# Frontier salience scan — 2026-03-09

This pass exists to resist two failure modes at once:

1. **archive sprawl**, and
2. **frontier monoculture**.

The archive now has hundreds of proposals.
A good pass should often re-rank, compress, and rebalance the portfolio rather than keep adding narrow ideas.

## Main judgment

This pass did **not** add another top-level proposal.

Instead, it did three things:

- re-read the archive as a **portfolio** rather than as one Cargo-only frontier,
- upgraded two under-specified ecosystem-multiplier proposals (**P-0076** and **P-0264**),
- and recorded a broader top-tier ranking for “epic” crates that would actually move the ecosystem.

## External signals worth honoring

- The 2025 State of Rust survey says that **resource usage (slow compile times and storage usage)** remains a major productivity problem, while **debugging** remains a top-tier pain point.
- The compiler performance survey says the **linking phase** is still a common complaint and that it is inherently different from the rest of compilation.
- Cargo’s own project-goal work on **rebuild avoidance** and **build-dir layout** shows that Rust increasingly has real substrate, but ordinary teams still lack compact explanation and support artifacts above it.
- Rust’s 2026 flagship goals still put major weight on **Just Add Async** and other ecosystem-ergonomics themes, which reinforces the importance of crates that make hard workflows boring rather than merely possible.
- Rust already has meaningful verification substrate (**Miri, Kani, Creusot, Prusti, Flux, Verus**), which makes cross-tool campaign artifacts with explicit policy and comparability contracts more important than inventing one more verifier.
- WebAuthn/passkeys now sit on a current W3C Level 3 Candidate Recommendation Snapshot plus an explicit FIDO conformance/interoperability ecosystem, which makes an interop/device-lab crate unusually timely.
- Text/i18n substrate is stronger than before (ICU4X 2.0, Unicode UAX #14, Rust shaping engines), but the Rust GUI ecosystem still lacks a shared layout/conformance artifact.
- Local-first work now has stronger Rust substrate (Automerge, Loro), but still lacks a boring “product kit” above CRDT engines.
- Cargo and nextest custom-harness surfaces are mature enough that the missing value for many standards ecosystems is increasingly a **shared conformance harness toolkit**, not another bespoke runner.
- crates.io now has very large populations in established categories, which is another reminder that the missing value is often **coordination artifacts** rather than “one more library in an already crowded bucket.”

## Broad ranking after this pass

This is the archive’s **broad** top tier right now, not merely the sharpest current Cargo sub-frontier.

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0242 Reproducible Build Evidence Kit**
3. **P-0256 Evidence Bundle Core Kit**
4. **P-0485 Verification Campaign Workbench Kit**
5. **P-0264 Rust Conformance Harness Toolkit**
6. **P-0076 Local-first Sync Kit**
7. **P-0197 Text Layout & Shaping Conformance Kit**
8. **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit**
9. **P-0503 Assurance Case Workbench Kit**
10. **P-0469 Cargo Rebuild Explanation Kit**

## Why these are the strongest “epic crate” bets

### 1. P-0468 Cargo Resolver Explanation Kit
Still the sharpest answer to one of the most recurring Rust questions: *why did Cargo choose this dependency/feature/version outcome?*

This remains top-tier because it attacks daily confusion with existing substrate and a compact artifact-first MVP.

### 2. P-0242 Reproducible Build Evidence Kit
This is one of the cleanest trust multipliers in the whole archive.
It helps maintainers, enterprises, downstream packagers, and incident responders at once.

### 3. P-0256 Evidence Bundle Core Kit
This is one of the best cross-cutting bets in the repository.
If it lands, dozens of protocol/interop/support crates stop reinventing redaction, signing, diffing, and deterministic packaging.

### 4. P-0485 Verification Campaign Workbench Kit
Rust no longer lacks verification tools in the absolute sense.
It lacks a boring, reviewable campaign artifact across heterogeneous tools, with explicit trust, green-policy, and comparability rules.
That is a stronger gap than inventing yet another verifier-adjacent DSL.

### 5. P-0264 Rust Conformance Harness Toolkit
This is an ecosystem multiplier hiding in plain sight.
Many future “interop kits” in this archive get cheaper and more coherent if a shared suite/runner/bundle substrate exists.

### 6. P-0076 Local-first Sync Kit
This remains one of the most ambitious-but-worthy product bets.
The missing value is not another CRDT paper or one more low-level engine; it is the boring deployable kit above them.

### 7. P-0197 Text Layout & Shaping Conformance Kit
Outside build tooling, this is one of the cleanest “Rust has pieces but not a reliable default workflow” gaps.
Correct text is a product requirement, not a niche feature, and the repo now has a clearer path for profile-pinned comparability instead of vague backend debates.

### 8. P-0200 WebAuthn & Passkeys Interop + Device Lab Kit
Passkeys are now important enough, and standardized enough, that a Rust interop/device-lab workflow could become a default operational tool rather than a curiosity. The sharper missing value is now a capability-receipted lab above WebAuthn Level 3, WebDriver virtual authenticators, Rust RP/authenticator substrate, and imported certification/device evidence — not another auth SDK.

### 9. P-0503 Assurance Case Workbench Kit
This is a strong upper-layer multiplier for safety/security evidence.
It should stay distinct from lower-level evidence producers, but it is one of the clearest “epic” ecosystem gaps if Rust wants to serve higher-assurance domains well.

### 10. P-0469 Cargo Rebuild Explanation Kit
Still extremely worthy because it turns a daily build-productivity complaint into a compact support artifact instead of another dashboard.

## What these top crates have in common

The strongest bets now usually satisfy most of these:

1. **They solve recurring pain, not one-off cleverness.**
2. **They sit above real substrate instead of waiting for future language/compiler miracles.**
3. **They produce a coordination artifact** (bundle, receipt, ledger, suite, diff, contract) that other people can consume.
4. **They help multiple sub-ecosystems at once.**
5. **They have an honest MVP that can ship without owning the whole world.**

## What should count as a worthy crate contribution now

A worthy or epic crate contribution in 2026 usually looks less like:

- “a wrapper around three existing crates”, or
- “another parser/SDK in a crowded category”,

and more like:

- **a boring default workflow artifact**,
- **a shared support bundle that makes failures reviewable**,
- **a portability/conformance harness that multiple implementations can share**, or
- **a trust/evidence layer that composes existing Rust substrate into something teams can actually operate**.

## What to de-emphasize for the next few passes

- more narrow protocol kits unless they clearly justify themselves against the current top tier,
- another generic parser/SDK where Rust already has credible substrate,
- and any proposal that cannot yet say what artifact it hands to another person.

## Practical rule for future passes

Before adding more proposal count, ask:

1. does this beat **P-0256** as a cross-cutting bundle/evidence substrate,
2. does it beat **P-0264** as a conformance multiplier,
3. does it beat **P-0076** as a product-level missing stack,
4. or does it beat the Cargo explainability cluster on day-to-day maintainer pain?

If not, prefer strengthening the current portfolio.

## What changed in the archive

Added:

- `meta/frontier-salience-2026-03-09.md`
- `entries/2026-03-09-157.md`

Updated:

- `proposals/localfirst-sync-kit.md`
- `proposals/rust-conformance-harness-toolkit.md`
- `README.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://doc.rust-lang.org/cargo/commands/cargo-test.html
- https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- https://nexte.st/docs/design/custom-test-harnesses/
- https://www.inkandswitch.com/essay/local-first/
- https://automerge.org/docs/hello/
- https://loro.dev/blog/v1.0
- https://www.unicode.org/reports/tr14/
- https://github.com/unicode-org/icu4x/blob/main/CHANGELOG.md
- https://github.com/harfbuzz/rustybuzz
- https://www.w3.org/TR/webauthn-3/
- https://fidoalliance.org/certification/functional-certification/conformance/
- https://fidoalliance.org/certification/interoperability-testing/
- https://model-checking.github.io/kani/
- https://creusot-rs.github.io/creusot/guide/
- https://viperproject.github.io/prusti-dev/
- https://flux-rs.github.io/
- https://github.com/rust-lang/miri
- https://www.omg.org/spec/SACM/2.3/About-SACM
- https://crates.io/
- https://crates.io/categories


## 2026-03-09 addendum — assurance case becomes more buildable

After the verification-campaign and evidence-bundle passes, **P-0503** is now much more implementable than it looked earlier in the day.

The sharper reading is not “Rust should get an assurance-case editor.”
It is:

- import reviewable evidence from lower-layer Rust tools,
- assemble a conservative claim graph,
- evaluate explicit status and freshness,
- emit a change-impact diff,
- and only then export GSN/SACM-shaped views.

That keeps **P-0503** in the broad top tier as an upper-layer multiplier rather than a decorative standards wrapper.


## 2026-03-09 addendum — local-first sync is now more handoff-ready

After the latest pass, **P-0076** is more buildable than it looked earlier in the day.

The sharper reading is no longer “Rust needs a local-first stack” in the abstract.
It is:

- freeze a repo contract above existing engines,
- emit sync-state / transport / membership receipts,
- classify divergence conservatively,
- and package the result as a redacted portable bundle.

That keeps **P-0076** in the broad top tier as one of the clearest product-level missing coordination artifacts in the archive.


## 2026-03-09 addendum — accessibility interop becomes more credible

After the latest pass, **P-0202** should be read less as “another accessibility abstraction” and more as a **capture / normalization / interop lab** above growing Rust accessibility substrate.

The sharper split is now:

- **P-0087** for toolkit-facing authoring/doctor/gating,
- **P-0202** for cross-platform capture, semantic diffs, scenario packs, and redacted handoff bundles.

That keeps accessibility work below the broad top tier for now, but it makes it a much more credible correctness-lab candidate than it looked when the repo still blurred those two layers together.


## 2026-03-09 addendum — local-first transport/bootstrap truth matters

After the latest pass, **P-0076** should be read even less as "pick a CRDT and a P2P library" and more as a crate that freezes a receiver-facing contract for:

- repo/profile identity,
- reliable-ordered sync assumptions,
- direct vs relay transport receipts,
- bootstrap method and redaction notes,
- membership epochs and revocation receipts,
- and conservative divergence classes.

That makes the proposal stronger because current Rust substrate is now good enough that the missing value is not hidden cleverness in the engine; it is the boring operational truth another person can actually inspect.


## 2026-03-09 addendum — async determinism becomes more buildable

After the latest pass, **P-0104** should be read less as “invent a new deterministic runtime” and more as a **portable profile / backend-receipt / transcript / replay-bundle kit** above today's substrate.

The sharper stack is now:

- **P-0104** for cross-backend deterministic simulation artifacts and adapters,
- **P-0114** for domain hardship/profile suites above that substrate,
- **P-0073** for observed-execution replay/debugger flows,
- and **P-0066** for rollback/state-hashing determinism in games.

That does not push async determinism into the broad top tier yet, but it makes the frontier much more credible and much more handoff-ready than it looked when the proposal was still mostly a good essay with stale UI citation markup.


## 2026-03-09 addendum — text layout is now more handoff-ready

After the latest pass, **P-0197** should be read less as “Rust needs more text infrastructure” and more as a **case / corpus / backend-receipt / semantic-diff / diagnosis** kit above real text substrate.

The sharper split is now:

- Unicode data and shaping engines as substrate,
- layout/fallback policy as explicit backend truth,
- and **P-0197** as the cross-backend correctness-lab layer that makes regressions portable.

That keeps **P-0197** firmly in the broad top tier as one of the clearest non-Cargo correctness-lab bets in the archive.


## 2026-03-09 addendum — text layout needs profile and decision-origin truth

The latest refinement should push **P-0197** one step further: a worthy crate here should not only freeze cases and outputs, but also make the **interpretation profile** and **decision origins** reviewable.

The sharper split is now:

- `layout-case` for the semantic request,
- `layout-profile` for Unicode/CSS/toolkit/editor policy expectations,
- backend capability receipts for what the lane can even claim,
- decision-origin receipts for where break/fallback/measurement choices really came from,
- and font-resolution receipts for what actually resolved at runtime.

That is a stronger and more portable contribution than another backend-specific text abstraction.

## 2026-03-09 refresh — passkey lab capability receipts and comparability truth

### Main judgment
- **P-0200** should now be read as a **scenario / capability / transcript / comparability / bundle** kit above existing Rust auth substrate.
- The strongest first browser lane is a Chromium-class virtual-authenticator lane, not a pretend all-browsers-equal story.
- The repo should preserve unstable or unreliable automation lanes as first-class facts rather than silently averaging them into “browser support”.

### Best next incubation targets in this stack
1. **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit**
2. **P-0264 Rust Conformance Harness Toolkit**
3. **P-0256 Evidence Bundle Core Kit**
4. **P-0503 Assurance Case Workbench Kit**

### Working rule
For follow-on work, prefer pinned scenario profiles, runner-capability receipts, comparability matrices, and imported device/certification evidence over adding another passkey integration framework.
