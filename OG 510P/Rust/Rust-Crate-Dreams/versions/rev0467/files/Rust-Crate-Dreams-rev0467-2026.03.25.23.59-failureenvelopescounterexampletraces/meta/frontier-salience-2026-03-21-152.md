# Frontier salience snapshot — 2026-03-21-152

This pass did **not** add another API framework, another code-first emitter, or another generator-first lane.
It deepened **P-0224 OpenAPI 3.1 + JSON Schema 2020-12 Toolchain Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- OpenAPI 3.1 now publishes its own Schema Object dialect built on top of JSON Schema Draft 2020-12;
- JSON Schema 2020-12 itself now makes bundling, dynamic references, and vocabulary posture more explicit;
- Rust now has credible parser/model crates (`openapiv3_1`, `oas3`) and validator substrate (`jsonschema`), plus code-first emitters like `utoipa`;
- but the ecosystem still lacks one reviewable contract for **what dialect was assumed**, **how refs were resolved**, **whether an artifact is a review bundle or projection**, **which consumer profile was checked**, and **whether a diff is descriptive or policy-backed**.

That combination means "supports OpenAPI 3.1" is now too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. **dialect identity** truth,
2. **ref-resolution route** truth,
3. **bundle / projection policy** truth,
4. **compatibility profile** truth,
5. **semantic-diff authority** truth.

## Main conclusion

Promote **P-0224** again, but keep it narrow.
The sharper next move is not another framework and not another generator.
It is a boring contract that keeps **dialect**, **resolution**, **projection**, **compatibility**, and **diff authority** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0224 OpenAPI 3.1 + JSON Schema 2020-12 Toolchain Kit** — strengthened because the substrate is real but the contract layer is still missing.
2. **P-0256 Evidence Bundle Core Kit** — remains strong because P-0224 wants portable review packs without private grammars.
3. **P-0244 SemVer API Diff Evidence Kit** — remains strong because descriptive diffs and verdict policy continue to need clear separation.
4. **P-0264 Rust Conformance Harness Toolkit** — remains strong because portability of scenario bundles still matters.
5. **P-0470 Cargo Package Review Kit** — remains strong because review artifacts still need packaged-surface authority and reproducible support bundles.

## Keep these boundaries sharp

- **P-0224** is dialect identity + ref-resolution route + bundle/projection policy + compatibility profile + semantic-diff authority.
- parser/model crates are separate.
- generic JSON Schema validation substrate is separate.
- code-first emitters are separate.
- generators and hosted governance portals are separate.

Do not let "OpenAPI support" flatten those into one fake crate.
