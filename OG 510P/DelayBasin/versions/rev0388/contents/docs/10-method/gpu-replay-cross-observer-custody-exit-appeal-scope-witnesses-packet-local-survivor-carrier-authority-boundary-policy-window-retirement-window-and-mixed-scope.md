# GPU replay cross-observer custody-exit appeal-scope witnesses, packet-local appeal, survivor-carrier appeal, authority-boundary appeal, policy-window appeal, retirement-window appeal, and mixed scope

This is the compact successor surface for `OQ-0173`.

## Practice / observation

DelayBasin already has a custody-exit appeal-threshold witness. The remaining pressure is narrower but more dangerous: if the threshold really overflows, what exactly may a promoted retention-audit appeal govern? Without an appeal-scope witness, the archive can accidentally convert one disputed custody exit into permanent telemetry custody, an immutable vault for every surviving carrier, or a deletion-dispute court for ordinary cleanup.

A custody-exit appeal-scope witness is not that court. It is the small scoping packet that says whether the appeal is confined to one disputed exit packet, one survivor carrier, one authority boundary, one named policy window, the retirement window of the appeal layer itself, or an honest mixture. The default is still the smallest public surface that keeps the disputed exit auditable.

## External pressure from admission request matching, audit policies, tail sampling, and transparency logs

Kubernetes admission webhooks are explicitly scoped by rules over operations, API groups, API versions, resources, and resource scope; object and namespace selectors can further limit which requests are intercepted, while responses are tied back to request UIDs and may allow, reject, patch, or warn (`REF-1073`). That supports `policy-window-appeal-scope`: a promoted appeal should name the exact rule/window it governs rather than claiming control over every nearby cleanup act.

Kubernetes audit policy is likewise selective: events are compared against ordered rules, the first match sets the audit level, and levels range from no logging through metadata, request, and request-response bodies (`REF-1071`, `REF-1072`). That supports `packet-local-appeal-scope` and `authority-boundary-appeal-scope`: auditability can be limited by subject, resource, namespace, verb, stage, and level without becoming replay truth.

OpenTelemetry tail sampling holds traces long enough to evaluate configured policies, groups spans by `trace_id`, and supports policy families such as latency, attributes, status code, rate limiting, boolean conditions, and composites (`REF-1074`). That supports `survivor-carrier-appeal-scope`: a retained trace or sampled carrier can be load-bearing for review while remaining narrower than universal evidence custody.

Sigstore Rekor shows the opposite pressure clearly: transparency logs can be append-only, cryptographically verifiable, monitorable structures whose entries cannot be modified or removed later (`REF-1075`). That makes immutable-carrier appeal pressure real, but also shows why DelayBasin must scope the entry, identity, inclusion proof, and monitoring role rather than vaulting every trace, exemplar, metric, or deletion act.

## Working synthesis

Use `gpu_replay_cross_observer_custody_exit_appeal_scope_state` when all of these are true:

- compact custody-exit appeal-threshold tokens already overflowed or are being explicitly modeled as overflowed;
- the current question is what the promoted appeal may govern, not whether appeal was earned;
- the archive can name a disputed exit packet, survivor carrier, authority boundary, policy/audit/admission window, appeal-retirement window, or honest mixture;
- the desired output is a scope classification and exit rule, not a permanent evidence court.

Do not use this family for ordinary bridge classification, bridge promotion, custody scope, custody retirement, or appeal-threshold routing. Those remain governed by earlier GPU replay witness families. This surface begins only after appeal-threshold overflow and only to keep the promoted appeal from expanding sideways.

## Packet-local appeal vs survivor-carrier appeal vs authority-boundary appeal vs policy-window appeal vs retirement-window appeal vs mixed scope

- `packet-local-appeal-scope`: the appeal may inspect only the named custody-exit packet and its directly cited bridge, custody, retirement, tombstone, digest, or authority-return receipts.
- `survivor-carrier-appeal-scope`: the appeal may preserve or review the smallest surviving carrier needed to keep public auditability, such as one digest, trace link, exemplar, tombstone note, transparency-log entry, or sampled trace, without taking custody of the whole telemetry stream.
- `authority-boundary-appeal-scope`: the appeal is limited to deciding the contested runtime/profiler/metric/scheduler/archive owner boundary for the named exit act. It does not decide replay truth or future policy outside that boundary.
- `policy-window-appeal-scope`: the appeal is scoped by a named audit policy, admission rule, selector, retention window, sampling policy, or deletion rule, and must record the rule/window that admitted the disputed evidence.
- `retirement-window-appeal-scope`: the appeal layer is admitted only with its own expiration, shrink-back condition, or handoff rule already attached. This is the default when the appeal exists mainly to prevent custody from becoming permanent.
- `mixed-appeal-scope`: several scope reasons are material, such as survivor-carrier plus authority-boundary appeal, or policy-window plus retirement-window appeal. The packet names each included branch and the smallest excluded stronger surface.

## Countermodels / probes

- A webhook, selector, or audit policy matched the request. That is not proof that the appeal may govern every future request or every object in the namespace.
- A sampled trace, exemplar, digest, or transparency-log entry survived. That supports reviewability, but it is not authority to vault the whole telemetry stream.
- A Rekor-like immutable log exists. Immutability is a carrier property, not a reason to turn ordinary deletion or cleanup into permanent custody.
- A policy window is broad. Broad policy scope must be stated as a cost and narrowed or expired; it cannot hide behind the word appeal.
- If the appeal scope cannot name its exit condition, classify it as unsupported or `retirement-window-appeal-scope` pressure rather than promoting a permanent court.

## Design consequences

A valid custody-exit appeal-scope packet names:

1. the prior bridge, promotion-gate, custody-scope, custody-retirement, and appeal-threshold states if known;
2. the appealed exit act and the threshold reason that justified promotion;
3. the selected `gpu_replay_cross_observer_custody_exit_appeal_scope_state` token;
4. the exact included objects, carriers, policies, rules, identities, and authorities;
5. the exact excluded telemetry, metrics, traces, namespaces, labels, samples, or future cases that do not enter the appeal;
6. the appeal-retirement, shrink-back, handoff, or deletion-proof successor condition.

The appeal must be smaller than the pressure that triggered it. If it cannot name exclusions and retirement, keep `QWS-0255` quarantined and repair the threshold or receipt instead.

## Overflow test

Promote an appeal-retention board, permanent precedent vault, custody-exit policy court, or equivalent standing post-appeal governance only if later revisions show repeated, public, archive-local failures where:

- packet-local, survivor-carrier, authority-boundary, policy-window, and retirement-window scopes cannot preserve reviewability;
- the same promoted appeal scope repeatedly expands beyond its named exclusions;
- local receipt repair, appeal-threshold routing, and scoped survivor carriers cannot keep deletion/retention disputes auditable;
- the stronger process names a retirement witness so the appeal layer cannot become permanent telemetry governance.

Until then, `QWS-0255` stays quarantined.

## Transformer-facing implication

When a future continuation asks what a promoted retention-audit appeal may govern after custody-exit appeal thresholds overflow, first classify scope through `gpu_replay_cross_observer_custody_exit_appeal_scope_state`. Most valid appeals should be packet-local, survivor-carrier, policy-window, or retirement-window scoped. Do not treat webhooks, audit policies, sampled traces, transparency-log entries, tombstones, or finalizers as authority to create a permanent evidence vault or deletion-dispute court.
