# Helm ↔ SlopOS seam map v0

Status: candidate proof fixture  
Revision: rev0204

## One sentence

Helm makes authority legible; SlopOS makes authority enforceable.

rev0204 turns that sentence into a small, testable seam map. Helm may prepare, explain, display, recall, and route a capability-mediated action. SlopOS owns admission, serialization, dedupe, order evidence, descriptor issuance, and fail-closed denial.

## Why this comes now

rev0203 proved repair attempts on the release-readiness specimen. That was necessary but still too internal: it showed Helm can represent truth and follow-through, not that Helm can be a shell companion to SlopOS.

rev0204 therefore adds the second specimen, `portal-net-consent-export`, around the SlopOS `portal.net.request` proof slice. This is the first hard place where a Helm button could become an actual capability action, so the seam must be explicit before UI polish or backend work.

## Seam law

| Helm object | SlopOS object / seam | Product rule |
|---|---|---|
| `action_warrant` | `CH-REQCTX` / ACP proposal | Helm explains intent and exact visible copy; SlopOS validates. |
| `consent_card` | volition / trusted-path evidence | Helm presents and records local volition; SlopOS may require it as action-bound witness. |
| `authority_diff` | ACP precondition and action digest binding | Helm shows what is being requested; SlopOS rejects stale/missing/mismatched basis. |
| `route_witness` | `svc:portal.net` serialization owner | Helm explains route; SlopOS owns ordering and serialization. |
| `receipt_path` | `CH-ACPOUT`, `CH-DENY`, `CH-NETLEASE` digest refs | Helm recalls exact outcomes; receipts do not become current live truth. |
| `retry_guard` | `CH-NETREQ.req_id` exact replay dedupe | Helm labels retry posture; SlopOS prevents duplicate effects. |
| `retention_posture` | artifact refs / digest-only receipt | Helm keeps minimization and forgetting visible; SlopOS descriptors remain exact issued-bounds evidence only. |

## Required chain for consequential actions

Every Helm surface that can arm a SlopOS-mediated action must expose this chain:

```text
proposal
→ authority_diff
→ presentation_surface
→ trusted_path_posture
→ gesture_evidence
→ volition_token_or_decline
→ approval_cut
→ slopos_admission_or_denial
→ receipt
→ retention_posture
```

Missing links weaken the surface. They do not silently become policy, approval, or authority.

## What Helm may do

Helm may:

- explain the proposed action;
- show the authority diff and data class;
- show trusted-path posture and spoof guard state;
- collect fresh local volition for one named action;
- show the SlopOS route and owner;
- show accepted, denied, duplicate, and stale-refused outcomes;
- show exact digest-only receipts;
- show retry/redelivery posture;
- show retention budget, minimization transform, forgetting authority, and sweep witness.

## What Helm must not do

Helm must not:

- create ambient socket, resolver, file, browser, policy, or workflow authority;
- infer permission from Recall;
- treat a receipt as current live truth;
- treat duplicate replay as a new acceptance;
- merge same-`req_id` mismatch into a prior request;
- spend stale evidence or background continuation as fresh user intent;
- hide denial, authority diff, trusted-path state, or retention budget;
- publish/export secret payloads merely because an operator saw a consent card;
- become a policy engine, network portal, workflow engine, approval engine, event bus, semantic layer, table format, canonical backend, or new pillar.

## SlopOS-specific cut for rev0204

rev0204 binds only one concrete action family:

```text
action_kind: portal.net.request
owner: svc:portal.net
request: CH-NETREQ v0
outcomes: CH-ACPOUT / CH-DENY
issued bounds: CH-NETLEASE v0
ordering: CH-ORDERTOK v0
retry/dedupe: CH-NETREQ.req_id exact replay only
conflict key family: domain.id
lane gate: cfg.params.lane.portal.net
```

This is not a generic portal abstraction. It is a single specimen bridge. Other portal families must earn their own fixtures.

## Companion imports narrowed

- From SlopOS rev0720: import the `portal.net.request` proof seam, not SlopOS's whole boundary archive.
- From ViewFS rev0154: import consent-card separation, trusted path lamps, gesture evidence, volition tokens, approval cuts, and receipts, not ViewFS's entire view model.
- From Schell rev0248: import retention budget / forgetting authority / minimization fence requirements, not a global memory service.
- From Foundry rev0082: import classification pins and crosswalk witnesses for small vocabularies, not a classification engine.
- From Steward rev0181: import retry/replay/redelivery guard rails, not a scheduler.
- From Harbor rev0093: import recheck windows and stale-surface guards, not an implementation monitor.
- From Ward rev0077: import delegation/handback authority separation, not a personnel registry.

## Next proof

The next proof is the fixture and checker pair:

- `fixtures/portal-net-consent-export/companion-seam-pack.json`
- `tools/check_portal_net_consent_export.py`

The pass condition is six cases: accepted export, lane-disabled denial, exact replay duplicate, same-req-id mismatch denial, stale Recall refusal, and retained/minimized receipt.


## rev0210 addendum: namespace/audience binding

rev0210 adds `namespace_binding_strip`, `account_tenant_destination_gate`, and `issuer_audience_resource_gate` to the required chain. This does not make Helm an identity provider or OAuth adapter. It only means a portal-net action card must show the exact account, tenant, workspace, subject namespace, destination origin, issuer, audience/resource, membership freshness, endpoint owner, environment, expiry, and non-authority before SlopOS admission.

A valid actor, fresh local volition, and verified trusted path are still insufficient when the namespace is wrong. Wrong workspace, tenant alias collision, personal/work profile split, stale membership, cross-tenant subject ID collision, destination mismatch, redirect rebinding, audience mismatch, unverified endpoint owner, and staging/prod issuer mix-up must block, refuse, quarantine, or require a fresh authority diff before effect.


## rev0212 resource-shape addendum

Helm now carries a `resource_shape_strip` over SlopOS `CH-NETREQ` body/projection/attachment/response descriptors. The strip shows payload schema, field projection, row scope, attachment inventory, MIME posture, transform lineage, query/body parameter freeze, archive inventory, response schema, and non-authority. It is evidence only; endpoint match, schema validation, filenames, MIME labels, row counts, summaries, and digests do not authorize egress or replace SlopOS admission.


## rev0212 effect propagation append

The companion chain now includes `effect_manifest_strip`, `downstream_propagation_gate`, `side_effect_inventory_gate`, and `postcondition_receipt_gate`. Payload match is not effect approval: Helm must show primary effect, hidden/visible side effects, fanout, callbacks, budget, idempotency effect, downstream trace, and postcondition receipt posture before any runtime exists.

## rev0213 temporal authority addendum

Portal-net rows now carry a temporal-authority strip for clock basis, approval window, volition expiry, revocation state, lease/membership epochs, callback/retry deadlines, retention expiry, schema sunset, and dedupe window. The strip is witness-only: it cannot authorize, extend, revoke, retry, or prove current live truth.
## rev0214 sync/cache state addendum

Portal-net rows now carry a sync/cache-state strip for online state, cache origin, cache/server/revocation epochs, partial sync gaps, conflicts, tombstone inventory, local mutation queue, cache digest, lease snapshot epoch, Recall snapshot posture, delayed revocation, and resume checkpoint. The strip is witness-only: it cannot authorize, flush a queue, treat offline cache as live truth, suppress revocation, or resume without recheckpoint.


## rev0215 presentation-integrity addendum

Portal-net rows now carry a presentation-integrity strip for surface origin, trusted-path state, redaction overlay, data class, stale/history badge, receipt badge, authority-badge posture, visual diff, screen-share state, screenshot/export posture, clipboard/copy-channel posture, assistive copy completeness, localized-copy match, and fail-closed rendering. The strip is witness-only: it cannot authorize, approve payloads, establish current live truth, spend consent, or replace SlopOS admission.

New seam additions:

```text
presentation_integrity_strip
redaction_display_gate
visual_overclaim_guard
copy_channel_guard
assistive_copy_gate
```

The compact law is: **what Helm displays must not leak, hide, or overclaim; what Helm displays still does not authorize.**

## rev0217 interpretation/readback addendum

rev0217 adds an interpretation/readback strip after presentation integrity. The strip does not add authority. It checks whether the surfaced explanation, generated summary, localization, assistive narration, glossary support, and operator readback preserve the same destination, payload scope, downstream effects, stale/history posture, retention expiry, recovery limits, and non-authority warnings that appeared in the exact copy.

New seam refs:

- `interpretation_readback_strip`
- `plain_language_gate`
- `summary_fidelity_gate`
- `translation_warning_gate`
- `operator_readback_gate`
- `ambiguity_recheck_gate`

The strip is still weaker than fresh local volition and SlopOS admission. A correct readback can allow Helm to continue presenting the arm path; it cannot consent, authorize, approve payload, approve effects, or prove current truth.


## rev0217 seam addition

After interpretation/readback, Helm adds `arming_ceremony_strip`, `arm_cut_digest_gate`, `separate_final_gesture_gate`, `unbundling_gate`, `cancel_path_gate`, and `slopos_order_after_arm_gate`. Helm renders and audits these strips; SlopOS still admits or denies the request.


## rev0218 execution-truth addition

After final arming, Helm still separates armed/submitted/admitted/acknowledged/accepted/delivered/completed/settled stages. The execution-truth strip is weaker than SlopOS authority and weaker than remote success; it only renders the strongest currently evidenced stage and any remainder.


## rev0221 addition — appeal/correction truth

Appeals, disputes, corrections, false-positive withdrawals, false-negative backfills, external support notes, supersession links, and rectification witnesses are now explicit evidence strips. They do not rewrite receipts, arm retries, bypass SlopOS, or become authority. The portal invariant index audits the proof vocabulary across registered layers without becoming policy.
