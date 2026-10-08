# 62 — Bootstrap Variants: Compiled Intent vs Evidence Kernel (v0.19)

You pointed out a key fork: do you start each run by compiling “what we’re doing” or by fixing “how we decide”?
Both are valuable. Unknown slice counts punish multi-round bootstraps, so you need two **one-shot** templates you can choose from.

This doc defines both templates and when each wins.

---

## Variant A: Compiled Intent Bootstrap (CI)
**Goal:** turn squishy human text into a crisp H0 + scope + success criteria.

Best when:
- the human goal is ambiguous / changing
- the project is new or you’re resuming after weeks
- agents tend to drift into philosophy instead of building

One-shot outputs (must fit in one agent slice):
- `H0` (1–2 lines)
- `Scope` (what is in/out)
- `Deliverable` (artifact / patch / proof / report)
- `Evidence target` (what counts as “done enough”)
- `Mode` recommendation (Gatekeeper/PatchOnly/etc.)

Failure mode:
- spends too many tokens on wording; delays doing work

Mitigation:
- cap CI to 12 lines and force immediate “first patch or first verifier” suggestion.

---

## Variant B: Evidence Kernel Bootstrap (EK)
**Goal:** fix “how we move votes” and “how counterexamples become decisive” first.

Best when:
- you already know the project goal
- you keep getting confident nonsense
- agents agree too easily without tests
- you’re in a high-uncertainty section where CE discovery matters

One-shot outputs:
- Minimal verifier set proposal (cheap/medium)
- CE certification definition for this run (what counts as a certifiable counterexample)
- Patch lane rules (diff format, integrator)
- “Disagreement introduction” requirement (see 66_...)

Failure mode:
- too procedural; can feel slow if you needed intent clarity first

Mitigation:
- EK ends with “run 1 cheap check” or “draft 1 minimal patch” immediately.

---

## Default recommendation
- First run on a new project/thread: CI
- Hard section / repeated failure / incoherence: EK
- Weeks-long sessions: CI on reopen, EK on hard disputes.

---

## MetaLLM usage
MetaLLM should:
- recommend CI vs EK based on telemetry (e.g., low evidence density => EK)
- keep both templates as files and choose per run without negotiation
