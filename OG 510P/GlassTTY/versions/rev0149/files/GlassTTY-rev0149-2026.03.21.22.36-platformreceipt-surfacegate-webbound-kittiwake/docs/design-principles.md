# Design principles

These principles are the shortest statement of what GlassTTY should optimize for as it grows.

## 1. Local-first control
GlassTTY should assume the operator and their private tooling are local. It should not require pretending browser surfaces have stable public APIs when they do not.

## 2. Visible operation by default
The browser should remain visible and inspectable. Hidden background browser control is not the default product posture.

## 3. Evidence before claim
Support claims, release claims, and “works for me” stories should resolve to named artifacts, not only narrative confidence.

## 4. Shared workflows, surface-specific adapters
A surface may need custom DOM logic, but the product should still speak in shared workflow language whenever possible.

## 5. Structured state over ad hoc strings
Future work should prefer normalizing outputs into state families and action outcomes rather than producing bespoke human-only readouts.

## 6. Honest degradation
When data is partial, stale, or uncertain, the system should say so explicitly. Unknown is better than guessed.

## 7. Drift is normal
Surface drift is not an exception path. It is a routine maintenance condition that should be detectable, classifiable, and actionable.

## 8. Support is scoped
“Supports X” is not specific enough. Support truth should always be scoped by surface, workflow, lane, and evidence window.

## 9. Autonomy is laddered
Autonomy should expand in levels with explicit permissions, approval requirements, stop conditions, and execution reporting.

## 10. Operator sovereignty
The operator can always inspect, interrupt, downgrade autonomy, or force a capture path. GlassTTY should not trap the user inside an opaque loop.

## 11. Archive truth matters
The repo’s evidence and memory discipline is a feature. New features should leave durable artifacts that future sessions can inherit.

## 12. Canon beats archaeology
The current intended product shape should be understandable from current docs. Handoffs and research notes are memory, not the main strategy surface.
