# DelayBasin: start here (for maintainers, including LLMs)

DelayBasin is a **method archive** for long-run human–LLM co-construction.

Non-negotiables:

- **Do not collapse levels.** Keep practice, observation, mechanism, speculation, disagreement, and quarantine distinct.
- **Do not treat archive hygiene as decoration.** Registries, trajectory maps, prompt pairs, and drift checks are part of the method.
- **Do not overclaim mechanism.** An observed effect is not yet an explanation.
- **Do not lose the prompt lineage.** Prompt pairs are state-transition operators and must be archived.
- **Do not let size explode.** Summarize, cite, link, and ratchet.
- **Do not coward out of risk.** If a high-value speculation is worth making, make it; if it is too wild for canon, quarantine it.
- **Transformers themselves are part of the subject matter.** This archive is partly about what this method implies about transformer behavior and self-modeling.

## Read first

1. `docs/00-meta/charter.md`
2. `docs/00-meta/trajectory-map.md`
3. `docs/00-meta/llm-runbook.md`
4. `docs/10-method/method-overview.md`
5. `docs/10-method/constitutional-pidgin-and-control-lexicon.md`
6. `docs/10-method/portable-state-interface.md`
7. `docs/10-method/typed-continuation-protocol.md`
8. `docs/10-method/certified-core-vocabulary-and-recertification.md`
9. `docs/10-method/certified-moves-and-procedural-admission.md`
10. `docs/10-method/promotion-contracts-and-staged-ratification.md`
11. `docs/10-method/temporal-demotion-and-decay-patrol.md`
12. `docs/10-method/self-stabilizing-recovery-and-legitimacy-kernel.md`
13. `docs/10-method/revision-receipts-and-audit-objects.md`
14. `docs/10-method/practice-observation-mechanism-speculation.md`
15. `docs/20-constitution/claim-registry.md`
16. `docs/20-constitution/invariant-registry.md`
17. `docs/20-constitution/open-question-registry.md`
18. `docs/20-constitution/decay-watch-registry.md`
19. `docs/20-constitution/recovery-kernel.md`
20. `docs/20-constitution/revision-receipt-contract.md`
21. `docs/50-promptcraft/prompt-pairs.md`
22. `docs/90-quarantine/wild-speculations-2026-03-08.md`

## One command

```bash
make lint
```

## What a good revision looks like

Each revision should do at least one of the following:

- reduce entropy,
- harden a guardrail,
- refine a mechanism hypothesis,
- clarify a disagreement,
- add or improve a prompt pair,
- convert a loose intuition into a stable diff surface,
- or place a risky but fertile idea into quarantine with explicit disconfirmation hooks.
- or preserve the move class that made the revision admissible in the first place.
- or review whether a canon-level claim has become stale enough to demote, shrink, or re-certify.
- or emit a compact revision receipt showing why this revision counted at all.
- or preserve one nearby rejected move when it materially shaped the accepted revision.

## Recovery hint

If you suspect drift, stale reopen, or context corruption, do not improvise your way forward. Use `MV-0010` / `recover-resync` via `docs/20-constitution/recovery-kernel.md` before claiming ordinary progress.
