## Current note (rev0380)
The pilot is now in its next phase:
- the first three receipts exist under `evidence/`;
- future work should renew them, narrow them, or diff them before widening the corpus much further.

# Design: Lane Default Evidence Pilot Program (`cargo lane-evidence` + renewal packs)

## Goal
Prove that the lane-default corpus can be maintained with **bounded evidence imports** instead of freehand re-justification.

The archive now has default cards.
This pilot proves how to keep them honest over time.

Read with:
- `design/lane-default-evidence-bundle.md`
- `design/reviewable-lane-defaults-corpus.md`
- `design/lane-default-evaluation-framework.md`
- `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`

## Pilot thesis
The corpus should not expand quickly until it can renew safely.
So the first pilot is not “publish ten more cards.”
It is:
- renew one easy card,
- renew one consequential card,
- add one bounded new card,
- and only then attempt a harder lane.

## Why now
The official signals support this rollout shape:
- Cargo and the Cargo Book now expose several of the exact inputs renewal needs: single-file packages, SBOM precursors, `public-dependency`, `--publish-time`, and build/layout work.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- crates.io now surfaces security, publishing, size, and timing signals directly on package pages or the index.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Rust’s challenges post says the real ecosystem problem is navigation and tacit knowledge, not merely missing libraries.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The survey says docs are still canonical even as LLM/editor mediation grows, which makes attachable evidence packs more urgent than prose-only defaults.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Ranked pilot sequence
### 1. CLI renewal lane
Subject:
- `defaults/conservative-internal-cli-2026Q1.md`

Prove:
- canon import,
- registry/advisory import for named crates,
- simple maintenance/support-envelope summary,
- renewal judgment with no change or narrow change.

Why first:
- narrow scope,
- strong canon,
- low hidden-operational complexity.

### 2. HTTP/service renewal lane
Subject:
- `defaults/conservative-http-service-2026Q1.md`

Prove:
- support-envelope facts,
- runtime-lock-in honesty,
- serious-alternative visibility,
- and a real diffable renewal report.

Why second:
- higher consequence,
- stronger chance of folklore without evidence discipline.

### 3. Script / repro / tiny utility addition lane
Subject:
- `defaults/script-repro-tiny-utility-2026Q1.md`

Prove:
- a new default card can be added directly from current official Cargo/Cargo Book signals;
- the card can be **default-with-caveats** rather than pretending stable permanence;
- and the corpus can publish bounded recommendations even when a feature is still on the stabilization path.

### 4. Safety-tilted candidate lane
Subject:
- a future safety-tilted or regulated default card.

Prove:
- dependency-lifecycle evidence,
- interop boundary evidence,
- async/runtime qualification posture,
- and explicit demotion or narrowing when evidence is not strong enough.

Why fourth:
- strategically important,
- but explicitly called out in the evaluation framework as unsafe to publish casually without stronger evidence imports.

## Reference commands
A reference prototype could expose:
- `cargo lane-evidence renew conservative-cli`
- `cargo lane-evidence renew conservative-http-service`
- `cargo lane-evidence add script-repro-tiny-utility`
- `cargo lane-evidence diff <scope>`
- `cargo lane-evidence pack <scope>`

## Success criteria
The pilot succeeds when:
- reviewers can tell why a card was kept, narrowed, or added;
- canon, registry signals, maintenance posture, support-envelope facts, and time/freshness remain visibly distinct;
- script/repro gets a bounded current default without over-claiming stability;
- and future LLM-driven revisions can use the evidence pack instead of improvising from memory.

## Non-goals
- mass-producing default cards;
- replacing package admission or maintenance stacks;
- pretending every useful signal is already machine-perfect;
- or turning unstable Cargo features into permanent public blessing before the scope is narrow enough.
