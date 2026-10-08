# Gap: terminal surfaces, console capabilities, input semantics, Unicode layout, graphics protocols, and reviewable terminal-app contracts

## What is missing
Rust has a strong terminal ecosystem, but it still lacks a **portable way to publish what a terminal-facing surface actually means**.

Today there is no standard way to say:
- whether an application expects plain stdout styling, full-screen alternate-screen rendering, or a richer TUI frame model,
- whether it needs raw mode, and if so which cleanup/restore guarantees it claims,
- whether it depends on keyboard enhancement protocols, bracketed paste, focus events, mouse capture, synchronized updates, or resize-event handling,
- whether color support is always-on, forced-off, auto-detected, env-driven, Windows-console-mediated, or terminal-probed,
- whether width/layout is based on codepoints, grapheme clusters, East Asian width rules, emoji heuristics, or a specific Unicode version,
- whether rendering assumes simple styled text only or also hyperlinks, images, Sixel/Kitty/iTerm graphics, or backend-specific escape capabilities,
- whether testing evidence comes from cell-buffer snapshots, virtual-terminal parsers, PTY transcripts, or emulator/back-end matrices,
- and what evidence actually ran: raw-mode cleanup vectors, alternate-screen restore vectors, Unicode layout vectors, resize/input vectors, graphics-protocol vectors, or headless snapshot probes.

That gap matters because Rust’s terminal ecosystem is not one thing.
`crossterm` exposes a broad cross-platform terminal-manipulation and input-event layer. Ratatui abstracts rendering over multiple backends and already has a dedicated `TestBackend` for integration-style checks. `termwiz` has a richer capability/probing and escape-semantics story. `anstream` and related style/color crates handle output-color negotiation. `unicode-width`, `unicode-segmentation`, and newer width engines show that layout policy is its own semantic lane. `reedline` proves interactive line-editing and bracketed-paste behavior matter. `vt100` and related parsers show that terminal-state evidence is testable. `ratatui-image` shows graphics-protocol support is real, not speculative.

So the missing contribution is not another TUI crate, color crate, or line editor.
It is a **reviewable terminal-surface layer** for publishing capability assumptions, render/input posture, Unicode layout rules, graphics support, lane identity, and evidence honestly.

Sources:
- https://docs.rs/crossterm
- https://docs.rs/crossterm/latest/crossterm/event/index.html
- https://docs.rs/ratatui/latest/ratatui/struct.Terminal.html
- https://ratatui.rs/concepts/backends/
- https://docs.rs/ratatui/latest/ratatui/backend/struct.TestBackend.html
- https://docs.rs/termwiz
- https://docs.rs/termwiz/latest/termwiz/caps/index.html
- https://docs.rs/termwiz/latest/termwiz/escape/index.html
- https://docs.rs/anstream/latest/anstream/struct.AutoStream.html
- https://docs.rs/unicode-width
- https://docs.rs/unicode-segmentation
- https://docs.rs/unicode-display-width
- https://docs.rs/reedline
- https://docs.rs/reedline/latest/reedline/struct.Reedline.html
- https://docs.rs/vt100/latest/vt100/
- https://docs.rs/ratatui-image

## The current seam is awkward
Rust already has several real terminal subcultures, but their semantics do not line up cleanly:
- Ratatui explicitly abstracts over Crossterm, Termion, and Termwiz backends, and its backend guide says applications usually still use the backend directly for keyboard, mouse, window events, raw mode, and the alternate screen;
- `crossterm` explicitly positions itself as a cross-platform terminal-manipulation library for text-based interfaces, including alternate screen, raw mode, style/color control, input events, mouse, resize, focus, and bracketed paste support;
- `termwiz` goes further on terminal capability probing and escape parsing, documenting both heuristic capability discovery and semantic encode/decode of escape sequences;
- color/style output is its own lane again: `anstream` documents automatic color detection, env-driven behavior such as `NO_COLOR` / `CLICOLOR`, and Windows fallback behavior when full virtual terminal processing is unavailable;
- Unicode layout remains fragmented: `unicode-width` documents width according to UAX #11-style rules, `unicode-segmentation` documents grapheme-cluster boundaries according to UAX #29, and `unicode-display-width` explicitly computes display width over grapheme clusters rather than raw codepoints;
- interactive terminal apps have still more semantics: `reedline` documents Unicode-aware editing and a distinct bracketed-paste mode that changes multiline paste behavior;
- testing and evidence are split too: Ratatui ships a `TestBackend` for buffer-oriented integration tests, while `vt100` parses terminal byte streams into an in-memory rendered terminal state;
- and richer terminal protocols already exist in practice: `ratatui-image` documents multiple graphics backends across Sixel, Kitty, and iTerm2 image protocols.

So the ecosystem is not missing *terminal crates*.
It is missing the **artifact family that records which capabilities, render assumptions, input semantics, Unicode/layout rules, graphics protocols, and test evidence a public terminal surface actually chose**.

The archive also needs a sharper lane map than it had before. The current ecosystem already separates at least six terminal lanes that are easy to flatten if the repo is not careful: styled-output/color-policy work (`anstream`), full-screen TUI work (Ratatui plus a backend), interactive line-editing (`reedline`), capability/protocol stacks (`termwiz`), parser/test evidence (`TestBackend` / `vt100`), and graphics/rich-protocol work (`ratatui-image`). A terminal-surface contract that does not preserve those lanes will overclaim almost immediately.

Sources:
- https://docs.rs/crossterm
- https://docs.rs/crossterm/latest/crossterm/event/index.html
- https://docs.rs/ratatui/latest/ratatui/struct.Terminal.html
- https://ratatui.rs/concepts/backends/
- https://docs.rs/ratatui/latest/ratatui/backend/struct.TestBackend.html
- https://docs.rs/termwiz
- https://docs.rs/termwiz/latest/termwiz/caps/index.html
- https://docs.rs/termwiz/latest/termwiz/escape/index.html
- https://docs.rs/anstream/latest/anstream/struct.AutoStream.html
- https://docs.rs/unicode-width
- https://docs.rs/unicode-segmentation
- https://docs.rs/unicode-display-width
- https://docs.rs/reedline
- https://docs.rs/vt100/latest/vt100/
- https://docs.rs/ratatui-image

## Why this matters
This gap matters because terminal semantics cut across many high-value Rust systems at once:
1. **CLI tools** — color, width, styling, and TTY detection decide whether output is readable, script-safe, or broken;
2. **full-screen TUIs** — raw mode, alternate screen, resize handling, Unicode layout, and backend choice decide whether the app behaves correctly;
3. **interactive shells and REPLs** — multiline paste, history UI, completion menus, cursor placement, and prompt rendering are terminal contracts, not implementation trivia;
4. **remote and CI execution** — headless testing, snapshot parsing, and capability fallbacks matter when the real terminal is absent or heterogeneous;
5. **cross-platform support** — Windows console differences, env-based color policy, and terminal capability probing leak into product claims quickly;
6. **richer terminal media** — images, hyperlinks, focus/mouse events, and keyboard-enhancement protocols are already real ecosystem demands rather than future wishcasting.

A worthy contribution here is therefore not another renderer, another style DSL, or another terminal abstraction.
It is a way to treat **terminal surfaces as reviewable ecosystem infrastructure**.

Sources:
- https://docs.rs/crossterm
- https://docs.rs/crossterm/latest/crossterm/event/index.html
- https://docs.rs/ratatui/latest/ratatui/struct.Terminal.html
- https://docs.rs/anstream/latest/anstream/struct.AutoStream.html
- https://docs.rs/reedline
- https://docs.rs/vt100/latest/vt100/
- https://docs.rs/ratatui-image

## What “good” looks like
A worthy contribution here is **not** one fake universal terminal badge.
It is a shared terminal-surface boundary:
- one `terminal-surface/v0` describing the top-level terminal family and intended interaction model,
- one `terminal-capability-profile/v0` describing raw-mode needs, alternate-screen posture, cursor-control assumptions, resize/focus/mouse/paste support, and fallback expectations,
- one `terminal-render-profile/v0` describing styled-output versus diffed-frame rendering, double-buffering or synchronized-update posture, color-depth assumptions, and cleanup/restore policy,
- one `terminal-input-profile/v0` describing keyboard, mouse, paste, focus, resize, and line-editor semantics,
- one `terminal-unicode-layout-profile/v0` describing width engine, grapheme policy, truncation/wrapping rules, Unicode-version assumptions, and ambiguous-width posture,
- one `terminal-graphics-profile/v0` describing hyperlinks, image/graphics protocols, inline-media posture, and fallback behavior,
- one `terminal-adapter-profile/v0` describing bridges between crossterm, termwiz, ratatui, line editors, parser/test backends, and style/color detection stacks,
- one `terminal-vector-set/v0` describing raw-mode cleanup, alternate-screen restore, Unicode layout, mouse/paste/focus, resize, color-negotiation, graphics-protocol, and headless snapshot vectors,
- one `terminal-check-report/v0` recording which vectors actually ran,
- and one `terminal-pack/v0` bundle for docs, CI, transcripts, screenshots, parser fixtures, and archaeology.

That would let Rust teams reason about terminal choices with **explicit artifacts** instead of a brittle mix of backend docs, escape-sequence lore, and screenshot-based confidence. The next refinement is explicit too: keep styled-output, full-screen TUI, line-editor, capability/probing, parser/test, and graphics lanes comparable without pretending they are one “terminal support” score.

## Non-goals
This gap should not be used to:
- replace `crossterm`, Ratatui, `termwiz`, line editors, or terminal parsers,
- define one canonical terminal backend or one canonical color/style stack,
- collapse rendering, input, Unicode layout, graphics protocols, and test evidence into one fake manifest,
- or pretend that "terminal support" can be solved by one abstraction trait.

The job is smaller and sharper:
**make terminal surfaces legible, honest, and checkable.**
