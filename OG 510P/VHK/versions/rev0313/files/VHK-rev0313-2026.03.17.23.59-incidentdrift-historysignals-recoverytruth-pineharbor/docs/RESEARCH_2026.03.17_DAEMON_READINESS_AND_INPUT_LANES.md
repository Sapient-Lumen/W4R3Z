# Research — daemon readiness and Linux input lanes

## Question

What should VHK learn from the current Linux input-helper ecosystem when deciding how honest its Wayland input story should be?

## What stood out

### 1) `ydotool` is explicitly daemon-backed

The current upstream README and Arch man page both treat `ydotoold` as part of the contract, not an optional footnote. The daemon is needed because the virtual input device takes time to appear and become usable.

### 2) `dotool` has two real operating modes

The public packaging/docs ecosystem around `dotool` keeps repeating the same practical lesson:

- one-shot `dotool` works
- `dotoold` + `dotoolc` is faster and better for repeated playback because the devices stay alive

That means a planner/doctor surface should not flatten `dotool` and `dotoolc` into the same proof state.

### 3) `wtype` is valuable because it is narrow

`wtype` is not a universal Linux text answer. It is a compositor-protocol fast path. That is useful, but only when the compositor exposes the virtual-keyboard protocol.

### 4) libei/EIS still matters strategically

libei continues to look like the long-term cross-compositor direction, but it is not the same thing as saying “Wayland input is solved now”. VHK should keep helper-backed routes explicit until the surrounding stack is more uniformly available.

## Product lesson for VHK

The repo should keep three truths separate:

1. helper/tool present
2. host permissions/protocols look plausible
3. the chosen lane is actually ready for repeated automation

That leads to a better Linux-native contract than a simpler but less honest “some helper exists on PATH, so we support it”.

## Concrete repo consequences

- doctor should probe daemon-backed lanes explicitly
- readiness/host packs should preserve those distinctions in review artifacts
- planner language should keep one-shot helper routes and daemon routes separable
- runtime auto-selection should eventually consult the same readiness truth instead of relying on binary presence alone
