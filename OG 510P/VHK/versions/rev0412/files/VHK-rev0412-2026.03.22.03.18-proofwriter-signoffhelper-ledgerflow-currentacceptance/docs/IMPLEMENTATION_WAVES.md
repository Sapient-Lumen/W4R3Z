# Implementation waves (`vhk plan-project`)

`implementation_waves` turns VHK's planning surfaces into a sequenced delivery
plan.

Instead of only saying which desktop target, toolchain, or verification gate
fits a project, the planner now groups the work into waves that teams can
actually execute.

## Why this exists

Linux-native automation usually fails in one of three ways:

- the project promises capabilities that the target session does not really have
- text/trigger surfaces are left implicit instead of exported and tested
- visual or always-on features are attempted before the portability boundary is
  understood

`implementation_waves` makes the order explicit so VHK can later drive setup
wizards, Studio onboarding, or backlog generation from the same strategy data.

## Shape

Each wave includes:

- `id`, `order`, `priority`, `title`
- `objective` and `why_now`
- `commands`
- `deliverables`
- `validation` checks
- `borrowed_patterns` from other tool/product shapes
- `related_capabilities` and `depends_on`

## Initial wave model

Current heuristics produce up to five waves:

1. **foundation-contract**
   - establish the desktop/session capability contract
   - export initial text/trigger surfaces
2. **text-and-prompt-tier**
   - move snippet/forms workflows into a fast text tier
3. **visual-debug-loop**
   - treat capture, selectors, and pointer boundaries as inspectable assets
4. **dispatch-and-daemons**
   - split always-on triggers, remap seams, and watcher services away from the
     heavier runner
5. **release-gates**
   - run capability-shaped acceptance checks before claiming portability

## Design intent

This is intentionally more delivery-shaped than `playbooks` or `next_steps`.
Those surfaces stay useful for recommendations and point actions, while
`implementation_waves` is meant to answer: "what should we build first, and in
what order, if we want a Linux-native result instead of a pile of experiments?"
