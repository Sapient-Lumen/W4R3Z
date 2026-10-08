# Design: Sunset Transition Stack (honest narrowing or ending of support without pretending code disappears)

## Goal
Treat **support narrowing, retirement, and honest end-of-life** as a first-class Rust ecosystem seam.

Rust has gotten better at talking about maintenance, support windows, successors, succession, and continuation.
But the archive still lacked a compact answer to a harder question:

> when a Rust crate, workspace, tool, or service should **stop being a normal default choice** — because support is narrowing, maintainers are stepping back, the domain is moving, or a successor exists — how should the ecosystem describe that transition honestly when the registry remains a durable archive and many users will keep encountering the old artifact anyway?

That missing layer is **not** just lifecycle metadata.
It is **not** just succession.
And it is **not** just fork continuity.
It sits beside them.
The retirement problem is not one blob called “deprecated”.
It contains distinct truths that ideal Rust should keep separate and reviewable:
- **sunset-subject truth** — which crate, workspace, tool, service, feature surface, or version line is actually narrowing or ending support;
- **narrowing-or-retirement intent truth** — whether the move is security-fix-only, compatibility-frozen, maintenance-only, deprecated-with-successor, deprecated-without-successor, archived, emergency-retired, or fully sunset;
- **last-supported-line truth** — which versions, platforms, MSRV bands, registries, or feature lanes remain supported and until when;
- **replacement-or-no-successor truth** — whether users should stay put, migrate to a successor, adopt a community continuation, carry locally, or accept that there is no blessed replacement;
- **registry-and-archive action truth** — whether the practical action is “do nothing but publish metadata”, yank a broken version, delete only if strict policy allows, archive the repo, freeze publishing, or move maintenance elsewhere;
- **consumer-off-ramp truth** — what migration guidance, warnings, support promises, or explicit non-promises downstream users receive;
- **closure-witness truth** — what evidence shows the sunset state is real: a published last-good line, a support-window declaration, a successor migration guide, a closing security note, or an explicit end-of-support announcement;
- **re-entry-or-terminal-state truth** — whether the subject may re-open, be adopted by a successor, be superseded by a fork, remain archived indefinitely, or disappear only under narrow deletion rules.

The point is to stop flattening “deprecated badge semantics”, “one yank”, “archived repo”, “no longer maintained”, and “please use this successor instead” into the same sentence.

## Why this seam matters now
Official Rust/Foundation/Cargo signals are unusually aligned here:
- Cargo’s manifest docs still define maintenance states such as `passively-maintained`, `as-is`, `looking-for-maintainer`, and `deprecated`, but they also say crates.io no longer displays badges directly. That means Rust still has lifecycle vocabulary without a strong shared review surface on the main registry.
  https://doc.rust-lang.org/cargo/reference/manifest.html
- Cargo’s publishing docs say a yank does **not** delete code, existing lockfiles continue to work, and crates.io aims to be a permanent archive. That means support withdrawal is not the same thing as disappearance.
  https://doc.rust-lang.org/cargo/reference/publishing.html
- RFC 3660 says crate deletion remains tightly constrained, and older or depended-on crates generally should not vanish. That means many real Rust artifacts will remain discoverable long after maintainers want users to stop selecting them by default.
  https://rust-lang.github.io/rfcs/3660-crates-io-crate-deletions.html
- RFC 3646 says the crates.io team wants to stop mediating transfer requests, and if the current owner is unreachable you should expect to pick a different name. That means sunset often borders, but should not be confused with, successor or continuation routes.
  https://rust-lang.github.io/rfcs/3646-remove-crate-transfer-mediation-policy.html
- The Rust Foundation’s 2026–2028 strategy centers sustainable maintenance and continuity, while the maintenance writeup says maintenance is ongoing, broad, and burnout-sensitive. Together those signals say narrowing support or retiring a project can be a legitimate stewardship act rather than proof of neglect.
  https://rustfoundation.org/strategic-plan/
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- Rust’s March 2026 challenges post says ecosystem navigation still depends too much on tacit knowledge and choice paralysis. Sunset state that lives only in READMEs, stale badges, or rumor makes that problem worse.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/

Together these signals say ideal Rust still needs a reviewable layer for **honest off-ramps** above lifecycle metadata, beside succession/fork routes, and below trust/admission/migration decisions.

## What each neighboring stack owns

### Lifecycle Ledger Kit
[`design/lifecycle-ledger-kit.md`](./lifecycle-ledger-kit.md) owns:
- declared lifecycle states;
- support windows;
- successor metadata;
- maintainer-help and handoff consent;
- lifecycle reports and diffs.

Its question is:
> what lifecycle facts are being declared or observed?

Sunset Transition begins when the archive needs a stronger answer:
> how does a project actually move from ordinary support to narrowed support or retirement, and what should downstream users do next?

Design rule: **lifecycle state is not yet a sunset program.**

### Succession Continuity Stack
[`design/succession-continuity-stack.md`](./succession-continuity-stack.md) owns:
- authority sharing or transfer;
- overlap windows;
- institutional continuity anchors;
- proof that a handoff actually worked.

Its question is:
> how does continuity survive when authority actually moves?

Sunset Transition begins when authority is **not** the center of the story.
Its question is:
> if support is narrowing or ending, what remains supported, what replaces it if anything, and how is that exit made legible?

Design rule: **not every sunset is a succession event.**

### Fork Continuity Stack
[`design/fork-continuity-stack.md`](./fork-continuity-stack.md) owns:
- continuation without transfer;
- relationship claims to the origin;
- public/local distribution routes for continuations;
- compatibility and witness posture for forks or renamed successors.

Its question is:
> if continuity exists outside the original authority path, what continuation route is being claimed?

Sunset Transition owns the sibling question:
> is the origin narrowing or ending support, and what off-ramp should downstream users follow even if the answer is “none yet”?

Design rule: **a sunset may point to a continuation, but it is not itself the continuation.**

### Migration Kit
[`design/migration-kit.md`](./migration-kit.md) owns:
- concrete move plans;
- data/config/code transitions;
- migration readiness and completion.

Its question is:
> how does a user actually move from A to B?

Sunset Transition owns the prior boundary:
> why should a user stop selecting A in the first place, and how much support remains while they decide?

### Trust Decision / Package Admission
[`design/trust-decision-stack.md`](./trust-decision-stack.md) and [`design/package-admission-stack.md`](./package-admission-stack.md) own:
- whether a subject should be trusted, warned on, held, or admitted;
- imported lifecycle, incident, identity, and policy evidence.

Their question is:
> should we still allow or recommend this here?

Sunset Transition owns the prerequisite truth:
> what kind of narrowing or retirement actually happened, and what off-ramp posture is being asserted?

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these quickly:
1. What exactly is sunsetting: the whole subject, one line, one feature lane, one target set, or only active feature work?
2. Is the move “security-fix-only”, “frozen but acceptable as-is”, “deprecated with successor”, “deprecated without successor”, or “archived”? 
3. What line remains supported, if any, and until when?
4. Is there a successor, a continuation, a local-carry recommendation, or explicitly **no** replacement?
5. What registry/archive actions are actually being taken: metadata only, yank, limited deletion, repo archival, or something else?
6. What should downstream users do now, and what promises should they **not** infer?
7. Is this sunset terminal, reversible, or expected to lead into succession/continuation later?

If the stack cannot answer those questions, it is still just a folk story about “this crate is kind of dead”.

## What an epic contribution should look like in practice
A serious contribution here is **not** another badge scheme, graveyard site, or hidden deprecation score.
It is a thin `cargo sunset` / `sunset-pack/v0` layer that makes narrowed support and end-of-life routes explicit, reviewable, and bounded.

That means:
1. **import lifecycle facts rather than replacing them**;
2. **treat support narrowing, deprecation, archiving, yanking, and true deletion as different lanes**;
3. **make replacement posture explicit**, including “no successor yet”;
4. **keep last-supported lines and support-window truth visible** rather than collapsing them into one deprecated bit;
5. **attach consumer off-ramps and non-promises** so downstream users know whether to migrate, carry, or stay on a frozen line knowingly;
6. **require closure witness and end-state posture** so an announced sunset can later be reviewed for whether it actually happened.

## Proposed artifact family

### `sunset-subject/v0`
Identifies what is narrowing or ending support.

Should record:
- subject identity;
- in-scope and out-of-scope components or version lines;
- related lifecycle / succession / continuation artifacts;
- current state before the sunset move.

### `support-narrowing-plan/v0`
States what is changing.

Should record:
- transition class (`security-fix-only`, `maintenance-only`, `compatibility-frozen`, `deprecated`, `archived`, `emergency-retired`, `sunset-complete`);
- effective date;
- review date or expiry if reversible;
- reason classes (`burnout-risk`, `domain-retired`, `successor-ready`, `security-risk`, `merge-into-other-project`, `no-capacity`, `experimental-conclusion`, ...);
- remaining support promises and explicit non-promises.

Design rule: **support narrowing is more specific than “deprecated”.**

### `last-supported-map/v0`
Describes what still counts as supported.

Should record:
- remaining supported versions / branches / MSRV bands / target sets;
- support class per line;
- support end dates or “indefinite but frozen” posture;
- backport or patch posture if any.

Design rule: **a sunset can leave a real supported tail.**

### `replacement-posture/v0`
States what users should do next.

Should record:
- replacement class (`verified-successor`, `community-continuation`, `local-carry`, `migrate-to-standard-library`, `no-replacement`, `case-by-case`);
- who asserts it;
- verification level;
- compatibility and migration summary;
- explicit absence of replacement when true.

Design rule: **“no successor” is a meaningful answer and should be representable.**

### `archive-action-report/v0`
Describes registry/repo/archive actions.

Should record:
- action class (`metadata-only`, `repo-archived`, `publish-frozen`, `selective-yank`, `delete-under-policy`, `docs-pointer-update`, `security-note-attached`);
- why that action was chosen;
- lockfile / install / discoverability consequences;
- linked publish/delete/yank receipts where relevant.

Design rule: **yank, archive, and delete are different operations with different guarantees.**

### `consumer-offramp/v0`
Explains downstream expectations.

Should record:
- intended audiences;
- migration recommendation or explicit absence;
- time budget / urgency / risk posture;
- enterprise or long-tail compatibility notes;
- support channels that remain or are ending.

Design rule: **consumer guidance is not the same thing as maintainer intent.**

### `sunset-witness/v0`
Shows the transition actually landed.

Should record:
- published last-good line or tagged terminal release;
- updated docs / README / registry pointers;
- successor or continuation links if present;
- incident or security notes if relevant;
- observed unresolved ambiguity.

Design rule: **announcement is not witness.**

### `sunset-end-state/v0`
States what happens after the transition.

Should record:
- terminal archive, frozen-supported tail, successor-led migration, reversible pause, or later succession/fork route;
- who can re-open or supersede the sunset;
- what evidence would change the state.

Design rule: **sunset should end somewhere reviewable, even if that end is “archived indefinitely”.**

### `sunset-pack/v0`
Checksummed bundle containing:
- `sunset-subject/v0`
- `support-narrowing-plan/v0`
- optional `last-supported-map/v0`
- optional `replacement-posture/v0`
- optional `archive-action-report/v0`
- optional `consumer-offramp/v0`
- optional `sunset-witness/v0`
- optional `sunset-end-state/v0`
- linked lifecycle / succession / continuation / migration / trust attachments.

## Ranked first execution lanes
1. **deprecated-with-successor lane**
   - prove that a maintainer can narrow support and direct users to a successor without pretending the old artifact vanished.
2. **security-fix-only tail lane**
   - prove that a line can remain intentionally supported but non-evolving, with last-supported-window truth explicit.
3. **no-successor lane**
   - model the honest but awkward case where maintainers step back and there is no blessed replacement yet.
4. **repo-archived but registry-persistent lane**
   - make visible the difference between an archived repository and a still-installable crate.
5. **selective-yank / broken-version lane**
   - keep tactical yanks distinct from broader retirement intent.
6. **later-continuation lane**
   - show how sunset state can later hand off into succession or fork continuity without rewriting history.

## Non-goals
- a universal deprecation score;
- automatic hiding or delisting of old packages;
- replacing trust/admission decisions with a sunset label;
- treating yanks as a general end-of-life mechanism;
- pretending deletion is broadly available or desirable;
- assuming every sunset should point to a successor.
