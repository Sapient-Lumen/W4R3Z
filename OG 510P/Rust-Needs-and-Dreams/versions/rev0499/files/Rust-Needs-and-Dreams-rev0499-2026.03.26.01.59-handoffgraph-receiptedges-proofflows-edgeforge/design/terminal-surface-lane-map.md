# Design: Terminal Surface Lane Map (styled output, full-screen TUI, line editing, capability-probing, parser/test backends, and graphics protocols)

## Goal
Make the archive more precise about **what kind of terminal claim is actually being made**.

Rust’s terminal ecosystem is strong, but the phrase “terminal support” still hides too much.
A color-aware CLI using `anstream`, a Crossterm event loop in raw mode, a Ratatui full-screen app on `CrosstermBackend`, a Termwiz capability/probing tool, a Reedline shell with bracketed paste, a `TestBackend` snapshot suite, a `vt100` parser check, and a `ratatui-image` graphics widget are **different but connected** lanes.

The worthy contribution here is therefore not another backend facade, style crate, or screenshot-heavy TUI showcase.
It is a **portable lane map and evidence boundary** that lets tools say which terminal lane they occupy, what assumptions attach to it, where adapters are lossy, and which downstream consumers may reuse the claim honestly.

Read this together with:
- [`design/terminal-surface-kit.md`](./terminal-surface-kit.md)
- [`design/terminal-surface-pilot-program.md`](./terminal-surface-pilot-program.md)
- [`design/cli-productization-stack.md`](./cli-productization-stack.md)
- [`design/process-surface-kit.md`](./process-surface-kit.md)
- [`proposals/epic-terminal-surface-kit.md`](../proposals/epic-terminal-surface-kit.md)

## Why this note is needed now
The current ecosystem signals line up around one conclusion: Rust needs a better **terminal-surface contract**, not just more terminal crates.

- Crossterm’s current docs keep terminal state sharp: raw mode changes input buffering and key handling, alternate-screen entry/leave is explicit, synchronized updates are explicit, and keyboard-enhancement support is queried rather than assumed.
  https://docs.rs/crossterm/latest/crossterm/terminal/index.html
- Crossterm’s event docs also keep event families separate: keyboard events need raw mode to work properly, while mouse and focus events must be enabled explicitly, and paste events are feature-gated.
  https://docs.rs/crossterm/latest/src/crossterm/event.rs.html
- Ratatui’s current backend docs explicitly say applications usually still use the backend directly to capture keyboard/mouse/window events and enable raw mode and alternate screen. Ratatui’s `Terminal` owns buffer/cursor/viewport state, but not all terminal-state policy by itself.
  https://ratatui.rs/concepts/backends/
  https://docs.rs/ratatui/latest/ratatui/struct.Terminal.html
  https://docs.rs/ratatui/latest/ratatui/backend/struct.CrosstermBackend.html
  https://docs.rs/ratatui/latest/ratatui/backend/struct.TermwizBackend.html
- Ratatui’s own panic-hook recipe is a direct reminder that cleanup/restore is a public contract, not a hidden courtesy; applications are expected to restore raw mode and the main screen on panic.
  https://ratatui.rs/recipes/apps/panic-hooks/
- Termwiz’s capability docs explain why terminal capability detection is messy across remote systems, stale terminfo, multiplexers, and local overrides; its escape module also keeps semantic encode/decode distinct from full terminal emulation.
  https://docs.rs/termwiz/latest/termwiz/caps/index.html
  https://docs.rs/termwiz/latest/termwiz/escape/index.html
- `anstream` proves styled-output/color policy is its own lane: it strips colors for non-terminals, respects `NO_COLOR` and `CLICOLOR`, and uses Windows console fallback when VT processing is unavailable.
  https://docs.rs/anstream/latest/anstream/struct.AutoStream.html
- Unicode layout is still visibly plural. `unicode-display-width` computes width over grapheme clusters rather than raw codepoints, which is a different claim from a simpler codepoint-width story.
  https://docs.rs/unicode-display-width/latest/unicode_display_width/
- Reedline makes interactive editing semantics explicit: bracketed paste materially changes multiline paste behavior and is not a generic “terminal feature” that every CLI should inherit silently.
  https://docs.rs/reedline/latest/reedline/struct.Reedline.html
- Ratatui `TestBackend` and `vt100` show that headless parser/buffer evidence is a real lane rather than screenshot theater.
  https://docs.rs/ratatui/latest/ratatui/backend/struct.TestBackend.html
  https://docs.rs/vt100/latest/vt100/
- `ratatui-image` proves richer graphics protocols are real present-tense territory: Sixel, Kitty, and iTerm2 support already exist as distinct graphics backends with protocol queries and fallbacks.
  https://docs.rs/ratatui-image/latest/ratatui_image/

## The lane map

### Lane 1 — Styled-output and color-policy lane
**What it is**
- Terminal-aware plain-text output with style/color negotiation.
- `anstream`, `anstyle`, simple color/style crates, and CLI output that may or may not require a TTY.

**Why it matters**
- This is the baseline lane most CLIs actually occupy.
- It is the cleanest place to declare `NO_COLOR` / `CLICOLOR` / non-TTY / Windows-fallback posture without dragging in full-screen TUI semantics.

**What the archive should preserve**
- style-only versus frame-rendered output,
- color-negotiation source (`env`, `tty-detect`, `probe`, `forced`),
- hyperlink/style assumptions,
- stream-specific differences,
- and non-TTY fallback behavior.

**What it should not pretend**
- that styled output implies raw mode,
- that color policy equals broader terminal-capability truth,
- or that screenshots say enough about negotiation behavior.

### Lane 2 — Full-screen TUI lane
**What it is**
- Buffer- or frame-oriented full-screen terminal apps.
- Ratatui plus a backend family such as Crossterm or Termwiz.

**Why it matters**
- This lane adds raw mode, alternate screen, viewport/buffer state, resize handling, and cleanup obligations.
- Ratatui explicitly keeps backend and application responsibilities visible rather than pretending the UI crate owns the whole terminal contract.

**What the archive should preserve**
- backend family,
- raw-mode and alternate-screen posture,
- synchronized-update or diff-buffer posture,
- resize/input assumptions,
- viewport/cursor/restore policy,
- and panic/teardown behavior.

**What it should not pretend**
- that all Ratatui apps share the same terminal contract,
- that full-screen rendering and line-editing shells are one lane,
- or that backend swaps are semantics-free.

### Lane 3 — Interactive line-editor / REPL lane
**What it is**
- Prompt-driven interactive editing with history, menus, completion, paste handling, and Unicode-aware editing.
- Reedline and adjacent prompt/editor crates.

**Why it matters**
- This lane changes input semantics more than rendering semantics.
- Bracketed paste, completion UI, multiline editing, and prompt redraw rules belong here rather than inside a generic TUI bucket.

**What the archive should preserve**
- line-editing posture,
- bracketed-paste behavior,
- completion/history/menu capabilities,
- blocking/polling/stream event model,
- and how prompts redraw or degrade on narrower capability terminals.

**What it should not pretend**
- that a line editor is just a tiny TUI,
- that raw mode implies line-editing semantics,
- or that Unicode-aware editing equals Unicode-aware rendering.

### Lane 4 — Capability-probing / protocol-semantic lane
**What it is**
- Terminal capability discovery, protocol probing, and semantic escape encode/decode.
- Termwiz-style capability and escape stacks.

**Why it matters**
- This lane answers a different question: what does the terminal actually support, especially across SSH, multiplexers, stale terminfo, and overrides?
- It is where terminal support becomes remote-system- and emulator-sensitive.

**What the archive should preserve**
- heuristics versus probe posture,
- remote/multiplexer caveats,
- semantic escape encode/decode scope,
- explicit override inputs,
- and unsupported or guess-based areas.

**What it should not pretend**
- that probing is the same as rendering,
- that a richer capability stack is a drop-in upgrade for every CLI,
- or that capability guesses are the same as verified support.

### Lane 5 — Parser/test-backend evidence lane
**What it is**
- Headless evidence built from in-memory buffers, virtual-terminal parsers, and snapshot-style checks.
- Ratatui `TestBackend`, `vt100`, and related test harnesses.

**Why it matters**
- This lane is the difference between “looks good on my terminal” and actual attachable evidence.
- It also keeps headless verification distinct from real-emulator or PTY-based checks.

**What the archive should preserve**
- buffer snapshot versus parsed byte-stream evidence,
- what real-terminal capabilities were not exercised,
- emulator/PTY gaps,
- and parity or drift between test backends and real backends.

**What it should not pretend**
- that parser/buffer checks prove PTY behavior,
- that screenshots are evidence,
- or that one headless backend validates all Unicode/layout/protocol paths.

### Lane 6 — Graphics / rich-terminal-protocol lane
**What it is**
- Hyperlinks, inline images, and richer terminal graphics protocols.
- `ratatui-image` and adjacent protocol-specific crates.

**Why it matters**
- This lane is already real and fragmented.
- Kitty, Sixel, iTerm2, and text-only halfblock fallbacks are adjacent answers, not one generic “image support” story.

**What the archive should preserve**
- graphics protocol family,
- query/probe posture,
- fallback policy,
- cell-space versus pixel-space assumptions,
- and scroll/overwrite caveats.

**What it should not pretend**
- that graphics support is part of ordinary styled-output support,
- that all terminal emulators will degrade identically,
- or that protocol choice is purely cosmetic.

## Adapter rules
A lane map becomes useful only if it names **lossy boundaries**.
The archive should therefore treat these as first-class adapter classes:

1. **styled-output ↔ full-screen TUI**
   - adds or removes raw-mode, alternate-screen, frame buffering, and teardown obligations.
2. **full-screen TUI ↔ line editor**
   - changes event and redraw semantics even when both use the same backend.
3. **backend abstraction ↔ capability probing**
   - can lose probe detail or replace verified capabilities with assumptions.
4. **real terminal ↔ parser/test backend**
   - can lose actual terminal-emulator behavior, PTY behavior, and some protocol details.
5. **text rendering ↔ graphics protocols**
   - can change layout, fallback, and emulator-compatibility guarantees.

Adapters should report not just “supported” or “unsupported”, but what semantics changed.

## What this changes in the archive
This note sharpens Terminal Surface Kit in one important way:

- the archive should stop treating **styled output**, **full-screen TUI**, **interactive line editors**, **capability/protocol stacks**, **parser/test backends**, and **graphics protocols** as one bucket;
- pilot programs should prove those lanes separately before speaking about “Rust terminal support” in general;
- downstream consumers should import only the lane facts they can honestly reuse.

The worthy contribution here is therefore a thin `cargo termsurf` / `terminal-pack/v0` layer whose lane profiles, adapter reports, vector reports, and consumer handoffs make terminal behavior reviewable without forcing one universal terminal abstraction.
