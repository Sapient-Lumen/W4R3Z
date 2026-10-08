# Research — wtype text fast paths and honest Wayland boundaries

## Thesis

The Linux lesson is not “Wayland text typing is solved now.”
The useful lesson is narrower:

- there is value in a **fast typed-text lane**
- on Wayland that lane is shaped by compositor/session protocol support
- so VHK should model `wtype` as an explicit fast path, not as a generic
  Wayland support claim

## What we learned from others

### 1) `wtype` is a narrow tool by design

The upstream project positions `wtype` as “xdotool type for wayland” and its
interface is purposely small: type text, hold/release modifiers, press/release
named keys, and adjust delay.

That is exactly why it is useful to VHK.
It looks like a thin injection edge, not like a whole automation runtime.

Product lesson for VHK:

- keep `wtype`-class typing behind a narrow adapter surface
- do not push prompts, selectors, retries, asset management, or proof logic into
  that layer
- use it when the target session has already proven the relevant protocol path

### 2) the protocol boundary is real, not theoretical

There is still visible upstream evidence that `wtype` can fail on desktops where
its virtual-keyboard path is not supported by the compositor/session in the way
users expect.

Product lesson for VHK:

- planning should keep `wtype` conditional unless host/session evidence says
  otherwise
- portable text/package exports and clipboard-first flows remain important even
  when a project also has a fast typed-text lane

### 3) portal progress changes trigger planning more than text-typing certainty

GNOME 48 materially improves the GlobalShortcuts portal story, which is a major
step for reviewed trigger ownership on GNOME-class sessions.
But that is not the same thing as promising a universal Wayland typed-text
backend.

Product lesson for VHK:

- keep portal-first trigger planning and typed-text planning as separate
  contracts
- one desktop can have a stronger global-shortcuts story without automatically
  becoming the best fast-typing story

### 4) helper daemons are still a different lane

Tools such as `ydotool` continue to matter because they occupy a different
position in the Linux stack: a broader low-level automation/helper posture with
uinput/service implications.

Product lesson for VHK:

- keep helper-daemon fallback lanes visible
- do not collapse `wtype`, clipboard-first text, and uinput-helper playback into
  one vague “Wayland input support” bucket

## Concrete repo implications

This research justifies the following planner behavior:

- explicit `wtype-wayland-text` surface choice
- explicit `wtype-narrow-wayland-text-lane` planner pattern
- explicit `wtype-virtual-keyboard-boundary` ecosystem lesson
- clipboard-first default text-toolchain posture on generic Wayland, with
  `wtype` still available as the promoted fast path when evidence supports it

## Sources consulted

- https://github.com/atx/wtype
- https://github.com/atx/wtype/issues/45
- https://github.com/ReimuNotMoe/ydotool/blob/master/README.md
- https://release.gnome.org/48/developers/
- https://thisweek.gnome.org/posts/2025/02/twig-189
