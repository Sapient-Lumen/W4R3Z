# Guidance for agents and future implementers

GlassTTY is intentionally designed for both human operators and local/private LLM-driven workflows.

## First rule

Do not confuse:
- current implementation truth
- current evidence truth
- designed target shape
- planned future work
- speculation

Speak precisely about which one you mean.

## Canon before archaeology

Read these first:
1. `README.md`
2. `STATUS.md`
3. `ROADMAP.md`
4. `TASKS.md`
5. `TASK_QUEUE.md`
6. `DECISIONS.md`
7. `PROJECT_MAP.md`
8. `docs/repo-canon.md`
9. `docs/design-principles.md`
10. `docs/canon-keys.md`
11. `docs/workflow-model.md`
12. `docs/workflow-catalog.md`
13. `docs/workflow-acceptance-checklists.md`
14. `docs/state-api.md`
15. `docs/state-contracts.md`
16. `docs/adapter-model.md`
17. `docs/support-truth.md`
18. `docs/support-record-template.md`
19. `docs/support-record-lifecycle.md`
20. `docs/drift-program.md`
21. `docs/drift-triage-playbook.md`
22. `docs/evidence-and-ledgers.md`
23. `docs/evidence-ledger-schema.md`
24. `docs/feature-traceability.md`
25. `docs/agent-policy-model.md`
26. `docs/autonomy-ladder.md`
27. `docs/implementation-program.md`

Read historical handoffs only after the canon leaves a question unanswered.

## What future implementers should optimize for

1. keep the generic bridge generic
2. make surface-specific logic explicit in adapters
3. build shared workflows and structured state before inventing more bespoke commands
4. preserve evidence for every support claim
5. treat drift detection as core maintenance infrastructure
6. keep the browser visible and the operator in control by default
7. add agent execution only with policy, approval, stop-condition, and execution-report surfaces
8. update support records when implementation or evidence changes support truth
9. use explicit traceability from feature theme to workflow, state, and release claim

## What to preserve in docs work

Preserve these shared vocabularies:
- surface keys
- workflow keys
- browser-lane keys
- state-family names
- support tiers
- drift severities
- artifact kinds
- agent modes

If you need a new noun, add it to `docs/canon-keys.md` before scattering it through the repo.

## What good future work looks like

Good changes usually do at least one of these:
- widen shared workflows across official surfaces
- improve structured state quality
- improve evidence quality and drift explainability
- make support truth more precise
- make agent execution safer and more inspectable
- reduce doc ambiguity for the next implementer
- connect current scripts and artifacts to the future canon more clearly
- replace hunches with named proofs, gates, and records

## What to avoid

- hidden strategic decisions living only in a handoff
- support claims with no evidence refs
- adapter logic that cannot explain receiver resolution
- one-off state payloads with no schema story
- agent actions with no outcome record
- vocabulary drift across docs for the same feature or workflow
- browser automation that bypasses the project’s visible-operator principle without an explicit policy reason
- widening autonomy without an explicit ladder level and permission story
