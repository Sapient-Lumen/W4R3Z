# Gap: Concrete renewal receipts and exact-identity hygiene

## The gap
The archive now has:
- real default cards,
- a corpus discipline,
- an evaluation framework,
- and an evidence-bundle design.

But it still lacked the thing a reviewer would actually ask for next:
> show me the latest receipt for this default.

Without that layer, the repo was still one step away from practical renewal.

## Why this matters
The latest Rust signals make this gap sharper, not smaller:
- the ecosystem-navigation problem is still described as **choice paralysis** and **tacit knowledge**;
- docs remain canonical while assistant/editor mediation rises;
- crates.io exposes richer package review surfaces than before;
- Cargo is moving toward more replayable evidence; and
- RustSec’s current advisory stream shows recent malicious lookalike crates whose names are easy to blur in conversation.

That last point matters more than it may seem.
If a default card says “serde-like tools” or “once-cell style helpers” without preserving exact identifiers, assistants and hurried humans can accidentally carry the wrong package identity forward.

## Missing artifact family
The archive needs:
- `evidence/README.md`
- one current receipt per maintained card
- cross-links from cards to receipts
- compact working-set/meta reminders for future LLM-driven edits

A later revision may add diff/index/schema layers, but the immediate missing value is readable receipts.

## Failure modes without this layer
- defaults remain prose-first and hard to replay;
- package identity drifts into fuzzy aliases;
- later assistants mistake lane judgments for package-admission judgments;
- widening the corpus becomes easier than renewing it.

## Practical first proof
The right first receipt set is:
1. conservative internal CLI,
2. conservative HTTP/service,
3. script/repro/tiny-utility.

Do not widen much beyond that until the receipt workflow feels normal.

## Non-goals
- a global crate trust score;
- replacing package admission;
- or pretending every lane can already be renewed mechanically.
