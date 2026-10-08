# Design: Fork Continuity Stack (community continuations, renamed successors, alternate homes)

## Goal
Treat **continuation without ownership transfer** as a first-class Rust ecosystem seam.

Rust has gotten better at saying that maintenance matters, that succession requires explicit authority movement, and that neutral support lanes now exist.
But the archive still lacked a compact answer to a harder question:

> if a Rust crate, workspace, tool, or service needs to continue **without** a clean ownership transfer, how should the ecosystem describe that continuation honestly — in naming, authority, distribution route, compatibility claims, and migration posture — without pretending it is the same project or leaving users with pure folklore?

That missing layer is **not** just lifecycle metadata, and it is **not** just succession.
It sits beside them.
The continuation problem is not one blob called “fork”.
It contains distinct truths that ideal Rust should keep separate and reviewable:
- **origin-subject truth** — which crate, workspace, tool, service, version line, or team is being continued, and what part of it is actually in scope;
- **continuation-intent truth** — whether the continuation is an emergency carry, maintained fork, compatibility continuation, governance split, renamed successor, alternate-registry continuation, neutral-home reissue, or experimental reboot;
- **authority-and-identity truth** — whether the continuation is same-maintainer, same-org, owner-approved, community-asserted, institution-hosted, or simply a new package with a claimed relationship;
- **distribution-route truth** — whether users consume it through a new crates.io package, a local `[patch]`, a git/path multiple-location override, an alternate registry, or some combination;
- **compatibility-and-migration truth** — whether the continuation is drop-in, semver-adjacent, migration-required, behaviorally divergent, or only conceptually related;
- **continuity-witness truth** — what evidence shows the continuation is real: releases, security response, docs upkeep, migration guidance, or accepted downstream adoption;
- **reconciliation-or-exit truth** — whether the lane is meant to merge back, supersede the origin, remain permanently divergent, or sunset once the original recovers.

The point is to stop flattening “there is a successor pointer”, “there is a local fork”, “there is a renamed community continuation”, and “the original owners approved a transfer” into the same sentence.

## Why this seam matters now
Official Rust/Foundation/Cargo signals are unusually aligned here:
- RFC 3646 says the crates.io team wants to stop mediating crate ownership transfer, and its guide-level explanation says if the current owner is unreachable and your direct contact attempts fail, you will need to pick a different crate name. That is direct pressure toward explicit continuation-without-transfer lanes rather than informal hope that the registry will arbitrate continuity for you.
  https://rust-lang.github.io/rfcs/3646-remove-crate-transfer-mediation-policy.html
- crates.io policy still says ownership transfer requires current-owner agreement. That means continuity cannot be inferred from abandonment suspicion, popularity, or social rumor.
  https://crates.io/policies
- Cargo’s overriding-dependencies docs say `[patch]` exists for testing bugfixes and carrying unpublished upstream work immediately. That makes local continuation a first-class operational lane rather than a hidden maintainer trick.
  https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
- Cargo’s source-replacement docs say replacement sources must contain **exactly the same source code** as the original source and are not appropriate for patching or private-registry divergence. That is a strong signal that mirrors and forks are different truths and should not share one narrative surface.
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- Cargo’s registries docs say alternate registries are real distribution lanes, but crates.io packages cannot depend on crates from other registries. That means “new home elsewhere” is possible, but it is not semantically the same as an ordinary crates.io successor.
  https://doc.rust-lang.org/cargo/reference/registries.html
- Cargo’s dependency docs say multiple locations let a package use a local git/path dependency while publishing against a registry version later. That creates a concrete bridge between local continuation and public named distribution, which should be reviewed rather than improvised.
  https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- The Rust Project’s crate-ownership policy explicitly names an **Expatriated** category for crates no longer intended to be official while still existing for external users. That proves the Rust ecosystem already has an official concept of continuity outside the original governing shell.
  https://forge.rust-lang.org/policies/crate-ownership.html
- The Rust Innovation Lab offers a neutral nonprofit home while keeping technical direction with current maintainers. That means some continuations are neither ad-hoc forks nor straight ownership transfers, but institutional relocations with real governance and funding implications.
  https://blog.rust-lang.org/2025/09/03/welcoming-the-rust-innovation-lab/
  https://rustfoundation.org/rust-innovation-lab/
- Rust’s March 2026 challenges post says ecosystem navigation still depends too much on tacit knowledge and choice paralysis. Forks, renamed successors, and alternate homes are exactly the sort of domain where invisible folklore currently dominates.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/

Together these signals say ideal Rust still needs a reviewable layer for **continuation without transfer** above lifecycle metadata and local overrides, beside succession, and below trust/admission/migration/distribution claims.

## What each neighboring stack owns

### Lifecycle Ledger Kit
[`design/lifecycle-ledger-kit.md`](./lifecycle-ledger-kit.md) owns:
- declared support, deprecation, and successor metadata;
- support windows;
- maintainer-help and handoff consent;
- lifecycle reports and diffs.

Its question is:
> what does the maintainer declare about support, deprecation, successors, and willingness to seek help or hand off?

Fork Continuity begins when a successor or fork claim needs stronger answers:
> if continuity will happen outside the original authority path, what kind of continuation is it and how should users consume it?

Design rule: **a successor pointer is not yet a trustworthy continuation route.**

### Succession Continuity Stack
[`design/succession-continuity-stack.md`](./succession-continuity-stack.md) owns:
- owner-approved co-maintainership;
- shared or transferred authority surfaces;
- overlap windows;
- institutional anchoring of transitions;
- proof that a handoff actually worked.

Its question is:
> how does continuity survive when authority is actually shared or transferred?

Fork Continuity begins when authority **does not** move cleanly, cannot move, or is deliberately kept separate.
Its question is:
> how does the ecosystem describe and consume continuity when the continuation is a sibling, successor, or divergence rather than a transfer?

Design rule: **continuation without transfer must not masquerade as succession.**

### Publisher & Source Identity Stack
[`design/publisher-source-identity-stack.md`](./publisher-source-identity-stack.md) owns:
- project/family claims;
- publish-authority facts;
- registry/source posture;
- downstream trust/policy/admission imports.

Its question is:
> who may publish what, under what source posture, and what identity claims are even in play?

Fork Continuity imports those facts to answer:
> what relationship to the origin is being claimed, and through which publication route is the continuation actually reaching users?

### Migration Kit
[`design/migration-kit.md`](./migration-kit.md) owns:
- concrete migration execution plans;
- code/config/data movement steps;
- migration readiness and exit criteria.

Its question is:
> how does a user or team actually move from A to B?

Fork Continuity owns the higher-level boundary:
> what is B, why is B related to A, and how strong is that continuity claim before a migration plan even begins?

### Trust Decision Stack / Package Admission Stack
[`design/trust-decision-stack.md`](./trust-decision-stack.md) and [`design/package-admission-stack.md`](./package-admission-stack.md) own:
- whether the continuation should be trusted or admitted;
- imported advisory/identity/policy evidence;
- actual admit/hold/warn decisions.

Their question is:
> should this package or route be allowed here?

Fork Continuity owns the prerequisite truth:
> what sort of continuation is this package actually claiming to be?

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these quickly:
1. Is this lane an owner-approved successor, a community continuation, a local emergency carry, a neutral-home relocation, or a more experimental divergence?
2. Where do users actually obtain it — local patch, git/path development override, new crates.io name, alternate registry, or another route?
3. What compatibility or migration claim is being made, and who is asserting it?
4. What evidence shows the continuation is alive enough to matter?
5. Is the lane meant to merge back, permanently diverge, supersede the origin, or expire?

If the stack cannot answer those five questions, it is still just a folk story about “the fork everyone knows to use”.

## What an epic contribution should look like in practice
A serious contribution here is **not** a forced-transfer service, public shame queue, fork marketplace, or global successor badge.
It is a thin `cargo continuation` / `continuation-pack/v0` layer that makes continuation routes explicit, reviewable, and bounded.

That means:
1. **import lifecycle and identity facts rather than replacing them**;
2. **treat local carries, public renamed successors, and alternate-registry homes as different lanes**;
3. **make authority relationship explicit** instead of letting users infer endorsement from naming or popularity;
4. **record compatibility and migration claims as claims with provenance** rather than letting one README sentence become canonical truth;
5. **require a continuity witness and an exit/rejoin posture** so a temporary carry cannot silently become a permanent fork mythology.

## Proposed artifact family

### `continuation-subject/v0`
Identifies the origin and the continuation subject.

Should record:
- origin crate/workspace/tool/service identity;
- continuation package/repo/registry identity;
- scope included and excluded;
- linked lifecycle/succession/identity artifacts;
- public versus restricted summary posture.

### `origin-relationship/v0`
States what relationship is being claimed.

Should record:
- relationship class (`owner-approved-successor`, `same-org-continuation`, `community-continuation`, `temporary-emergency-carry`, `alternate-registry-home`, `institutional-relocation`, `experimental-reboot`, `conceptual-successor`);
- who is asserting the relationship;
- verification level (`same-maintainer`, `same-org`, `explicit-owner-approval`, `registry-verified`, `institution-hosted`, `community-asserted`);
- reason text / reason codes;
- known disputes, unknowns, or non-claims.

Design rule: **relationship is not compatibility.**

### `continuation-intent/v0`
States what this continuation is for.

Should record:
- intent class (`keep-security-fixes-flowing`, `resume-general-maintenance`, `carry-blocking-fix`, `preserve-name-adjacent-ecosystem-home`, `change-governance`, `change-distribution-home`, `reboot-design`, `sunset-origin-with-successor`);
- expected duration (`temporary`, `open-ended`, `until-transfer`, `until-merge-back`, `permanent-divergence`);
- owner / sponsor / institution / maintainers in scope;
- explicit review date and next-decision trigger.

Design rule: **intent is not yet evidence that users should move.**

### `distribution-route/v0`
Describes how users actually consume the continuation.

Should record:
- route kind (`local-patch`, `git-multiple-location`, `path-multiple-location`, `renamed-crates-io-package`, `alternate-registry-package`, `neutral-home-republish`, `private-registry-only`);
- whether the route is local-only, org-local, or ecosystem-visible;
- whether the route is exact-copy, patch, or divergent code line;
- credential/auth/source posture where relevant;
- constraints and non-goals (for example, “crates.io package cannot depend on alternate-registry crate”).

Design rule: **distribution route is not endorsement.**

### `compatibility-migration-report/v0`
Captures the compatibility claim.

Should record:
- compatibility class (`drop-in`, `semver-adjacent`, `migration-required`, `data-migration-required`, `conceptually-related-only`);
- who assessed the compatibility;
- API / config / data / runtime differences;
- patchability / lockfile / registry consequences;
- linked migration guide or explicit absence of one.

Design rule: **compatibility without provenance is folklore.**

### `continuation-witness/v0`
Shows the continuation is operational.

Should record:
- releases or publish receipts;
- security or incident handling evidence;
- docs/support cadence;
- adoption evidence or institutional acceptance;
- continuity failure or stall signals if they appear.

Design rule: **announcement is not witness.**

### `continuation-exit/v0`
States how the continuation ends or stabilizes.

Should record:
- merge-back, owner-approved transfer, permanent divergence, superseded-by-other-successor, sunset, or unresolved;
- who can declare that exit;
- what evidence is needed;
- what downstream consumers should update.

Design rule: **temporary carries need a real end state.**

### `continuation-pack/v0`
Checksummed bundle containing:
- `continuation-subject/v0`
- `origin-relationship/v0`
- `continuation-intent/v0`
- `distribution-route/v0`
- optional `compatibility-migration-report/v0`
- optional `continuation-witness/v0`
- optional `continuation-exit/v0`
- linked lifecycle/succession/identity/migration/trust attachments
- bounded consumer handoffs.

## Ranked first execution lanes
1. **owner-approved renamed-successor lane**
   - prove that a package renamed for continuity can publish a clear relationship, migration posture, and witness without pretending transfer never happened.
2. **community continuation lane**
   - prove that a continuation can be explicit and reviewable even when the original owner is unreachable and the registry will not mediate.
3. **local emergency carry lane**
   - model the common path from `[patch]` or git override to either merge-back, named successor, or exit.
4. **neutral-home relocation lane**
   - prove that nonprofit or institutional hosting can be represented as a continuation route without collapsing into either “same project, nothing changed” or “totally new fork”.
5. **alternate-registry / private-home lane**
   - keep internal or enterprise continuations legible without pretending they are ordinary crates.io successors.
6. **reconciliation lane**
   - show how merge-back, supersession, or permanent divergence becomes visible to downstream migration/trust/admission consumers.

## Non-goals
- forced takeover or registry-namespace reclamation machinery;
- public scoreboards of which fork is “the real one”;
- silently treating popularity as legitimacy;
- conflating exact-copy mirrors with divergent continuations;
- assuming every continuation should become a public crates.io successor;
- replacing migration plans, trust policy, or package admission with one fork label.
