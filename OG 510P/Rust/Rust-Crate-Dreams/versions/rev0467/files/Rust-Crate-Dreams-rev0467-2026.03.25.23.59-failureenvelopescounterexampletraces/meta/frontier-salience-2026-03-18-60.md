# Frontier salience snapshot — 2026-03-18 (60)

This pass did **not** promote a brand-new ecosystem-wide lane.
It sharpened an existing **shipping and adoption accelerator**:

- **P-0466 Python Wheel ABI & Free-Threading ShipKit** — because the archive still lacked a believable answer to “what exact compatibility promise is this Rust-backed Python extension release making?”

## Main judgment

The next worthy move here was **not** another binding generator, another package uploader, or another generic Python build backend.
Those either already exist in serious form or are too broad for a believable artifact-bearing `0.1`.

The sharper missing layer is the **Python extension compatibility contract** above today’s substrate, especially once three more facts are kept explicit:

- **ABI target class** — version-specific ABI, `abi3`, split free-threaded wheels, or an `abi3t` horizon.
- **Thread-support declaration** — whether the module is actually declaring itself safe to run with the GIL disabled, and where manual review still lives.
- **Variant horizon** — whether the release story assumes only today’s tags or is honest about accepted `abi3t` / wheel-variant evolution.

That move is better grounded now because:

- PyO3 already provides a serious build/distribution substrate including `abi3`; citeturn324357view5turn539480search1
- PyO3’s current free-threading docs make thread-safety declarations and `gil_used` posture explicit; citeturn377112view1turn790458view2
- Python 3.14 made free-threaded builds officially supported; citeturn404209view3
- Python’s extension HOWTO still says free-threaded builds do not currently support the Limited C API / Stable ABI and therefore need separate wheels today; citeturn790458view1
- maturin has real free-threading support but still has open `abi3.abi3t` follow-on work in March 2026; citeturn324357view2turn596666view1
- cibuildwheel now treats `3.14+` free-threaded wheels as normal enough to stop requiring the old opt-in; citeturn324357view3turn790458view4
- and Python packaging accepted both **PEP 803** and the broader **wheel-variants** work, so the compatibility surface is clearly still moving. citeturn404209view2turn790458view0turn404209view0

So the gap is no longer “Rust cannot ship Python extensions.”
The gap is that teams still rarely get a **reviewable cargo-native Python compatibility artifact** above PyO3 configuration, wheel tags, repair steps, CI selectors, and packaging-policy drift.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest troubleshooting lanes.
5. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
6. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
7. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — now one of the clearest **Band B shipping-kit** opportunities because the substrate exists but the boring compatibility contract still does not.
8. **P-0168 Rust Android Mobile Kit** — still a strong shipping-kit lane with explicit platform-policy pressure.
9. **P-0451 Cfg Availability Ledger Kit** — still the sharpest item-level conditional-support truth lane.
10. **P-0510 Crate Capability Contract & Interop Profile Kit** — still the strongest producer-side fact surface for a single crate.

## Why this won over adjacent candidates right now

- It beat **another generic FFI helper** because the sharper pain is no longer bindings generation but release-contract truth.
- It beat **more package-publishing automation** because the missing value is reviewable compatibility policy, not one more upload wrapper.
- It beat **broader Python/Rust platform ambitions** because a compact shipkit is more believable than a giant ecosystem bet.
- It beat **Apple/Python drift follow-ons** because the core Python compatibility vocabulary needed to be sharper first.

## What changed in the archive

Added:
- `entries/2026-03-18-240.md`
- `meta/frontier-salience-2026-03-18-60.md`
- `meta/python-wheel-abi-free-threading-shipkit-product-plan-2026-03-18.md`
- `fixtures/python-wheel-abi-free-threading-shipkit/README.md`
- `fixtures/python-wheel-abi-free-threading-shipkit/abi-target.report.schema.json`
- `fixtures/python-wheel-abi-free-threading-shipkit/thread-support.report.schema.json`
- `fixtures/python-wheel-abi-free-threading-shipkit/variant-horizon.report.schema.json`
- `fixtures/python-wheel-abi-free-threading-shipkit/scenarios/abi3_nonfree_plus_cp314t_split/`
- `fixtures/python-wheel-abi-free-threading-shipkit/scenarios/pymodule_gil_used_true_requires_runtime_optout_note/`
- `fixtures/python-wheel-abi-free-threading-shipkit/scenarios/abi3t_future_policy_waits_for_tooling/`

Updated:
- `proposals/python-wheel-abi-free-threading-shipkit.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`

## What this pass deliberately did not do

It did **not** collapse:

- classic `abi3`,
- version-specific wheels,
- `t` wheels,
- PyO3 thread-safety declarations,
- accepted `abi3t` evolution,
- and future wheel-variant surfaces

into one fake “Python support” story.

## Sources

- https://pyo3.rs/v0.28.2/building-and-distribution
- https://pyo3.rs/v0.28.2/building-and-distribution/multiple-python-versions
- https://pyo3.rs/v0.28.2/free-threading
- https://docs.python.org/3/howto/free-threading-extensions.html
- https://docs.python.org/3/whatsnew/3.14.html
- https://www.maturin.rs/changelog.html
- https://github.com/PyO3/maturin/issues/3064
- https://cibuildwheel.pypa.io/en/stable/options/
- https://peps.python.org/pep-0803/
- https://peps.python.org/pep-0825/
- https://peps.python.org/
