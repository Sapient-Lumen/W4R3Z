# Audit — rev0158

## Scope

This audit began from the rev0157 release artifact and asked whether the cube’s strongest internal guarantees were actually reachable by a fresh player, ChatGPT-style context, or provider-native subagent without private coaching. It also inspected the request-run sidecar trust boundary for link substitution, ambiguous recovery, and documentation drift.

The audit did not treat model quality, provider isolation, or narrative quality as properties the kernel can prove.

## Parent baseline

Rev0157 already provided:

- strict request-scoped run v2 topology;
- digest-bound least-context task cards;
- parent-only accept and commit;
- exact rollback kernel preparation;
- frozen direct replay;
- authenticated post-commit recovery at the historical request head;
- and a cooperative owner-only same-run lock.

Those mechanisms passed their existing regression suite and were retained.

## Finding A158-01 — the player entrance was described but not typed

**Risk.** “Will you DM?” could be routed socially by a model, but the low-level request contract represented every message as undifferentiated player input. A literal host could treat the invitation as dialogue or an attempted in-world action.

**Repair.** Added `lacuna.turn-request.v3`, source protocol v2, and explicit `input_kind` with values `session-control` and `play-turn`. Added v2 compatibility that deterministically defaults historical packets to `play-turn`.

**Evidence.** Turn packet, orchestration, entrance, CLI, schema, and compatibility tests cover valid typing, invalid-kind refusal, card propagation, source metadata, and old-request commit behavior.

## Finding A158-02 — no single executable start composed bootstrap, selection, and run issuance

**Risk.** A fresh workspace model still had to infer campaign-library setup, selection, actor IDs, run flags, and the fact that the first sentence was control text. This undermined the one-sentence claim for less capable coordinators.

**Repair.** Added `play start` and `lacuna.play-start.v1`. It resolves a cube/library, bootstraps only absent or empty paths, refuses foreign nonempty overlays, selects only an unambiguous campaign, derives campaign roles, opens typed session control, and returns the complete next action.

**Evidence.** Tests cover the literal default sentence, CLI start, safe bootstrap refusal, sole-campaign selection, multi-campaign ambiguity, zero fictional assertions after start, and schema validation.

## Finding A158-03 — task cards were exact but the cross-provider handoff could still be path-only

**Risk.** `NEXT.md` named a complete local card, but a ChatGPT context or remote worker may not have filesystem access. A coordinator could improvise a shortened prompt, omit the return schema, merge hidden context, or ask the worker to discover files.

**Repair.** Added `turn run dispatch` and `lacuna.agent-dispatch.v1`. The envelope embeds the exact current task card, provider alias, input kind, canonical digest, exact return contract, parent command, authority split, and nonclaims. Dispatch refuses parent-owned states and unknown providers.

**Evidence.** Tests compare the embedded object and digest with the retained card, validate the exchange schema, check provider routing and Markdown legibility, and prove parent-owned-stage refusal.

## Finding A158-04 — authoritative member reads trusted path-opening behavior too much

**Risk.** Manifest digests are meaningful only when the bytes hashed are from the same ordinary file whose pathname and metadata were inspected. Plain path reads can follow symlinks, accept hard links, read special files, consume unbounded input, or observe a substituted pathname.

**Repair.** Centralized all run-sidecar reads in `_read_run_member_bytes`. It uses descriptor/path identity checks before and after bounded reads and refuses symlinks, hard links, nonregular files, oversize members, mutation during read, and detected path substitution.

**Evidence.** Adversarial tests cover manifest and artifact symlinks, same-byte hard links, a 16 MiB limit violation, and mocked pathname substitution.

## Finding A158-05 — pointer damage had no safe, narrow repair command

**Risk.** `NEXT.md` is deterministic and nonauthoritative, but operators could be tempted to hand-edit it or rebuild more important artifacts after a pointer failure.

**Repair.** Added `turn run recover`. It audits every authoritative member while ignoring only the current pointer, replaces only `NEXT.md`, then repeats full audit. It refuses when any authoritative artifact has changed.

**Evidence.** Tests prove byte-for-byte preservation of every authoritative member, tampered-packet refusal, symlink-pointer replacement without touching its external target, and final full audit.

## Finding A158-06 — one adversarial failure path raised the wrong exception shape

**Risk.** During the new pathname-substitution audit, the final refusal branch constructed `LacunaError` with a duplicated positional message. The intended integrity refusal could degrade into an unrelated `TypeError`, losing the structured error code expected by hosts.

**Repair.** Corrected the exception construction and added a regression that forces the post-read pathname to report a different inode. The result is now `turn-run-member-unsafe` with an explicit substitution message.

**Evidence.** The focused handoff/integrity suite passes the forced branch.

## Finding A158-07 — operator documentation mixed completed and future boundaries

**Risk.** Current guides still made some rev0157 features sound prospective, omitted the exact direct start/dispatch path, and did not consistently tell weaker hosts what not to infer.

**Repair.** Reworked the player entrance, one-sentence start, ChatGPT, model entrance, provider, multi-agent, turn-run, threat, glossary, protocol, roadmap, design, root adapter, and integration documents. Provider configuration guides record primary documentation URLs and explicitly warn that syntax may change.

**Evidence.** Provider-config tests assert root intent routing, role aliases, parent ownership, ChatGPT capability honesty, primary-source URLs, and drift language. Markdown relative-link validation is part of release acceptance.

## Refactor assessment

The most important refactor is the consolidation of sidecar member reading. Integrity policy no longer depends on each caller remembering how to open, bound, authenticate, decode, and parse a file. Dispatch also reuses the existing card generator and run audit rather than creating a parallel prompt system. `play start` composes campaign, model-reference, and run APIs rather than bypassing them.

No database/event migration was introduced. The kernel mutation path and exact preparation protocol were not forked.

## Residual risks

- Dispatch is a rendered handoff, not a provider invocation or attestation.
- Provider runtimes may ignore checked-in tool or subagent policies.
- Same-user or parent-directory attackers remain outside the sidecar integrity guarantee.
- Distinct runs against one cube are not serialized by the per-run lock; stale-head refusal is still the cross-run guard.
- SQLite and sidecar writes are not one transaction; post-commit receipt recovery is covered, but begin-time orphan indexing is not.
- Run v2 contains absolute paths and has no relocation protocol.
- A configured chat can begin play, but durable ChatGPT persistence still needs a human or connected host.
- No comparative experiment yet shows that typed custody or subagent separation improves fiction.

## Acceptance disposition

The full release suite is expected to contain 199 unit/end-to-end tests, including nine new handoff/integrity tests and five direct-play tests. Final counts, clean-extraction results, schema validation, manifest integrity, and smoke results are recorded in `../acceptance/ACCEPTANCE_rev0158.json`.
