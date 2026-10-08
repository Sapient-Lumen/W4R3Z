# Audit — rev0161

## Scope

This audit examined whether Lacuna could make a fair, runnable comparison of its retcon checkpoint against simpler baselines, and whether ordinary/managed run creation still admitted path-authority or partial-publication ambiguity.

## Findings and dispositions

### A-161-01 — no executable comparative harness

**Severity:** high research-validity gap  
**Disposition:** fixed

Prior revisions implemented the mechanism but could not answer whether it helped. Rev0161 adds a fixed four-condition capsule, exact seed clones, hidden assignment, serial opaque dispatch, frozen returns, blind ratings, and post-rating unblinding.

### A-161-02 — ordinary turn path named by caller without exact `Cube` equality

**Severity:** high authority-confusion risk  
**Disposition:** fixed

`begin_turn_run` accepted both an open `Cube` and a caller string but did not prove they named the same directory. It now resolves both strictly and refuses with `turn-run-cube-path-mismatch` before sidecar publication.

### A-161-03 — run directories became visible incrementally

**Severity:** medium crash/observer ambiguity  
**Disposition:** fixed within one-filesystem boundary

Turn and checkpoint runs previously created their authoritative directory before all required initial members existed. A shared private staging/publish primitive now exposes the final directory only after lock, artifacts, manifest, and pointer have been written. Failure cleanup is regression-tested.

Residual: story-ledger request events and sidecar publication are not one transaction. An event may survive a later sidecar-publication failure.

### A-161-04 — scenario invocation did not bind ordinary calls to script steps

**Severity:** high experimental-custody risk  
**Disposition:** fixed

Every invocation now names `script_step_id`; checkpoint calls must also name the same designated `checkpoint_step_id`. Accepted ordinary turns occur exactly once in script order.

### A-161-05 — accepted narration could be omitted from a partial-failure transcript

**Severity:** high selective-reporting risk  
**Disposition:** fixed

For completed, failed, and refused cells, accepted ordinary-turn invocations must match the retained transcript step IDs exactly. A host cannot retain an accepted call while dropping its player-visible result from the comparison.

### A-161-06 — declared context could be reused across conditions

**Severity:** high contamination risk  
**Disposition:** fixed as declaration-level enforcement

Before writing a candidate cell return, the runner reads prior accepted returns and refuses any reused declared `context_id`. Audit repeats the check. Non-null provider `invocation_id` values are globally unique.

Residual: a dishonest host can relabel one real conversation with distinct IDs; Lacuna lacks provider attestation.

### A-161-07 — role-separated topology could collapse silently

**Severity:** high treatment-integrity risk  
**Disposition:** fixed

Managed conditions enforce exact accepted role counts/order. Serial requires one shared declared context per checkpoint. Role-separated requires four pairwise-distinct declared contexts. Prompt-only permits only monolithic checkpoint calls; forward-only permits none.

### A-161-08 — pending or recorded clone contamination

**Severity:** high baseline-integrity risk  
**Disposition:** fixed

Every audit opens all four clones. Pending cells must equal the seed head/event count. Recorded cells must equal their frozen receipt. Mutation before activation or after acceptance refuses.

### A-161-09 — “blind” could be overclaimed

**Severity:** high claim-hygiene risk  
**Disposition:** constrained, not eliminated

The packet omits structured condition labels, private prompts, invocation metadata, and assignment. Fixed nonclaims explicitly state that style, failures, or leaked method names can reveal a condition semantically. Human prior knowledge is outside Lacuna's view.

### A-161-10 — hidden randomization could be overclaimed

**Severity:** high claim-hygiene risk  
**Disposition:** constrained, not eliminated

Assignment is deterministically reconstructible from a retained 32-byte host seed and committed before results. Nonclaims state that this is not externally witnessed randomness and does not detect discarded unpublished runs.

### A-161-11 — ratings and mechanics could be conflated

**Severity:** medium inference risk  
**Disposition:** fixed

The report separately structures mechanical outcomes, host-declared execution totals, and human rating summaries. It labels sums/counts as descriptive, not calibrated utility, significance, or causal estimates.

### A-161-12 — private drivers available beside blind artifacts

**Severity:** medium operational leakage risk  
**Disposition:** documented boundary

The run is owner-private. Raters must receive only `70-blind-rating-packet.json`; workers must receive only the active dispatch. Broad filesystem access defeats the intended information boundary. Cryptographic compartmentalization is not supplied.

## Refactor review

The publication helper centralizes previously duplicated lock/staging/cleanup behavior. Turn and checkpoint begin paths now manufacture policy-bound objects before directory publication, then use the same whole-directory transition. Regression tests patch initial manifest writing and require no final or staged directory to remain.

## Negative tests added

- wrong open-cube/supplied-path pair refuses before turn publication;
- failed initial turn publication leaves no visible/staged run;
- failed initial checkpoint publication leaves no visible/staged run;
- scenario initial publication cleanup;
- role-separated shared context refuses without mutation;
- cross-cell context reuse refuses before any write;
- duplicate/misordered script-step execution refuses;
- accepted turn omitted from failed transcript refuses;
- pending clone contamination is detected;
- recorded clone mutation invalidates frozen custody;
- rehashed assignment tamper is rejected; and
- exact seed path binding is required.

## Acceptance judgment

The implementation is suitable as an auditable single-block comparison runner and as a clearer subagent/context curriculum. It is not yet a study result. The next research-critical layer is a replicate-bundle protocol with preregistration digest, external assignment witness option, retained provider response attestations where available, and analysis that preserves failures and rater disagreement.
