# Red Team & Adversaries (and dual-use policy)

## 6.1 Purpose
Red teaming exists to prevent naive “nice” policies from being exploited and to surface failure modes that matter for real-world robustness.

## 6.2 Adversary families (high-level)
The lab includes adversary templates such as:
- unconditional defectors,
- manipulative togglers (cooperate to build trust then exploit),
- “apology loop” and reputation-laundering patterns,
- payoff-control families (e.g., extortion-like dynamics),
- collusion / coalition exploitation (in multi-agent worlds).

Implementation details MUST live in private registries and be treated as sensitive.

## 6.3 Dual-use policy (required)
This project has dual-use risk: better defense often implies better offense.

Therefore:
- adversary code and exact exploit recipes MUST be tagged **SENSITIVE**,
- sensitive artifacts MUST NOT be published by default,
- the system MUST support “public-safe export” that strips:
  - adversary implementations,
  - exact trigger patterns,
  - and any strategy parameters that directly enable exploitation.

Public-safe exports MAY include:
- high-level descriptions,
- failure envelopes (“this class exists; here’s what it exploits”),
- and mitigation patterns (defensive) without recipe-level details.

## 6.4 “Silent zones” (explicit)
Certain discoveries may be kept entirely internal.
The lab SHOULD support:
- `export --public` (redacted)
- `export --internal` (full)
- a denylist registry for probes/adversaries that never leave the machine.

## 6.5 Evaluation ethics guardrail
Red teaming must not become “build the best vampire.”
Rules:
- adversaries are used to test robustness,
- not to optimize offensive capabilities beyond what is necessary for defense.

## 6.6 Regression: failures become probes
Every discovered exploit becomes:
- a minimal counterexample probe (when possible),
- a regression test,
- and an entry in the failure-mode taxonomy.

## 6.7 Human-facing summaries (required)
Because humans must understand what happened:
- every red-team failure MUST produce a narrative summary,
- citing concrete evidence (probe id, rounds, deltas),
- and a recommended mitigation direction.

The narrative MUST avoid revealing sensitive exploit details in public-safe mode.
