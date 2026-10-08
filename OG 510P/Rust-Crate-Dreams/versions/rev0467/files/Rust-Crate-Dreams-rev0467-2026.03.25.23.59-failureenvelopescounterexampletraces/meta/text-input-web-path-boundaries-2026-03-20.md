# text-input web path boundaries — 2026-03-20

This note exists to stop future passes from collapsing multiple web editing paths into one fake “WASM text input support” story.

## Keep these lanes separate

1. **Visible surface**
   - canvas / GPU text surface
   - DOM text widget
   - native toolkit widget bridged into web host

2. **Editable / focused surface**
   - same visible node
   - hidden input / textarea proxy
   - EditContext attached to a custom element
   - delegated DOM editable region

3. **Composition/event ingress**
   - browser composition / beforeinput events
   - EditContext events
   - forwarded hidden-input events
   - toolkit-native imported events

4. **Geometry sync**
   - caret rect updates
   - selection bounds updates
   - character bounds updates
   - fullscreen / transformed-surface drift

5. **Accessibility mirror**
   - native accessible text node
   - offscreen DOM mirror
   - toolkit-exported accessibility surface
   - none / manual review

## Why this matters

A web text surface can appear to “work” while several different truths remain hidden:

- the user is really typing into a hidden DOM node,
- the candidate window is anchored approximately or detached,
- provisional text is rendered outside the visible caret line,
- fullscreen or transformed rendering breaks geometry,
- or assistive technology still cannot inspect the same text the user sees.

The sharper current gap is therefore not just “web IME support.”
It is one **reviewable contract for edit path, geometry sync, and mirror honesty**.

## Archive homes

- **P-0027 text-input-kit** — transaction/selection engine + backend receipts + web-path / geometry truth
- **P-0087 UI Accessibility Doctor Kit** — authoring-side semantic doctoring and release gating
- **P-0202 Accessibility Capture & Interop Lab** — observer-side platform capture and semantic diff
- **P-0197 Text Layout & Shaping Conformance Kit** — layout/shaping correctness and profile truth
- **P-0092 GUI Testing & Snapshot Harness Kit** — broader GUI regression and snapshot workflows
