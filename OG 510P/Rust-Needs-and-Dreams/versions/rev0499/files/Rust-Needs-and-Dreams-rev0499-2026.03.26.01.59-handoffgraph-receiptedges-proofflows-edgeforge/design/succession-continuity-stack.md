# Design: Succession Continuity Stack (co-maintainership, authority transfer, continuity overlap, neutral homes)

## Goal
Treat **maintainer turnover and continuity transitions** as a first-class Rust ecosystem seam.

Rust has gotten better at saying that maintenance matters, that keystone projects deserve backing, and that real support lanes now exist.
But the archive still lacked a compact answer to a harder question:

> when a Rust crate, tool, service, or team needs continuity through maintainer change, **what exactly has to move, in what order, under what authority, with what overlap, and with what proof that continuity is real rather than merely hoped for?**

That missing layer is **not** just lifecycle metadata, and it is **not** just support routing.
It sits between them.
The continuity problem is not one blob called “succession.”
It contains distinct truths that ideal Rust should keep separate and reviewable:
- **continuity-subject truth** — which crate, workspace, tool, service, release line, or team is under continuity review;
- **intent truth** — whether the current maintainer wants co-maintainership, temporary relief, transfer, neutral hosting, or only a narrower delegation;
- **authority-surface truth** — which concrete powers must move or be shared: crates.io ownership, publish authority, Trusted Publishing settings, CI workflows, release pipelines, domains/docs/repo roles, policy authority, incident contacts, or fiscal/governance hooks;
- **overlap-and-transfer truth** — who overlaps with whom, what runbooks or release knowledge must move, what is delegated versus retained, and what date/condition ends the overlap;
- **institutional-anchor truth** — whether the answer is an individual co-maintainer, an org/team handoff, a fiscal sponsor, a neutral home, or a stronger governance shell;
- **continuity-proof truth** — what evidence shows the transition actually worked: a release happened, a security response worked, a docs/update cadence continued, or a route failed and needs escalation.

The point is to stop flattening “we found someone new” and “continuity is now real” into the same sentence.

## Why this seam matters now
Official Rust/Foundation/Cargo signals are unusually aligned here:
- The Rust Foundation’s 2026–2028 strategy explicitly calls for funding models for ongoing maintenance, transparent support criteria, contributor→maintainer pathways, and support for under-resourced core crate owners. That is continuity language, not only maintenance language.
  https://rustfoundation.org/strategic-plan/
- The Rust Foundation Maintainers Fund announcement says the fund will be shaped openly and with accountability, should provide reliable support, and should align with Rust Project priorities. That means “support” increasingly has to survive personnel change rather than only easing today’s queue pressure.
  https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/
- The maintenance writeup says maintenance is broad and ongoing in Rust and is not reducible to visible feature work. That is exactly why continuity transfer needs explicit artifacts: invisible work is the first thing that disappears during a bad handoff.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- The October 2025 program-management update says some Rust teams rely on one or two people just to stay afloat, and that long-term maintainers losing jobs has made sustainable support urgent. That is a direct continuity-risk signal.
  https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/
- crates.io policy says ownership transfer requires explicit current-owner approval. That is a strong reminder that succession cannot be approximated from inactivity, popularity, or social rumor; authority transfer is a real design surface.
  https://crates.io/policies
- crates.io now supports Trusted Publishing for multiple CI providers and a Trusted-Publishing-only mode, which means publish authority can be centralized in automation and must be intentionally re-routed during maintainer transition.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo’s publishing docs say publish tokens live in local credentials and should be revoked if leaked. That is another concrete continuity seam: the question is not only “who will maintain this crate?” but also “which secrets, automations, and authority paths are being retired or replaced?”
  https://doc.rust-lang.org/cargo/reference/publishing.html
- The Rust Innovation Lab shows a real continuity lane above simple co-maintainership: a stable, neutral home with governance support, legal/admin backing, and fiscal sponsorship for important Rust infrastructure.
  https://rustfoundation.org/rust-innovation-lab/
  https://rustfoundation.org/media/rust-foundation-launches-rust-innovation-lab-with-rustls-as-inaugural-project/
- The Rust Foundation’s sustainable-stewardship statement says package infrastructure already carries rising costs while depending on a small set of organizations and individuals. That is ecosystem continuity pressure, not only project-local burnout.
  https://rustfoundation.org/media/rust-foundation-signs-joint-statement-on-open-source-infrastructure-stewardship/

Together these signals say ideal Rust still needs a reviewable layer for **continuity transition** above lifecycle intent and support routing, and below release/trust/admission/institutional claims.

## What each neighboring stack owns

### Lifecycle Ledger Kit
[`design/lifecycle-ledger-kit.md`](./lifecycle-ledger-kit.md) owns:
- declared lifecycle state;
- successor metadata;
- support windows;
- maintainer-help or handoff consent.

Its question is:
> what does the maintainer declare about support, deprecation, successor posture, and willingness to seek help or transfer?

Design rule: **declared succession intent is not the same as a workable continuity plan.**

### Stewardship Support Routing Stack
[`design/stewardship-support-routing-stack.md`](./stewardship-support-routing-stack.md) owns:
- intervention-class selection;
- privacy/eligibility posture;
- support-route decisions;
- accepted or declined backing.

Its question is:
> what kind of help should be routed here?

Succession Continuity begins when the selected route implies an actual transfer or shared-control program.
Its question is:
> how does that route become a real, safe, reviewable continuity transition?

### Publisher & Source Identity Stack
[`design/publisher-source-identity-stack.md`](./publisher-source-identity-stack.md) owns:
- project/family claims;
- publish-authority facts;
- registry/source posture;
- trust/policy consumer imports.

Its question is:
> who may publish, under what source/authority posture?

Succession Continuity imports those facts to answer:
> which authority surfaces must change, and which can remain delegated or automated?

### Keystone Stewardship Stack
[`design/keystone-stewardship-stack.md`](./keystone-stewardship-stack.md) owns:
- criticality and blast radius;
- obligations that follow;
- escalation significance.

Its question is:
> why does this subject matter enough that continuity risk is unusually costly?

Design rule: **keystone status raises continuity stakes; it does not by itself solve continuity mechanics.**

### Institutional Overlay Stack
[`design/institutional-overlay-stack.md`](./institutional-overlay-stack.md) owns:
- durable local defaults;
- org-local rules;
- local governance deltas.

Its question is:
> what does normal policy look like inside this institution or host?

Succession Continuity owns the transition boundary where a project might move into a new org/team/home in the first place.

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these quickly:
1. What continuity event is actually being attempted: relief, shared stewardship, transfer, institutionalization, or emergency replacement?
2. What authority surfaces must move, and which should remain with the prior steward during overlap?
3. What knowledge/runbook/release/incident responsibilities must be transferred, not merely named?
4. What proof will show the new arrangement is functioning?
5. What happens if the new arrangement fails, stalls, or only partially lands?

If the stack cannot answer those five questions, it is still just a good-faith handoff story.

## What an epic contribution should look like in practice
A serious contribution here is **not** an automatic ownership-transfer engine, public pressure mechanism, or forced escrow system.
It is a thin `cargo succession` / `continuity-pack/v0` layer that makes continuity transitions explicit, reviewable, and safely bounded.

That means:
1. **import declared lifecycle and support-route intent rather than replacing them**;
2. **model concrete authority surfaces** instead of pretending every transition is only social;
3. **support overlap windows and partial delegation** instead of assuming instant total transfer;
4. **treat institutionalization as one lane among several** rather than the universal answer;
5. **require continuity proof** so “new maintainer announced” does not count as “continuity secured”.

## Proposed artifact family

### `succession-subject/v0`
Identifies the subject under continuity review.

Should record:
- crate/workspace/tool/service/team identity;
- scope included and excluded;
- release lines and registries in scope;
- linked lifecycle/support/keystone artifacts;
- public versus restricted summary posture.

### `succession-intent/v0`
States what transition is actually being attempted.

Should record:
- intent class (`co-maintainer`, `release-relief`, `shared-publish`, `full-transfer`, `institutional-hosting`, `emergency-replacement`, `sunset-with-successor`);
- who is stepping back, staying involved, or entering;
- why this transition exists now;
- urgency, review date, and explicit unknowns.

Design rule: **intent is not yet execution.**

### `authority-surface-map/v0`
Maps the concrete powers and obligations that continuity must cover.

Should record surfaces like:
- crates.io owners / teams;
- Trusted Publishing configuration and allowed CI issuers;
- local API tokens or token retirement plans;
- repo/org/admin roles;
- release pipeline control;
- incident/security contact lanes;
- domain/docs/service ownership;
- fiscal/governance/admin authority where relevant.

Design rule: **authority surfaces are plural.**
A project can “change maintainer” while leaving the dangerous or operationally critical powers untouched.

### `continuity-overlap-plan/v0`
Makes overlap and knowledge transfer explicit.

Should record:
- overlap start/end or trigger conditions;
- release shadowing or paired-review windows;
- docs/runbook/credential rotation tasks;
- retained vetoes or retained obligations;
- proof checkpoints.

Design rule: **overlap is a real lane, not an embarrassing intermediate state.**

### `continuity-anchor/v0`
Declares what durable home the transition points toward.

Examples:
- existing maintainer + added co-maintainer;
- org/team stewardship;
- employer-backed maintainer time;
- neutral nonprofit/fiscal sponsor;
- bounded emergency steward;
- no durable anchor yet.

Design rule: **a continuity plan without an anchor may still be useful, but it should say so plainly.**

### `continuity-witness/v0`
Records what actually happened.

Should record:
- accepted / partial / failed / reversed / renewed state;
- specific authority changes completed;
- release or incident drills executed under the new arrangement;
- unresolved gaps;
- next review or escalation trigger.

Design rule: **announcement is not witness.**

### `continuity-pack/v0`
Bundle format linking:
- `succession-subject/v0`
- `succession-intent/v0`
- `authority-surface-map/v0`
- optional `continuity-overlap-plan/v0`
- optional `continuity-anchor/v0`
- optional `continuity-witness/v0`
- imported lifecycle/support/identity/keystone artifacts.

## Ranked first execution lanes
1. **co-maintainer / release-relief lane**
   - best first proof because it exercises overlap, limited authority sharing, and continuity witness without demanding full transfer.
2. **publish-authority transition lane**
   - prove crates.io owner changes, Trusted Publishing reroutes, and token retirement as explicit surfaces.
3. **keystone project institutionalization lane**
   - prove when a project needs a neutral home, governance support, or fiscal sponsorship rather than only another individual maintainer.
4. **emergency continuity lane**
   - prove the stack can handle sudden maintainer loss, job loss, or urgent incident-response continuity without pretending the answer is already durable.
5. **consumer handoff lane**
   - only after the above should trust/admission/atlas/support-program consumers summarize continuity posture.

## Anti-goals
Do not turn this stack into:
- a community pressure tool for taking over crates;
- an inactivity-triggered transfer mechanism;
- a global leaderboard of “healthy” versus “abandoned” projects;
- a secret escrow system that bypasses crates.io policy;
- or one more generic governance essay with no artifact surfaces.

The stack is about **reviewable continuity transition**, not forced centralization.
