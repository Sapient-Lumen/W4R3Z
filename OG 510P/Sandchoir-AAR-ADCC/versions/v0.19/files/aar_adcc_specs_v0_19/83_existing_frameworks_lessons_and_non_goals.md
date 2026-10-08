# 83 — Existing Frameworks: Lessons + Non-Goals (v0.19)

Many multi-agent orchestration frameworks exist, but your constraints differ:
- free-user CLI clients (no API budget)
- unknown slice counts / truncation
- bounded view assembly as the core optimization target

## 1) What exists (examples)
- AutoGen: multi-agent conversation framework / group chat manager
- LangGraph: supervisor patterns + persistence (threads/checkpoints/time travel)
- Semantic Kernel: group chat orchestration manager
- CrewAI: task/agent orchestration patterns
- OpenHands: agent SDK + sandbox tools (terminal/editor/workspace)

## 2) What we borrow
- Supervisor pattern (MetaLLM) as coordinator, but with **small levers**
- Persistence/time travel semantics (threads, checkpoints, forks)
- Tool execution as explicit objects (EXEC#) rather than implicit tool calls
- Observability-first culture: telemetry and reason codes

## 3) What we don't do (early)
- Full group-chat transcripts as “truth” (context bloat)
- Multi-round protocol elections as hot path (slice variance punishes it)
- Letting agents rewrite kernel code (spaghetti governance)
- Automatic evidence veto (evidence persuades; votes allocate)

## 4) Your unique twist
- Bounded, deterministic, diffable AAR views are a first-class product
- Early CTRL capture + JSON repair ladder are central
- Integrator + patch exports replace concurrent file editing
