---
id: P-0296
title: BPMN 2.0 + DMN Conformance Workbench Kit — model linting, FEEL/decision fixtures, and replayable process evidence
status: idea
domains: [enterprise, workflow, rules, conformance, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://www.omg.org/spec/BPMN/2.0/
  - https://www.omg.org/spec/DMN/1.4/About-DMN
  - https://crates.io/crates/dsntk
---

# Problem

Rust is gaining BPMN and DMN building blocks, but they are split across parsers, toy engines, and FEEL evaluators. What is still missing is a **conformance workbench** that makes BPMN/DMN assets testable, lintable, and reproducible across teams.

This proposal deliberately **merges** workflow and decision-model concerns into one workbench because real deployments mix them: BPMN orchestration, DMN decisions, and FEEL expressions all meet at the integration boundary.

# What it provides

- `process-lint` — static checks for BPMN/DMN model portability, anti-patterns, and executable subsets.
- `feel-fixtures` — deterministic FEEL corpus runner.
- `decision-replay` — DMN evaluation traces and golden outputs.
- `process-evidence` — replayable execution/event bundles for BPMN runs.
- `cargo process-model` — lint, evaluate, diff, and package `*.processbundle.zip` artifacts.

# Users & user stories

- **Platform teams**: “Reject models that rely on engine-specific quirks before they hit production.”
- **Rust workflow engine authors**: “Run the same fixture corpus and compare results.”
- **Consultancies / integrators**: “Send a bundle that explains why a process path or decision outcome diverged.”
- **Business automation teams**: “Keep BPMN/DMN assets under test in CI, not only in a vendor UI.”

# Prior art (and why it’s insufficient)

- `dsntk` is a promising DMN/FEEL toolkit.
- `bpmn-engine`, `bpm-engine-bpmn`, `snurr`, and older `bpxe` crates show active interest in BPMN.
- Vendor ecosystems like Camunda have strong FEEL and BPMN/DMN tooling, but they are not a Rust-native, engine-neutral workbench.

# Design goals

1. **Conformance-first** — focus on portability and explainability before “full engine” ambition.
2. **Executable subsets** — clearly label what is portable, experimental, or vendor-specific.
3. **Golden traces** — every evaluation/run should be diffable.
4. **Asset-centric CI** — useful to teams that version BPMN/DMN files in Git.
5. **Split static lint from dynamic replay** — keep simple checks fast.

# Non-goals

- Not a full enterprise workflow platform.
- Not a GUI modeler.
- Not a replacement for heavy BPM suites.

# Architecture & API sketch

```rust
pub struct ModelVerdict {
    pub portability: PortabilityLevel,
    pub warnings: Vec<LintWarning>,
}

pub trait DecisionEngine {
    fn eval(&self, model: &DmnModel, input: &serde_json::Value) -> EvalTrace;
}

pub trait ProcessRunner {
    fn run(&self, model: &BpmnModel, input: &serde_json::Value) -> ProcessTrace;
}
```

Bundle draft: `model/`, `inputs/`, `trace.jsonl`, `verdicts.json`, `goldens/`, `notes.md`.

# Security / safety model

- Put hard limits on model size, recursion depth, and execution time.
- Treat FEEL and script-like extensions as potentially hostile.
- Separate “pure conformance mode” from any unsafe plug-in execution.

# Maintenance & governance plan

- Keep conformance corpora independent from any one engine.
- Version fixture packs by BPMN/DMN/FEEL conformance level.
- Encourage adapters for existing crates instead of forcing one runtime.

# Milestones

## 0.1
- Static linting for BPMN/DMN portability
- FEEL golden corpus runner
- Decision replay traces

## 0.2
- BPMN execution trace bundles
- Cross-engine comparison adapter traits
- CI-friendly `cargo process-model lint`

## 1.0
- Stable `*.processbundle.zip`
- Published fixture corpus for common patterns
- Clear “portable subset” guidance others can build on

# Open questions

- Which BPMN/DMN features belong in the portable subset?
- How should vendor-specific FEEL extensions be represented in fixtures?
- Is a separate CMMN/form workbench eventually warranted, or should this crate stay bounded?

# Sources

- OMG BPMN 2.0: https://www.omg.org/spec/BPMN/2.0/
- OMG DMN 1.4: https://www.omg.org/spec/DMN/1.4/About-DMN
- `dsntk`: https://crates.io/crates/dsntk
- `bpmn-engine`: https://crates.io/crates/bpmn-engine
- `bpm-engine-bpmn`: https://crates.io/crates/bpm-engine-bpmn
- `snurr`: https://crates.io/crates/snurr
- `bpxe`: https://crates.io/crates/bpxe
- Camunda FEEL docs: https://docs.camunda.io/docs/components/modeler/feel/what-is-feel/
