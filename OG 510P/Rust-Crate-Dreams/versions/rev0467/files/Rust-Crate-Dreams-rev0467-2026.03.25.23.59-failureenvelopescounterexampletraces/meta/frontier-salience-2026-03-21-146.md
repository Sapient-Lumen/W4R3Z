# Frontier salience snapshot — 2026-03-21-146

This pass did **not** add another tensor engine, linear-algebra backend, or Arrow bridge crate.
It deepened **P-0003 Array API**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- the Python Array API standard explicitly treats fragmentation, semantics, data interchange, device support, conformance, and inspection as standardization-worthy;
- `ndarray` documents dense n-D arrays with row-major default order plus views, slicing, and custom strides;
- `nalgebra` documents a low-dimensional linear-algebra focus with one parametrizable matrix family;
- `faer` documents a performance focus for medium/large dense matrices with column-major layout;
- `linalg-traits` proves generic abstraction is useful but also explicitly documents semantic operator mismatch between `ndarray` and `nalgebra`;
- `candle` and `burn` make device/backend and dtype/default behavior real support-surface facts;
- `arrow-array` is explicit enough about columnar arrays and low-level buffers that it should be treated as adjacent interop substrate, not automatic proof of dense-core compatibility.

That combination means “supports arrays” is now too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. **semantic profile truth**,
2. **layout/view truth**,
3. **device/dtype truth**,
4. **namespace coverage truth**,
5. and **interop-route truth**.

## Main conclusion

Promote **P-0003** sharply upward, but keep it narrow.
The sharper next move is not a universal tensor framework.
It is a boring contract that keeps **profile**, **layout**, **device/dtype**, **namespace coverage**, and **interop routes** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0532 Async Runtime Assurance Profile Kit** — still strongest because runtime-family and qualification posture remain major ecosystem gaps.
2. **P-0003 Array API** — strengthened because real numerics substrate exists, but receiver-facing array-support contracts are still fragmented.
3. **P-0002 Wasm Plugin Kit** — still strong because receiver-facing plugin contracts remain fragmented.
4. **P-0106 Test Run Artifact Standard Kit** — still strong because portable run-contract truth remains fragmented.
5. **P-0533 Error Surface Contract Kit** — still strong because identity/audience/remediation/sensitivity remain broadly under-specified.

## Keep these boundaries sharp

- **P-0003** is semantic profile + layout/view + device/dtype + namespace coverage + interop-route truth.
- dense-array implementations are separate substrate.
- linear-algebra libraries are separate substrate.
- tensor backends/autodiff frameworks are adjacent but separate implementation layers.
- Arrow/columnar arrays are adjacent interop substrate.
- sparse arrays remain a separate future lane.

Do not let “array support” flatten those into one fake crate.
