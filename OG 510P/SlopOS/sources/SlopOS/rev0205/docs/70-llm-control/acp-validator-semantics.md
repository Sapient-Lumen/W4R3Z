# ACP validator semantics (slice v0)

Purpose: provide a *small* semantics that can be model-checked and later mechanized, showing that **untrusted text cannot create authority**.
This is a refinement slice: the ACP is non-TCB operationally, but we still formalize it because we want strong, reviewable guarantees about *how* automation is allowed to act.

## Inputs
- Untrusted text/model output + tool outputs (treated as data)
- A proposed action value `a` parsed from **CH-ACP v0** (including `meta.reqctx_digest = digest(CH-REQCTX v1)`)
- Optional approval tokens (CH-AUTHZ v0) / capabilities (explicit)

## State (minimal)
Let ACP state `S_acp` contain:
- `Policy`: optional pinned policy bundle handle (**CH-POLICY v0**, veto-only) used to *deny* otherwise-authorized actions (D-POLICY)
- `Approvals`: set of approval tokens (each binds to `digest(a)`, schema version, expiry)
- `Caps`: handles to authority tokens (capability references; never inferred from text)
- `Now`: monotonic time source (assumption **A-BOOT-2** when used)
- `Log`: append-only transcript entries (**CH-LOG v0**)

Optional (profile-gated, supports sequence reasoning):
- `Ledger`: bounded summary of *authority-relevant* accepted effects (e.g., grants/mints/config writes), sufficient to enforce a declared policy invariant over **sequences**
- `Fuel`: a bounded counter/budget used to make sequence properties model-checkable and to force fail-closed behavior when automation would otherwise run “unbounded”

ACP does **not** have ambient access to privileged mutation; effects occur only by emitting kernel actions through **IF-ACP** / **IF-KABI**.

## Validator step relation
Define `validate: S_acp × a -> (S_acp', outcome)` where `outcome` is either:
- `Reject(code, deny_digest?)`
- `Accept(effect)` where `effect` is a *closed* enum of effect requests that map to kernel actions.

Required properties:
- **Totality / fail-closed**: for all inputs, `validate` returns a result; malformed/unknown kinds reject.
- **Authorization binding**: acceptance requires a matching approval/cap bound to `digest(a)` (**I-AUTHZ-1**).
- **Expiry enforcement**: if expiry is enabled, acceptance requires `Now < expiry` (**I-TIME-1**).
- **Request-context binding**: every CH-ACP action MUST carry `meta.reqctx_digest = digest(CH-REQCTX v1)` (non-authoritative; I-REQCTX-3).
  - The validator MUST resolve and validate the referenced CH-REQCTX descriptor (canonical decode; bounds; closed keys) and fail closed on missing/invalid/unresolvable contexts (PO-REQCTX-VALIDATE; PO-ACT-REQCTX).
  - The validator MUST treat CH-REQCTX as **veto-only** information: it may be used to deny/narrow behavior (deadline/cancel intent; call-chain veto), but never to grant privileged effects.

- **Transcript binding**: every `Accept/Reject` appends a deterministic log entry containing schema version + canonical bytes/digest + **reqctx_digest** + result (**I-LOG-1**).
  - For `Reject(..)`, validators SHOULD emit a structured denial receipt (**CH-DENY v0**) and include `deny_digest = digest(CH-DENY v0)` in the corresponding CH-LOG entry when present.
  - For lane/cfg-param gating denials, producers MUST bind the gate key into the denial receipt:
    - If the rejecting condition is a missing/false `cfg.params.lane.*` toggle, emit CH-DENY with `deny_code = "lane-disabled"` and set `reason.kind="lane"`, `reason.ref_key=<cfg.params.* key>` for the gate (registry-closed; `config-toggle-registry.md`).
    - If the rejecting condition is a non-lane cfg-param veto (workflow posture knob), emit CH-DENY with `deny_code = "cfg-deny"` and set `reason.kind="lane"`, `reason.ref_key=<cfg.params.* key>` for the knob (registry-closed; `config-toggle-registry.md`).
  - For policy/authority denials, producers MUST bind the policy handle digest into the denial receipt (prevents “which policy?” from drifting into ambient state):
    - If the rejection is due to missing/expired approval/cap binding, emit CH-DENY with `deny_code = "missing-approval"` or `"expired-approval"` and set `reason.kind="policy"`, `reason.ref_digest = digest(CH-POLICY v0)` or `digest(CH-POLICYHANDLE v0)`.
    - If the rejection is due to veto-only policy evaluation (D-POLICY), emit CH-DENY with `deny_code = "policy-deny"` and set `reason.kind="policy"`, `reason.ref_digest = digest(CH-POLICY v0)` or `digest(CH-POLICYHANDLE v0)`.
  - `deny_code` values are closed-world per `deny-code-registry.md`; validators MUST reject unknown codes (fail closed).
  - Validators SHOULD also emit a non-authoritative outcome receipt (**CH-ACPOUT v0**) for each `Accept/Reject` decision on CH-ACP actions:
    - binds `action_digest` (and `kind`) and echoes `reqctx_digest`,
    - carries `conflict_key_digest` / `order_digest` when applicable (D-COMMUTE observability),
    - and, for deterministic rejections where CH-DENY is emitted, references `deny_digest`.
    The receipt is indexed by `action_digest` (or `out_id`) in a profile-defined receipt store; persistence/export is gated by policy (CH-OBSPOL) but the wire shape is stable.

- **Kind metadata closure + commutativity discipline**: per-kind conflict key derivation and commutativity/ordering stance are closed-world and pinned by `acp-action-kind-registry.md`.
  - The per-kind **commutation predicate** and the **normalized observation boundary** used by swap-order commutativity tests are pinned in `acp-commutativity-predicate-registry.md` (I-ACP-COMMUTE-1; PO-ACP-COMMUTE-PREDMAP).
  - If the kind has a conflict key, the validator deterministically computes `conflict_key_digest = digest(CH-CONFLICTKEY v0)` from `target/params` (or rejects if derivation fields are malformed).
  - If the kind is **ordered**, the validator requires `meta.order_digest = digest(CH-ORDERTOK v0)` and `meta.conflict_key_digest` and checks scope binding (I-ORDERTOK-2); missing/mismatched/expired tokens reject.
  - Transcripts record the derived `conflict_key_digest` and, when ordered, the `order_digest` in `CH-LOG v0` entries; when D-EXPLAIN is enabled, CH-RECEIPT records SHOULD also carry these digests as non-authoritative observability metadata (PO-ACT-KINDMETA).

- **Retry safety + dedupe keys are explicit (D-RETRYSAFE)**: for any kind whose registry retry-safety states **at-least-once-safe**, the validator/owner service MUST implement duplicate suppression keyed by the schema-pinned idempotency key (e.g., CH-EFFCON `contract_id`, CH-JOBREQ `job_id`, CH-TIMEREQ `req_id`, CH-NOTIF.id). Dedupe keys are non-authoritative: they may be used to deny/narrow or to return a deterministic cached/no-op outcome, but never to grant privileged effects. Duplicate suppression MUST occur before any effect and outcomes MUST be transcript-visible (CH-LOG/CH-ACPOUT) (I-RETRY-1; PO-RETRY-DEDUP).
  - When CH-ACPOUT is emitted for an accepted-but-deduped proposal, producers SHOULD set `effect = "duplicate_suppressed"` (CH-ACPOUT v0) so retries are auditable without reading implementation-specific logs.
  - For `capshell.exec`, practical at-least-once safety additionally assumes the pinned capshell output normal form: exportable outputs are referenced as `digest(CH-AREF v0)` and duplicates return the same output digests (see `docs/30-architecture/capshell-output-normal-form-v0.md`).

- **Workflow automation is exec-pack + reqctx + contract + argv + env + cwd + stdio-bound (optional)**: if D-CAPSHELL is enabled and the action kind is `capshell.exec`, acceptance additionally requires:
  - a valid `exec_pack_digest = digest(CH-EXECPACK v2)` (capshell execution pack; completeness seal), which binds:
    - `reqctx_digest = digest(CH-REQCTX v1)` (non-authoritative; veto-only correlation hook), and
      - the validator MUST require `reqctx_digest` to match the action’s `meta.reqctx_digest` (fail closed; PO-CAPSHELL-REQCTX-BIND),
    - `effcon_digest = digest(CH-EFFCON v0)` (veto-only effect contract),
    - `argv_digest = digest(CH-ARGV v0)` (typed argv tokens), and
      - within the referenced CH-ARGV, executable selection is **explicit and unique**: validators MUST require **exactly one** `desc` token with `role="exec"` and MUST NOT resolve an executable from `lit` tokens or an **ambient PATH** (see `docs/30-architecture/capshell-exec-selector-posture-v0.md`).
    - `env_digest = digest(CH-ENV v0)` (typed environment tokens; no ambient env inheritance),
    - `cwd_digest = digest(CH-CWD v0)` (typed working-directory selector; no ambient cwd inheritance),
    - `stdio_digest = digest(CH-STDIO v0)` (typed stdio bindings; no ambient stdio/TTY inheritance),
    - `fdset_digest = digest(CH-FDSET v0)` (typed extra child-handle bindings; no ambient handle/FD table inheritance).
  - If `cfg.params.capshell.minimal_context=true`, validators MUST additionally require the referenced execution context to be *minimal* (PO-CAPSHELL-MINCTX-ENF):
    - CH-ENV `env` list is empty (no inherited baseline env; no explicit env variables),
    - CH-CWD selector is `kind="empty"`,
    - CH-STDIO bindings are exactly `(stdin.kind="null", stdout.kind="drop", stderr.kind="drop")`,
    - CH-FDSET `fds` list is empty,
    Violations MUST fail closed and SHOULD emit CH-DENY with deny_code `cfg-deny` and `reason.kind="lane"`, `reason.ref_key="cfg.params.capshell.minimal_context"`.
  - If `cfg.params.capshell.require_plumbmsg=true`, validators MUST additionally require the referenced CH-EXECPACK v2 to include `plumbmsg_digest = digest(CH-PLUMBMSG v0)` and MUST resolve + canonically validate the referenced CH-PLUMBMSG descriptor before any effect (PO-PLUMBMSG-VALIDATE; PO-CAPSHELL-PLUMBMSG-REQ).
    - Missing `plumbmsg_digest` MUST fail closed and SHOULD emit CH-DENY with deny_code `plumbmsg-missing` and bind `reason.kind="schema"`, `reason.ref_schema="CH-PLUMBMSG v0"`.
  - If `cfg.params.capshell.require_budget_lease=true` **and** `cfg.params.lane.metering=true`, validators MUST require the bound request context (CH-REQCTX v1 referenced by `meta.reqctx_digest` and by CH-EXECPACK v2) to include at least one `budget_desc_digests` entry whose digest resolves and validates as **CH-BUDGET v0** (no implicit sponsorship; I-BUDGET-1; PO-CAPSHELL-BUDGET-REQ). Resolution is non-ambient: do not dereference locators; treat schema mismatches as missing (`reqctx-budget-ref-posture-v0.md`).
    - Missing or unresolvable/invalid budget descriptors MUST fail closed and SHOULD emit CH-DENY with deny_code `budget-missing` and bind `reason.kind="reqctx"`, `reason.ref_schema="CH-REQCTX v1"`, and `reason.ref_digest=meta.reqctx_digest`.

  The validator also requires a policy-allowlisted mapping from the action’s declared effect families to the runner’s allowed channels.
  - The validator MUST treat CH-EFFCON as veto-only (I-EFFCON-1): a contract can only *reduce* what the runner may do.
  - Any attempt by the runner to invoke an effect family not listed in the active contract MUST fail closed and be transcript-visible (I-EFFCON-2; PO-CAPSHELL-ENF).
  - Any `desc_schema` referenced in the bound CH-ARGV/CH-ENV MUST be permitted by the active contract’s effect list per the CH-EFFCON “Workflow-bound descriptor allowlist”; mismatches MUST fail closed and SHOULD be treated as CH-DENY `effcon-violation` (bind `reason.ref_digest = effcon_digest`).
  - If a `capshell.exec` proposal is rejected because `exec_pack_digest` is missing, validators SHOULD emit CH-DENY with deny_code `execpack-missing`.
  - If a `capshell.exec` proposal is rejected because the exec-pack `reqctx_digest` does not match the action `meta.reqctx_digest`, validators SHOULD emit CH-DENY with deny_code `reqctx-mismatch` and bind `reason.kind = "reqctx"`, `reason.ref_schema = "CH-REQCTX v1"`, and `reason.ref_digest = meta.reqctx_digest`.
  - If a `capshell.exec` proposal is rejected due to a contract violation, validators SHOULD emit CH-DENY with deny_code `effcon-violation` and bind `reason.kind = "effcon"` to the relevant contract digest.
  - If a `capshell.exec` proposal is rejected because `argv_digest` cannot be validated or bound to already-held descriptors/handles, validators SHOULD emit CH-DENY with deny_code `argv-bind-failed` and bind `reason.kind = "schema"`, `reason.ref_schema = "CH-ARGV v0"`, and `reason.ref_digest = argv_digest`.
  - If a `capshell.exec` proposal is rejected because the CH-ARGV has no usable executable selector (missing/ambiguous `role="exec"`), validators SHOULD also use CH-DENY `argv-bind-failed` with the same schema-bound reason fields.
  - If a `capshell.exec` proposal is rejected because `env_digest` cannot be validated or bound to already-held descriptors/handles, validators SHOULD emit CH-DENY with deny_code `env-bind-failed` and bind `reason.kind = "schema"`, `reason.ref_schema = "CH-ENV v0"`, and `reason.ref_digest = env_digest`.
  - If a `capshell.exec` proposal is rejected because `cwd_digest` cannot be validated or bound to already-held descriptors/handles, validators SHOULD emit CH-DENY with deny_code `cwd-bind-failed` and bind `reason.kind = "schema"`, `reason.ref_schema = "CH-CWD v0"`, and `reason.ref_digest = cwd_digest`.
  - If a `capshell.exec` proposal is rejected because `stdio_digest` cannot be validated or bound to already-held descriptors/handles, validators SHOULD emit CH-DENY with deny_code `stdio-bind-failed` and bind `reason.kind = "schema"`, `reason.ref_schema = "CH-STDIO v0"`, and `reason.ref_digest = stdio_digest`.
  - If a `capshell.exec` proposal is rejected because `fdset_digest` cannot be validated or bound to already-held descriptors/handles (or because the runner would inherit extra ambient handles), validators SHOULD emit CH-DENY with deny_code `fd-bind-failed` and bind `reason.kind = "schema"`, `reason.ref_schema = "CH-FDSET v0"`, and `reason.ref_digest = fdset_digest`.


- **Attention portal requests are schema-bound and killable (optional)**: if D-ATTN is enabled and the action kind is `portal.attn.request`, acceptance additionally requires:
  - lane gate `cfg.params.lane.portal.attn` enabled (missing/false denies; PO-LANE-KILL),
  - a valid `notif_digest = digest(CH-NOTIF v0)` whose referenced bytes pass canonical CH-NOTIF validation (PO-NOTIF-VALIDATE),
  - and (when CH-NOTIF includes `actions[*]`), that each action binds to allowlisted intent schemas (`CH-ROUTE v0` / `CH-ACP v0`) by digest (PO-ATTN-ACTIONBIND).
  The validator MUST treat the request as non-authoritative data and invoke the portal only via explicit portal capabilities; it MUST emit transcript-visible outcomes (CH-ACPOUT/CH-DENY) including the derived `conflict_key_digest` and (because the kind is ordered within a domain) the `order_digest` when accepted (PO-ACP-ATTN-REQUEST).


- **Timeproof sampling is schema-bound and killable (optional)**: if D-TIMEPROOF is enabled and the action kind is `portal.clock.timeproof.sample`, acceptance additionally requires:
  - lane gates `cfg.params.lane.portal.clock` **and** `cfg.params.lane.timeproof` enabled (missing/false denies; PO-LANE-KILL),
  - a valid `timereq_digest = digest(CH-TIMEREQ v0)` whose referenced bytes pass canonical CH-TIMEREQ validation (PO-TIMEREQ-VALIDATE),
  - and (when the profile uses authenticated time for security decisions) deterministic verification + monotonic-apply rules for the resulting time proof artifact (PO-TIMEPROOF-VERIFY; PO-TIMEPROOF-APPLY).
  The validator MUST treat the request as non-authoritative data and invoke the portal only via explicit portal capabilities (no ambient NTP/DNS); it MUST emit transcript-visible outcomes (CH-ACPOUT/CH-DENY) including the derived `conflict_key_digest` and (because the kind is ordered within a domain) the `order_digest` when accepted (PO-ACP-TIMEPROOF-SAMPLE).

- **Network lease requests are schema-bound and killable (optional)**: if D-NETLEASE is enabled and the action kind is `portal.net.request`, acceptance additionally requires:
  - lane gate `cfg.params.lane.portal.net` enabled (missing/false denies; PO-LANE-KILL),
  - a valid `netreq_digest = digest(CH-NETREQ v0)` whose referenced bytes pass canonical CH-NETREQ validation (PO-NETREQ-VALIDATE),
  - and (when the kind claims **at-least-once-safe**) portal-side dedupe keyed by CH-NETREQ.req_id with transcript-visible duplicate suppression (D-RETRYSAFE; PO-RETRY-DEDUP).
  The validator MUST treat the request as non-authoritative data and invoke the portal only via explicit portal capabilities (no ambient socket constructors); it MUST emit transcript-visible outcomes (CH-ACPOUT/CH-DENY) including the derived `conflict_key_digest` and (because the kind is ordered within a domain) the `order_digest` when accepted, and SHOULD include a digest-only receipt reference to the emitted CH-NETLEASE descriptor when safe (PO-ACP-NET-REQUEST; PO-NETLEASE-VALIDATE).

- **Entropy portal requests are schema-bound and killable (optional)**: if D-NONDET is enabled and the action kind is `portal.entropy.request`, acceptance additionally requires:
  - lane gate `cfg.params.lane.portal.entropy` enabled (missing/false denies; PO-LANE-KILL),
  - a valid `entreq_digest = digest(CH-ENTREQ v0)` whose referenced bytes pass canonical CH-ENTREQ validation (PO-ENTREQ-VALIDATE),
  - and (when the kind claims **at-least-once-safe**) portal-side dedupe keyed by CH-ENTREQ.req_id with transcript-visible duplicate suppression (D-RETRYSAFE; PO-RETRY-DEDUP).
  The validator MUST treat the request as non-authoritative data and invoke the portal only via explicit portal capabilities (no ambient RNG constructors); it MUST emit transcript-visible outcomes (CH-ACPOUT/CH-DENY) including the derived `conflict_key_digest` and (because the kind is ordered within a domain) the `order_digest` when accepted, and SHOULD include a digest-only receipt reference to the emitted CH-ENTROPY descriptor when safe (PO-ACP-ENTROPY-REQUEST; PO-ENTROPY-VALIDATE).

- **Job portal submissions are schema-bound and killable (optional)**: if D-JOBS is enabled and the action kind is `portal.jobs.submit`, acceptance additionally requires:
  - lane gate `cfg.params.lane.portal.jobs` enabled (missing/false denies; PO-LANE-KILL),
  - a valid `jobreq_digest = digest(CH-JOBREQ v0)` whose referenced bytes pass canonical CH-JOBREQ validation (PO-JOBREQ-VALIDATE),
  - and deterministic enforcement of declared constraints/bounds by the portal (PO-JOBS-ENF).
  The validator MUST treat the request as non-authoritative data and invoke the portal only via explicit portal capabilities (no ambient cron/alarms); it MUST emit transcript-visible outcomes (CH-ACPOUT/CH-DENY) including the derived `conflict_key_digest` and (because the kind is ordered within a domain) the `order_digest` when accepted (PO-ACP-JOBS-SUBMIT).

- **Background portal requests are schema-bound and killable (optional)**: if D-BGLEASE is enabled and the action kind is `portal.background.request`, acceptance additionally requires:
  - lane gate `cfg.params.lane.portal.background` enabled (missing/false denies; PO-LANE-KILL),
  - a valid `bgreq_digest = digest(CH-BGREQ v0)` whose referenced bytes pass canonical CH-BGREQ validation (PO-BGREQ-VALIDATE),
  - and deterministic enforcement of background/autostart clamps, renew/review posture, and revoke/expiry semantics by the portal (PO-BGLEASE-ENF).
  The validator MUST treat the request as non-authoritative data and invoke the portal only via explicit portal capabilities (no ambient daemons/autostart registries); it MUST emit transcript-visible outcomes (CH-ACPOUT/CH-DENY) including the derived `conflict_key_digest` and (because the kind is ordered within a domain) the `order_digest` when accepted (PO-ACP-BGLEASE-REQUEST).

- **Policy is veto-only (optional)**: if D-POLICY is enabled, `validate` consults the pinned policy bundle deterministically (errors deny) and treats policy only as an additional restriction, not as a grant (**I-POLICY-1**, **I-POLICY-2**).
  - Policy denials MUST be emitted as CH-DENY with deny_code `policy-deny` and `reason.kind="policy"` bound to the policy digest (receipt surface; no ambient “which policy?”).

### Deny codes used by ACP validators (v0 seed)

ACP validators SHOULD use these CH-DENY codes for `Reject(..)` outcomes (all are defined in `deny-code-registry.md`):
- `invalid-schema`
- `unknown-kind`
- `missing-approval`
- `expired-approval`
- `policy-deny`
- `lane-disabled`
- `cfg-deny`
- `effcon-violation`
- `execpack-missing`
- `plumbmsg-missing`
- `reqctx-mismatch`
- `argv-bind-failed`
- `env-bind-failed`
- `cwd-bind-failed`
- `stdio-bind-failed`
- `fd-bind-failed`
- `conflict-key-invalid`
- `order-witness-missing`
- `order-witness-invalid`
- `budget-missing`
- `budget-exhausted`
- `internal-error`

### Ordering denials are digest-bound (receipt surface; no ambient state)

Ordering/commutativity failures are a common drift seam: without a receipt-shaped binding, transcripts degrade into “something about ordering” and tooling can’t reliably audit which serialization domain was involved.

ACP validators SHOULD emit CH-DENY with these **digest bindings** (all non-authoritative; D-COMMUTE observability only):
- `deny_code = conflict-key-invalid`: set `reason.kind="ordering"` and set `conflict_key_digest = meta.conflict_key_digest` (rejecting digest).
- `deny_code = order-witness-missing`: set `reason.kind="ordering"` and include `conflict_key_digest` (validator-derived) to name the ordered domain even when `meta.order_digest` is absent.
- `deny_code = order-witness-invalid`: set `reason.kind="ordering"`, include `order_digest = meta.order_digest`, and SHOULD include `conflict_key_digest` (validator-derived).

These bindings keep “Hybrid + commutativity” honest under retries/concurrency and prevent hidden ambient state from becoming the de-facto explanation surface.

### Policy/authority denials are digest-bound (receipt surface; no ambient state)

Policy is explicitly pinned as a veto-only input (CH-POLICY). A frequent drift seam is that “missing approval” / “policy denied” becomes an ad-hoc string without naming *which* pinned policy handle was in force.

When CH-DENY is emitted for these classes, ACP validators MUST bind the policy digest (non-authoritative; audit-only):
- `deny_code = missing-approval`: set `reason.kind="policy"` and bind `reason.ref_digest = digest(CH-POLICY v0)` or `digest(CH-POLICYHANDLE v0)`.
- `deny_code = expired-approval`: set `reason.kind="policy"` and bind `reason.ref_digest = digest(CH-POLICY v0)` or `digest(CH-POLICYHANDLE v0)`.
- `deny_code = policy-deny`: set `reason.kind="policy"` and bind `reason.ref_digest = digest(CH-POLICY v0)` or `digest(CH-POLICYHANDLE v0)`.

Sequence-scoped (optional; explicitly *not* a default claim):
- **Bounded sequence discipline**: if `Ledger/Fuel` are enabled, acceptance must preserve the declared sequence invariant (**I-LLM-2**) and decrement/charge `Fuel` on each accepted step; exhaustion rejects deterministically (**PO-ACT-COMPOSE**).

## Planner hint lane (optional; correctness-neutral)

LLM tooling may propose *plans* that reorder or batch actions using commutativity metadata (D-COMMUTE), but:
- the validator’s correctness does **not** depend on planner hints,
- and the validator must reject any plan step that crosses an **ordered** boundary without explicit ordering witnesses.

## Theorem shape (what we aim to show)
For an action space `A_acp`:
1) If `I-LLM-1` holds initially, then after any sequence of ACP steps, **no privileged effect occurs without explicit authorization** (supports **C-LLM-1**).
2) If the `Ledger/Fuel` profile is enabled, then any accepted sequence stays within the declared bounds for authority-relevant effects (supports **I-LLM-2**; does *not* claim full unbounded “no laundering”).
3) Transcript replay: re-running `validate` on logged accepted actions yields the same outcomes (supports **PO-LOG-REPLAY**).

## Evidence plan (tight)
- **E1**: property tests + adversarial prompt/tool corpus:
  - “propose unsafe” → reject;
  - “missing approval” → reject;
  - “bad binding/expiry” → reject;
  - **ordered kind without order_digest/conflict_key_digest** → reject;
  - **ordered kind with mismatched conflict_key_digest/scope** → reject.
- **E2**: bounded model check of `validate` for a small state/action bound.
  - baseline: “text cannot create authority” (I-LLM-1)
  - optional profile: bounded-sequence discipline via `Ledger/Fuel` (I-LLM-2)
