# Direct-upload feedback audit — rev0163

## Scope

This audit reviewed the two rev0160 companion artifacts supplied alongside the accepted rev0162 repository:

- `LACUNA_DIRECT_UPLOAD_EXPERIMENT_KIT_rev0160`;
- `LACUNA_LLM_IN_CHARGE_FIELD_MANUAL_rev0160.md`.

The question was not whether every statement was individually sensible. It was whether the advice still serves two distinct recipients:

1. a player who should be able to say “Will you DM?” and enjoy a game; and
2. a researcher testing the retcon-planning bottleneck without silently leaking detailed futures into continuation.

The review also compared the current product-facing claims with official documentation available on 2026-06-25 and treated product labels as changing host behavior rather than stable kernel facts.

## Disposition summary

| Feedback theme | Disposition | Rev0163 action |
|---|---|---|
| One long ChatGPT context confounds the forgetting experiment | **Accepted; highest priority** | Added an authenticated post-commit narrator capsule and a required fresh-narrator treatment topology |
| Checkpoint workers need exact least-context cards and parent-only authority | **Retained** | Existing managed dispatch/accept/commit boundary remains; scenario validation is stricter |
| State-card body may exist only in the private sidecar | **Accepted and elevated** | Added explicit root/operator warnings and capsule preservation guidance |
| Capability-first routing is better than relying on product names | **Retained** | Added a short root `OPERATE_LACUNA.md` entrance |
| Human paste bridge and card-only worker contexts are useful | **Retained** | Documented as honest low-automation paths rather than pseudo-attestation |
| A shared Project is a clean context-isolation boundary | **Rejected** | Current guidance says Project memory is a confound for the clean condition |
| Temporary/fresh chats automatically prove no inherited instructions or memory | **Rejected as overclaim** | Guidance requires recording Custom Instructions/settings and labels freshness as declared |
| Fixed `/mnt/data/lacuna-lab` paths should be the universal operator convention | **Not promoted** | Kept host paths outside the portable kernel; active-run absolute-path strictness remains |
| The large rev0160 manual should be shipped as the main entrance | **Superseded** | Replaced with a short root entrance plus focused operator protocol; detailed doctrine remains in existing docs |
| Helper OpenAI driver, session tarball tool, and host-specific scripts belong in core | **Deferred/external** | Provider credentials, network transport, archive policy, and relocation remain host responsibilities |
| Provider/model aliases or invocation IDs prove execution/isolation | **Rejected** | Existing explicit host-declaration nonclaims retained |
| Same-context serial roles are worthless | **Rejected** | They remain valid functionality and control conditions; they are simply not the clean bottleneck condition |

## Finding DUA163-01 — worker separation stopped one context too early

**Problem.** Rev0162's `lacuna-role-separated` condition required distinct generator, judge, compressor, and verifier contexts. The narrator that continued after the checkpoint was not required to be fresh or bound to the compressed state card. A host could satisfy the recorded role topology while the continuing narrator retained every rejected future from the parent conversation.

**Repair.** Added `lacuna.checkpoint-narrator-capsule.v1` and:

```bash
./lacuna checkpoint run narrator-capsule RUN_PATH
```

The capsule is available only after committed-run audit. It is built from the authenticated request, proposal, receipt, and digests and excludes candidate, judgment, and verifier inputs from its construction interface.

Scenario treatment validation now requires a fresh narrator context after each completed role-separated checkpoint and binds the first subsequent turn to the exact checkpoint ID and capsule digest.

## Finding DUA163-02 — the controls did not specify context persistence

**Problem.** The previous scenario contracts distinguished checkpoint role contexts but left ordinary narrator persistence implicit. An operator could use fresh narration contexts in a control or reuse contexts in the treatment, weakening causal interpretation.

**Repair.** Every condition contract now declares `continuation_mode`:

- `forward-only`, `prompt-only-retcon`, and `lacuna-serial`: `persistent-context`;
- `lacuna-role-separated`: `fresh-narrator-capsule`.

The first three conditions must use one declared context across the complete cell. The role-separated treatment uses one narrator context per story segment, with a new segment after every completed checkpoint.

## Finding DUA163-03 — the original scenario template did not observe continuation after the checkpoint

**Problem.** The single-step default scheduled a checkpoint after its final narration. A run could satisfy checkpoint-role machinery without producing any later player-visible turn from the compressed state, making the forgetting treatment vacuous.

**Repair.** Scenario capsules now require a following ordinary step after every checkpoint. The default template includes an explicit post-checkpoint continuation probe, and final-step checkpoints refuse before run publication.

## Finding DUA163-04 — state-card retention was easy to miss

**Problem.** A checkpoint commit can bind the selected card's digest while the full card body remains only in the private sidecar. Losing that sidecar can leave a valid cube that cannot reproduce the intended hidden continuation guidance.

**Repair.** The new root entrance, fresh-narrator guide, capsule nonclaims, and revision records state this explicitly. The capsule carries the exact card body and digest; it does not pretend the ledger can reconstruct omitted private text.

## Finding DUA163-05 — onboarding was comprehensive but not legible

**Problem.** The rev0160 field manual bundled product notes, command reference, threat model, helpers, rehearsal transcript, experiment design, and large copies of repository documentation into one file. It contained valuable analysis but was a poor first task for a human or weaker model and was version-locked to rev0160.

**Repair.** Added `OPERATE_LACUNA.md` as the portable entrance. It contains the player path, capability routing, managed run loop, clean experimental reset, recovery rules, and trust boundary. Details link to focused, maintained repository documents.

The giant manual is not copied into the release. This avoids a second stale documentation tree and removes hardcoded host paths and model-version claims from the normal entrance.

## Finding DUA163-06 — product surfaces must be treated as experimental variables

**Problem.** Names such as Project, Temporary Chat, Agent, subagent, or API do not by themselves establish the supplied-context boundary. Project memory can intentionally share context; Temporary Chat can still apply Custom Instructions; subagents can share readable files; API calls can be linked through response/conversation state.

**Repair.** The operator guide records these as host controls and asks experiments to retain the actual settings, context identifiers, capsule digest, and filesystem scope. Lacuna continues to call all such metadata host declarations rather than provider attestations.

## Finding DUA163-07 — useful host helpers should not widen the kernel

**Problem.** The direct-upload kit proposed session archives, provider drivers, fixed-path imports, and fresh-call scripts. They can be useful for a specific lab but mix credentials, product SDKs, retention policy, network failure, and relocation semantics into the stable custody boundary.

**Disposition.** Keep them external until a host adapter has its own threat model and conformance tests. Rev0163 implements only the portable semantic seam—the deterministic narrator capsule and topology custody—inside Lacuna.

## Finding DUA163-08 — observed canon can still live outside the cube

**Problem.** Lacuna retains transcript digests rather than transcript bodies. A fresh narrator that receives only typed audience context can lose continuity-critical observations from narration-only turns, while a persistent-context control still remembers them.

**Disposition.** The operator protocol now requires a preregistered public-context policy. Either material observed canon is typed and the capsule is the whole continuation input, or the same exact player-visible transcript/public summary is separately digest-bound and supplied to every condition. The capsule command does not claim transcript completeness, and hidden parent history must never be used as the substitute.

## Refactor assessment

The implementation uses one new narrow module, `src/lacuna/continuation.py`, rather than adding product-specific behavior to the checkpoint engine. Managed checkpoint audit authenticates the full chain; the capsule builder accepts only the minimal already-authenticated objects. Scenario topology validation consumes checkpoint/capsule identifiers as declarations and does not claim provider enforcement.

Database schema 8 and event schema 1 remain unchanged. The capsule is a private host sidecar artifact, not a story-ledger event or authority grant.

## Residual risks

- A hostile or careless parent can supply extra context despite recording a valid capsule digest.
- A provider can retain or correlate information outside the visible prompt.
- A capsule may be schema-valid but omit artistically essential information.
- The selected state card may overcommit one explanation or preserve the wrong unknowns.
- A random canary can expose leakage when it appears, but cannot prove isolation when absent.
- Direct-upload persistence, encryption, archive/restore, credentials, and provider invocation remain external.

## Disposition

The rev0160 feedback contained one decisive experimental correction—the post-checkpoint narrator reset—and several valuable operating cautions. Rev0163 promotes those into a small executable contract and concise onboarding, while declining to ship stale product claims, a duplicated manual, or host-specific utilities as kernel features.
