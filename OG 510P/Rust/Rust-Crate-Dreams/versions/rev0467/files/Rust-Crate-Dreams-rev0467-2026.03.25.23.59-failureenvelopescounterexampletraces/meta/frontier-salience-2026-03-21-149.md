# Frontier salience snapshot — 2026-03-21-149

This pass did **not** add another verifier, another sanitizer lane, or another theorem-prover wrapper.
It deepened **P-0485 Verification Campaign Workbench Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- Rust’s 2026 flagship themes now explicitly include **Safety-Critical Rust** with certified tooling, specifications, and evidence;
- the January 2026 safety-critical Rust post is explicit that verification and evidence demands rise with criticality;
- the Rust Foundation’s Safety-Critical Rust Consortium is explicitly interested in guidelines, static analysis tools, and formal methods;
- Miri, Kani, Creusot, Prusti, Flux, and Verus now form a real spread of verification lanes, but they do not by themselves give another team one boring campaign artifact;
- Kani contracts/stubs, Creusot replay, Prusti trusted functions, Flux compile-time refinements, and Verus trusted/external components all sharpen why trust surface must be explicit rather than implied.

That combination means “we ran some verification tools” is now too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. **obligation inventory truth**,
2. **lane-semantics truth**,
3. **trust-ledger truth**,
4. **policy-evaluation truth**,
5. **comparability / drift truth**.

## Main conclusion

Promote **P-0485** upward, but keep it narrow.
The sharper next move is not a new verifier and not a full assurance platform.
It is a boring contract that keeps **obligations**, **lane semantics**, **trust**, **policy**, and **comparability** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0532 Async Runtime Assurance Profile Kit** — still strongest because qualification-friendly runtime posture remains a live gap.
2. **P-0485 Verification Campaign Workbench Kit** — strengthened because the verification substrate is now broad enough that cross-tool campaign truth is the sharper missing layer.
3. **P-0503 Assurance Case Workbench Kit** — still strong because higher-layer review/import artifacts remain fragmented.
4. **P-0073 Async Replay Debugger Kit** — still strong because honest replay-support contracts remain fragmented.
5. **P-0081 Stable Plugin Host Kit** — still strong because native-plugin support contracts remain fragmented.

## Keep these boundaries sharp

- **P-0485** is obligation inventory + lane semantics + trust ledger + policy evaluation + campaign comparability truth.
- tool-local verification lanes are substrate.
- generic evidence bundles are separate.
- assurance-case / certification-consumer lanes are separate.
- single-tool sanitizer or UB lanes are separate.

Do not let “verification support” flatten those into one fake crate.
