# Epic Proposal: Trust Decision Stack (`cargo trust-decision` + `trust-decision-pack/v0`)

## One-sentence pitch
Create a thin stack-level contract that makes Rust trust review boring: a portable boundary that links **trust evidence**, **explicit policy decisions**, **waivers**, and **thin consumer views** without collapsing them into one score or one mega-tool.

## Deliverables
- `cargo trust-decision` reference tool
- schemas:
  - `trust-decision-brief/v0`
  - `trust-decision-diff/v0`
  - `trust-decision-pack/v0`
  - `trust-decision-view/v0`
  - `trust-decision-handoff/v0`
- adapters/importers for:
  - `trust-report/v0`
  - `trust-diff-report/v0`
  - `trust-import-profile/v0`
  - `policy-decision-report/v0`
  - `policy-diff-report/v0`
  - selected lifecycle / name-risk / inventory / signed-binary imports
- docs:
  - lockfile review recipe
  - build/proc-macro split-scope recipe
  - freshness/cooldown review recipe
  - package/release attachment guide
  - thin-view guide for PRs, registries, search, and adoption briefs

## Why now (signals)
- crates.io now surfaces a Security tab, GitLab Trusted Publishing, TP-only mode, blocked risky GitHub triggers, and `pubtime`, so the registry is finally emitting enough machine-usable trust inputs to justify a shared stack layer.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- the crates.io malicious-crate policy now routes routine malware removals through RustSec advisories as the durable record, which increases the value of local attachable artifacts and diffable decisions instead of ambient blog-post awareness.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Cargo Vet already proves the ecosystem has serious trust and policy ingredients: built-in criteria, imported audits, trusted-publisher windows, subtree-sensitive policy, multi-repository aggregation, and `audit-as-crates-io` handling for ambiguous first-party/third-party boundaries.
  https://mozilla.github.io/cargo-vet/how-it-works.html
  https://mozilla.github.io/cargo-vet/config.html
  https://mozilla.github.io/cargo-vet/trusted-entries.html
  https://mozilla.github.io/cargo-vet/multiple-repositories.html
  https://mozilla.github.io/cargo-vet/first-party-code.html
- Cargo publishing remains permanent, which keeps pre-publish and pre-release decision quality strategically important.
  https://doc.rust-lang.org/cargo/reference/publishing.html
- Rust’s 2026 flagship work keeps supply-chain concerns active through public/private dependencies and SBOM support, which increases the value of a review boundary that can compose with package, release, and inventory work.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Non-goals
- replacing `cargo vet`, `cargo policy`, RustSec, crates.io, or registry moderation;
- defining one global trust policy for all Rust projects;
- inventing a scalar crate-trust number;
- making registry/search/assistant summaries the canonical trust record;
- flattening lifecycle, inventory, provenance, and support signals into one security badge.

## Lane rule
Execute this epic with [`design/trust-decision-lane-map.md`](../design/trust-decision-lane-map.md) as the separation rule so registry facts, RustSec advisories, cargo-vet attestations, cargo-deny policy lints, artifact recovery, local waivers, and thin consumer views do not collapse into one fake verdict.

## Strategic value
This deserves promotion because it gives the archive a missing **evidence-to-decision composition point**.
With it:
- trust evidence can stay issuer-aware and scope-aware;
- policy decisions can stay explicit and diffable;
- package/release/adoption consumers can import trust posture without re-scraping CI or registries;
- registry/search/PR/assistant views can become thinner and more honest because the canonical linked artifacts already exist.

The prize is not another dashboard.
The prize is a durable decision boundary that other tools can import.

## Proposed shape
Ship a narrowly scoped stack-level layer:
1. import trust-evidence artifacts as the canonical signal layer;
2. import policy decisions and waivers as the canonical verdict layer;
3. preserve scope, issuer, and freshness distinctions in stack-level diffs;
4. emit bounded handoffs for package/release/adoption consumers;
5. emit thin view profiles for PRs, registries, search, and assistants;
6. validate that every rendered view can link back to the underlying evidence and decisions.

## Critical design bet
The critical bet is that **trust-decision truth stops at reviewable evidence, rules, and bounded rendered views**.
That means:
- trust signals remain canonical for facts and attestations,
- policy remains canonical for rules, waivers, and verdicts,
- stack-level packs and views coordinate them,
- but the stack does not become the sole owner of registry truth, release truth, installation truth, or support truth.

Without that boundary, the contribution either stays too weak to matter or bloats into a fake universal supply-chain platform.

## Milestones
1. **v0 stack pack + lockfile lane**
   - `trust-decision-brief` / `trust-decision-pack`
   - import `trust-report` + `policy-decision-report`
2. **v0.2 split-scope lane**
   - preserve runtime/build/dev/proc-macro distinctions
   - attach scope-sensitive diffs
3. **v0.3 publisher/freshness lane**
   - import Trusted Publishing / `pubtime` / trusted-publisher windows
   - expose cooldown-aware changes
4. **v0.4 package/release lane**
   - attach to Package Admission / Release Truth without flattening them
5. **v1 thin consumer views**
   - emit `trust-decision-view` / `trust-decision-handoff`
   - support registry/search/PR/adoption/assistant consumers with explicit overclaim boundaries

## Execution order
Use [`design/trust-decision-pilot-program.md`](../design/trust-decision-pilot-program.md) as the stack-level rollout:
1. lockfile evidence-to-policy lane,
2. build / proc-macro split-scope lane,
3. publisher/freshness/cooldown lane,
4. package/release-attachment lane,
5. thin consumer-view lane.

Use [`design/trust-signals-pilot-program.md`](../design/trust-signals-pilot-program.md) and [`design/policy-pilot-program.md`](../design/policy-pilot-program.md) as the leaf-level execution plans beneath it.

## Success metrics
- trust evidence and policy decisions can travel together without losing issuer/scope/freshness truth;
- waivers and `INCONCLUSIVE` states remain visible in stack-level summaries;
- package/release/adoption consumers can import the decision boundary without re-scraping upstream tools;
- thin views can summarize the result without becoming the new source of truth;
- the ecosystem gets one explainable trust-decision seam instead of scattered policy YAML, review comments, and registry folklore.
