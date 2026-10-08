# Epic proposal: Terminal Surface Kit

## Thesis
One of the more worthy ecosystem contributions in Rust now would be a **portable review layer for terminal surfaces**.

Rust programs increasingly depend on richer terminal behavior: raw mode, alternate screens, color negotiation, mouse and focus events, bracketed paste, Unicode-aware layout, test backends, virtual-terminal parsers, and even image protocols. But today those semantics are usually published only through backend choice, screenshots, and example code.

Rust does not need one more terminal crate nearly as much as it needs a boring, explicit `terminal-pack/v0`, plus a lane map and pilot program that keep styled output, TUIs, line editors, capability/probing stacks, parser/test evidence, and graphics protocols from collapsing into one story.

## Why now
The timing is good:
- Ratatui already abstracts over multiple backends and explicitly documents that real applications still care about raw mode, alternate screen, event capture, and terminal properties;
- `crossterm` already exposes a wide cross-platform terminal surface, including raw mode, alternate screen, resize events, mouse events, focus events, and bracketed paste;
- `termwiz` already treats capability probing and escape semantics as first-class concerns;
- `anstream` already proves that style/color policy is its own portability layer rather than a detail hidden inside printing macros;
- Unicode layout is visibly not settled into one trivial rule: `unicode-width`, `unicode-segmentation`, and grapheme-aware display-width crates expose different useful pieces of the problem;
- `reedline` already shows that interactive terminal editing changes semantics around paste, Unicode, multiline interaction, and menus;
- Ratatui `TestBackend` and `vt100` already prove that terminal evidence can be machine-checked rather than screenshot-checked;
- `ratatui-image` already shows richer terminal graphics protocols are real ecosystem territory.

That means the next major terminal seam is visible before it has converged.
This is exactly when a reviewable contract is more valuable than another backend abstraction. The new design center should therefore be read together with `design/terminal-surface-lane-map.md` and `design/terminal-surface-pilot-program.md`, not just the base kit.

Sources:
- https://docs.rs/crossterm
- https://docs.rs/crossterm/latest/crossterm/event/index.html
- https://docs.rs/ratatui/latest/ratatui/struct.Terminal.html
- https://ratatui.rs/concepts/backends/
- https://docs.rs/termwiz
- https://docs.rs/termwiz/latest/termwiz/caps/index.html
- https://docs.rs/termwiz/latest/termwiz/escape/index.html
- https://docs.rs/anstream/latest/anstream/struct.AutoStream.html
- https://docs.rs/unicode-width
- https://docs.rs/unicode-segmentation
- https://docs.rs/unicode-display-width
- https://docs.rs/reedline
- https://docs.rs/ratatui/latest/ratatui/backend/struct.TestBackend.html
- https://docs.rs/vt100/latest/vt100/
- https://docs.rs/ratatui-image

## What should be built
A first credible version should ship:
1. `terminal-surface/v0`, `terminal-capability-profile/v0`, `terminal-render-profile/v0`, `terminal-input-profile/v0`, `terminal-unicode-layout-profile/v0`, `terminal-graphics-profile/v0`, `terminal-adapter-profile/v0`, `terminal-vector-set/v0`, `terminal-check-report/v0`, and `terminal-pack/v0`
2. one styled-output pilot showing explicit color-negotiation and non-TTY fallback posture
3. one Ratatui-on-Crossterm pilot publishing raw-mode, alternate-screen, resize, and Unicode layout assumptions
4. one Termwiz pilot publishing capability-probing and escape-semantics posture
5. one interactive editor pilot publishing bracketed-paste, completion, and multiline behavior
6. one headless evidence lane using parser or test-backend checks
7. one richer-protocol pilot publishing image/hyperlink/graphics support and fallback behavior

The winning version is compact, semantic, and boundary-aware.
It should make terminal behavior legible together rather than canonizing one backend stack. It should also make the lane split explicit: styled-output first, TUI second, line-editor third, capability/probing fourth, parser/test fifth, graphics sixth.

## Initial pilots
- **Styled CLI lane** — color/style negotiation with explicit non-TTY and env behavior
- **Full-screen TUI lane** — raw mode, alternate screen, resize handling, buffer layout, cleanup behavior
- **Capability-probing lane** — terminal capability discovery and escape semantics
- **Interactive shell lane** — bracketed paste, Unicode editing, menus/history/completion posture
- **Headless-evidence lane** — parser or test-backend validation instead of screenshot-only confidence
- **Graphics lane** — image/hyperlink protocol support with fallback declarations

## Milestones
1. **v0 artifacts + vocabulary**
   - publish schemas and minimal examples
   - document capability, rendering, input, layout, graphics, and evidence vocabulary
2. **v0.2 output + TUI pilots**
   - ship one styled-output pilot and one full-screen TUI pilot
   - show where raw mode, color negotiation, and alternate-screen expectations diverge
3. **v0.3 Unicode + evidence depth**
   - add layout-policy and headless-evidence artifacts
   - capture grapheme/width assumptions explicitly
4. **v0.4 graphics + ecosystem adapters**
   - add richer protocol and adapter artifacts
   - publish fallback behavior clearly
5. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one identical backend stack

## Success metrics
- Library authors can review terminal-state, render, input, Unicode layout, and graphics assumptions without reverse-engineering them from examples.
- Applications can distinguish style-only output from full-screen raw-mode TUIs and interactive line editors.
- Reviewers can tell color negotiation, width policy, and cleanup posture apart.
- CI can attach terminal evidence stronger than screenshots alone.
- Backend migrations become diffable instead of surprising.

## Archive fit
This proposal fills a real gap in the archive:
- **Command Surface Kit** handles a tool’s own CLI parse/help/transcript surface,
- **Process Surface Kit** handles subprocesses, PTYs, and supervision,
- **A11yKit** handles accessibility and GUI-adjacent testing concerns,
- **Localization Surface Kit** handles locale/message semantics,
- **Runtime Capability Kit** handles whether terminal- or console-adjacent authority exists at all.

But none of those is the portable contract for **raw mode, alternate screen, input-event posture, Unicode layout rules, graphics protocols, cleanup guarantees, and attachable terminal evidence**.
Terminal Surface Kit is the missing substrate above Rust’s already powerful and already fragmented terminal ecosystem.
