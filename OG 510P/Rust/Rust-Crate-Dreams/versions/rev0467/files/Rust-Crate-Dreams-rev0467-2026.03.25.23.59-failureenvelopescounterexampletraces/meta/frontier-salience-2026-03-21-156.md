# Frontier salience snapshot — 2026-03-21-156

This pass did **not** add another async bridge macro, another executor helper, or another generic trait-refactoring crate.
It deepened **P-0458 Async Dyn Transition Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- Rust's 2026 flagships still explicitly list **stabilize `async fn in dyn trait`** inside **Just Add Async**;
- the async-fundamentals explainer and its allocation chapter make it clear that dyn async support is about **object surface** and **allocation authority**, not just syntax;
- `async-trait` still provides the common type-erasure path for dyn support today;
- `trait-variant` provides a send-split specialization path that is adjacent but not the same thing as dyn dispatch;
- `dynosaur` and `dynify` prove there are at least two distinct bridge families beyond plain type erasure;
- `mockall` shows that macro ordering and canonical imports are real downstream compatibility constraints.

That combination means “supports async traits” is now far too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. **recipe identity** truth,
2. **object surface** truth,
3. **allocation posture** truth,
4. **tooling interop** truth,
5. **native readiness** truth.

## Main conclusion

Promote **P-0458** upward again, but keep it narrow.
The sharper next move is not another proc macro.
It is a boring transition contract that keeps **recipe**, **surface**, **allocation**, **tooling interop**, and **native readiness** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0458 Async Dyn Transition Kit** — strengthened because the transition window is still live and the comparison layer is still missing.
2. **P-0532 Async Runtime Assurance Profile Kit** — remains adjacent because runtime choice still affects async adoption, without becoming the same lane.
3. **P-0073 Async Replay Debugger Kit** — remains adjacent because runtime incidents and recipe migration are different review problems.
4. **P-0095 Task Supervision & Restart Kit** — remains adjacent because long-lived async work still needs restart truth once the trait-object story is settled.
5. **P-0534 Service Readiness & Drain Contract Kit** — remains adjacent because service lifecycle depends on async substrate but is not the same transition problem.

## Keep these boundaries sharp

- **P-0458** is recipe identity + object surface + allocation posture + tooling interop + native readiness.
- bridge macros are substrate.
- runtime portability is separate.
- replay/debugging is separate.
- service/readiness lifecycle is separate.

Do not let “async dyn support” flatten those into one fake crate.
