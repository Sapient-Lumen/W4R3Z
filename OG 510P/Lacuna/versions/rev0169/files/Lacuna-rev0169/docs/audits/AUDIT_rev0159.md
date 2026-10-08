# Audit — rev0159

## Scope

This audit began from the accepted rev0158 artifact and asked whether Lacuna could serve as an executable, hyperlegible adapter for the generator → judge → compressor → verifier loop proposed in Gwern’s “Better Fiction via Retcon Planning,” without weakening ordinary play, historical compatibility, or kernel custody.

The audit examined request typing, model-facing cardinality, information flow, deterministic selection, narrow authority, provider dispatch, exact preparation, post-commit recovery, and documentation claims. It did not treat model creativity, aesthetic quality, provider isolation, or comparative efficacy as kernel properties.

## Parent baseline

Rev0158 contributed typed session control, one-command play start, embedded provider dispatch, descriptor-stable run-member reads, pointer-only recovery, and 199 passing tests. Rev0157’s rollback preparation and exact later-head historical receipt recovery remained the commit boundary. Those paths were preserved rather than replaced.

## Finding A159-01 — no typed boundary separated a checkpoint from ordinary play

**Risk.** A host could smuggle backstage planning into a normal director turn or infer checkpoint authority from prose after issuance.

**Repair.** Added request v4, grant v2, source protocol v3, and explicit `request_purpose`. `checkpoint begin` issues purpose `checkpoint`; ordinary entrances issue purpose `play`. Version-specific validators preserve v2/v3 compatibility.

**Evidence.** Request, source metadata, grant allowlist, orchestration compatibility, schema, and end-to-end tests cover v4 issuance and historical v2/v3 behavior.

## Finding A159-02 — a claimed rollout could contain no inspectable forward work

**Risk.** The initial candidate draft allowed a summary plus optional body hash/retention declaration. A generator could claim it rolled a hypothesis forward while giving the judge no exact sequence to inspect.

**Repair.** Replaced the optional-body contract with an explicit `turns` array containing exactly one nonempty ordered beat per policy horizon turn.

**Evidence.** Candidate validation and schema tests reject missing/extra beats and exercise a nondefault seven-turn horizon.

## Finding A159-03 — weaker models had to infer output cardinality

**Risk.** Instructions named a candidate count and horizon, but a literal model still had to construct the correct array length and IDs from prose.

**Repair.** Generator templates now preallocate every candidate and rollout beat; judge templates preallocate one complete score object per candidate.

**Evidence.** Task-card tests assert exact object counts, stable IDs, and policy-sized horizon structure.

## Finding A159-04 — dispatch validation was initially shape-oriented

**Risk.** A schema-valid envelope could retain the right embedded card while changing provider alias, role, return contract, save path, or parent command.

**Repair.** Added strict dispatch field validation and exact envelope recomputation from the validated embedded card and provider route.

**Evidence.** Tampered alias and card tests refuse; all five provider routes and eight provider roles are exercised.

## Finding A159-05 — verifier language overclaimed full selection checking

**Risk.** The least-context verifier does not receive raw rejected candidates and all scores, so it cannot independently reproduce winner selection.

**Repair.** Renamed and narrowed the check to proposal-visible selection-evidence consistency. Parent assembly alone revalidates raw candidates, blind view, arithmetic, eligibility, tie rule, winner, and selected compression.

**Evidence.** Verifier templates, schema, guide, and tests now distinguish advisory scope from parent custody.

## Finding A159-06 — later-head checkpoint retry lacked direct regression coverage

**Risk.** Ordinary turn recovery already supported a later valid head, but the checkpoint wrapper could accidentally require the committed checkpoint head to remain current.

**Repair.** Routed checkpoint commit through the same historical reconstruction and exact event-chain comparison, then added a checkpoint-specific later-head test.

**Evidence.** The test commits a checkpoint, advances the cube through an unrelated valid write, retries the identical checkpoint commit, receives `delivery.mode = recovered` with `historical_snapshot_used = true`, and observes no duplicate events.

## Finding A159-07 — provider mappings were duplicated across entrances

**Risk.** Ordinary run dispatch, checkpoint dispatch, model briefs, and provider files could drift in aliases or supported routes.

**Repair.** Centralized provider definitions and role aliases in `src/lacuna/providers.py`; entrance and run code consume the same registry.

**Evidence.** Provider configuration tests parse every Codex/Claude/Gemini role file, assert read-only/no-tool contracts, and verify ChatGPT/guide checkpoint instructions.

## Finding A159-08 — the checkpoint could have become a parallel commit engine

**Risk.** A bespoke checkpoint mutation path would duplicate grant, disclosure, stale-head, exact-event, recovery, and projection logic.

**Repair.** Assembly emits the existing turn proposal shape. Review uses the real turn preparation path under rollback; commit and recovery use the existing exact replay boundary.

**Evidence.** End-to-end tests cover source issuance, all four cards, assembly, advisory verification, review, commit, exact retry, later-head recovery, and ledger verification.

## Finding A159-09 — selected-candidate identity was only implicit inside the aggregate candidate digest

**Risk.** Candidate artifact digest plus selected ID is sufficient to reconstruct the winner, but downstream custody did not carry one explicit canonical digest of the chosen candidate object. That made the most important compression input less locally legible than the request, judgment, protected state, and state card.

**Repair.** Added `selected_candidate_sha256` to selection evidence, proposal schema validation, and the durable custody-source metadata. A shared candidate lookup helper now drives compressor-card construction and evidence generation.

**Evidence.** Proposal tests independently hash the exact selected candidate and assert both proposal evidence and source metadata match; schema and checkpoint suites pass.

## Finding A159-10 — active documentation still described the checkpoint as future work

**Risk.** A recipient—especially a weaker model or ChatGPT bridge—would not know which steps exist, who owns them, or what remains external.

**Repair.** Added the complete checkpoint operator guide; updated player, ChatGPT, model entrance, provider, multi-agent, root instructions, design mapping, protocol, threat, glossary, roadmap, architecture, research, decisions, and acceptance records.

**Evidence.** Relative-link checks, provider-content tests, schema inventory, clean extraction, and launcher/CLI smoke form part of release acceptance.

## Refactor assessment

The main refactor is architectural reuse. Checkpoints add a typed context compiler and validation chain above the existing turn kernel rather than creating new event semantics. The provider registry removes duplicated routing data. Exact template builders and dispatch recomputation turn important prose expectations into deterministic objects.

No database or event-schema migration was introduced. Ordinary play packets, run v2, preparation v1, receipt v3, particle/factor custody, consequence repair, fair-play seals, and historical recovery remain on their existing paths.

## Residual risks

- Lacuna does not invoke models or attest provider/model/version, sampling, isolation, independence, or exact context delivery.
- Provenance stripping cannot prevent semantic fingerprints, shared memory, or collusion.
- Required rollout beats prove only that exact text was supplied, not that a faithful simulation occurred.
- Aesthetic scores and deterministic selection can be biased, gameable, or simply wrong.
- Exact speculative artifacts remain sensitive host-side files without bundled encryption, archive, or deletion policy.
- A serial fallback preserves artifact identity but provides no independent contexts.
- The checkpoint walk is stateless across CLI invocations; a managed sidecar and invocation receipts remain future work.
- Automatic trigger policy and the comparative Gwern experiment remain unimplemented.
- SQLite and external artifact storage are separate durability/confidentiality domains.

## Acceptance disposition

The release is acceptable when all 216 tests pass in the worktree and clean extraction, every JSON/TOML/schema parses, relative Markdown links resolve, the manifest verifies, the launcher reports version 0.159.0, and a clean checkpoint roundtrip reaches accepted commit plus exact later-head recovery without duplicate events. Final measured values are recorded in `../acceptance/ACCEPTANCE_rev0159.json`.
