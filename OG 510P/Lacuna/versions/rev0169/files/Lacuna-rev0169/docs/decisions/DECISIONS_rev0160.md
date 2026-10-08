# Decisions — rev0160

## D160-01 — make managed checkpoint runs the normal operator surface

**Decision.** Add a strict request-scoped sidecar state machine and document it as the default path. Retain the rev0159 stateless commands for custom hosts.

**Why.** Correct schemas are insufficient when a recipient must privately remember stage, filenames, routes, retries, and commit rules. The cube should compile the next allowed context and command.

**Rejected.** A prose checklist alone; automatic inference from whichever files happen to exist; replacing the lower-level protocol.

## D160-02 — keep the run outside the story ledger

**Decision.** `run.json`, cards, rejected futures, scores, model returns, and invocation receipts remain private host sidecars.

**Why.** They are speculative process custody, not story facts. Recording every failed model call as canon would conflate experiment history with represented-world truth.

**Consequence.** Retention, encryption, archive, redaction, and deletion remain host policy. The managed run is auditable but not automatically durable or confidential like the event ledger.

## D160-03 — fix all provider routes at begin

**Decision.** Require one complete role-to-provider map before the first worker call. A route cannot change inside a run.

**Why.** This makes mixed-provider experiments reproducible and prevents later relabelling. It also lets every historical dispatch be recomputed exactly.

**Rejected.** Choosing a provider independently on every dispatch; silently falling back from empty overrides; treating provider name as execution proof.

## D160-04 — make dispatch complete, current-stage, and nonauthoritative

**Decision.** `lacuna.checkpoint-run-agent-dispatch.v1` embeds the exact role card, route alias, return schema, staging path, accept command, failure command, authority split, and nonclaims.

**Why.** Chat contexts and subagents should not need local filesystem access or protocol inference. Embedding the complete card reduces missing-context errors.

**Boundary.** The dispatch invokes nothing and grants no assembly, review, commit, recovery, or presentation authority.

## D160-05 — record attempts as host declarations

**Decision.** Retain ordered accepted and failed invocation receipts with exact card/dispatch/output digests and optional model/version/ID/timing metadata. Label them explicitly `host-declared`.

**Why.** Operational custody is better than an invisible retry history, but claiming provider attestation would be false.

**Rejected.** No attempt records; treating supplied model names as verified identity; requiring a vendor SDK or signature scheme in the kernel.

## D160-06 — exactly one accepted receipt per retained role output

**Decision.** A retained candidates/judgment/compression/verifier artifact is valid only with one accepted invocation receipt. Failed attempts may precede it; none may follow acceptance for that role.

**Why.** This gives every retained worker output a unique place in the ordered run history and prevents silent output replacement.

## D160-07 — make failure nonadvancing

**Decision.** `record-failure` writes custody but leaves the current status and card unchanged.

**Why.** Provider errors, timeouts, invalid output, refusals, and interruptions are not model-role completion. The next attempt should use the same exact card and route.

## D160-08 — one authoritative manifest; derived pointer only

**Decision.** `run.json` owns state. `NEXT.md` is a byte-audited deterministic view that may be reconstructed independently.

**Why.** Human/model legibility needs a simple next step, while recovery must not turn a mutable Markdown file into authority.

**Rejected.** Inferring state from `NEXT.md`; repairing missing authoritative artifacts; accepting multiple plausible next actions.

## D160-09 — reconstruct the full chain on every transition

**Decision.** Audit rebuilds each downstream card/proposal from validated upstream objects and rechecks route, invocation, review, receipt, cube, and pointer custody.

**Why.** Fixed filenames and matching digests are not enough if a semantically wrong but rehashed object can be substituted.

**Cost.** Audits are intentionally more expensive than shallow file checks. A narrow internal receipt helper removes only duplicated replay after the full chain is already validated.

## D160-10 — terminal verifier refusal

**Decision.** A `refuse` return produces `verifier-refused`; that run cannot dispatch again or commit.

**Why.** Editing findings or flipping status would destroy the meaning of the retained verifier attempt. Corrective work belongs in a fresh source-bound run.

## D160-11 — parent manufactures review immediately after a verifier pass

**Decision.** Acceptance of a passing verifier triggers parent-only kernel review and writes `70-checkpoint-review.json`, moving directly to `ready-to-commit`.

**Why.** The verifier is advisory. Readiness should name the actual rollback-tested kernel result rather than ask the operator to infer another hidden parent step.

## D160-12 — bind begin to the exact open cube path

**Decision.** The supplied resolved path must equal `Cube.root.resolve(strict=True)` before sidecar creation.

**Why.** An API should not freeze context from one cube object while directing later audit/commit to another path.

## D160-13 — validate source objects before publishing a run directory

**Decision.** Verify the cube and manufacture the checkpoint request and generator card before creating the sidecar directory.

**Why.** Ordinary policy/identity validation errors should not leave run-shaped orphans. Actual interruption during filesystem publication remains a separate durability risk.

## D160-14 — strict project-version binding, no managed-run migration

**Decision.** A managed manifest audits only under the exact creating Lacuna version. Paths are absolute and runs are nonrelocatable.

**Why.** Silent reinterpretation of active workflow state is more dangerous than explicit incompatibility. A future migration/export protocol must define semantic conversion deliberately.

## D160-15 — share sidecar security primitives

**Decision.** Extract descriptor reads, path/member checks, locks, digesting, and shell rendering into one internal module used by ordinary and checkpoint runs.

**Why.** Security-sensitive duplicate code will drift. The abstractions are sidecar-level, not turn-specific.

## D160-16 — keep public and internal receipt validation separate

**Decision.** Expose a public full-chain checkpoint receipt validator. Permit an internal document validator only after the caller has already validated the complete chain.

**Why.** External callers need a safe standalone API. Managed commit/audit should not repeat identical expensive preparation replay. The internal helper is a performance boundary, not an authority shortcut.

## D160-17 — no automatic trigger or provider invocation

**Decision.** The parent decides when to open a checkpoint and delivers dispatches through its chosen human, API, chat, or subagent mechanism.

**Why.** Trigger policy, credentials, billing, timeouts, sampling, provider retention, and product-specific agent APIs change quickly and belong above the stable custody seam.

## D160-18 — do not infer efficacy from operational completeness

**Decision.** Describe rev0160 as making the retcon experiment runnable and auditable, not as proving it improves fiction or science.

**Why.** Fixed routes, exact artifacts, and invocation custody answer reproducibility and silent-cheating questions. They do not answer creative quality, search coverage, independence, calibration, or player preference.

## D160-19 — enforce invocation capacity before publication

**Decision.** Cap one managed run at 1,000 invocation receipts and refuse a 1,001st accepted or failed attempt before writing any new receipt or manifest state.

**Why.** The exchange schema already bounds the list. Checking only during post-write audit could turn a resource-limit refusal into a self-created invalid run.

## Consequences for the next revision

The highest-value next work is a comparative scenario-capsule runner and live provider-conformance evidence. It should reuse the managed run as the experimental spine, randomize condition labels, retain honest cost/latency/model declarations, and keep human ratings separate from mechanical custody measures. Broader worker authority is not the next requirement.
