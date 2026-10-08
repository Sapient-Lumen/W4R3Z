# Design: Terminal Surface Kit

Read this together with:
- [`design/terminal-surface-lane-map.md`](./terminal-surface-lane-map.md)
- [`design/terminal-surface-pilot-program.md`](./terminal-surface-pilot-program.md)
- [`design/cli-productization-stack.md`](./cli-productization-stack.md)
- [`design/process-surface-kit.md`](./process-surface-kit.md)
- [`proposals/epic-terminal-surface-kit.md`](../proposals/epic-terminal-surface-kit.md)

## Problem statement
Rust terminal applications and terminal-aware libraries already span several distinct semantic lanes:
- basic styled output and color-aware CLIs,
- full-screen alternate-screen TUIs,
- interactive line editors and REPLs,
- richer terminal-capability/probing stacks,
- virtual-terminal parsers and test backends,
- and emerging graphics/media protocols inside terminals.

But those surfaces are usually published indirectly through crate choice, screenshots, examples, or bug reports.
There is still no compact, portable way to declare:
- whether raw mode or alternate screen is required, optional, or avoided,
- what input-event families are actually consumed,
- how color/style support is negotiated,
- what Unicode width/grapheme/layout rules are assumed,
- whether richer graphics protocols are used,
- how cleanup and restore are handled,
- and which terminal checks actually ran.

Terminal Surface Kit should provide that missing review layer.
It should sit above terminal backends and below application-specific UI logic.

## Design goals
1. **Make terminal claims explicit**
   - raw mode, alternate screen, input families, Unicode/layout policy, color negotiation, and graphics posture should be declared, not inferred.
2. **Preserve real backend differences**
   - Crossterm, Termwiz, Ratatui backends, line editors, parser/test stacks, and simple style-output crates should remain distinguishable.
3. **Separate rendering from input and layout**
   - output styling, frame rendering, input capture, width policy, and graphics support are different semantic axes.
4. **Treat cleanup/restore as part of the contract**
   - terminal-state restoration is a product guarantee, not a courtesy.
5. **Make testing evidence first-class**
   - snapshot buffers, parser-driven state checks, PTY transcripts, and emulator matrices should be attachable evidence, not ad hoc screenshots.
6. **Stay useful on stable Rust and across platforms**
   - the kit should document capability posture honestly rather than assuming uniform Unix semantics.

## Core artifacts
### 1. `terminal-surface/v0`
Top-level declaration for a terminal-facing surface.
Fields should include:
- `surface_id`
- `kind` (`styled-output`, `line-editor`, `full-screen-tui`, `hybrid`, `terminal-protocol-tooling`)
- `interaction_model`
- `primary_backends`
- `target_platforms`
- `requires_tty`
- `headless_test_lane`
- `docs` / `owners` / `version`

### 2. `terminal-capability-profile/v0`
Declares terminal-state and capability assumptions:
- raw mode (`required`, `optional`, `never`)
- alternate screen posture
- cursor visibility/movement assumptions
- resize-event expectations
- focus-event support
- mouse-capture support
- bracketed-paste support
- keyboard-enhancement posture
- restore guarantees and failure caveats

### 3. `terminal-render-profile/v0`
Declares output/render semantics:
- stream-oriented versus frame-oriented rendering
- color model (`none`, `ansi16`, `ansi256`, `truecolor`, `auto`)
- color-negotiation lane (`env`, `tty-detect`, `cap-probe`, `forced`)
- style assumptions (bold/italic/underline/hyperlink)
- synchronized-update posture
- diffed-buffer versus immediate-write behavior
- fallback behavior for reduced capability terminals

### 4. `terminal-input-profile/v0`
Declares input semantics:
- key-event lane
- mouse lane
- paste lane
- focus lane
- resize lane
- line-editing semantics
- completion/history/menu posture
- blocking/poll/stream event model

### 5. `terminal-unicode-layout-profile/v0`
Declares text-layout assumptions:
- width engine / crate
- grapheme engine / crate
- Unicode version assumptions if declared
- ambiguous-width posture
- emoji / ZWJ handling posture
- truncation/wrapping policy
- cell-width versus grapheme-layout distinctions

### 6. `terminal-graphics-profile/v0`
Declares richer terminal protocol use:
- hyperlinks
- inline images / graphics
- supported protocols (Kitty / Sixel / iTerm2 / none)
- query/probe strategy
- fallback to text placeholders or plain rendering
- scroll/overwrite caveats

### 7. `terminal-adapter-profile/v0`
Declares bridges and glue:
- Ratatui on Crossterm / Termwiz / Termion
- style-output through `anstream`
- line editors embedded into TUIs or CLIs
- parser/test adapters (`vt100`, backends, PTYs)
- graphics protocol adapters

### 8. `terminal-vector-set/v0`
Attachable vectors for:
- raw-mode entry/restore
- alternate-screen entry/restore
- color negotiation
- Unicode-width/grapheme layout
- wrapping/truncation
- mouse/focus/paste events
- resize handling
- graphics-protocol detection/fallback
- headless parser/snapshot parity

### 9. `terminal-check-report/v0`
Machine-readable record of:
- what vectors ran,
- under which terminal/emulator/OS matrix,
- what was skipped,
- what requires a real TTY or PTY,
- and what remains illustrative-only.

### 10. `terminal-pack/v0`
Bundle for CI artifacts, transcripts, parser fixtures, screenshots, and docs.

## Default policy
- **Raw mode must be explicit.**
- **Alternate-screen use must be explicit.**
- **Color negotiation must be explicit.**
- **Unicode width and grapheme policy must be explicit.**
- **Graphics protocol use must be explicit.**
- **Restore/cleanup guarantees must be explicit.**
- **Headless testing claims must be explicit.**
- **Best-effort and backend-specific outcomes are valid outcomes.**

## What the kit should provide to others
- **Application authors:** a way to state what their terminal UX truly requires.
- **Library authors:** a way to publish backend, input, layout, and cleanup semantics honestly.
- **Tooling authors:** a way to compare crossterm, termwiz, ratatui, and parser/test lanes without flattening them.
- **Reviewers:** a way to tell style-only output, line-editing shells, and full-screen TUIs apart.
- **Migration work:** a way to compare backend switches or Unicode/layout engine changes with attachable evidence.

## Overlap boundaries
- **Not Command Surface Kit:** that kit owns a tool’s parse/help/completion/manpage surface; Terminal Surface Kit owns terminal-state, render, input, and layout semantics once the command is running.
- **Not Process Surface Kit:** that kit owns spawned-child pipes, PTYs, and supervision; this kit owns the application’s own terminal interaction contract.
- **Not A11yKit:** that kit owns accessibility semantics and UI test substrate across GUI stacks; this kit owns terminal capability/input/render truth.
- **Not Localization Surface Kit:** that kit owns locale/message/fallback semantics; this kit owns how terminal layout renders already-chosen strings.
- **Not Filesystem or Runtime Capability Kits:** those kits own authority and path semantics; this kit only records terminal behavior.

## Hard problems (explicitly scoped)
1. **Raw mode and restore are operationally sharp**
   - the kit should record guarantees and caveats, not pretend cleanup is always perfect.
2. **Unicode layout is not one rule**
   - codepoint width, grapheme segmentation, emoji handling, and ambiguous-width posture should remain separate lanes.
3. **TTY detection and color policy are not identical**
   - env-based color controls, tty detection, and capability probing should stay distinct.
4. **Graphics protocols are optional and fragmented**
   - do not let image/hyperlink support masquerade as generic terminal support.
5. **Testing comes in multiple forms**
   - buffer tests, parser-based tests, PTY transcripts, and emulator matrices should remain distinguishable.

## Evaluation plan
The ranked rollout now lives in [`design/terminal-surface-pilot-program.md`](./terminal-surface-pilot-program.md).

The short version:
1. styled-output truth first,
2. full-screen TUI second,
3. interactive line-editor third,
4. capability-probing/protocol-semantic fourth,
5. parser/test-backend evidence fifth,
6. graphics-protocol truth sixth.

Success bar:
- projects can publish terminal assumptions without inventing their own schema,
- reviewers can distinguish lane family, render/input/layout/probe posture, and graphics posture cleanly,
- terminal cleanup and fallback behavior become visible before release,
- adapter lossiness becomes explicit instead of implicit,
- and the ecosystem gets a reusable boundary above today’s fragmented terminal stack without flattening meaningful differences.
