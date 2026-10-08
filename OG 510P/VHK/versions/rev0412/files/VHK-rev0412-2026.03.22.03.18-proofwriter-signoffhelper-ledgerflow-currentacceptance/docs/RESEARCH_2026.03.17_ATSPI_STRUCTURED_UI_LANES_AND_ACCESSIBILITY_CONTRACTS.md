# Research — AT-SPI structured UI lanes and accessibility contracts

Date: 2026-03-17
Revision: REV0274

## Why this note exists

VHK has long wanted to grow beyond raw coordinates, titles, and screenshots. The
repo already knew that accessibility mattered, but the planner still left that
knowledge stranded in doctor probes and roadmap prose.

The real Linux lesson is sharper than just “support accessibility someday”:

- AT-SPI is a separate contract with its own bus and health checks
- explorer/debugger tools make semantic UI targeting reviewable
- automation wrappers can sit on top of AT-SPI without pretending every app has
  a good tree

## What others are doing that matters

### 1) AT-SPI is explicit infrastructure, not hidden magic

The at-spi2-core bus docs are clear that accessibility traffic uses a separate
bus and that normal clients find it through `org.a11y.Bus.GetAddress`.

That matters because VHK should not model accessibility as a vague side effect
of “window support.” It is its own host/session contract.

### 2) Accerciser shows the value of an inspector loop

Accerciser remains useful because it keeps the accessibility tree inspectable.
That is a product lesson, not just a debugging convenience:

- semantic selectors need inspection
- event flows need observation
- widget capabilities need review before an automation route is trusted

### 3) dogtail shows how automation can layer on top

Dogtail demonstrates the stack shape very directly: AT-SPI at the base,
`pyatspi` above it, then a friendlier automation layer on top.

That layered shape matches VHK's design instincts well. VHK should not rebrand
all of AT-SPI as its own runtime. It should model a structured UI lane with
explicit fallbacks and host checks.

## Product implication for VHK

VHK should now keep three context layers visible at once:

- desktop metadata bridges (`wmctrl`, `hyprctl`, `swaymsg`, `kdotool`, etc.)
- AT-SPI structured UI targeting for apps that expose real widget semantics
- vision/pixel/OCR fallbacks for apps where either of the above is weak

That means the planner should surface an explicit accessibility-shaped lane and
not force every structured UI problem into either “window metadata” or “vision.”

## Concrete repo effect in REV0274

`plan-project` now exposes this lesson in machine-readable form:

- `atspi-structured-ui` in surface choices
- `atspi-structured-selector-lane` in reference patterns
- `atspi-separate-bus-structured-automation` in ecosystem lessons
- `window-introspection` toolchain guidance now keeps `AT-SPI/Accerciser` and
  `dogtail/pyatspi` visible next to desktop metadata bridges

This is still not the same thing as shipping a full Accerciser-style inspector
inside VHK. But it is an important product step: VHK now plans for the lane it
claims to care about.
