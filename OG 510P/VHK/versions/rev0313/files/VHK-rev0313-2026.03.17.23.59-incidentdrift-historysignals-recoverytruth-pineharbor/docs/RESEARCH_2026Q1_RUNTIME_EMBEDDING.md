# Research notes: runtime handoff and Python embedding (2026 Q1)

This pass was about learning from adjacent packaging ecosystems without copying
fantasy promises into VHK.

## 1) PyPA docs reinforce that wheelhouses are the honest bridge

The pip repeatable-installs docs explicitly call out wheelhouses as
"installation bundles" built with `pip wheel`, and they also make the critical
constraint explicit: compiled wheels are typically OS/architecture specific.
That is a very good fit for VHK's next step because it encourages a reviewable
runtime handoff without pretending those artifacts are universally portable.

## 2) PyPA guidance still points to venv as the reversible install surface

The Python packaging guide keeps recommending `venv` for isolated third-party
installs. That matches VHK's need for smoke tests and native-install rehearsal:
a local venv is a safer, reversible proof point than mutating the system Python
just to see whether a bundle/runtime pair is viable.

## 3) Flatpak's Python docs validate one requirements file + generator bridge

The official Flatpak Python page is unusually direct: once dependency graphs get
non-trivial, `flatpak-pip-generator --requirements-file=requirements.txt` is the
recommended bridge for generating manifest JSON. That makes VHK's runtime-pack
shape more obvious: generate the requirements file once, then let package lanes
consume it instead of retyping dependency lore.

## 4) AppImage docs reinforce path discipline, not magic Python portability

The AppDir docs keep the contract simple: AppRun is the entry point, AppDir is
the package source tree, and everything should stay rooted in predictable paths.
That does not solve Python embedding on its own, but it *does* justify reserving
a stable embedded-runtime path for future work instead of scattering runtime
bits across ad-hoc locations.

## 5) Product-shape implication for VHK

The right next move is not "claim self-contained packaging now".
The right move is:

- preserve the reviewed bundle lane
- preserve the package skeletons
- add a reviewable runtime handoff
- keep helper-daemon/portal/compositor claims separate from Python package
  claims

That is the VHK shape this pass implements.
