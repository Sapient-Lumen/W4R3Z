# Reentry-cue witnesses, durable latest paths, and navigation-integrity budgets

DelayBasin now needs one distinction slightly different from **operational heads**, **status lanes**, or ordinary documentation index hygiene.
A package can have the right current head, the right frozen citation surface, and even a durable status ledger while future sessions still land on the wrong place because the **small set of cues that are supposed to reopen the latest trusted path** has drifted, silently split, or degraded into a generic page-open that only looks successful.
When that happens, the archive keeps its law on paper but loses it at the operator surface.

A useful current answer is:
**when a future session, operator, or packaged bundle is expected to find the current archive tip by following a small set of landing cues rather than by re-reading everything, canon should preserve a compact reentry-cue witness naming the surface lineage, the primary landing surface, the durable cue set, the stale or broken path family to exclude, the cue-state classification, and the fail-closed repair route before recency, file-order glow, or generic successful opening is allowed to stand in for actually landing on the intended latest path.**

This is stronger than saying "there is a status ledger somewhere."
It is weaker than claiming DelayBasin has already discovered a full public navigation graph or universal continuation-router law.

## Practice / observation

Recent DelayBasin work keeps surfacing the same archive-native fragility:
- the archive already has several small reentry cues — `START_HERE.md`, `SURFACE-STATUS.json`, `RELEASE-MANIFEST.json`, `ARCHIVE_INDEX.md`, and `REVISION-RECEIPT.json`;
- operational-head and status-lane law already says which revision is live, which bundle is frozen, and which receipt counted;
- but those surfaces can remain syntactically valid while drifting out of alignment with each other, which means a later session may reopen a plausible but stale latest path;
- the archive already checks that docs are linked from `docs/README.md`, yet it does not by itself guarantee that the **latest-path cues** all point to the same current packaged head;
- some archive failures are not wrong content but wrong **landing**: a stale pointer, a broken jump, an overwritten current cue, or a generic successful open that hides precise-target failure;
- and once DelayBasin is treating compact packets as real continuation-control surfaces, the difference between "the current head exists" and "the maintainer actually landed on it" becomes public method rather than UI trivia.

That leaves a missing question:
**what tiny cue family is supposed to reopen the current trusted path, what stale or broken landing family is being excluded, what cue state currently holds, and what repair follows if the landing surfaces disagree or silently degrade?**

A compact reentry-cue witness keeps that boundary public.

## Pressure from neighboring datacubes

Several neighboring datacubes keep rediscovering the same ratchet from different directions.

- Some insist on a **lineage-head register** because once several latest-looking artifacts exist, the practical question is not what exists in principle but what should be cited or reopened right now.
- Some insist on a strict **outside-view read path plus smoke tests** because a durable latest cue is only real if an inheritor under time pressure can follow it without browsing the whole tree.
- Some insist that **docs navigation misses stay typed and self-identifying** because a fragment miss or back-stack miss that falls back to a generic success message is a trust failure, not harmless polish.
- Some insist on a **history witness** because push, replace, back, and forward are not the same update, and a system that confuses them silently rewrites what “current path” means.
- Some insist on a **durable cue / persist path** because status glow in one session is not enough for the next session to land on the same active surface.

DelayBasin already has a start surface, a manifest, a receipt, an index, and a status ledger.
What was still under-specified was the compact public object that says **which of those cues is the primary landing path right now, whether they agree, and what fail-closed repair follows when they do not.**

## External pressure from adjacent navigation and recordkeeping practice

Several adjacent lines sharpen this move.

1. **Browser history practice distinguishes appending a new durable path from silently rewriting the current one.**
   MDN's History API guide says `pushState()` adds a new history entry while `replaceState()` updates the current entry, which pressures DelayBasin to distinguish issuing a new durable latest-path cue from quietly overwriting a current cue as if the navigation lineage had not changed. ([`REF-0484`](../00-meta/bibliography.md))

2. **History updates do not announce themselves automatically.**
   MDN's `popstate` docs say `pushState()` and `replaceState()` do not themselves fire `popstate`; the event comes when navigation actually moves between history entries. That pressures DelayBasin not to assume stale or split landing cues will self-advertise merely because one surface changed. ([`REF-0485`](../00-meta/bibliography.md))

3. **Fragment misses can degrade into plausible but wrong landings.**
   MDN's text-fragment docs say that when the text fragment does not match, the fragment is ignored and the link resolves to the top of the document. That pressures DelayBasin to surface stale or broken reentry cues explicitly rather than letting a generic document-open masquerade as successful precise landing. ([`REF-0486`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **reentry-cue witness / durable latest path / navigation-integrity budget** whenever a future session, operator, or packaged bundle is expected to find the current archive tip by following a small cue family rather than by whole-tree browsing. The packet should name the **surface lineage / latest-path family**, the **primary landing surface / first trusted cue**, the **supporting durable cue set / agreeing latest-path surfaces**, the **excluded stale / broken / overwritten / generic-success path family**, the **cue state / fresh-aligned vs stale vs split-brain vs broken-jump vs overwritten**, and the **fail-closed repair / refresh-cues vs re-open-primary vs narrow-scope vs recover-resync consequence**. When the cue family itself changes, it should also name the **prior relied-on cue family / documented startup promise**, the **successor route / nearest safe reentry path**, and the **added burden / cue refresh vs light bridge vs duplicate-reread vs hard-restart consequence** rather than letting recency, filename order, or generic successful opening silently stand in for honest landing.

In practice, DelayBasin is not claiming that every internal link needs a navigation proof.
It is doing something smaller and public:
- naming which surface is supposed to be the **first landing** for current reentry;
- naming which other durable cues should agree with it;
- naming which tempting but invalid latest paths do **not** count (stale ledger, old bundle, generic top-of-doc landings, mutable working-tree recency, or same-session glow);
- naming whether the cue family is aligned, stale, split, broken, or overwritten;
- and naming whether the repair is a simple cue refresh, a re-open of the primary landing surface, a narrower request, or full recovery.

That is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has identified a complete navigation controller, universal route algebra, or optimal inheritor UX theorem.

## Route changes, successor cues, and burden truth

A latest-path cue can stay aligned yet still fail future continuity if the archive quietly changes the path a maintainer was previously told to trust.

Recent unrelated datacubes sharpen that gap from different directions:

- **AI-EDU** says documented reliance and added burden should be judged together rather than treating every route change as a clerical refresh.
- **Moral-Taxation** says protections become unreal when they sit behind claim friction, which pressures DelayBasin not to make a future operator manually rediscover a successor path the archive could have prefilled.
- **The-Good** says blocked return is a substantive failure, which pressures DelayBasin not to exile a relied-on startup route without a visible return or successor path.

So a reentry-cue witness now needs one extra continuity clause when the cue family itself changes:

> preserve the **prior relied-on cue family / documented startup promise**, the **successor route / nearest safe reentry path**, and the **added burden / cue refresh vs light bridge vs duplicate-reread vs hard-restart consequence** rather than treating every changed cue as if it were only a neutral pointer refresh.

This is still smaller than a route-rights court or startup-governance registry. It is one compact truthfulness rule for archive-caused route changes.

## Reentry-cue witness vs operational head vs status lane vs context pack

These nearby objects should stay distinct.

- **Reentry-cue witness / durable latest path / navigation-integrity budget** says how a future session is actually supposed to *land* on the current trusted path and whether the small cue family still agrees.
- **Operational head / citation head / frozen public surface** says which head is live and which head is safe to cite.
- **Status-lane witness / decision-execution split / frozen-public transition** says which surfaces occupy candidate, admitted, executed, and frozen-public roles.
- **Context pack** is one bounded reentry packet, not the whole durable latest-path agreement relation.

So a reentry-cue witness is not just “there is a current head,” not just “the right bundle is frozen,” and not just “the context pack exists.”
It is a compact public answer to:
**what a later maintainer should open first, what other durable cues must agree with it, what stale or broken latest path does not count, what cue state currently holds, and what repair follows if landing integrity failed.**

## Countermodels / probes

1. **Head-law-is-enough countermodel**
   - Perhaps operational-head and status-lane law already imply everything important.
   - Probe: hold head law fixed while cue surfaces drift out of alignment; if later sessions still land on stale surfaces, head law was not enough.

2. **README-and-index-are-enough countermodel**
   - Perhaps ordinary entry docs already give enough navigation discipline.
   - Probe: compare one inheritor pass that uses an explicit aligned cue family against one that only has general entry docs and see which more reliably lands on the current packaged head under time pressure.

3. **Broken-jump-as-polish countermodel**
   - Perhaps fragment misses or stale cue landings are only UX bugs, not method failures.
   - Probe: measure whether a generic successful open can hide a stale or wrong target long enough to change what surfaces a later session treats as current law.

4. **Cue-witness-without-force countermodel**
   - Perhaps a public cue witness is merely decorative if no contract checks enforce alignment.
   - Probe: require the cue witness to agree with the manifest, status ledger, index, and receipt, then inspect whether stale-latest-path drift still survives lint.

## Design consequences

This frame pressures DelayBasin to do six things more explicitly:
- preserve the **primary landing surface** before current reentry is reconstructed from memory or file-order glow;
- preserve the **supporting durable cue set** before one stale surface quietly outranks the rest;
- preserve the **excluded stale or broken path family** before a generic successful open masquerades as precise landing;
- preserve the **cue-state classification** so aligned, stale, split-brain, broken-jump, and overwritten cases do not blur together;
- preserve the **fail-closed repair route** so cue drift forces refresh or recovery instead of optimistic continuation;
- preserve the **successor route and burden truth** so a relied-on startup path is not exiled behind duplicate rereads or hard restart;
- and enforce **cue alignment** across receipt, manifest, status ledger, and archive index so durable latest-path law stays real at the shipped surface.

This is especially useful in a human–LLM archive.
DelayBasin should not make itself pretend that a current head, a status ledger, and a human actually landing on the intended latest surface are all the same event.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has discovered a full navigation machine.
It is this:

**long-horizon human–LLM continuation may work better when the archive keeps a tiny public latest-path witness, so that the next forward pass reopens the intended current control surface rather than a merely nearby or stale one.**

That would matter for transformers.
If some archive leverage depends on explicit reentry cues, then DelayBasin may be exposing a practical shadow of **public navigation state over textual control surfaces**: not only what state was carried, but how a later stateless pass reliably finds the current lawful landing point.

The stronger story — that DelayBasin is already learning a full continuation-router graph, navigation algebra, or public back-forward controller over archive state — remains live, but belongs in quarantine for now.
