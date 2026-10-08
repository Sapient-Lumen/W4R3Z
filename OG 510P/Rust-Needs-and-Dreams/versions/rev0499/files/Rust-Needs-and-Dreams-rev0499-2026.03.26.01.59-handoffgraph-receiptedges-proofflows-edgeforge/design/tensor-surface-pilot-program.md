# Design: Tensor Surface Pilot Program (CPU Dense Truth → Device/Autodiff Truth → Interchange/Storage Truth → Consumer Imports)

## Goal
Turn **Tensor Surface Kit** into a ranked execution program so the archive can answer a practical question: what is the first boring, portable, ecosystem-shaping contribution that would materially improve Rust’s numerical/array/tensor story?

The pilot program should not chase a universal “NumPy for Rust” or a winner-takes-all tensor runtime. Read [`design/tensor-surface-lane-map.md`](./tensor-surface-lane-map.md) first: each pilot lane should prove one **dense-array, matrix/linalg, runtime-tensor/device, persisted-array, interchange, or adapter/import** claim rather than collapsing them together.
It should sequence the contribution so each lane proves something concrete before the next lane widens scope.

## Why a pilot program is necessary
Array and tensor proposals become vague very quickly because the ecosystem mixes several distinct axes and lane identities:
- dense arrays versus linear algebra matrices,
- borrowed views versus owned tensors,
- CPU-only lanes versus device-aware backends,
- autodiff versus non-autodiff surfaces,
- zero-copy interchange versus copy-required adaptation,
- and in-memory tensors versus stored multidimensional arrays.

A credible plan therefore needs to decide:
- which truth is worth standardizing first,
- which adapters are honest enough to publish even when they are lossy or copy-heavy,
- and which consumers should import tensor-surface artifacts later rather than being collapsed into the first version.

## Ranking principle
Prefer lanes that:
1. already have multiple serious Rust implementations,
2. expose real support ambiguity today,
3. unlock downstream model/data/offload work,
4. can publish bounded evidence instead of giant arrays,
5. and do not require declaring a universal runtime winner.

## Ranked pilot lanes

### Lane A — Dense CPU arrays and matrix/view truth first
Focus first on the part of the ecosystem where support ambiguity is already visible but tractable:
- `ndarray` dense arrays and views,
- `nalgebra` fixed/dynamic matrix families,
- `faer` owned/borrowed matrix lanes,
- explicit shape/dtype/layout/view/ownership artifacts,
- honest adapter reports that can say `exact`, `copy-required`, `partial`, or `unsupported`.

Why first:
- the ecosystem already has serious libraries here,
- many downstream crates depend on these semantics indirectly,
- and this lane proves the archive can describe interoperability without forcing one library to win.

### Lane B — Device and autodiff truth second
Once CPU-array truth is stable, widen into device-aware tensor lanes:
- Candle tensor/device/layout posture,
- Burn backend/device/autodiff posture,
- precision/quantization notes when they materially alter support,
- adapter reports that record host/device movement rather than hiding it.

Why second:
- this is where scientific, ML, and accelerator workflows start to overlap,
- but it is easier to reason about after shape/layout/view truth exists.

### Lane C — Interchange and storage truth third
Only then widen into persistence and exchange surfaces:
- DLPack exchange lanes,
- Zarr multidimensional-array storage lanes,
- model/tensor storage attachments such as SafeTensors or Burn Store,
- Arrow attachments where useful as an adjacent structured-data lane,
- explicit zero-copy / borrowed / copy-required / lossy / unsupported results.

Why third:
- this is where the ecosystem most needs honesty,
- and it is where fake universal abstractions become most tempting.

### Lane D — Consumer imports fourth
Only after the surface is legible should downstream kits start importing it:
- Model Surface Kit imports tensor-runtime/storage facts,
- Offload Surface Kit imports device and transfer assumptions,
- Dataset Surface Kit imports multidimensional storage attachments where relevant,
- Geospatial Surface Kit imports raster/array adapter truth where useful.

Why fourth:
- the first victory is a stable tensor contract,
- not making every adjacent kit depend on it immediately.

## Concrete pilot designs

### Pilot 1 — `ndarray` / `nalgebra` / `faer` compatibility pack
Publish:
- one `tensor-surface/v0` for a shared numerical package,
- shape/dtype/layout/view profiles for each lane,
- adapter profiles for the supported conversions,
- check reports proving which conversions are exact, copy-required, or unsupported.

Success condition:
- the pack makes library-family differences obvious without treating them as bugs.

### Pilot 2 — Candle / Burn device-profile pack
Publish:
- one tensor surface per runtime lane,
- device/autodiff profiles,
- precision and backend notes,
- adapter reports that explicitly record host/device transfers or unsupported conversions.

Success condition:
- device/backprop/runtime posture becomes explicit enough that downstream model/offload consumers could import it later.

### Pilot 3 — DLPack / Zarr / store-fidelity pack
Publish:
- interchange profiles for DLPack and storage profiles through Zarr or model-store lanes,
- adapter reports that state whether shape/layout/dtype metadata survives,
- negative cases for unsupported or lossy exchanges.

Success condition:
- zero-copy stops being README folklore and becomes a checked claim class.

### Pilot 4 — Consumer-import proof
Publish:
- one model-oriented importer,
- one offload-oriented importer,
- optionally one dataset/geospatial importer,
- each importing tensor-surface artifacts instead of re-inventing tensor truth locally.

Success condition:
- the archive proves the kit composes without turning adjacent kits into tensor kits.

## What v0 should explicitly avoid
- no universal Rust numerical runtime,
- no fake “canonical tensor object” that flattens arrays, matrices, runtime tensors, and storage-backed arrays,
- no giant benchmark suite pretending performance alone defines the surface,
- no forced zero-copy promise where copies or layout loss are the honest answer,
- no attempt to absorb dataset, model, or offload truth into one mega-format.

## Expected output of the pilot program
If the pilots succeed, the next archive step should be clear:
- keep `Tensor Surface Kit` as a Tier 1/2 substrate proposal,
- deepen adapters only where the reports are honest,
- and promote consumer imports only after the tensor contract itself is stable.

If the pilots fail, that failure should still be useful:
- it may show that some lanes belong in Dataset / Model / Offload kits instead,
- or that only a narrower dense-array/matrix subset is ready for standardization now.
