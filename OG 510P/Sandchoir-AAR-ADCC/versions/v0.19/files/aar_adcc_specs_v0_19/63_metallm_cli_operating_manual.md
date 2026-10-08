# 63 — MetaLLM-CLI Operating Manual (v0.19)

MetaLLM is a *separate* ruling LLM that does not participate in agent deliberation.
It is an operator-augmentation and runtime governor.

This doc defines how MetaLLM fits end-to-end.

## 1) Responsibilities (what MetaLLM does)
- Observability:
  - reads telemetry (time_to_ctrl, parse rate, truncation)
  - inspects suppression diagnostics (why items were hidden)
  - watches evidence density
- Control-plane steering:
  - recommends mode changes (Gatekeeper/PatchOnly/Freeze)
  - recommends budget profile adjustments
  - recommends exploration toggles
  - recommends weight tweaks (human-approved)
- Arbitration support:
  - suggests integrator selection (if votes unclear)
  - suggests discriminative checks to break deadlocks
  - triages REQs (44_)
- Stability maintenance:
  - triggers compaction
  - triggers snapshots/checkpoints
  - helps restore from checkpoints after failures

## 2) What MetaLLM must NOT do (early)
- rewrite kernel code
- unilaterally change invariants
- conduct protocol elections as a bottleneck
- silently run ad-hoc commands without a logged EXEC# (53_)

## 3) How MetaLLM “talks” to the router
MetaLLM is a router client. It:
- reads: `telemetry`, `state`, `viewdiff`, `cap show`
- writes: `mode`, `compact`, `snapshot`, `weights set`, `req add`, `verifier run`

MetaLLM changes config; the router enforces invariants.

## 4) Parallelism pattern (your workflow)
You can run MetaLLM concurrently with the 3–5 agents:
- agents are working in their terminals
- MetaLLM watches router state and intervenes
- human can interrupt MetaLLM to set H0 or override priorities

This is the cheapest way to “get a second brain” without multi-agent elections.

## 5) MetaLLM prompt contract
MetaLLM should be prompted to:
- prefer small reversible levers
- always propose a discriminative test or patch, not more debate
- keep every recommendation to <= 5 lines
- explain which invariant it’s preserving (not optional)

## 6) Failure playbook (MetaLLM)
If parse failures rise:
- enable stronger BCC + CTRLJSON
- enable JSON healing
- CAP probe guided decoding if available
If truncation spikes:
- disable DISCOVERY/RANDOM
- shrink views to mandatory/HOT only
If consensus collapse:
- require 1 cheap verifier before patch selection
- require 1 objection line per agent (66_)

Prompt library: see 68_prompt_pack_agent_and_metallm.md for CI/EK/PatchOnly/Gatekeeper templates.

Implementation ergonomics: Router CLI (79_) + experiments (80_) + telemetry exports (82_).
