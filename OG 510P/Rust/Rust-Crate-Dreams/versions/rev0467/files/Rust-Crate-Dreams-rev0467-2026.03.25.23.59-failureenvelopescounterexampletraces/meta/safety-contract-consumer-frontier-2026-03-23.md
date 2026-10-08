# Frontier note — Safety Contract Consumer Kit after the 2026 safety-critical and contracts signals

## Why this lane still looks strategically important

The safety-critical thread in Rust is no longer hypothetical.
Current official material says Rust is already deployed in production for IEC 61508 SIL 2 and IEC 62304 Class B contexts, but also says ecosystem support thins out as teams move toward higher-criticality software.
At the same time, the 2026 flagships explicitly keep **certified tooling, specifications, and evidence for functional safety** in the top-tier roadmap.

That means any crate that helps teams turn emerging contract substrate into honest, reviewable, reusable artifacts has a stronger audience than it did even a year ago.

## Why the old framing was not yet sharp enough

The earlier archive framing for **P-0453** centered on extraction, diffing, runtime profiles, and cross-tool receipts.
That was directionally right, but still too easy to flatten into:

- one contract snapshot,
- one downstream “supported tools” list,
- one receipt,
- and an implied claim that the semantic meaning of “consumed” was close enough.

Current sources make that unsafe.

The std-contracts goal explicitly says the same contract substrate should support:

1. **runtime checks when users opt in**, and
2. a **compiler interface for external tools** to retrieve contracts.

That is already at least two materially different consumer lanes.
And `verify-rust-std` makes the plurality even more concrete by accepting multiple tools with different proof/search/specification models.

## Main frontier claim

The next valuable move for **P-0453** is to treat **contract authority**, **consumer coverage**, and **semantic lane** as first-class artifacts.

That yields a sharper missing crate:

> not another verifier, not a universal contract translator, but a reviewer-facing consumer layer that can say what the contract surface was, who supplied it, what each consumer actually used, and which semantics still fence the result.

## Why this could be an epic crate contribution

This lane can plausibly become an ecosystem hinge if it stays small and honest.
It could let:

- std-contract work,
- safety-critical linting,
- unsafe audits,
- verification campaigns,
- and multiple proof/checking tools

participate in one reviewable handoff without pretending to unify their semantics.

That is the kind of thing other people can actually adopt:

- suppliers can export one contract-consumption bundle,
- customers can reopen and diff it,
- verification teams can plug in new tools without rewriting the bundle format,
- and assessors can see exactly where runtime-check evidence stops and proof-tool evidence begins.
