# Testing

GlassTTY testing now needs to cover more than “does the extension build?” and “did one browser path work?”

## Test layers

### 1. Generic infrastructure tests
- extension build/typecheck
- native host and broker correctness
- protocol and packaging checks
- CLI and doctor/report helpers

### 2. State contract tests
- state-family shape and nullability
- action/outcome record shape
- structured degradation behavior

### 3. Adapter tests
- surface detection
- receiver resolution
- composer read/write behavior
- submit and latest-turn behavior
- drift regression checks against saved fixtures

### 4. Evidence tests
- support bundle generation
- comparison bundle generation
- ledger updates
- operator handoff / attempt continuity

### 5. Release-gate tests
- support claims remain tied to evidence
- workflow-specific smoke outputs stay inspectable
- support matrix rows have current proof

## Important idea

The repo should gradually move toward testing support claims in surface/workflow language, not only tool-language.

Examples:
- “Claude composer-write still passes”
- “ChatGPT latest-turn-read still emits structured turn state”
- “AI Studio support-capture still produces a support bundle”

## Current leverage

The existing smoke, doctor, readiness, handoff, and attempt lanes are already valuable. The next step is to reinterpret them through surface/workflow/support truth rather than treat them as isolated operational tools.
