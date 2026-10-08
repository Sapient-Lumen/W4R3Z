# Research notes: explicit evidence lanes and operator proof targets

## Why this revision exists

VHK had already learned how to describe:
- current host truth
- configured vs installed vs live portal truth
- target-fit drift against a flagship lane
- claim witnesses and wrong-host proof

But there was still one practical gap: maintainers could not *pin* one explicit
evidence lane across planner, claim, promotion, and audit flows. Reports would
default back to the flagship lane even when the operator really wanted to ask a
more concrete question such as: “judge this sway box specifically against the
GNOME Wayland flagship” or “use this machine only as evidence for wlroots.”

## Lessons from adjacent Linux automation work

### 1) Linux automation support is still lane-specific

AutoKey still teaches the cautionary version of the problem: the official
project remains X11-first while Wayland work proceeds in separate streams. That
means proof should stay attached to one real desktop/input lane, not a generic
“Linux works” story.

### 2) Scope and precedence matter as much as raw capability

Espanso remains strongest where it keeps scope explicit: configuration
precedence, app-specific rules, and current Wayland limitations. That is a
product lesson for VHK too. A selected evidence lane is a scope control for
proof, not just a cosmetic option.

### 3) Portal and input stacks are layered

The portal docs, InputCapture docs, and libei docs all reinforce the same idea:
routing, backend installation, live interface availability, and the input
transport layer are different truths. A report that forgets which lane it is
trying to prove is too easy to misread.

## Product conclusion

VHK should let operators carry one explicit evidence lane through review flows:
- planner strategy
- claim generation
- claim auditing
- promotion review
- capability audit

The selected lane should stay visible in JSON, Markdown, and refresh scripts,
with an explicit selection source (`explicit` vs `flagship-default`). That keeps
proof portable and honest: rerunning the review should not silently change the
question the report is answering.
