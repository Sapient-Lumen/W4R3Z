# Correctness-lab frontier — 2026-03-09

## Main judgment

A non-Cargo frontier deserves more explicit attention now:

- **text/i18n correctness**, where Rust now has credible layout substrate but still lacks a shared conformance and repro layer;
- **passkeys/WebAuthn interop**, where Rust now has real auth substrate and growing automation support but still lacks a normalized scenario + evidence workflow.

A third adjacent frontier now looks more credible too:

- **cross-platform accessibility interop**, where AccessKit and platform adapters are meaningful substrate but teams still lack a portable capture/diff/repro lab.

The pattern in all three areas is the same:

1. the standards and building blocks are real,
2. Rust substrate is no longer hypothetical,
3. backend or runner choice is still moving,
4. and the still-missing crate is increasingly a **lab kit** rather than another core engine.

## Why now

### Text/layout side
- `parley` and `cosmic-text` make Rust-native text layout a real ecosystem frontier instead of a blank space.
- ICU4X 2.0 means the i18n substrate is maturing, but it also means version pinning and upgrade-diff discipline matter more.
- Unicode UAX #14 and UAX #29 provide normative anchors, but they still leave higher-level layout choices above the algorithm.
- Active backend churn (for example, Bevy’s move toward Parley) is evidence that the ecosystem needs a comparison and migration layer, not another premature “winner takes all” claim.

### Passkeys/WebAuthn side
- WebAuthn is now broad, practical platform surface rather than experimental novelty.
- Rust has real substrate in `webauthn-rs` and `passkey-rs`.
- WPT/WebDriver virtual-authenticator support means automation is finally mature enough to support a useful Rust interop lab.
- But that automation maturity is uneven across lanes, which strengthens the case for explicit capability receipts and comparability classes instead of fake browser parity.

## Best next incubation targets in this frontier
1. **P-0197 Text Layout & Shaping Conformance Kit**
2. **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit**
3. **P-0202 Cross-Platform Accessibility Interop & Conformance Kit**
4. **P-0264 Rust Conformance Harness Toolkit**
5. **P-0256 Evidence Bundle Core Kit**

## Working rule

When a domain now has:

- a real standard surface,
- some maintained Rust substrate,
- and active backend or runner churn,

prefer proposing:

- corpora,
- scenario DSLs,
- normalized outputs,
- bundles,
- diffs,
- and diagnosis kits.

Do **not** default to proposing another engine, parser, renderer, or server SDK unless the archive can show that the substrate itself is still truly missing.

## False gap patterns to avoid

1. “The backend choice is still unsettled, so Rust needs one more backend.”
2. “The spec exists, so conformance/interop tooling is solved.”
3. “A useful Rust crate here must be a full framework or platform.”

The sharper missing crate is often the **reviewable correctness lab** above real substrate.


## Accessibility side
- AccessKit is now the right “implement once” substrate for many Rust UI stacks, which is strong evidence that the remaining gap is higher-level than raw bindings.
- Platform adapters for winit, Unix/AT-SPI, Windows/UIA, and macOS/NSAccessibility make cross-platform capture and normalization much more plausible than it looked when Rust GUI accessibility was mostly aspirational.
- That makes **P-0202** more interesting as an interop/capture lab, while **P-0087** remains the toolkit-facing doctor/gating surface.
