# Public-state packets, discoverability exclusions, and overflow tests

This is the compact successor surface for `OQ-0111`.

DelayBasin already had a real witness-vocabulary surface plus live status lanes, but one pressure kept recurring in durable rereads:
later careful passes could still see that something was the current public bundle and yet quietly import nearby ideas such as **draft**, **prerelease**, **latest**, **private**, **listed**, or **search-indexed** as if they were all the same compact token.
Some surfaces are public enough to cite.
Some are still working surfaces.
Some are deprecated but still public.
Some are absent.
And several adjacent systems keep showing that **access control**, **release maturity**, and **search discoverability** are real neighboring distinctions rather than synonyms for archive public state.

The compact repair is:
**preserve one explicit public-state packet that says the existing admitted `public_state` family is already the right bounded place to keep archive public-citation posture public, while keeping release maturity, access control, and search discoverability in neighboring prose or explicit future extensions rather than silently inside the token.**

This does **not** justify a publication court, exposure senate, search-authority board, or general public-governance layer.
It only resolves the missing compact successor surface for a family DelayBasin already admitted.

## Practice / observation

DelayBasin's current status surfaces already distinguish admitted decision, packaged execution, and frozen public citation posture.
That was enough to stop many revisions from collapsing into one “latest” vibe.
But a smaller gap remained:
- some later rereads could still smuggle **draft** or **prerelease** maturity into `public_state` as if “not latest yet” were the same thing as “not public”;
- some could still smuggle **private** or **restricted** access into `public_state` as if access control were the same axis as archive citation posture;
- some could still smuggle **listed** or **search-indexed** discovery into `public_state` as if being findable through ambient search were the same thing as being a valid frozen public surface;
- and some could still treat one local checker literal or nearby synonym as stronger than the controlled family stored in `WITNESS-VOCABULARY.json`.

The archive therefore did not need a larger publication controller first.
It needed one compact packet that says the admitted `public_state` family is already the right public place to preserve **archive citation posture**, and that neighboring visibility or maturity distinctions stay outside the token unless a later explicit extension is honestly required.

## External pressure from release maturity, access control, and search discoverability practice

Current release, registry, and search systems repeatedly keep nearby public-looking distinctions separate.

1. GitHub release management distinguishes **draft**, **prerelease**, **latest**, and published release-feed visibility, and its release API says drafts and prereleases cannot be set as latest. That pressures DelayBasin to keep `public_state` narrower than release-maturity or latest-label language. ([`REF-0813`](../00-meta/bibliography.md), [`REF-0814`](../00-meta/bibliography.md))

2. npm's access matrix distinguishes **scope**, **access level**, **who can view/download**, and **who can write**, while package-visibility changes flip public versus private access explicitly. That pressures DelayBasin to keep access control adjacent to public-state comparison rather than silently inside it. ([`REF-0815`](../00-meta/bibliography.md), [`REF-0816`](../00-meta/bibliography.md))

3. Google Search Central says `noindex` keeps content out of Google Search while the content can still be visited directly by users with a link. That pressures DelayBasin to keep search discoverability separate from archive citation posture. ([`REF-0817`](../00-meta/bibliography.md))

4. Google Search Central also says robots.txt is not a way to hide pages from Google Search and blocked URLs can still appear in results. That pressures DelayBasin not to flatten crawler posture into a simple public/private state token. ([`REF-0818`](../00-meta/bibliography.md))

5. GitHub security advisories for public repositories can be privately discussed and fixed before later publication. That pressures DelayBasin to keep private drafting posture distinct from later public disclosure posture rather than collapsing both into one vague “public enough” state. ([`REF-0819`](../00-meta/bibliography.md))

## Working synthesis

> DelayBasin should preserve one compact **public-state packet / honest-public citation posture** on archive status surfaces, and the admitted family should stay the existing `public_state` tokens **`working`**, **`frozen-citable`**, **`deprecated-public`**, and **`absent`**. Use the token only to name archive public-citation posture. Keep release maturity words such as **draft**, **prerelease**, or **latest**, access words such as **private** or **restricted**, and search-discoverability words such as **listed**, **noindex**, or **search-indexed** outside the token unless a later explicit registry extension is honestly required. Keep the family narrow. Extend only explicitly and fail closed on drift.

## Public state vs maturity vs access vs discoverability

This distinction is the heart of the successor surface.

- **`public_state`** says whether the archive currently treats the surface as working-only, frozen and citable, deprecated but still public, or absent.
- **release maturity** says whether some release-like object is draft, prerelease, latest, or otherwise staged inside a release system.
- **access control** says who can read, download, or write a thing.
- **discoverability** says whether ambient listing or search can find it, whether it is link-routed only, or whether crawler rules are involved.

A surface can be `frozen-citable` even if it is not search-indexed.
A surface can be discoverable in a feed yet still not be the right frozen citation head.
A surface can be privately drafted before later publication without changing what `frozen-citable` means for the archive.
A surface can disappear from one listing without that alone proving it was never a valid public citation surface.

So the packet does not add a new court.
It only makes the already-admitted separation easier to reopen honestly.

## Countermodels / probes

1. **Existing-vocabulary-is-already-enough countermodel**
   - Maybe the general witness-vocabulary note plus current checkers already keep public-state comparison honest.
   - Probe: inspect later rereads and see whether operators still smuggle draft, private, latest, or noindex-style language into `public_state` even though the family already exists.

2. **Need-new-discoverability-family-now countermodel**
   - Maybe DelayBasin should add a whole new controlled discoverability token family immediately.
   - Probe: first test whether one compact successor packet plus explicit exclusions already keeps search/listing language from mutating `public_state`.

3. **Public-state-token-is-too-thin countermodel**
   - Maybe `working` vs `frozen-citable` vs `deprecated-public` vs `absent` is too small to be useful.
   - Probe: compare later packaging and citation passes and inspect whether the narrow family still preserves the archive question that actually matters: what may currently count as the frozen public citation surface.

## Design consequences

- keep the controlled `public_state` family unchanged in `WITNESS-VOCABULARY.json` for now;
- explicitly govern `public_state` across `SURFACE-STATUS.json` and `REVISION-RECEIPT.json` rather than leaving receipt copies to feel local;
- preserve one compact successor surface for the family so later passes can reopen archive-public truth directly;
- keep maturity, access, listing, and search-discoverability detail outside the token itself;
- and quarantine any stronger publication court, exposure senate, or search-authority board unless repeated overflow shows that one compact packet is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact packet is no longer enough — for example, if DelayBasin honestly needs standing governance over access posture, staged-public maturity, listing policies, or discoverability-state classes that cannot be expressed as one bounded `public_state` family plus surrounding prose.

Until then, prefer this compact successor surface over a publication court, exposure senate, or search-authority board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something slightly sharper than “what looks public right now?”
It is also preserving **what archive citation posture currently applies**, while refusing to let adjacent release, access, or search vocabulary silently become the governing token.
That matters because later stateless passes can otherwise keep the prose while losing the small machine-comparable public-state answer that the witness layer was supposed to buy.
