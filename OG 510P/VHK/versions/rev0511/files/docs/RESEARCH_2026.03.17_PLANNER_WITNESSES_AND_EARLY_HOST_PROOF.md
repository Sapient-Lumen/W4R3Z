# Research notes: planner witnesses and early host proof

## Why this revision exists

VHK had already learned a lot of Linux-native honesty in later-stage packs:
- host truth vs portal route truth
- target-fit vs local host drift
- claim witnesses vs wrong-host proof
- promotion gates that refuse to treat the wrong machine as clean evidence

But the core planner still lagged behind. `plan-project` could describe routes,
surfaces, target environments, and promotion waves while still hiding the most
important evidence boundary until later overlays.

That made it too easy to read the planner as pure strategy prose instead of as
strategy plus evidence discipline.

## Lessons carried in from adjacent Linux automation tools

### 1) Wayland/X11 boundaries stay real

AutoKey still teaches the cautionary version of this story: the official project
still presents itself as Linux/X11, while Wayland support lives in separate
workstreams and in-progress PRs/forks. A Linux automation planner should never
flatten that kind of split into a single “supported on Linux” headline.

### 2) Scope and precedence need to stay explicit

Espanso remains strongest where it names boundaries clearly: scoped configs,
include/exclude rules, and explicit limitations in current Wayland behavior.
That is a product lesson for VHK too. Evidence should say which lane a host can
prove, not just whether the project seems generally healthy.

### 3) Portal truth is layered, not singular

The upstream portal docs and libei docs continue to reinforce the same product
lesson: configured routing, installed backend reality, live frontend interfaces,
and session input transport are different layers. Treating them as one check box
creates operator confusion.

## Product conclusion

The planner should surface one compact witness contract early:
- which target lanes the planner currently recommends
- what support level each lane looks like
- whether the current host is aligned, degraded, drifted, neutral, or unknown
- whether portal/desktop truth makes the current machine believable evidence

That is small enough for terminal/JSON use, but strong enough to keep Linux
support claims honest before maintainers ever open the editable claim manifest.
