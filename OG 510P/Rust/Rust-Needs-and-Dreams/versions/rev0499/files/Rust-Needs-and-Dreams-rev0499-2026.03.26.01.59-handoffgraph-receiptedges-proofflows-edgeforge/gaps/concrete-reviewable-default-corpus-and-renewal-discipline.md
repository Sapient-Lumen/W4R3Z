# Gap: a concrete corpus of reviewable default cards

## What is missing
Rust increasingly has the **theory** for better ecosystem guidance, but it still lacks a maintained **corpus** of scoped default cards.

The missing layer is no longer just “recommendation posture” or even “reviewable defaults” in the abstract.
The missing thing is a current set of answers such as:
- what is the conservative internal CLI default right now?
- what is the conservative HTTP/service default right now?
- what is the right default for adding one Rust component to a larger polyglot workspace?

without collapsing those answers into universal ecosystem truth.

## Why this matters now
The official Rust signals are aligned:
- ecosystem navigation still depends too much on tacit knowledge and choice paralysis;
- users still need a good “starter set” story;
- online docs remain canonical while machine-mediated learning rises;
- registry and docs-host signals are better than they used to be;
- and companion tools are the preferred place for many ecosystem workflows.

References:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## The current failure mode
Today the ecosystem often jumps between:
1. candidate-space maps,
2. one-off project advice,
3. starter templates,
4. local org overlays,
5. and assistant folklore.

What is still under-built is the maintained middle layer:
**public scoped default cards with visible alternatives and renewal rules.**

## What good would look like
A good solution would publish:
- a default card for one recurring project class;
- serious alternatives;
- canonical references;
- explicit escalation triggers;
- renewal inputs;
- and diffable change history.

## Why the archive should care
The archive already has the abstractions.
What it needed was the corpus.
Until that corpus exists, the project will keep being tempted to invent new stacks instead of proving that its current recommendation theory can survive contact with real recurring project classes.
