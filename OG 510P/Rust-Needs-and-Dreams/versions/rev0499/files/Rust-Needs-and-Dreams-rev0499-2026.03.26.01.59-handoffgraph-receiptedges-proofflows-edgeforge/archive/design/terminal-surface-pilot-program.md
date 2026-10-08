# Design: Terminal Surface Pilot Program

## Goal
Turn Terminal Surface Kit from a good conceptual map into a **ranked execution plan**.

Rust already has enough terminal machinery to prove the gap is real.
The next step is not more backend accumulation.
It is a pilot sequence that shows Rust projects can publish **reviewable terminal-surface truth** across styled output, full-screen TUIs, line editors, capability/probing stacks, parser/test backends, and graphics protocols without pretending those lanes have already converged.

Read this together with:
- [`design/terminal-surface-kit.md`](./terminal-surface-kit.md)
- [`design/terminal-surface-lane-map.md`](./terminal-surface-lane-map.md)
- [`design/cli-productization-stack.md`](./cli-productization-stack.md)
- [`design/process-surface-kit.md`](./process-surface-kit.md)
- [`proposals/epic-terminal-surface-kit.md`](../proposals/epic-terminal-surface-kit.md)

## Why this needs its own design layer
The Terminal Surface Kit already defines the artifact family: surface/profile/vector/check/pack artifacts.

What it did **not** yet answer clearly enough is:
- which terminal lanes should be piloted first,
- which distinctions are worth locking in early,
- how to keep styled output separate from TUI and line-editor claims,
- how to keep capability probing separate from rendering claims,
- and what counts as pilot success versus another terminal demo.

Without that layer, terminal-surface work risks two bad outcomes:
1. **backend flattening** — the archive starts implying all terminal libraries differ only in polish or ergonomics;
2. **demo theater** — screenshots, GIFs, or one happy-path demo impersonate evidence for cleanup, color negotiation, Unicode layout, or protocol support.

## Design principles
1. **Start from exact lane identity.** Every pilot should say which terminal lane it is proving.
2. **Keep output, input, layout, and probing distinct.** They are connected, but not interchangeable.
3. **Treat cleanup/restore as public contract.** Raw mode and alternate screen are product obligations, not just setup code.
4. **Treat Unicode layout as explicit policy.** Width and grapheme semantics are not decorative implementation details.
5. **Treat parser/test evidence as its own lane.** Headless evidence is useful, but it must not silently overclaim real-emulator behavior.
6. **Treat graphics protocols as optional and fragmented.** Image support should not masquerade as generic terminal support.
7. **Prefer vectors that reveal lossiness.** Non-TTY color stripping, panic restore, resize, bracketed paste, grapheme width, and graphics fallback vectors matter more than feature matrices.
8. **Consumer handoffs must stay bounded.** A CLI reviewer, support engineer, or distribution consumer should only claim the lane facts actually exported.

## Artifact family
### 1. `terminal-pilot-brief/v0`
Why this terminal lane is being piloted.

Should record:
- pilot id and summary
- lane family (`styled-output`, `full-screen-tui`, `line-editor`, `capability-probing`, `parser-test`, `graphics`)
- why the lane matters now
- intended consumer(s)
- why the lane is tractable now

### 2. `terminal-lane-profile/v0`
The declared contract for the lane.

Should record:
- backend or protocol family
- raw-mode / alternate-screen posture if relevant
- color/input/layout/probe expectations
- cleanup/restore requirements
- platform limits
- adapter/lossiness notes
- explicit unsupported areas

### 3. `terminal-query-budget/v0`
The bounded questions the pilot must answer.

Should record:
- named semantic questions in scope
- required answer fields
- required uncertainty classes
- mandatory vector coverage
- explicit out-of-scope questions

### 4. `terminal-consumer-handoff/v0`
How a downstream consumer may reuse the pilot.

Should record:
- consumer class (`cli-review`, `tui-review`, `support`, `migration`, `docs`, `distribution`, `agent-runner`)
- which artifacts are consumed directly
- which claims remain advisory only
- what the consumer must still verify independently

### 5. `terminal-pilot-scorecard/v0`
Decides whether widening is justified.

Should ask:
- did the pilot preserve lane identity honestly?
- did it make lossy adapters explicit?
- did it attach concrete vectors and reports?
- did at least one real consumer import it?
- did it avoid claiming universal terminal support?

### 6. `terminal-pilot-pack/v0`
Bundle of:
- pilot brief
- lane profile
- query budget
- consumer handoff
- terminal-surface artifacts from the base kit
- scorecard
- references and rendered summaries

## Ranked first pilots

### 1) Styled-output truth lane
**Why first**
- It is the baseline lane most Rust CLIs actually occupy.
- Current `anstream` docs already expose enough sharp semantics to justify a pack immediately: non-TTY stripping, `NO_COLOR`/`CLICOLOR` handling, and Windows console fallback.

**Primary artifacts**
- `terminal-surface/v0`
- `terminal-render-profile/v0`
- `terminal-capability-profile/v0`
- vectors for non-TTY output, env-driven color policy, forced color, and Windows fallback posture

**Primary consumers**
- CLI reviewers
- docs/transcript consumers
- distribution/support consumers

### 2) Full-screen TUI lane
**Why second**
- This is where raw mode, alternate screen, resize, buffer state, and panic/restore obligations become sharp.
- Ratatui already exposes the right split between backend choice and application responsibility.

**Primary artifacts**
- `terminal-surface/v0`
- `terminal-capability-profile/v0`
- `terminal-render-profile/v0`
- `terminal-input-profile/v0`
- vectors for raw-mode enable/disable, alternate-screen restore, resize handling, synchronized update posture, and buffer diff/render evidence

**Primary consumers**
- TUI reviewers
- app maintainers
- migration and support consumers

### 3) Interactive line-editor lane
**Why third**
- This is where user-facing input behavior becomes much richer than plain event loops.
- Reedline already proves bracketed paste, multiline editing, menus, and completion posture deserve explicit review.

**Primary artifacts**
- `terminal-input-profile/v0`
- `terminal-capability-profile/v0`
- `terminal-unicode-layout-profile/v0`
- vectors for bracketed paste, completion menus, history redraw, multiline validation, and narrow-terminal fallback

**Primary consumers**
- shell/REPL authors
- support/docs consumers
- migration reviewers

### 4) Capability-probing / protocol-semantic lane
**Why fourth**
- This is the lane that keeps remote systems, multiplexers, and stale terminfo reality visible.
- It should arrive after the simpler rendering/input lanes are already explicit, so the archive does not mistake probing for universal rendering truth.

**Primary artifacts**
- `terminal-capability-profile/v0`
- `terminal-adapter-profile/v0`
- vectors for remote/multiplexer heuristics, override inputs, capability query results, and semantic escape encode/decode coverage

**Primary consumers**
- terminal tools
- migration reviewers
- protocol/graphics consumers

### 5) Parser/test-backend evidence lane
**Why fifth**
- Headless evidence is valuable, but it should arrive only after the lanes it claims to represent are explicit.
- This lane proves the archive can distinguish buffer snapshots and parser reconstructions from real-terminal behavior.

**Primary artifacts**
- `terminal-vector-set/v0`
- `terminal-check-report/v0`
- `terminal-adapter-profile/v0`
- vectors for buffer snapshots, parser reconstruction, Unicode/layout parity checks, and declared exclusions for PTY/real-emulator behavior

**Primary consumers**
- CI reviewers
- docs/QA consumers
- migration consumers

### 6) Graphics / rich-terminal-protocol lane
**Why sixth**
- This lane is real, but should not become the default narrative for terminal work.
- `ratatui-image` is strong enough to pilot now, but only after text/render/input/probing lanes are already explicit.

**Primary artifacts**
- `terminal-graphics-profile/v0`
- `terminal-capability-profile/v0`
- `terminal-adapter-profile/v0`
- vectors for protocol query, protocol selection, text fallback, image placement caveats, and unsupported-emulator behavior

**Primary consumers**
- rich TUI apps
- support/docs consumers
- distribution/release reviewers

## Graduation criteria
A terminal-surface pilot should graduate only when it has:
1. an explicit pilot brief;
2. a lane profile naming the terminal lane under review;
3. a bounded query budget with named vectors;
4. at least one consumer-handoff artifact;
5. concrete check reports or attached evidence;
6. a scorecard showing the pilot remained lane-specific and did not claim universal terminal truth.

## Anti-goals
- one giant terminal manifest that erases styled output, TUI, line-editor, probing, test, and graphics differences;
- narrating every backend crate as a semantic superset of the others;
- treating cleanup as an implementation detail rather than a public contract;
- treating parser/test results as proof of real-emulator behavior;
- widening to remote agent consoles or accessibility layers before the terminal lanes are stable.

## Why this is an ecosystem contribution
Rust already has strong terminal crates.
What it still lacks is a compact, reviewable way to say **which terminal lane a public surface actually occupies, what evidence checked it, and how much downstream consumers may safely infer**.

A good Terminal Surface Pilot Program would give the ecosystem that missing middle layer.
It would make terminal behavior more boring, comparable, and honest without forcing one universal terminal abstraction.
