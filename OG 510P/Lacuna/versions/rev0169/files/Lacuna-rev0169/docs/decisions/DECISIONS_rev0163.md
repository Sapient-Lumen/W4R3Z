# Decisions — rev0163

## D-163-01 — treat continuation isolation as a separate boundary

Distinct generator, judge, compressor, and verifier contexts do not imply that the narrator continuing the story is fresh. The strongest treatment must reset the creative continuation context after commit.

## D-163-02 — compile the bottleneck only from an authenticated committed run

`checkpoint run narrator-capsule` first performs the full managed-run audit and refuses before `committed`. A proposal, verifier pass, or ready-to-commit review is insufficient.

## D-163-03 — make rejected artifacts impossible builder inputs

The capsule builder accepts request, proposal/compression, receipt, and their retained digests. It has no candidates, judgment, or verifier parameters. Structural omission is safer than asking a parent to redact a complete private run manually.

## D-163-04 — keep the capsule outside story canon

The capsule is a deterministic private host artifact. It is not a ledger event, assertion, selected world, commitment, authority grant, or proof that the compressed explanation is true.

## D-163-05 — generate on demand rather than add a new committed-run state

The accepted receipt remains the authoritative terminal run artifact. Generating a capsule read-only avoids a second filesystem publication state after commit while still producing a canonical digest for handoff.

## D-163-06 — make the committed pointer teach the next clean step

A committed checkpoint's `NEXT.md` now names `narrator-capsule`. The operator should not need to remember an external helper or infer that checkpoint completion is not yet narrator forgetting.

## D-163-07 — make controls persist context deliberately

`forward-only`, `prompt-only-retcon`, and `lacuna-serial` use one declared context for the entire cell. Freshening a control opportunistically would erase part of the intended comparison.

## D-163-08 — make role-separated continuation segmental

The narrator may persist between checkpoints, but every completed checkpoint ends that narrator segment. The next ordinary turn must use a new context and name the exact checkpoint and capsule digest on every attempt.

## D-163-09 — retain host-declaration language

Context IDs, managed checkpoint IDs, and capsule digests let Lacuna detect internally inconsistent topology. They do not prove provider execution, prompt contents, memory erasure, independence, or tool isolation.

## D-163-10 — require an observable turn after every scenario checkpoint

A checkpoint after the final script step cannot affect any retained post-checkpoint narration. Such a capsule now refuses. The default template includes a checkpointed departure followed by an explicit continuation probe.

## D-163-11 — replace the mega-manual with layered onboarding

Ship one concise root operating entrance and one focused fresh-narrator guide. Keep detailed doctrine in maintained repository documents rather than embedding copies, generated CLI help, product notes, and helper source into one version-locked manual.

## D-163-12 — do not promote host-specific drivers into the kernel

API credentials, network calls, ChatGPT/Codex product state, session archives, fixed sandbox paths, encryption, and restore policy remain host concerns. The stable kernel addition is the provider-neutral capsule and topology contract.

## D-163-13 — preserve database and event schemas

The change concerns private exchange artifacts and experiment validation. Database schema 8 and event schema 1 remain unchanged; no migration is justified.
## D-163-14 — treat public-context parity as host experiment custody

The core capsule carries typed audience custody and accepted checkpoint narration but does not invent or reconstruct external transcript bodies. A study must preregister either typed-canon operation or the same separately digest-bound player-visible history for every condition. Hidden parent history is never an acceptable substitute.

