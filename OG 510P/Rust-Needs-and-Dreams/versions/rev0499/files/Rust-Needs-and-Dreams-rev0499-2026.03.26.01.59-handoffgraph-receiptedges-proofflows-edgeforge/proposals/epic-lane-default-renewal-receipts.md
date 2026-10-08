# Proposal: Epic Lane Default Renewal Receipts

## Worthy contribution
A thin, reviewable **lane-default renewal receipt** layer that turns default-card renewal from archive lore into attachable evidence.

The archive now has the right pieces to make recommendations:
- navigation bundles,
- scoped default cards,
- evaluation framework,
- and an evidence-bundle design.

What is still missing is the concrete public artifact that says:
> here is the latest renewal receipt for this lane, here is what was actually checked, and here is why the default did or did not change.

That is the worthy next contribution.

## Why this is worthy
Rust’s current ecosystem problem is not just missing packages.
It is that useful default guidance still tends to live in:
- maintainer memory,
- issue threads,
- chat folklore,
- or assistant synthesis that is hard to audit later.

The official signals all reinforce that diagnosis:
- the Rust challenges post says choice paralysis and tacit knowledge are live problems;
- the survey says docs remain canonical while machine-mediated learning rises;
- crates.io now exposes more useful review surfaces directly;
- Cargo keeps moving toward more replayable evidence;
- and recent RustSec typo/malicious-package removals show why exact package identity matters in any recommendation workflow.

A renewable receipt layer turns that into a concrete control surface instead of another essay.

## MVP
Ship a first public corpus of renewal receipts for:
1. conservative internal CLI,
2. conservative HTTP/service,
3. script/repro/tiny-utility.

Each receipt should:
- identify the exact default card;
- separate canon / registry / API / maintenance / support-envelope / freshness inputs;
- record the renewal verdict;
- cross-link back to the default card;
- and preserve exact package identities for named crates.

## Why this won over nearby candidates
### Won over “many more default cards”
Because the corpus already risked widening faster than it could be renewed honestly.

### Won over “a universal starter-set portal”
Because Rust’s own current discourse warns against flattening guidance into one broad blessing story.

### Won over “package-admission first”
Because that remains an important build-first seam, but the current repo’s immediate gap is not admission theory.
It is renewable receipts for the defaults it has already published.

### Won over “full machine schema first”
Because the archive should prove the review loop in readable form before freezing a heavy formal contract.

## Imported substrate
This epic composes:
- `design/adoption-navigation-bundle.md`
- `design/reviewable-lane-defaults.md`
- `design/reviewable-lane-defaults-corpus.md`
- `design/lane-default-evaluation-framework.md`
- `design/lane-default-evidence-bundle.md`

## MVP proof
The MVP proves:
- the archive can keep a default card current without freehand re-arguing the world;
- exact package identity can be preserved for assistants and humans alike;
- and reviewable defaults can remain bounded instead of drifting into hidden authority.

## What not to build
- a global best-crates scoreboard;
- a hidden recommendation model;
- an assistant-only chooser with no receipts;
- or a schema-heavy platform before the archive has stabilized the human receipt workflow.

## Exit condition
This epic becomes “real” when at least three maintained default cards have current receipts and future revisions naturally renew receipts before widening the corpus.
