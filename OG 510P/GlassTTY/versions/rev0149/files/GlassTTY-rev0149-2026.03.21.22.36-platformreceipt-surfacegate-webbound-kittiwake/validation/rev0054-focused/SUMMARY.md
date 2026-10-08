# GlassTTY rev0054 focused validation

This focused validation bundle was generated in-container on 2026-03-09 after the receiver-priming revision landed.

Validated successfully here:
- extension typecheck
- extension build
- deterministic receiver inventory check
- deterministic receiver priming-plan check
- pytest: protocol
- pytest: state
- pytest: broker
- pytest: cli
- pytest: native host
- pytest: validate-release helper

Known limitation of this environment:
- a first umbrella `scripts/validate-release.py` run only completed its early steps before stopping unexpectedly, so this folder records the focused reruns that did complete instead of claiming a full umbrella pass

Not proven here:
- live Chromium/native-messaging/browser round-trip
- live multi-frame Claude.ai tab exercising receiver priming end to end
- heavier fixture/dev helper sweeps beyond the focused checks above
