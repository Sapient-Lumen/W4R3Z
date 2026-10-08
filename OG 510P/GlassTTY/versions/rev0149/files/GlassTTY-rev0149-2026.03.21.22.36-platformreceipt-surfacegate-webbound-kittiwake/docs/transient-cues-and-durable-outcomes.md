# Transient cues and durable outcomes

GlassTTY should distinguish fast, ephemeral UI cues from durable success evidence.

## Transient cues

Examples:
- toast/snackbar banners
- loading spinners
- temporary status text
- brief button-label changes
- short-lived alerts
- animation-only confirmations

Transient cues are useful, but they are not enough for strong workflow claims on their own.

## Durable outcomes

Examples:
- a latest assistant turn exists and is readable
- generation status reaches a stable non-transient state
- composer content changed and readback confirms it
- route/conversation identity changed as expected and remained stable
- a support bundle contains inspectable state/action artifacts

## Canonical rule

Transient cues may raise confidence, but they do not close the loop by themselves.

GlassTTY should prefer this chain:
1. note the transient cue
2. capture it as evidence
3. look for the durable state change it predicts
4. keep the action result conservative if the durable change never arrives

## Workflow consequences

### turn-submit
A flashing submit confirmation, spinner, or toast is not enough. Expect at least one durable post-submit signal such as generation state, turn-list mutation, or stable route/context change.

### generation-read
A brief live-region or status change should not force `generating` or `complete` unless it aligns with visible durable state.

### latest-turn-read
A banner claiming a response is ready is weaker than a readable turn payload.

### support-capture
Support bundles should record both:
- the transient cue observed
- the durable follow-up that did or did not materialize

## Failure language

Prefer:
- “transient success cue observed; durable outcome not yet confirmed”
- “toast present, but latest turn missing”
- “spinner cleared without stable turn/state evidence”

Avoid:
- “success” when only the cue exists
- “generation complete” when the state is inferred from a toast alone
