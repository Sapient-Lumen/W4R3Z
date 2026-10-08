# Frontier salience snapshot — 2026-03-21-141

This pass did **not** add another runtime reflection crate, another derive helper, or another code-generation-only schema lane.
It sharpened **P-0439 Comptime Reflection Bridge Kit** into a more implementation-ready bridge contract.

## Why this frontier moved up

The current Rust substrate now makes the bridge problem unusually concrete:

- the Rust project’s reflection/comptime goal is explicitly about `const fn`-based compile-time reflection that produces const-eval values and is **not** yet a full runtime type-system reintegration surface;
- `bevy_reflect` already provides a runtime registry/derive world, while its docs also say generic monomorphized representations still need manual registration;
- `facet` already provides `SHAPE` associated const metadata with layout, fields, docs, and attributes, while `facet-reflect` adds runtime value access and mutation-adjacent APIs;
- `serde_reflection` already extracts useful format descriptions, but that authority class is narrower than general type-shape reflection.

That combination means the missing crate is not another reflection implementation.
It is a **bridge** that can publish **schema source**, **coverage scope**, **execution posture**, and **loss accounting** across today’s divergent reflection-like sources and tomorrow’s experimental compile-time adapters.

## Main conclusion

Promote **P-0439** upward again, but keep it narrow.
The next worthy move is not a final reflection standard and not a runtime reflection replacement.

It should stay focused on:

1. freezing reflection-like exports into a small portable schema core,
2. making **source authority** explicit,
3. making **coverage scope** explicit,
4. making **execution posture** explicit,
5. and attaching one compact **loss-accounting** bundle to every bridge export.

## Ranked near-term frontier from this pass

1. **P-0439 Comptime Reflection Bridge Kit** — strengthened because the language experiment is live while today’s reflection-like crates already expose different authority and runtime-dependence classes.
2. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strong because ecosystem choice still needs reviewable starter-set artifacts.
3. **P-0486 Debuggability Support Contract Kit** — still strong because debugger-family/capability ceilings remain broad downstream pain.
4. **P-0520 Crate Lifecycle Surface Pack Kit** — still strong because stop/drain/barrier truth keeps showing up across domains.
5. **P-0532 Async Runtime Assurance Profile Kit** — still strong because runtime-family selection and qualification basis remain live ecosystem problems.

## Keep these boundaries sharp

- **P-0439** is the bridge contract across reflection-like sources.
- `bevy_reflect` and `facet` remain their own reflection systems.
- `serde_reflection` remains a format-schema lane.
- the Rust reflection/comptime goal remains an experimental language substrate, not a frozen product contract.

Do not let “has reflection metadata” flatten those lanes into one fake crate.
