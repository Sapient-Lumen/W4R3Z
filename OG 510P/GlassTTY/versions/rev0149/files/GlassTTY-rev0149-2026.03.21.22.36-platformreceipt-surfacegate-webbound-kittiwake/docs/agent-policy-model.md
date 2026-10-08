# Agent policy model

GlassTTY should support private/local LLM-driven operation without abandoning visible operator control.

## Operating modes

### Human-piloted
A human issues commands directly and watches the browser.

### Assisted
A model suggests next actions, but a human triggers each one.

### Approval-required agent
A model can prepare or stage actions, but execution requires approval for gated actions.

### Bounded autonomous agent
A model can execute within explicit policy limits and stop conditions.

## Policy concerns

A policy should define:
- allowed surfaces
- allowed workflows
- max repeated action count
- whether write/submit actions require approval
- whether cross-surface relay is allowed
- required evidence outputs
- stop conditions
- escalation triggers

## Stop conditions

Examples:
- receiver confidence drops below threshold
- latest-turn read becomes ambiguous
- generation status is unknown too long
- support tier is below allowed threshold
- unexpected modal or route change appears
- repeated no-op or failure outcomes occur

## Why this matters

“Let my local LLM talk to browser AIs” is powerful, but only if the repo can say:
- what it was allowed to do
- what it tried
- what happened
- why it stopped
- what evidence it left behind
