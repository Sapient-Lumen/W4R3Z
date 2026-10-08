# Epic Proposal: Lane Default Corpus (`cargo lane-corpus` + maintained default cards)

## One-sentence pitch
Give Rust a maintained public corpus of **scoped, reviewable default cards** for recurring project classes so teams can import bounded current guidance without pretending the ecosystem has one universal blessed stack.

## Why this is worthy
The archive has already concluded that the ecosystem’s problem is not simply “too few libraries”.
The more current problem is:
- too much tacit knowledge,
- too many respectable choices,
- too little reusable default guidance,
- and too much drift between current canon and repeated advice.

A default-corpus contribution would attack that directly.

## Deliverables
- a small maintained corpus of default cards under `defaults/`
- `design/lane-default-evaluation-framework.md`
- `design/reviewable-lane-defaults-corpus.md`
- one renewal protocol and diff discipline
- optional thin tooling:
  - `cargo lane-corpus list`
  - `cargo lane-corpus show <scope>`
  - `cargo lane-corpus diff <scope>`
  - `cargo lane-corpus renew <scope>`

## Initial corpus lanes
1. conservative internal CLI / automation
2. conservative HTTP/service baseline
3. polyglot workspace component
4. script / repro / tiny utility
5. safety-tilted conservative lane

## Why now
- Rust’s March 20, 2026 challenges post says ecosystem navigation still suffers from choice paralysis and tacit knowledge.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- Rust’s December 2025 vision work says users need help finding a good “starter set” of crates, while making clear that broad blessing is risky.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 State of Rust survey says online docs remain canonical while LLM/editor-mediated workflows are rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io’s January 2026 update added Security-tab advisories, Trusted-Publishing-only mode, SLOC, source links, and `pubtime`, improving review and renewal inputs.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo’s February 2026 development-cycle note says plugins matter because Cargo cannot be everything to everyone.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Non-goals
- one global leaderboard of crates
- a hidden recommendation score
- replacing Atlas or project-specific adoption briefs
- replacing starter templates or project bootstrappers
- auto-generating public defaults with no review owner

## Success criteria
- teams can import a bounded default card instead of restarting the recommendation debate from zero;
- serious alternatives remain visible;
- canonical references remain attached;
- default renewals and demotions are diffable;
- assistants stop needing to improvise the whole answer.

## Strategic value
This is a practical path toward a Rust ecosystem that is more helpful than “it depends” while still avoiding accidental permanent blessing.
That is exactly the balance current official Rust signals are calling for.
