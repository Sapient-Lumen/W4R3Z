# Design note: Stewardship Support Routing Stack (Maintenance Reality + Keystone Stewardship + institutional support lanes)

## Goal
Define the **division of labor and routing boundary** between maintenance evidence, keystone/criticality evidence, and the concrete support lanes that can respond.

Rust now has stronger signals that maintenance and infrastructure support matter, but it still lacks a compact answer to a practical ecosystem question:

> when a Rust crate, tool, service, or team is stretched, critical, or continuity-sensitive, **what kind of help should be routed, by whom, under what constraints, and until what exit?**

This note is **not** a grant portal, public health dashboard, or hidden allocator.
It is a stack note explaining how existing archive pieces should compose:
- [`design/maintenance-reality-stack.md`](./maintenance-reality-stack.md)
- [`design/lifecycle-ledger-kit.md`](./lifecycle-ledger-kit.md)
- [`design/stewardship-ops-kit.md`](./stewardship-ops-kit.md)
- [`design/stewardship-pilot-program.md`](./stewardship-pilot-program.md)
- [`design/keystone-stewardship-stack.md`](./keystone-stewardship-stack.md)
- [`design/institutional-overlay-stack.md`](./institutional-overlay-stack.md)
- [`design/policy-kit.md`](./policy-kit.md)
- [`design/ecosystem-incident-response-stack.md`](./ecosystem-incident-response-stack.md)

## Why this note is needed now
Rust’s current signals are no longer saying only “maintenance matters” or “critical projects deserve support” in the abstract.
They are saying there are now **multiple real support lanes**, with different shapes, obligations, privacy needs, and review consequences:
- the Rust Foundation’s 2026–2028 strategy is explicitly about strengthening infrastructure, sustaining maintainers, growing adoption, and empowering the community;
- the Rust Foundation Maintainers Fund is being designed for transparent, accountable, long-term maintainer support aligned with Rust Project priorities and continuity needs;
- the Rust Foundation’s maintenance writeup says maintenance is broad, often invisible, and burnout-sensitive, which means help requests cannot be reduced to “more commits” or “this bug is urgent”;
- the October 2025 program-management update says maintenance often loses out to feature funding and that some teams effectively rely on one or two people just to stay afloat;
- the Rust Innovation Lab shows a different support lane entirely: not stipends, but fiscal sponsorship, governance, legal, networking, marketing, and administrative backing in a neutral nonprofit environment; and
- the 2025 State of Rust survey says concern about developer/maintainer support persists and explicitly asks companies to support Rust contributors and crate authors they depend on.

Together these signals say the missing layer is no longer only “show maintenance reality” or “identify keystone projects”.
The missing layer is the boundary that keeps these distinct truths separate:
- **support need**,
- **support class**,
- **eligibility / privacy / governance constraints**,
- **selected route**,
- and **accepted or declined backing**.

Without that layer, Rust keeps falling into two bad patterns:
1. **dashboard without intervention** — we can see that something is strained, but not what kind of help should actually follow; and
2. **support without reviewability** — funding, co-maintainership, fiscal sponsorship, or emergency relief happens, but the surrounding need, scope, and exit remain folklore.

## Stack layers

### 1) Maintenance Reality Stack: evidence that help may be needed
[`design/maintenance-reality-stack.md`](./maintenance-reality-stack.md) owns:
- declared lifecycle posture;
- queue policy, snapshots, and pressure findings;
- explicit help requests and mentoring capacity;
- support-window and successor/handoff intent;
- visibility policy around public versus restricted operational signals.

Its question is:
> what is the day-to-day maintenance and continuity reality, and where is strain or explicit need already visible?

Design rule: **Maintenance Reality proves there may be a need, but it should not silently decide which intervention is appropriate.**

### 2) Keystone Stewardship Stack: why the project matters and what obligations follow
[`design/keystone-stewardship-stack.md`](./keystone-stewardship-stack.md) owns:
- criticality classification and blast radius;
- governance and stewardship posture;
- current institutional support posture;
- continuity and obligation expectations;
- keystone risk registers and transitions.

Its question is:
> why does this subject matter enough that continuity or institutional support needs special treatment?

Design rule: **criticality is not the same thing as support selection.**
A keystone project can still need only a small intervention; a non-keystone project can still need an urgent bounded one.

### 3) Stewardship Support Routing Stack: selecting the right intervention class
This new layer owns:
- what support classes are in play;
- what evidence justifies each class;
- what privacy and governance constraints apply;
- what route is selected or declined;
- and what review/expiry cadence keeps the support honest.

Its question is:
> given the support need and the project context, what kind of help is actually warranted here, and how should that help be routed?

This layer should keep the following support classes visibly separate:
- **volunteer help** — triage, review, docs, reproductions, mentoring;
- **role help** — co-maintainer, release-manager, ops relief, succession support;
- **paid maintainer support** — stipend, contract, employer-funded time, maintainer-fund support;
- **institutional support** — fiscal sponsorship, legal/admin support, governance hosting, infrastructure backing;
- **restricted-response support** — incident or security handling where raw details cannot be fully public;
- **local/org support** — company or institutional overlays that only apply inside one adoption context.

Design rule: **support routing is a choice among intervention classes, not one scalar “support score”.**

### 4) Succession Continuity Stack: making routed continuity help real
[`design/succession-continuity-stack.md`](./succession-continuity-stack.md) owns the transition mechanics that begin once a selected route implies real continuity change:
- co-maintainer addition versus full transfer;
- publish-authority and Trusted-Publishing changes;
- release/incident overlap windows;
- knowledge/runbook handoff;
- institutional anchoring and continuity witness.

Its question is:
> once a continuity-sensitive route is selected, how does that route become a real, reviewable transition instead of a hopeful announcement?

Design rule: **support routing chooses the intervention class; Succession Continuity owns the handoff/overlap/authority-transfer program when continuity must actually change.**

### 5) Downstream support programs and consumers
This layer becomes worthwhile only when real consumers can import it without collapsing the facts.
Examples include:
- Rust Foundation Maintainers Fund style decisions;
- Innovation Lab / neutral-hosting lanes;
- local company or consortium support programs;
- maintainer-coordination groups seeking co-maintainers or release relief;
- Atlas / adoption / keystone consumers wanting a bounded summary;
- incident or release consumers that need to know what support lane became active;
- assistants and dashboards that should summarize the route, not invent one.

Design rule: **consumers import a reviewed route; they do not infer it from raw popularity or queue stats alone.**

## What an epic contribution should look like in practice
A worthy contribution here is not “build a global maintainer allocator”.
It is a thin `cargo supportroute` / `support-route-pack/v0` layer that makes real intervention choices portable and reviewable.

That means:
1. **import existing evidence instead of rescoring the world**
   - import lifecycle, stewardship, keystone, incident, and local-overlay evidence rather than replacing them;
2. **keep intervention classes first-class**
   - do not flatten volunteer help, paid maintainer support, and institutional hosting into one bucket;
3. **make privacy and governance posture explicit**
   - some support requests can be public, some restricted, some only summary-shareable;
4. **make the route reviewable over time**
   - why this route, who owns it, when is it revisited, and what ends it;
5. **make exits explicit**
   - accepted support should not silently become a permanent obligation when it was meant as a bridge or bounded intervention.

## Proposed artifact family
The lower kits should keep owning their native artifacts.
This stack should remain thin and route-facing.

### `support-subject/v0`
Identifies the subject under review:
- crate / workspace / tool / service / team identity;
- scope included and excluded;
- linked maintenance/keystone source artifacts;
- public versus restricted subject notes.

### `support-need-profile/v0`
States what need is being reviewed:
- need class (`triage-overload`, `review-bottleneck`, `release-pressure`, `succession-risk`, `criticality-without-backing`, `incident-support`, `institutionalization-need`, etc.);
- urgency and expected duration;
- evidence slice imported from maintenance/keystone/incident artifacts;
- explicit unknowns and non-claims.

Design rule: **need is not yet route.**

### `support-lane-catalog/v0`
Declares which intervention classes exist in a given environment:
- volunteer help lanes;
- co-maintainer / release-relief lanes;
- stipends / grant / contract lanes;
- employer-time / sponsor lanes;
- fiscal sponsorship / governance-hosting lanes;
- restricted security/incident lanes;
- local-only overlays.

Should record:
- minimum evidence expectations;
- privacy requirements;
- governance constraints;
- incompatibilities and non-goals.

Design rule: **catalogs are environment-specific; they are not one global Rust constitution.**

### `support-routing-decision/v0`
The selected route.

Should record:
- chosen intervention class or deliberate no-route decision;
- why this lane was selected over nearby alternatives;
- owner / sponsor / host / coordinator;
- public summary versus restricted detail posture;
- review date / expiry / next decision trigger;
- explicit exit conditions.

Design rule: **a route is a reviewed decision, not a descriptive tag.**

### `support-acceptance-report/v0`
What actually happened after routing.

Should record:
- accepted / declined / pending / partial states;
- support actually provided;
- duration and conditions;
- obligations created or explicitly not created;
- follow-up or renewal posture.

Design rule: **selection is not acceptance, and offer is not continuity.**

### `support-transition-report/v0`
Before/after posture changes.

Should capture:
- what need was being addressed;
- what support posture changed;
- what remained unresolved;
- whether the route reduced queue pressure, continuity risk, or criticality mismatch;
- whether the support should now downgrade, renew, or hand off elsewhere.

### `support-route-pack/v0`
Checksummed bundle containing:
- `support-subject/v0`
- `support-need-profile/v0`
- `support-lane-catalog/v0` or pointer
- `support-routing-decision/v0`
- optional `support-acceptance-report/v0`
- optional `support-transition-report/v0`
- imported maintenance/keystone/incident/local-overlay attachments
- bounded consumer handoffs.

## Ranked first execution lanes
1. **maintainer-help routing lane**
   - convert explicit help requests and queue pressure into a reviewable decision between volunteer relief, co-maintainer search, release help, or “monitor only”.
2. **keystone continuity lane**
   - for projects with real blast radius, distinguish “this deserves neutral backing” from “this just needs some review relief”.
3. **fiscal sponsorship / governance-hosting lane**
   - prove that neutral-hosting routes can be represented without pretending every project needs a foundation home.
4. **paid maintainer-support lane**
   - separate direct maintainer support or employer-funded time from more structural interventions.
5. **incident-linked support lane**
   - prove that containment/reissue pressure can request bounded support without turning incident response into a permanent support claim.
6. **public-summary / restricted-detail lane**
   - show how to publish enough route truth for ecosystem coordination without overexposing sensitive operational details.

## Non-goals
- a public leaderboard of “most deserving” projects;
- automatic support allocation from stars, downloads, or commit counts;
- replacing maintainer judgment, foundation governance, or local sponsor decisions;
- collapsing every help request into a funding problem;
- forcing every route to be public;
- treating accepted support as a forever commitment unless that was explicitly declared.

## Archive implications
- The archive should now treat **support routing** as its own seam above Maintenance Reality and beside Keystone Stewardship, rather than leaving it as one paragraph inside stewardship pilots.
- Future revisions should prefer **reviewable intervention classes, explicit privacy posture, and acceptance/exit artifacts** over vague language like “this project needs more support”.
- Maintainers Fund, Innovation Lab, sponsor, overlay, incident, and release-support discussions should now import **need evidence**, **route choice**, **accepted backing**, and **review/exit posture** separately.
- The existing `support-routing-profile/v0` idea inside [`design/stewardship-pilot-program.md`](./stewardship-pilot-program.md) should be treated as an early proving surface for this broader stack rather than the whole answer.

## References (signals)
- Rust Foundation Strategic Plan: 2026–2028:
  https://rustfoundation.org/strategic-plan/
- Rust Foundation Maintainers Fund announcement:
  https://rustfoundation.org/media/announcing-the-rust-foundation-maintainers-fund/
- What is maintenance, anyway?
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- Program management update — October 2025:
  https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/
- Rust Foundation launches Rust Innovation Lab with Rustls:
  https://rustfoundation.org/media/rust-foundation-launches-rust-innovation-lab-with-rustls-as-inaugural-project/
- 2025 State of Rust survey results:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
