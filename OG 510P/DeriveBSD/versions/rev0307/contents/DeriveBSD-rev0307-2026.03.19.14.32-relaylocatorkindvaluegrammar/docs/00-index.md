# DeriveBSD archive index

## New in 2026-03-19r307

- Decide publish-session relay remote-locator-value posture by accepting `adrs/ADR-0167-publish-session-relay-remote-locator-values-follow-locator-kind.md`, adding `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`, and tightening `net.publish.session` so `relay.remote_locator.value` now follows locator kind: `uri-hint` values stay URI-shaped without query/fragment while `portal-object` / `object-path` / `opaque` values stay non-URI-shaped, keeping relay-side value text from smuggling URL folklore back into support-session or tailnet lanes (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that remote-locator-value posture through the temporary-sharing, access-model, tailnet, ingress, risk, runbook, hygiene, juicy-lesson, README, and discovery surfaces, so the relay-side kind/value pair now tells one coherent share-shape story instead of leaving value text free to contradict the chosen lane (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/570-publish-session-access-model-posture-boundary.md`, `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`, `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`, `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_remote_locator_value_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_publish_session_remote_locator_value_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r306

- Decide publish-session relay remote-locator posture by accepting `adrs/ADR-0166-publish-session-relay-remote-locator-kind-follows-access-model.md`, adding `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`, and tightening `net.publish.session` so `relay.remote_locator.kind` now follows access model: `uri-hint` stays in the `relay-url` lane, `peer-relay` stays `portal-object` / `opaque`, and `reverse-forward` stays `object-path` / `opaque`, keeping the relay join from quietly reopening URI/session drift after endpoint grammar was already fixed (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that remote-locator posture through the temporary-sharing, access-model, tailnet, ingress, risk, runbook, hygiene, juicy-lesson, reference, README, and discovery surfaces, so the relay side of the receipt now tells the same share-shape story as `published_endpoint` (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/570-publish-session-access-model-posture-boundary.md`, `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`, `docs/575-publish-session-endpoint-hints-follow-access-model.md`, `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_remote_locator_contract.py`, wire it into `tools/hygiene.py`, update older publish-session guardrails to synthesize peer-relay/tailnet examples with the new relay-side locator posture, and regenerate generated discovery/version docs (`tools/check_publish_session_remote_locator_contract.py`, `tools/check_publish_session_access_model_contract.py`, `tools/check_publish_session_support_session_contract.py`, `tools/check_publish_session_tailnet_access_model_contract.py`, `tools/check_publish_session_endpoint_hint_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r306

- Decide publish-session endpoint-hint posture by accepting `adrs/ADR-0165-publish-session-endpoint-hints-follow-access-model.md`, adding `docs/575-publish-session-endpoint-hints-follow-access-model.md`, and tightening `net.publish.session` so `relay-url` and `reverse-forward` temporary sharing now requires `hostname + port` while `peer-relay` sharing keeps URL/host endpoint hints absent, keeping each temporary-sharing lane on a coherent endpoint grammar without inventing a bigger adapter registry (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that endpoint-hint posture through the temporary-sharing, locator, access-model, ingress, risk, runbook, hygiene, juicy-lesson, and discovery surfaces, so URL-shaped, tailnet/device-name, and support-session peer handoff stop reusing the same mixed locator language (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/565-publish-session-session-scoped-locator-posture-boundary.md`, `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`, `docs/570-publish-session-access-model-posture-boundary.md`, `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`, `docs/575-publish-session-endpoint-hints-follow-access-model.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_endpoint_hint_contract.py`, wire it into `tools/hygiene.py`, update older publish-session guardrails to synthesize peer-relay/tailnet examples with the new endpoint-hint posture, and regenerate generated discovery/version docs (`tools/check_publish_session_endpoint_hint_contract.py`, `tools/check_publish_session_support_session_contract.py`, `tools/check_publish_session_access_model_contract.py`, `tools/check_publish_session_tailnet_access_model_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r304

- Decide publish-session public-webhook validation-hint posture by accepting `adrs/ADR-0164-publish-session-public-webhook-shares-require-validation-hints.md`, adding `docs/574-publish-session-public-webhook-shares-require-validation-hints.md`, and tightening `net.publish.session` so `public-webhook` temporary sharing now requires `audience.validation_hint`, keeping callback publication evidentially verifiable without standardizing a provider-specific webhook subsystem (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that public-webhook validation-hint posture through the temporary-sharing, audience, secret-handoff, ingress, risk, runbook, hygiene, juicy-lesson, reference, and discovery surfaces, so public callback publication stops being URL-shaped-but-validation-hand-wavy (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`, `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`, `docs/574-publish-session-public-webhook-shares-require-validation-hints.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_webhook_validation_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_publish_session_webhook_validation_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r303

- Decide publish-session audience-binding-hint posture by accepting `adrs/ADR-0163-publish-session-audience-bound-shares-require-binding-hints.md`, adding `docs/573-publish-session-audience-bound-shares-require-binding-hints.md`, and tightening `net.publish.session` so `provider-identity` / `organization-users` temporary sharing now requires `identity_provider_hint` while `named-recipients` temporary sharing requires `recipient_hint`, keeping audience-bound receipts explainable without choosing a provider-specific roster subsystem (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that binding-hint posture through the temporary-sharing, audience, ingress, risk, runbook, hygiene, juicy-lesson, reference, and discovery surfaces, so audience-bound shares stop being formally non-public but evidentially hand-wavy (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`, `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`, `docs/573-publish-session-audience-bound-shares-require-binding-hints.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_binding_hints_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_publish_session_binding_hints_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r302

- Decide publish-session audience-bound human-share access-model posture by accepting `adrs/ADR-0162-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`, adding `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`, and tightening `net.publish.session` so `organization-users` and `named-recipients` temporary sharing now stays `relay-url` shaped, completing the first useful access-model matrix without forcing the recipient/exposure matrix up front (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that audience-bound human-share access-model posture through the temporary-sharing, audience, access-model, ingress, risk, runbook, hygiene, juicy-lesson, and discovery surfaces, so ordinary authenticated preview/demo sharing now stays visibly URL-shaped instead of borrowing support-peer or tailnet vocabulary (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`, `docs/570-publish-session-access-model-posture-boundary.md`, `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_human_share_access_model_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_publish_session_human_share_access_model_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r301

- Decide publish-session tailnet reverse-forward posture by accepting `adrs/ADR-0161-publish-session-tailnet-shares-stay-reverse-forward-shaped.md`, adding `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`, and tightening `net.publish.session` so tailnet temporary sharing now stays `reverse-forward` shaped whenever the receipt says `tailnet`, `tailnet-users`, `tailnet-identity`, or `tailnet-device-name`, keeping the private tailnet lane from regressing into URL-shaped relay folklore (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that tailnet reverse-forward posture through the temporary-sharing, locator, access-model, ingress, risk, runbook, hygiene, juicy-lesson, and discovery surfaces, so private tailnet sharing now reads as a device-name/reverse-forward lane instead of a public-share URL with tailnet prose attached (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/565-publish-session-session-scoped-locator-posture-boundary.md`, `docs/570-publish-session-access-model-posture-boundary.md`, `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_tailnet_access_model_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_publish_session_tailnet_access_model_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r300

- Decide publish-session access-model posture by accepting `adrs/ADR-0160-publish-session-access-model-posture-boundary.md`, adding `docs/570-publish-session-access-model-posture-boundary.md`, and tightening `net.publish.session` so `public-link` / `public-webhook` temporary sharing now stays `relay-url` shaped while `support-peer` temporary sharing stays `peer-relay` shaped, keeping support handoffs from regressing into generic tunnel-URL folklore without forcing the full matrix up front (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that access-model posture through the temporary-sharing, support-session, ingress, risk, runbook, hygiene, juicy-lesson, and discovery surfaces, so public callback/demo sharing remains visibly URL-shaped while support-peer sharing remains visibly peer/session-shaped (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`, `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`, `docs/570-publish-session-access-model-posture-boundary.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Remove the lingering example-validation warning by adding `spec/intent.role.binding.event.policy-consume-success.schema.json`, so `spec/examples/intent.role.binding.event.policy-consume-success.json` now has a same-named schema companion instead of depending on manual reviewer memory.

## New in 2026-03-19r299

- Decide publish-session support-session authority posture by accepting `adrs/ADR-0159-publish-session-support-peer-shares-require-support-session-authority.md`, adding `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`, and tightening `net.publish.session` so `support-peer` temporary sharing now requires `authority.trigger = support-session` plus `authority.support_session_digest`, keeping support-flavored relay shares bound to an exact `support.session` evidence object instead of generic support prose (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that support-session authority join through the temporary-sharing, support-session, ingress, risk, runbook, hygiene, juicy-lesson, reference, and discovery surfaces, so B/C support handoffs stay practical while A/D support publication remains exact-session-shaped rather than freestanding relay folklore (`docs/291-remote-assistance-sessions-as-evidence.md`, `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`, `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`, `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_support_session_contract.py`, wire it into `tools/hygiene.py`, and regenerate the generated discovery/version docs (`tools/check_publish_session_support_session_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r298

- Decide publish-session secret consumption semantics posture by accepting `adrs/ADR-0158-publish-session-secret-consumption-semantics.md`, adding `docs/568-publish-session-secret-consumption-semantics-boundary.md`, and tightening `net.publish.session` so secret-gated temporary sharing now also requires `published_endpoint.secret_handoff.consumption_posture`, making `single-use-secret` mean `single-successful-admission` while `shared-secret` stays `reusable-until-expiry` (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that secret consumption semantics posture through the temporary-sharing, ingress, risk, runbook, hygiene, juicy-lesson, reference, and discovery surfaces, so B/C secret-gated sharing can distinguish one-time recipient handoff from reusable temporary secret posture without reopening provider-specific behavior (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`, `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md`, `docs/568-publish-session-secret-consumption-semantics-boundary.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_secret_consumption_contract.py`, wire it into `tools/hygiene.py`, and regenerate the generated discovery/version docs (`tools/check_publish_session_secret_consumption_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r297

- Decide publish-session secret lifetime-coupled posture by accepting `adrs/ADR-0157-publish-session-secret-lifetime-coupled-to-session-authority.md`, adding `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md`, and tightening `net.publish.session` so secret-gated temporary sharing now also requires `published_endpoint.secret_handoff.lifetime_binding = session-authority-bounded` plus `secret_handoff.expires_at`, making the separate handoff secret expire no later than the publish-session authority instead of becoming a longer-lived shadow grant (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that secret lifetime-coupled posture through the temporary-sharing, ingress, risk, runbook, hygiene, juicy-lesson, reference, and discovery surfaces, so B/C secret-gated sharing stays both redacted and actually temporary rather than leaving behind a still-valid secret after the session has ended (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`, `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_secret_lifetime_contract.py`, wire it into `tools/hygiene.py`, and regenerate the generated discovery/version docs (`tools/check_publish_session_secret_lifetime_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r296

- Decide publish-session redacted locator + separate secret-handoff posture by accepting `adrs/ADR-0156-publish-session-redacted-locators-and-separate-secret-handoff.md`, adding `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`, and tightening `net.publish.session` so secret-gated temporary sharing now requires `published_endpoint.secret_handoff.secret_receipt_digest` while `url_hint` / `path_prefix` stay query/fragment-free locator hints, keeping usable `single-use-secret` / `shared-secret` material off the receipt/log/support-bundle surface (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that secret-handoff posture through the temporary-sharing, ingress, risk, runbook, hygiene, juicy-lesson, reference, and discovery surfaces, so B/C secret-gated sharing stays practical without turning bearer URLs into the real access/evidence channel (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_secret_handoff_contract.py`, wire it into `tools/hygiene.py`, and regenerate the generated discovery/version docs (`tools/check_publish_session_secret_handoff_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r295

- Decide publish-session session-scoped locator posture by accepting `adrs/ADR-0155-publish-session-session-scoped-locator-posture.md`, adding `docs/565-publish-session-session-scoped-locator-posture-boundary.md`, and tightening `net.publish.session` so temporary sharing now records `published_endpoint.locator_posture`, keeping public/org/support relay locators `session-scoped` while allowing `tailnet-device-name` only for `tailnet`, so reserved relay domains, custom DNS, or remembered public hostnames do not become a backdoor durable-ingress story (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that locator posture through the temporary-sharing, ingress, risk, runbook, hygiene, juicy-lesson, reference, and discovery surfaces, so B/C temporary sharing stays session-shaped even at the naming layer while durable/stable published names continue to force the `net.listen.*` lane (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`, `docs/565-publish-session-session-scoped-locator-posture-boundary.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_locator_posture_contract.py`, wire it into `tools/hygiene.py`, and regenerate the generated discovery/version docs (`tools/check_publish_session_locator_posture_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r294

- Decide publish-session end conditions and no-auto-resume posture by accepting `adrs/ADR-0154-publish-session-end-conditions-and-no-auto-resume-posture.md`, adding `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`, and tightening `net.publish.session` so temporary sharing now records explicit lifecycle end conditions plus `resume_policy = new-session-with-fresh-authority`, making relay-backed shares reboot-cleared and unable to silently auto-resume from remembered daemon/config state (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that lifetime posture through the temporary-sharing, ingress, risk, runbook, hygiene, juicy-lesson, reference, and discovery surfaces, so B/C sharing remains explicitly session/lease-shaped while durable restart-persistent publication stays on the `net.listen.*` lane (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`, `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_lifetime_contract.py`, wire it into `tools/hygiene.py`, and regenerate the generated discovery/version docs (`tools/check_publish_session_lifetime_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r293

- Decide relay-backed publish-session audience/publicness posture by accepting `adrs/ADR-0153-publish-session-audience-binding-and-publicness-posture.md`, adding `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`, and tightening `net.publish.session` so temporary sharing now records an explicit audience class plus auth mode (`organization-users`, `named-recipients`, `support-session-peer`, `public-webhook`, `public-link`) instead of letting `internet` silently mean anonymous public by default (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that posture through the temporary-sharing, ingress, risk, runbook, hygiene, juicy-lesson, reference, and discovery surfaces, so B/C human sharing stays audience-bound by default while public callback or public-link publication remains an explicit exception posture (`docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_access_posture_contract.py`, wire it into `tools/hygiene.py`, and regenerate the generated discovery/version docs (`tools/check_publish_session_access_posture_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-19r292

- Decide temporary service sharing as a relay-backed publish-session boundary by accepting `adrs/ADR-0152-relay-backed-publish-sessions-for-temporary-service-sharing.md`, adding `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, and introducing `net.publish.session` so B/C preview/demo/webhook sharing now stays local-first, leased, and transport-joined instead of regressing to shadow tunnels or casual public listeners (`spec/net.publish.session.schema.json`, `spec/examples/net.publish.session.json`).
- Reduce archive entropy by threading that boundary through the ingress/risk/runbook/hygiene/juicy-lesson/reference surfaces, so durable host ingress stays on `net.listen.*`, temporary sharing stays relay-backed, and A/D do not inherit workstation/developer tunnel habits as production posture (`docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/266-open-questions-and-risk-register.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_publish_session_contract.py`, wire it into `tools/hygiene.py`, and regenerate the generated discovery/version docs (`tools/check_publish_session_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r291

- Decide remembered-role spent-authority winner-shape summaries by accepting `adrs/ADR-0151-role-binding-policy-consumed-denials-carry-consuming-event-action.md`, adding `docs/561-role-binding-policy-consumed-denials-carry-consuming-event-action.md`, and tightening `intent.role.binding.event` so non-interactive `policy-consumed` denials now also require `consuming_event_action`, making the earlier successful winner's `initialized` vs `updated` shape directly queryable and turning `consumed_previous_binding_digest` into a required summary for updated winners and a forbidden field for initialized winners instead of leaving that absence ambiguous (`spec/intent.role.binding.event.schema.json`, `spec/intent.role.binding.event.write-denied.policy-window.schema.json`, `spec/examples/intent.role.binding.event.write-denied.policy-window.json`, `spec/examples/intent.role.binding.event.policy-consume-success.json`).
- Reduce archive entropy by threading the consuming-event-action rule through the remembered-role event/retry/evidence/support/risk/runbook/README/juicy-lesson surfaces, so detached support bundles and host-local retry logic can tell whether the winning event created state or updated prior state without reopening the winner event body (`docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`, `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md`, `docs/561-role-binding-policy-consumed-denials-carry-consuming-event-action.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_role_binding_policy_consumption_action_contract.py`, wire it into `tools/hygiene.py`, and regenerate the generated discovery/version docs (`tools/check_role_binding_policy_consumption_action_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r290

- Decide remembered-role spent-authority old-edge summaries by accepting `adrs/ADR-0150-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md`, adding `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md`, and tightening `intent.role.binding.event` so non-interactive `policy-consumed` denials may now also carry `consumed_previous_binding_digest` for updated winners, exposing the earlier winning event's replaced `previous_binding.digest` as evidence-only summary data instead of forcing support/retry/export clients to reopen the winner event body (`spec/intent.role.binding.event.schema.json`, `spec/intent.role.binding.event.write-denied.policy-window.schema.json`, `spec/examples/intent.role.binding.event.write-denied.policy-window.json`, `spec/examples/intent.role.binding.event.policy-consume-success.json`).
- Reduce archive entropy by threading the consumed-previous-binding-digest rule through the remembered-role event/precondition/retry/evidence/support/risk/runbook/README/juicy-lesson surfaces, so detached support bundles and host-local retry logic can query the winner's full old→new binding edge without broadening the subsystem (`docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`, `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`, `docs/32-curated-references.md`).
- Add `tools/check_role_binding_policy_consumption_previous_binding_digest_contract.py`, wire it into `tools/hygiene.py`, and regenerate the generated discovery/version docs (`tools/check_role_binding_policy_consumption_previous_binding_digest_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r289

- Decide remembered-role spent-authority review summaries by accepting `adrs/ADR-0149-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`, adding `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`, and tightening `intent.role.binding.event` so non-interactive `policy-consumed` denials now also require `consumed_diff_digest`, exposing the earlier winning event's reviewed `intent.role.binding.diff` digest as evidence-only summary data instead of forcing support/retry/export clients to reopen the winner event body (`spec/intent.role.binding.event.schema.json`, `spec/intent.role.binding.event.write-denied.policy-window.schema.json`, `spec/examples/intent.role.binding.event.write-denied.policy-window.json`, `spec/examples/intent.role.binding.event.policy-consume-success.json`).
- Reduce archive entropy by threading the consumed-diff-digest rule through the remembered-role diff/event/policy/retry/evidence/support/risk/runbook/README/juicy-lesson surfaces, so detached support bundles and host-local retry logic can query both the winning remembered-role result and the winning reviewed diff without broadening the subsystem (`docs/542-role-binding-diff-as-review-surface.md`, `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`, `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_role_binding_policy_consumption_diff_digest_contract.py`, wire it into `tools/hygiene.py`, and regenerate the generated discovery/version docs (`tools/check_role_binding_policy_consumption_diff_digest_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r288

- Decide remembered-role spent-authority result summaries by accepting `adrs/ADR-0148-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`, adding `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`, and tightening `intent.role.binding.event` so non-interactive `policy-consumed` denials now also require `consumed_binding_digest`, exposing the earlier winning event's resulting binding digest as evidence-only summary data instead of forcing support/retry/export clients to reopen the winner event body (`spec/intent.role.binding.event.schema.json`, `spec/intent.role.binding.event.write-denied.policy-window.schema.json`, `spec/examples/intent.role.binding.event.write-denied.policy-window.json`, `spec/examples/intent.role.binding.event.policy-consume-success.json`).
- Reduce archive entropy by threading the consumed-binding-digest rule through the remembered-role event/policy/retry/evidence/support/risk/runbook/README/juicy-lesson surfaces, so detached support bundles and host-local retry logic can query both the winning event and the resulting remembered-role digest without broadening the subsystem (`docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`, `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`, `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_role_binding_policy_consumption_binding_digest_contract.py`, wire it into `tools/hygiene.py`, and regenerate the generated discovery/version docs (`tools/check_role_binding_policy_consumption_binding_digest_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r287

- Decide remembered-role spent-authority offline verification by accepting `adrs/ADR-0147-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`, adding `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`, and tightening `intent.role.binding.event` so non-interactive `policy-consumed` denials now require `consumed_by_event_digest` in addition to `consumed_by_event_id`, binding the denial to the canonical bytes of the earlier successful consuming event instead of trusting only an id pointer (`spec/intent.role.binding.event.schema.json`, `spec/intent.role.binding.event.write-denied.policy-window.schema.json`, `spec/examples/intent.role.binding.event.write-denied.policy-window.json`, `spec/examples/intent.role.binding.event.policy-consume-success.json`).
- Reduce archive entropy by threading the digest-bound consuming-event rule through the remembered-role event/policy/retry/evidence/support/risk/runbook/README/juicy-lesson surfaces, so detached support bundles and deterministic exports can verify the exact winner event that justified `already-applied` rather than relying on live journal lookup (`docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_role_binding_policy_consumption_digest_contract.py`, wire it into `tools/hygiene.py`, extend the curated references with RFC 6920 and OCI descriptor digest guidance, and regenerate the generated discovery/version docs (`tools/check_role_binding_policy_consumption_digest_contract.py`, `tools/hygiene.py`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r286

- Decide remembered-role retry/export recovery summaries by accepting `adrs/ADR-0146-role-binding-retries-need-a-stable-recovery-interpretation-field.md`, adding `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md`, and tightening `intent.role.binding.event` so non-interactive `policy-consumed` denials now carry `recovery_interpretation` as an evidence-only stable summary (`policy-consumed` or `already-applied`) instead of leaving bundle/query surfaces to recompute the retry story from raw joins (`spec/intent.role.binding.event.schema.json`, `spec/intent.role.binding.event.write-denied.policy-window.schema.json`, `spec/examples/intent.role.binding.event.write-denied.policy-window.json`).
- Reduce archive entropy by threading the new stable recovery summary through the remembered-role event/policy/replay/evidence/support/risk/runbook/README/juicy-lesson surfaces, so support bundles and host-local admin/reconcile tools can query one field while the durable denial reason remains unchanged (`docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`, `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_role_binding_policy_recovery_interpretation_contract.py`, wire it into `tools/hygiene.py`, extend the idempotent-retry curated references with AWS's stable-response guidance, and regenerate the generated discovery/version docs (`tools/check_role_binding_policy_recovery_interpretation_contract.py`, `tools/hygiene.py`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r285

- Decide remembered-role spent-authority retry collapse by accepting `adrs/ADR-0145-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, adding `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, and tightening `intent.role.binding.event` wording plus the canonical policy-window denial example so non-interactive `policy-consumed` retries may surface as **already-applied** only when the joined consuming event proves the same exact mutation tuple instead of collapsing every spent authorization into ambient success (`spec/intent.role.binding.event.schema.json`, `spec/examples/intent.role.binding.event.write-denied.policy-window.json`).
- Reduce archive entropy by threading the exact-match recovery rule through the remembered-role event/policy/evidence/support/risk/runbook/README/juicy-lesson surfaces, so crash-retry and support flows can now distinguish “already happened” from “some other winner consumed it first” without inventing a broader transaction or idempotency-key subsystem (`docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`, `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`, `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_role_binding_policy_consumption_recovery_contract.py`, wire it into `tools/hygiene.py`, add idempotent-retry references to `docs/32-curated-references.md`, and regenerate generated discovery/version docs (`tools/check_role_binding_policy_consumption_recovery_contract.py`, `tools/hygiene.py`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r284

- Decide the remembered-role spent-authorization winner pointer by accepting `adrs/ADR-0144-role-binding-policy-consumed-denials-point-to-consuming-event.md`, adding `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`, and tightening `intent.role.binding.event` so non-interactive `reason_code = policy-consumed` now requires `consumed_by_event_id` pointing at the earlier successful consuming event instead of leaving “spent by what?” to log archaeology (`spec/intent.role.binding.event.schema.json`, `spec/intent.role.binding.event.write-denied.policy-window.schema.json`, `spec/examples/intent.role.binding.event.write-denied.policy-window.json`).
- Reduce archive entropy by threading the consuming-event pointer rule through the remembered-role event/policy/evidence/support/risk/README/juicy-lesson surfaces, so support bundles and retry logic can now answer “who already spent this exact authorization?” without inventing a larger replay or transaction subsystem (`docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`, `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`, `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`, `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`, `README.md`).
- Add `tools/check_role_binding_policy_consumption_pointer_contract.py`, wire it into `tools/hygiene.py`, extend the runbook/hygiene guardrails, and regenerate generated discovery/version docs (`tools/check_role_binding_policy_consumption_pointer_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r283

- Decide remembered-role denial precedence by accepting `adrs/ADR-0143-role-binding-denial-precedence-between-policy-and-precondition.md`, adding `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`, and tightening the remembered-role event wording so non-interactive apply now evaluates `policy-denied` / `policy-consumed` / `policy-expired` before `precondition-failed`, with `policy-consumed` winning over later expiry instead of letting spent authorizations decay into a stale-state or generic age story (`spec/intent.role.binding.event.schema.json`, `spec/intent.role.binding.event.write-denied.precondition.schema.json`, `spec/examples/intent.role.binding.event.write-denied.policy-window.json`).
- Reduce archive entropy by threading the denial-precedence rule through the remembered-role event/policy/precondition/evidence/support/risk/README/juicy-lesson surfaces, so reconcile/import/admin implementations now have one deterministic denial ladder and support bundles can distinguish “re-issue authority” from “re-read state” without inventing a larger transaction family (`docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`, `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`, `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`, `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`, `README.md`).
- Add `tools/check_role_binding_denial_precedence_contract.py`, wire it into `tools/hygiene.py`, extend the runbook/hygiene guardrails, and regenerate generated discovery/version docs (`tools/check_role_binding_denial_precedence_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

- Decide the remembered-role non-interactive policy-failure vocabulary by accepting `adrs/ADR-0142-role-binding-policy-window-denials-need-typed-reasons.md`, adding `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`, extending `intent.role.binding.event.reason_code` with `policy-expired` and `policy-consumed`, and adding a canonical policy-window denial subtype/example so expired or already-consumed exact-mutation authorizations no longer collapse into generic `policy-denied` (`spec/intent.role.binding.event.schema.json`, `spec/intent.role.binding.event.write-denied.policy-window.schema.json`, `spec/examples/intent.role.binding.event.write-denied.policy-window.json`).
- Reduce archive entropy by threading the typed policy-window denial rule through the remembered-role event/policy/evidence/support/risk/README/juicy-lesson surfaces, so support bundles and reconcile logs can now distinguish “never allowed”, “expired before apply”, and “already consumed” without inventing a larger transaction family (`docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`, `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`, `README.md`).
- Add `tools/check_role_binding_policy_denial_contract.py`, extend the risk-flag registry with `role-binding-policy-expired` / `role-binding-policy-consumed`, wire the new check into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_role_binding_policy_denial_contract.py`, `spec/examples/risk.flag.registry.json`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r281

- Decide the remembered-role non-interactive issuance-identity boundary by accepting `adrs/ADR-0141-role-binding-policy-decisions-need-unique-instance-identity.md`, adding `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`, and tightening `spec/intent.role.binding.policy.profile.schema.json` so remembered-role exact-mutation policy decisions now carry `decision_instance_id` instead of letting separately issued single-apply authorizations for the same tuple collapse to the same digest (`spec/intent.role.binding.policy.profile.schema.json`, `spec/examples/intent.role.binding.policy.profile.json`, `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`).
- Reduce archive entropy by threading the unique issuance-identity rule through the remembered-role event/evidence/support/risk/README/juicy-lesson surfaces, so non-interactive role-binding evidence can now distinguish “fresh issuance for the same tuple” from “reused prior authorization” without inventing a broader admin transaction family (`docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`, `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`, `README.md`).
- Add `tools/check_role_binding_policy_instance_identity_contract.py`, wire it into `tools/hygiene.py`, extend the runbook/hygiene guardrails, and regenerate generated discovery/version docs (`tools/check_role_binding_policy_instance_identity_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r280

- Decide the remembered-role policy freshness/consumption boundary by accepting `adrs/ADR-0140-role-binding-policy-decisions-are-short-lived-and-single-apply.md`, adding `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`, and tightening `spec/intent.role.binding.policy.profile.schema.json` so non-interactive remembered-role policy decisions now carry `must_apply_before` plus `max_successful_events = 1` instead of behaving like reusable standing permission (`spec/intent.role.binding.policy.profile.schema.json`, `spec/examples/intent.role.binding.policy.profile.json`, `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`).
- Reduce archive entropy by threading the short-lived single-apply rule through the remembered-role event/evidence/support/risk/README/juicy-lesson surfaces, so support bundles and event review can now distinguish exact mutation tuple from bounded apply window without inventing a broader admin transaction family (`docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`, `README.md`).
- Add `tools/check_role_binding_policy_apply_window_contract.py`, wire it into `tools/hygiene.py`, extend the runbook/hygiene guardrails, add official reference pointers for single-use wrapping and short-lived credentials, and regenerate generated discovery/version docs (`tools/check_role_binding_policy_apply_window_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r279

- Decide the exact-mutation shape for remembered-role policy authority by accepting `adrs/ADR-0139-role-binding-policy-decisions-bind-exact-mutation.md`, adding `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`, and introducing `spec/intent.role.binding.policy.profile.schema.json` plus its canonical example so a joined `policy_decision_digest` now binds the exact host/profile/trigger/binding tuple instead of a vague class of allowed role-binding writes (`spec/intent.role.binding.policy.profile.schema.json`, `spec/examples/intent.role.binding.policy.profile.json`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`).
- Reduce archive entropy by threading the exact-mutation policy-profile rule through the role-binding event/evidence/support/risk/README/juicy-lesson surfaces, so non-interactive role-binding evidence now distinguishes *which policy record* from *which exact mutation tuple* without inventing a separate admin transaction family (`docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`, `README.md`).
- Add `tools/check_role_binding_policy_profile_contract.py`, wire it into `tools/hygiene.py`, extend the runbook/hygiene guardrails, add official reference pointers for exact object-bound admission and default-association XML policy guidance, and regenerate generated discovery/version docs (`tools/check_role_binding_policy_profile_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-18r278

- Decide the remembered-role authority-lane normalization by accepting `adrs/ADR-0138-role-binding-authority-lanes-not-invocation-surfaces.md`, adding `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`, and removing `admin-cli` from `intent.role.binding.event.trigger` so event triggers now name authority/apply lanes while local or remote admin tooling identifies itself in `source.*` and non-interactive writes still compile through `policy.decision` (`spec/intent.role.binding.event.schema.json`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `spec/examples/intent.role.binding.event.policy-reconcile.json`).
- Reduce archive entropy by renumbering the remembered-role juicy-lesson sequence, threading the authority-lane rule through workstation/evidence/risk/readme surfaces, and clarifying that local-admin viability in profile C comes from host-local `policy.decision` rather than a separate trigger dialect (`docs/110-juicy-os-lessons.md`, `docs/410-desktop-viability-checklist.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/266-open-questions-and-risk-register.md`, `README.md`).
- Add `tools/check_role_binding_authority_contract.py`, wire it into `tools/hygiene.py`, extend the runbook/hygiene guardrails, add official reference pointers for policy-managed default associations and admission-style policy separation, and regenerate generated discovery/version docs (`tools/check_role_binding_authority_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r277

- Decide the remembered-role support/import provenance join by accepting `adrs/ADR-0137-role-binding-support-import-join-via-content-import-receipt.md`, adding `docs/547-role-binding-support-import-join-via-content-import-receipt.md`, and extending `intent.role.binding.event` with `import_receipt_digest` so `trigger = support-import` now points back to the exact typed `content.import.receipt` that produced or attempted the mutation instead of restore-log folklore (`spec/intent.role.binding.event.schema.json`, `spec/intent.role.binding.event.support-import.schema.json`, `spec/examples/intent.role.binding.event.support-import.json`).
- Reduce archive entropy by adding explicit remembered-role event subtype schemas for `policy-reconcile`, `support-import`, and stale-write denial, eliminating the old unmatched-example warnings while keeping the subtype surface small and explicit (`spec/intent.role.binding.event.policy-reconcile.schema.json`, `spec/intent.role.binding.event.support-import.schema.json`, `spec/intent.role.binding.event.write-denied.precondition.schema.json`, `tools/validate_spec_examples.py`).
- Add `tools/check_role_binding_import_contract.py`, wire it into `tools/hygiene.py`, refresh the runbook/hygiene guardrails, and regenerate generated discovery/version docs (`tools/check_role_binding_import_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r276

- Decide the remembered-role stale-write rule by accepting `adrs/ADR-0136-role-binding-diff-precondition-and-conflict-denial.md`, adding `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`, and extending `intent.role.binding.event` with `reason_code` plus `observed_binding` so `intent.role.binding.diff.from_binding.digest` now acts as the mutation precondition and stale writes leave typed `precondition-failed` evidence instead of silently rebasing (`spec/intent.role.binding.event.schema.json`, `spec/examples/intent.role.binding.event.write-denied.precondition.json`).
- Tighten the remembered-role workstation/evidence/support/profile wiring so interactive and non-interactive role-binding changes now share one compare-and-swap rule across desktop viability, host/AppVM boundary, event/support surfaces, approval posture, risk register, juicy lessons, README, and curated references (`docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/410-desktop-viability-checklist.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/474-high-risk-approval-posture-by-profile.md`, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_role_binding_precondition_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_role_binding_precondition_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r275

- Decide the non-interactive authority join for remembered role/default mutations by accepting `adrs/ADR-0135-role-binding-policy-decision-join-for-noninteractive-mutations.md`, adding `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, and extending `intent.role.binding.event` with `policy_decision_digest` so `policy-reconcile` changes now point at the exact existing `policy.decision` record that authorized them instead of inheriting workstation prompts or daemon folklore (`spec/intent.role.binding.event.schema.json`, `spec/examples/intent.role.binding.event.policy-reconcile.json`).
- Tighten the remembered-role evidence/support/profile wiring so snapshot + diff + event now has an explicit non-interactive policy lane alongside the interactive consent lane across the workstation boundary, evidence spine, support bundles, approval posture, risk register, runbook, juicy lessons, README, and curated references (`docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/410-desktop-viability-checklist.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/474-high-risk-approval-posture-by-profile.md`, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_role_binding_policy_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_role_binding_policy_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r274

- Decide the interactive workstation authority lane for remembered role/default changes by accepting `adrs/ADR-0134-role-binding-consent-lane-for-interactive-workstation-mutations.md`, adding `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`, and introducing constrained `intent.role.binding` consent request/receipt profiles so trusted-settings UI changes now reuse the generic consent substrate with secure-attention prompts instead of drifting into unreceipted settings writes (`spec/intent.role.binding.consent.request.profile.schema.json`, `spec/intent.role.binding.consent.receipt.profile.schema.json`, `spec/examples/intent.role.binding.consent.request.profile.json`, `spec/examples/intent.role.binding.consent.receipt.profile.json`).
- Tighten the remembered-role evidence chain so `intent.role.binding.event` can now join back to interactive approval evidence through `consent_receipt_digest`, and thread that approval boundary through the workstation, consent, support-bundle, evidence-spine, risk, runbook, juicy-lesson, and README surfaces (`spec/intent.role.binding.event.schema.json`, `spec/examples/intent.role.binding.event.json`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/256-consent-ux-contract.md`, `docs/410-desktop-viability-checklist.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/474-high-risk-approval-posture-by-profile.md`, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_workstation_role_binding_consent_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_workstation_role_binding_consent_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r273

- Decide the remembered-role/default durable mutation trace by accepting `adrs/ADR-0133-role-binding-event-as-durable-mutation-evidence.md`, adding `docs/543-role-binding-event-as-durable-mutation-evidence.md`, and introducing `intent.role.binding.event` so trusted settings/admin changes to browsing/communications role ownership now leave a typed event-journal and support-bundle trail instead of shell-history or desktop-settings folklore (`spec/intent.role.binding.event.schema.json`, `spec/examples/intent.role.binding.event.json`).
- Tighten the workstation/evidence/support-bundle wiring so remembered-role/default changes now compile to a stable snapshot-plus-diff-plus-event model across structured event logs, incident bundles, desktop viability, host/AppVM boundary, risk, runbook, juicy lessons, and README surfaces (`docs/215-structured-event-log-as-evidence.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/410-desktop-viability-checklist.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, `docs/542-role-binding-diff-as-review-surface.md`, `docs/543-role-binding-event-as-durable-mutation-evidence.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_workstation_role_binding_event_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_workstation_role_binding_event_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r272

- Decide the remembered-role/default drift review surface by accepting `adrs/ADR-0132-role-binding-diff-as-review-surface.md`, adding `docs/542-role-binding-diff-as-review-surface.md`, and introducing `intent.role.binding.diff` so trusted settings/admin changes to browsing/communications role ownership now review as compact snapshot-to-snapshot posture diffs instead of desktop-registry or settings-blob folklore (`spec/intent.role.binding.diff.schema.json`, `spec/examples/intent.role.binding.diff.json`).
- Tighten the workstation/evidence/diff-registry wiring so `intent.role.binding.diff` is now attached to the same review funnel as other posture diffs and remembered-role changes compile to a stable snapshot-plus-diff model across desktop viability, host/AppVM boundary, drift bundles, evidence spine, risk, runbook, juicy lessons, and README surfaces (`docs/229-evidence-spine-overview.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/410-desktop-viability-checklist.md`, `docs/430-diff-surface-registry.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, `docs/542-role-binding-diff-as-review-surface.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/32-curated-references.md`, `docs/00-index.md`).
- Add `tools/check_workstation_role_binding_diff_contract.py`, wire it into `tools/hygiene.py`, refresh the runbook/hygiene guardrails, and regenerate generated discovery/version docs (`tools/check_workstation_role_binding_diff_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r271

- Decide the workstation remembered-role/default state boundary by accepting `adrs/ADR-0131-workstation-role-slot-bindings-as-typed-state-boundary.md`, adding `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, and introducing `intent.role.binding` with a deliberately small role/target vocabulary so profile B now keeps remembered `browsing` / `communications` targets in typed host-owned state instead of ambient desktop registries (`spec/intent.role.binding.schema.json`, `spec/examples/intent.role.binding.json`).
- Tighten the intent-routing/workstation evidence wiring so allow-path `intent.route.receipt` now carries `role_binding_digest`, and thread that remembered-state boundary through portal/desktop/risk/runbook/README surfaces (`spec/intent.route.receipt.schema.json`, `spec/examples/intent.route.receipt.json`, `docs/179-portals-and-powerbox.md`, `docs/199-intent-routing-and-plumbing.md`, `docs/410-desktop-viability-checklist.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_workstation_role_binding_contract.py`, fix `tools/gen_context_pack.py` so must-read extraction keeps only real repo paths, wire the new guardrail into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_workstation_role_binding_contract.py`, `tools/gen_context_pack.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r270

- Decide the workstation role-bound chooser/default-app floor by accepting `adrs/ADR-0130-workstation-role-bound-intent-targets-and-chooser-floor.md` and adding `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`, so profile B now resolves cross-compartment URI handling through trusted host-managed target roles, limits chooser scope to pre-enrolled targets or bounded disposable/persistent variants of the same role, and keeps first-open prompts from silently rewriting global defaults from untrusted context.
- Tighten the intent-routing/workstation/risk/runbook/reference wiring and extend `intent.route.receipt` with `target_role` plus `resolution_mode` (`role-default`, `trusted-chooser`, `policy-pinned`) so route evidence explains both *which handler ran* and *how the target was selected* (`docs/199-intent-routing-and-plumbing.md`, `docs/179-portals-and-powerbox.md`, `docs/410-desktop-viability-checklist.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/539-workstation-intent-routed-uri-opening-floor.md`, `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `spec/intent.route.receipt.schema.json`, `spec/examples/intent.request.json`, `spec/examples/intent.route.receipt.json`, `docs/00-index.md`).
- Add `tools/check_workstation_intent_role_boundary.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_workstation_intent_role_boundary.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r269

- Decide the workstation cross-domain data-transfer floor by accepting `adrs/ADR-0128-workstation-cross-domain-datatransfer-floor.md`, adding `docs/538-workstation-cross-domain-datatransfer-floor.md`, and tightening `ui.datatransfer` so profile B now treats clipboard/file movement as an explicit brokered lane with **no ambient shared cross-domain clipboard**, **single-delivery by default**, and **no gesture-native cross-domain drag&drop requirement** in the baseline workstation floor (`spec/ui.datatransfer.grant.schema.json`, `spec/ui.datatransfer.receipt.schema.json`, `spec/examples/ui.datatransfer.grant.json`, `spec/examples/ui.datatransfer.receipt.json`).
- Decide the workstation URI-opening floor by accepting `adrs/ADR-0129-workstation-intent-routed-uri-opening-floor.md` and adding `docs/539-workstation-intent-routed-uri-opening-floor.md`, so profile B now treats cross-compartment URI opening as an explicit intent-routing act, keeps the trusted host from becoming the default renderer for untrusted `http` / `https`, routes `http` / `https` into a designated browsing compartment, routes `mailto` into a designated communications compartment, and keeps `file://` out of the cross-domain URI lane.
- Tighten the workstation portal/desktop/risk/runbook/reference wiring and add `tools/check_workstation_datatransfer_boundary.py` plus `tools/check_workstation_uri_open_boundary.py`, then regenerate generated discovery/version docs (`docs/179-portals-and-powerbox.md`, `docs/199-intent-routing-and-plumbing.md`, `docs/205-data-transfer-portals-clipboard-and-dnd.md`, `docs/410-desktop-viability-checklist.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/538-workstation-cross-domain-datatransfer-floor.md`, `docs/539-workstation-intent-routed-uri-opening-floor.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`, `tools/check_workstation_datatransfer_boundary.py`, `tools/check_workstation_uri_open_boundary.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## New in 2026-03-17r266

- Decide the workstation GUI transport floor by accepting `adrs/ADR-0127-workstation-remoted-session-surface-boundary.md` and adding `docs/537-workstation-remoted-session-surface-boundary.md`, so profile B now treats a labeled remoted session surface as the baseline GUI crossing, prefers small-role or single-app AppVMs for ergonomics, and defers seamless host-native per-window guest integration to a later bounded lane instead of making it a hidden requirement for workstation viability.
- Tighten the workstation graphics/desktop/risk/runbook wiring so the display boundary now points at the same session-surface-first decision instead of treating remoted windows and whole-session remoting as equivalent baseline answers (`docs/536-workstation-display-composition-and-gpu-boundary.md`, `docs/410-desktop-viability-checklist.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_workstation_session_surface_boundary.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_workstation_session_surface_boundary.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r265

- Decide the workstation display/GPU boundary by accepting `adrs/ADR-0126-workstation-display-composition-and-gpu-boundary.md` and adding `docs/536-workstation-display-composition-and-gpu-boundary.md`, so profile B now keeps trusted composition on the host, treats remoted guest windows/surfaces as the baseline GUI crossing, accepts software-rendered or simple 2D guest output as the viability floor, and keeps ambient host X11/DRM/render-node authority plus direct guest GPU passthrough out of the ordinary workstation lane.
- Tighten the workstation/device/risk/runbook/reference wiring so desktop viability, host/AppVM boundary docs, and device-authority posture now point at the same host-owned-composition + software-first-remoting decision instead of leaving graphics as an ambient exception (`docs/410-desktop-viability-checklist.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/476-device-authority-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_workstation_graphics_boundary.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_workstation_graphics_boundary.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r264

- Decide the hardware support qualification target-scope boundary by accepting `adrs/ADR-0125-hardware-support-qualification-target-scope-boundary.md`, adding `docs/535-hardware-support-qualification-target-scope-boundary.md`, and tightening the support lane so support targets now carry `release_train`, positive claims now publish `qualification.target_binding`, and proof can no longer silently float across release trains or boot-manifest lineages (`spec/hw.support.matrix.schema.json`, `spec/hw.support.qualification.profile.schema.json`, `spec/hw.support.qualification.receipt.schema.json`, `spec/hw.compat.report.schema.json`, `spec/examples/hw.support.matrix.json`, `spec/examples/hw.support.qualification.profile.json`, `spec/examples/hw.support.qualification.receipt.json`, `spec/examples/hw.compat.report.json`).
- Tighten the hardware compatibility/workstation/profile/risk/runbook wiring so `hw.compat.report` can emit `qualification-target-mismatch`, surface `matched_target_binding` plus `target_scope_state`, and keep workstation trusted-UI support honest when a proof only applies to an older train (`docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/410-desktop-viability-checklist.md`, `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`, `docs/529-hardware-support-promotion-and-qualification-boundary.md`, `docs/530-hardware-support-qualification-receipt-boundary.md`, `docs/531-hardware-support-qualification-profile-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_hw_support_qualification_target_scope_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_hw_support_qualification_target_scope_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r263

- Decide the hardware support conditions / known-limitations boundary by accepting `adrs/ADR-0124-hardware-support-conditions-and-known-limitations-boundary.md`, adding `docs/534-hardware-support-conditions-and-known-limitations-boundary.md`, and tightening `hw.support.matrix` so non-fully-supported entries now publish typed `conditions[]` with stable `condition_id`, `reason_code`, and `required_posture` instead of caveat prose (`spec/hw.support.matrix.schema.json`, `spec/examples/hw.support.matrix.json`).
- Tighten the qualification-receipt and compatibility-report wiring so non-fully-supported claims snapshot `support_claim.condition_ids`, preflight can surface `matched_condition_ids`, and `hw.compat.report` can emit `support-condition-triggered` when a published caveat/prerequisite participated in the outcome (`spec/hw.support.qualification.receipt.schema.json`, `spec/examples/hw.support.qualification.receipt.json`, `spec/hw.compat.report.schema.json`, `spec/examples/hw.compat.report.json`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/410-desktop-viability-checklist.md`, `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/529-hardware-support-promotion-and-qualification-boundary.md`, `docs/530-hardware-support-qualification-receipt-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_hw_support_conditions_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_hw_support_conditions_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r262

- Decide the hardware support qualification-status boundary by accepting `adrs/ADR-0123-hardware-support-qualification-status-boundary.md`, adding `docs/533-hardware-support-qualification-status-boundary.md`, and tightening `hw.support.qualification.receipt` so `decision.status` now has operational semantics with required `status_effective_at`, typed `reason_code`, and `replacement_receipt_digest` for supersession instead of leaving lifecycle state as unused schema vocabulary (`spec/hw.support.qualification.receipt.schema.json`, `spec/examples/hw.support.qualification.receipt.json`).
- Tighten the hardware compatibility/workstation/promotion/risk/runbook wiring so current positive support claims must point at an `accepted` receipt, and `hw.compat.report` can now distinguish `qualification-superseded` / `qualification-revoked` from ordinary `qualification-stale` support drift (`spec/hw.compat.report.schema.json`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/410-desktop-viability-checklist.md`, `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/529-hardware-support-promotion-and-qualification-boundary.md`, `docs/530-hardware-support-qualification-receipt-boundary.md`, `docs/531-hardware-support-qualification-profile-boundary.md`, `docs/532-hardware-support-qualification-freshness-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_hw_support_qualification_status_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_hw_support_qualification_status_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-17r261

- Decide the hardware support qualification-freshness boundary by accepting `adrs/ADR-0122-hardware-support-qualification-freshness-boundary.md`, adding `docs/532-hardware-support-qualification-freshness-boundary.md`, and tightening the hardware support lane so `hw.support.qualification.profile` now defines `freshness.max_age_days_by_stage` / `reverify_on`, while `hw.support.qualification.receipt` carries concrete `fresh_until` bounds instead of leaving “recently verified” as support-team folklore (`spec/hw.support.qualification.profile.schema.json`, `spec/examples/hw.support.qualification.profile.json`, `spec/hw.support.qualification.receipt.schema.json`, `spec/examples/hw.support.qualification.receipt.json`).
- Tighten the hardware compatibility/workstation/promotion/risk/runbook wiring so `hw.compat.report` can emit `qualification-stale`, workstation consent can explain stale support evidence, and matched support claims now carry typed freshness semantics instead of vague timestamps (`spec/hw.compat.report.schema.json`, `spec/examples/hw.compat.report.json`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/410-desktop-viability-checklist.md`, `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/529-hardware-support-promotion-and-qualification-boundary.md`, `docs/530-hardware-support-qualification-receipt-boundary.md`, `docs/531-hardware-support-qualification-profile-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_hw_support_qualification_freshness_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_hw_support_qualification_freshness_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-16r260

- Decide the hardware support qualification-profile boundary by accepting `adrs/ADR-0121-hardware-support-qualification-profile-boundary.md`, adding `docs/531-hardware-support-qualification-profile-boundary.md`, introducing `spec/hw.support.qualification.profile.schema.json`, and tightening the hardware support lane so positive `hw.support.matrix` claims now carry `qualification.profile_digest` in addition to `qualification.receipt_digest`, keeping support claims bound to both a typed standard and a typed proof (`spec/hw.support.matrix.schema.json`, `spec/examples/hw.support.matrix.json`, `spec/hw.support.qualification.profile.schema.json`, `spec/examples/hw.support.qualification.profile.json`, `spec/hw.support.qualification.receipt.schema.json`, `spec/examples/hw.support.qualification.receipt.json`).
- Tighten the receipt/example/workstation/profile/risk wiring so `hw.support.qualification.receipt` now records `check_results[]`, receipt evidence can explicitly say `boot` / `suspend-resume`, and support promotion can no longer depend on lab-specific playlists or remembered test steps (`docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/410-desktop-viability-checklist.md`, `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`, `docs/529-hardware-support-promotion-and-qualification-boundary.md`, `docs/530-hardware-support-qualification-receipt-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_hw_support_qualification_profile_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_hw_support_qualification_profile_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-16r259

- Decide the hardware support qualification-receipt boundary by accepting `adrs/ADR-0120-hardware-support-qualification-receipt-boundary.md`, adding `docs/530-hardware-support-qualification-receipt-boundary.md`, introducing `spec/hw.support.qualification.receipt.schema.json`, and tightening `hw.support.matrix` so positive support claims now carry `qualification.receipt_digest` instead of leaving the real proof in ticket systems or lab folklore (`spec/hw.support.matrix.schema.json`, `spec/examples/hw.support.matrix.json`, `spec/hw.support.qualification.receipt.schema.json`, `spec/examples/hw.support.qualification.receipt.json`).
- Tighten the existing hardware compatibility/workstation/profile/risk wiring so target-specific gating can surface `matched_qualification_receipt_digests` and B/D trusted-UI or support bundles can point at the exact typed evidence object behind a matched support claim (`spec/hw.compat.report.schema.json`, `spec/examples/hw.compat.report.json`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/410-desktop-viability-checklist.md`, `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`, `docs/529-hardware-support-promotion-and-qualification-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_hw_support_qualification_receipt_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_hw_support_qualification_receipt_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-16r258

- Decide the hardware support-promotion boundary by accepting `adrs/ADR-0119-hardware-support-promotion-and-qualification-boundary.md`, adding `docs/529-hardware-support-promotion-and-qualification-boundary.md`, and tightening `hw.support.matrix` so positive support claims now carry a typed `qualification` summary (`stage`, `verified_roles`, `evidence_floor`, `regression_policy`, `last_verified_at`) instead of letting `supported` / `conditional` / `canary-only` degrade into release-note folklore (`spec/hw.support.matrix.schema.json`, `spec/examples/hw.support.matrix.json`).
- Tighten the hardware compatibility/workstation/runbook/risk wiring around that promotion boundary so B/D trusted-UI and bundled-support claims now require explicit `rollback-or-recovery` / `trusted-ui-basic` qualification floor where appropriate, and the archive now points readers at one typed answer for how support labels graduate across release trains (`docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/410-desktop-viability-checklist.md`, `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_hw_support_promotion_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_hw_support_promotion_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-16r257

- Decide the hardware support/admission catalog boundary by accepting `adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md`, adding `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`, and introducing a native `hw.support.matrix` schema/example so approved-hardware claims can travel as digest-bound release/reset catalogs keyed by hardware-class summaries instead of spreadsheets, per-host allowlists, or support folklore (`spec/hw.support.matrix.schema.json`, `spec/examples/hw.support.matrix.json`).
- Tighten the existing `hw.compat.report` shape plus the hardware/workstation docs so compatibility preflight can now record explicit support-matrix join state and emit `support-matrix-miss`, `trusted-ui-floor-risk`, and `recovery-path-missing` instead of hiding support/admission decisions in notes (`spec/hw.compat.report.schema.json`, `spec/examples/hw.compat.report.json`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `docs/410-desktop-viability-checklist.md`, `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_hw_support_matrix_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_hw_support_matrix_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-16r256

- Decide the lazy-mount authority / fallback / evidence boundary by accepting `adrs/ADR-0117-verified-lazy-tree-mount-materialization-and-evidence-boundary.md`, adding `docs/527-verified-lazy-tree-mount-materialization-and-evidence-boundary.md`, and tightening the existing `tree.mount.plan` / `tree.mount.receipt` shapes so verified tree projection now states `materialize` / `prefetch` / `lazy`, explicit fallback posture, and explicit fetch-evidence scope instead of letting backend magic or silent downgrade become deployment folklore (`spec/tree.mount.plan.schema.json`, `spec/tree.mount.receipt.schema.json`, `spec/examples/tree.mount.plan.json`, `spec/examples/tree.mount.receipt.json`).
- Tighten the lazy-mount lesson, distribution references, runbook, juicy-lesson, risk-register, README, and archive-map docs around that boundary so lazy projection stays a reviewable transport lane, ordinary evidence stays digest/summary-first, and stronger path-level fetch tracing remains explicit rather than ambient (`docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`, `docs/119-casync-cvmfs-distribution.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/266-open-questions-and-risk-register.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_tree_mount_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_tree_mount_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-16r255

- Decide the base-system authority boundary by accepting `adrs/ADR-0116-derived-base-sets-and-pkgbase-adapter-boundary.md`, adding `docs/526-derived-base-sets-and-pkgbase-adapter-boundary.md`, and introducing a native `base.set` schema/example so DeriveBSD now treats native `base.set` artifacts as canonical while keeping the v0 split intentionally small (`kernel`, `userland`, `toolchain`) instead of letting `pkgbase` become deployment authority (`spec/base.set.schema.json`, `spec/examples/base.set.json`).
- Tighten the pkgbase lesson, RFC-0079, runbook, juicy-lesson, risk-register, curated-reference, README, and archive-map docs around that boundary so A–D now share one derivation-first base story and patchsets / host generations stay bound to `base.set` digests rather than package-manager folklore (`docs/111-packaged-base-pkgbase.md`, `rfcs/RFC-0079-packaged-base-and-sets.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/266-open-questions-and-risk-register.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_base_set_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_base_set_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r254

- Keep later stronger packet-capture evidence checks metadata-first by accepting `adrs/ADR-0115-packet-capture-strong-export-remote-reverification-boundary.md`, adding `docs/525-packet-capture-strong-export-remote-reverification-boundary.md`, and introducing generic/packet transport reverification receipts plus canonical stronger packet examples so follow-up evidence re-checks join the computed export+acceptance receipts and keep `reverification.body_downloaded = false` instead of re-downloading packet bytes or trusting portal screenshots (`spec/transport.reverification.receipt.schema.json`, `spec/packet.capture.export.transport.reverification.receipt.profile.schema.json`, `spec/examples/transport.reverification.receipt.json`, `spec/examples/packet.capture.export.transport.reverification.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, support-handoff, export-posture, risk-register, hygiene, runbook, juicy-lesson, curated-reference, README, and archive-map docs around that remote-reverification boundary so later stronger `packet.capture.normalized` follow-up now uses typed metadata-only `transport.reverification.receipt` evidence and preserves the same accepted remote validator / protection posture / locator (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`, `docs/525-packet-capture-strong-export-remote-reverification-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_reverification_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_reverification_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r253

- Keep stronger packet-capture raw-byte export discoverable after handoff by accepting `adrs/ADR-0114-packet-capture-strong-export-remote-locator-continuity-boundary.md`, adding `docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`, and tightening the transport/transport-acceptance/export schemas plus canonical stronger packet-export examples so `result.remote_locator`, `acceptance.remote_locator`, and `adapter.remote_locator` stay aligned instead of leaving later evidence retrieval to portal folklore (`spec/transport.receipt.schema.json`, `spec/transport.acceptance.receipt.schema.json`, `spec/export.receipt.schema.json`, `spec/packet.capture.export.transport.receipt.profile.schema.json`, `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, `spec/packet.capture.export.receipt.profile.schema.json`, `spec/examples/packet.capture.export.transport.receipt.profile.json`, `spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, support-handoff, export-posture, risk-register, hygiene, runbook, juicy-lesson, README, and archive-map docs around that remote-locator boundary so stronger `packet.capture.normalized` handoff now preserves one typed recipient-side locator for later retrieval/review instead of leaving operators to portal folklore (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`, `docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_remote_locator_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_remote_locator_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r252

- Keep stronger packet-capture raw-byte export honest about recipient-side durability by accepting `adrs/ADR-0113-packet-capture-strong-export-remote-protection-posture-boundary.md`, adding `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`, and tightening the transport-acceptance/export schemas plus canonical stronger packet-export examples so `acceptance.remote_protection` and `adapter.remote_protection` stay aligned instead of letting any recipient-accepted upload quietly count as durable evidence (`spec/transport.acceptance.receipt.schema.json`, `spec/export.receipt.schema.json`, `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, `spec/packet.capture.export.receipt.profile.schema.json`, `spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, support-handoff, export-posture, risk-register, hygiene, runbook, juicy-lesson, curated-reference, README, and archive-map docs around that remote-protection boundary so stronger `packet.capture.normalized` handoff now names the recipient-side overwrite/delete-resistance posture instead of treating acceptance alone as a durable-evidence claim (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`, `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_remote_protection_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_remote_protection_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r251

- Keep stronger packet-capture raw-byte export on one stable remote representation/version validator by accepting `adrs/ADR-0112-packet-capture-strong-export-remote-validator-continuity-boundary.md`, adding `docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`, and tightening the transport/acceptance/export schemas plus canonical stronger packet-export examples so `result.remote_validator`, `acceptance.remote_validator`, and `adapter.remote_validator` stay aligned instead of letting the proof chain collapse back to object id alone (`spec/transport.receipt.schema.json`, `spec/transport.acceptance.receipt.schema.json`, `spec/export.receipt.schema.json`, `spec/packet.capture.export.transport.receipt.profile.schema.json`, `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, `spec/packet.capture.export.receipt.profile.schema.json`, `spec/examples/packet.capture.export.transport.receipt.profile.json`, `spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, support-handoff, export-posture, risk-register, hygiene, runbook, juicy-lesson, README, and archive-map docs around that remote-validator boundary so stronger `packet.capture.normalized` handoff now preserves the strongest remote representation/version token the adapter can see instead of treating one remote object id as the whole story (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`, `docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_remote_validator_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_remote_validator_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r250

- Keep stronger packet-capture raw-byte export on one stable remote object id by accepting `adrs/ADR-0111-packet-capture-strong-export-remote-object-continuity-boundary.md`, adding `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`, and tightening the packet-capture export receipt profile/example so canonical stronger export now requires `adapter.remote_id` and keeps it aligned with transport/acceptance object references (`spec/packet.capture.export.receipt.profile.schema.json`, `spec/examples/packet.capture.export.receipt.profile.json`, `spec/examples/packet.capture.export.transport.receipt.profile.json`, `spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, export-posture, support-handoff, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that remote-object continuity boundary so stronger `packet.capture.normalized` handoff now stays on the same remote object identifier all the way through transport, recipient acceptance, and final export evidence instead of treating “some object in CASE-8841” as good enough (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`, `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`, `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`, `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_remote_object_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_remote_object_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r249

- Keep stronger packet-capture raw-byte export recipient acceptance about the exact accepted bytes by accepting `adrs/ADR-0110-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`, adding `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`, and tightening the packet-capture transport-acceptance profile/example so stronger recipient acceptance now requires `acceptance.remote_artifact_digest` rather than a remote reference alone (`spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, `spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, export-posture, support-handoff, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that remote-digest boundary so stronger `packet.capture.normalized` handoff now stays on the same normalized digest all the way through recipient-side acceptance instead of treating “accepted something in CASE-8841” as good enough (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/517-packet-capture-strong-export-digest-stability-boundary.md`, `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`, `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`, `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_recipient_digest_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_recipient_digest_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r248

- Keep stronger packet-capture raw-byte export recipient-bound by accepting `adrs/ADR-0109-packet-capture-strong-export-destination-bound-approval-boundary.md`, adding `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`, and tightening the packet-capture export consent request / export receipt shapes so stronger approval now binds `action.destination`, packet-capture export receipts can carry destination `domain`, and the canonical stronger packet-export examples keep the same approved ticket/recipient/domain tuple instead of approving bytes in the abstract (`spec/consent.request.schema.json`, `spec/export.receipt.schema.json`, `spec/packet.capture.export.consent.request.profile.schema.json`, `spec/examples/packet.capture.export.consent.request.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, consent, transport, evidence-spine, export-posture, support-handoff, high-risk-approval, risk-register, hygiene, runbook, juicy-lesson, curated-reference, and archive-map docs around that recipient-binding boundary so `consent.request.action.destination`, `transport.receipt.destination`, `transport.acceptance.receipt.recipient`, and `export.receipt.destination` now have to keep the same approved destination tuple for stronger `packet.capture.normalized` export (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/256-consent-ux-contract.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/474-high-risk-approval-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`, `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_destination_binding_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_destination_binding_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r247

- Keep final stronger packet-capture raw-byte export distinct from mere send success by accepting `adrs/ADR-0108-packet-capture-strong-export-recipient-acceptance-boundary.md`, adding `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`, adding `spec/transport.acceptance.receipt.schema.json` plus `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, and tightening the canonical stronger packet-export examples so final `packet.capture.normalized` export now carries `delivery_state = recipient-accepted` plus `transport_acceptance_receipt_digest` instead of stopping at transport success (`spec/transport.acceptance.receipt.schema.json`, `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json`, `spec/examples/transport.acceptance.receipt.json`, `spec/examples/packet.capture.export.transport.acceptance.receipt.profile.json`, `spec/packet.capture.export.receipt.profile.schema.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, export-posture, support-handoff, risk-register, hygiene, runbook, juicy-lesson, curated-reference, and archive-map docs around that closure boundary so stronger export now joins `transport.acceptance.receipt`, keeps the same normalized digest through recipient acceptance, and only counts as final once the recipient-side lane accepted the artifact (`docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/516-packet-capture-strong-export-transport-boundary.md`, `docs/517-packet-capture-strong-export-digest-stability-boundary.md`, `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_acceptance_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_acceptance_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r246

- Keep stronger packet-capture raw-byte export digest-stable by accepting `adrs/ADR-0107-packet-capture-strong-export-digest-stability-boundary.md`, adding `docs/517-packet-capture-strong-export-digest-stability-boundary.md`, and tightening the canonical packet-capture stronger-export examples so redaction / import / approval / transport / export receipts now all line up on the same normalized artifact digest instead of disconnected placeholders (`spec/examples/redaction.receipt.packet-capture.json`, `spec/examples/content.import.packet-capture.receipt.json`, `spec/examples/packet.capture.export.consent.request.profile.json`, `spec/examples/packet.capture.export.consent.receipt.profile.json`, `spec/examples/packet.capture.export.transport.receipt.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the packet-capture export, transport, evidence-spine, export-posture, risk-register, hygiene, runbook, juicy-lesson, curated-reference, and archive-map docs around that boundary so `consent.request.action.artifact_digest`, `transport.receipt.artifact.digest`, and `export.receipt.artifact.digest` now have to keep the same normalized digest for stronger `packet.capture.normalized` export (`docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/229-evidence-spine-overview.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/516-packet-capture-strong-export-transport-boundary.md`, `docs/517-packet-capture-strong-export-digest-stability-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_digest_stability_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_digest_stability_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r245

- Keep completed stronger packet-capture raw-byte export on the generic transport lane by accepting `adrs/ADR-0106-packet-capture-strong-export-transport-boundary.md`, adding `docs/516-packet-capture-strong-export-transport-boundary.md`, and adding a constrained packet-capture export transport receipt profile/example so completed `packet.capture.normalized` handoff stays transport-bound instead of ending at local-file staging (`spec/packet.capture.export.transport.receipt.profile.schema.json`, `spec/examples/packet.capture.export.transport.receipt.profile.json`).
- Tighten the packet-capture export, transport, support-handoff, evidence-spine, export-posture, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that boundary so stronger `packet.capture.normalized` export now requires `transport_receipt_digest`, rejects `destination.type = file` as completed handoff, and keeps a local save subordinate to the actual receipted transport act (`spec/packet.capture.export.receipt.profile.schema.json`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`, `docs/229-evidence-spine-overview.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/516-packet-capture-strong-export-transport-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_transport_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_transport_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## New in 2026-03-09r244

- Keep stronger packet-capture raw-byte export on the generic consent lane by accepting `adrs/ADR-0105-packet-capture-strong-export-approval-evidence-boundary.md`, adding `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, and adding constrained packet-capture export consent request/receipt profile schemas/examples so stronger `packet.capture.normalized` export binds policy/artifact/lease state, requires secure attention, and uses explicit non-`auto` approval evidence (`spec/packet.capture.export.consent.request.profile.schema.json`, `spec/packet.capture.export.consent.receipt.profile.schema.json`, `spec/examples/packet.capture.export.consent.request.profile.json`, `spec/examples/packet.capture.export.consent.receipt.profile.json`).
- Tighten the packet-capture export, consent, support-handoff, evidence-spine, export-posture, high-risk-approval, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that boundary so `packet.capture.normalized` export now requires `consent_receipt_digest` and stronger packet raw-byte export cannot collapse into automatic background uploader folklore (`spec/packet.capture.export.receipt.profile.schema.json`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/256-consent-ux-contract.md`, `docs/229-evidence-spine-overview.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/474-high-risk-approval-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `docs/00-index.md`).
- Add `tools/check_packet_capture_export_approval_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_approval_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r243

- Keep stronger packet-capture raw-byte export on the generic export lane by accepting `adrs/ADR-0104-packet-capture-export-proof-chain-and-profile-posture.md`, adding `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, and adding constrained packet-capture export policy/receipt profile schemas/examples so `packet.capture.summary` stays the ordinary export class while `packet.capture.normalized` remains a proof-bound stronger action (`spec/packet.capture.export.policy.profile.schema.json`, `spec/packet.capture.export.receipt.profile.schema.json`, `spec/examples/packet.capture.export.policy.profile.json`, `spec/examples/packet.capture.export.receipt.profile.json`).
- Tighten the export, packet-capture, support-handoff, evidence-spine, export-posture, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that boundary so stronger packet exports carry typed `supporting_evidence` joins back to the session / summary / import / redaction chain instead of collapsing into normalized `.pcapng` folklore (`spec/export.receipt.schema.json`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/229-evidence-spine-overview.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_export_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_export_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## New in 2026-03-09r242

- Make packet-capture participation in support bundles mechanically selectable by accepting `adrs/ADR-0103-packet-capture-evidence-joins-in-incident-bundles.md`, adding `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`, and extending the canonical `incident.bundle` include-knob / includes surfaces so packet troubleshooting now joins bundles through typed session/summary/import/redaction receipt digests instead of drifting into `extra` or raw `.pcapng` payload defaults (`spec/incident.bundle.schema.json`, `spec/examples/incident.bundle.json`, `spec/bundle.plan.schema.json`).
- Tighten the incident-bundle, support-handoff, bundle-plan, evidence-spine, packet-capture, export, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that boundary so bundle tooling carries packet-capture proof joins while raw packet bytes remain a stronger separate export action (`docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_bundle_contract.py`, wire it into `tools/hygiene.py`, and regenerate generated discovery/version docs (`tools/check_packet_capture_bundle_contract.py`, `tools/hygiene.py`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/420-context-pack.md`).

## New in 2026-03-09r241

- Keep packet-capture normalization on the archive-wide deterministic redaction lane by accepting `adrs/ADR-0102-packet-capture-normalization-redaction-receipt-boundary.md`, adding `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, and adding constrained packet-capture redaction transform/receipt schemas/examples so stronger imported captures gain typed normalization proof instead of a tool-side-effect story (`spec/redaction.transform.packet-capture.schema.json`, `spec/redaction.receipt.packet-capture.schema.json`, `spec/examples/redaction.transform.packet-capture.json`, `spec/examples/redaction.receipt.packet-capture.json`).
- Tighten the packet-capture import, redaction, export, incident-bundle, evidence-spine, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that boundary so normalized raw-byte derivatives only become ordinary review/export candidates when the import receipt points at generic redaction evidence ending at `packet-records-only` (`spec/content.import.packet-capture.receipt.schema.json`, `spec/examples/content.import.packet-capture.receipt.json`, `docs/195-deterministic-redaction-transforms.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/266-open-questions-and-risk-register.md`, `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `README.md`).
- Add a lightweight guardrail that keeps packet-capture normalization schemas, examples, and docs aligned so `strip-metadata` cannot drift away from typed `redaction-transform` / `redaction-receipt` proof (`tools/check_packet_capture_normalization_contract.py`, `tools/hygiene.py`).
- Refresh the curated-reference and generated discovery/version surfaces for the packet-capture normalization proof boundary (`docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r240

- Keep stronger packet-capture artifacts on a typed safe-open import lane by accepting `adrs/ADR-0101-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, adding `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, and adding constrained `content.import.*` specialization schemas/examples for packet-capture strong-artifact intake and normalization (`spec/content.import.packet-capture.plan.schema.json`, `spec/content.import.packet-capture.receipt.schema.json`, `spec/examples/content.import.packet-capture.plan.json`, `spec/examples/content.import.packet-capture.receipt.json`).
- Tighten the packet-capture session, summary, export, incident-bundle, evidence-spine, risk-register, hygiene, runbook, juicy-lesson, and archive-map docs around that boundary so foreign or sideband/decryption-bearing captures stay on the safe-open lane and only normalized `packet-records-only` derivatives or `packet.capture.summary` become ordinary promotion/export candidates (`docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`, `docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md`, `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `README.md`).
- Add a lightweight guardrail that keeps the typed packet-capture strong-artifact import schemas, examples, and docs aligned so the official path cannot drift back into host-open `.pcapng` folklore (`tools/check_packet_capture_import_contract.py`, `tools/hygiene.py`).
- Refresh the curated-reference and generated discovery/version surfaces for the typed packet-capture import contract (`docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-09r239

- Keep retained raw packet files subordinate to the typed capture lane by accepting `adrs/ADR-0100-packet-capture-local-artifact-metadata-and-retention-boundary.md`, adding `docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md`, and tightening the canonical `packet.capture.session` / `packet.capture.summary` schemas/examples so local artifacts carry explicit `max_local_retention_seconds`, `metadata_posture`, and `retention_until` state instead of relying on filename/tool folklore.
- Tighten the packet-capture session, summary, export, incident-bundle, evidence-spine, risk-register, runbook, juicy-lesson, hygiene, and archive-map docs around that boundary so Derive-generated raw capture artifacts stay `packet-records-only` by default while stronger sideband/decryption-material cases remain explicit exceptions (`docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`, `docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_artifact_contract.py`, wire it into `tools/hygiene.py`, refresh the curated-reference surface, and regenerate generated discovery/version docs (`tools/check_packet_capture_artifact_contract.py`, `tools/hygiene.py`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## New in 2026-03-08r238

- Keep packet-capture review portable by accepting `adrs/ADR-0099-packet-capture-selector-compiler-boundary.md`, adding `docs/509-packet-capture-selector-compiler-boundary.md`, and introducing the canonical typed `packet.capture.selector` schema/example so `packet.capture.session` carries reviewable capture intent rather than a backend-specific filter string.
- Tighten the packet-capture session, summary, export, incident-bundle, evidence-spine, risk-register, runbook, hygiene, and archive-map docs around that selector/compiler boundary so backend filter expressions remain compiled detail while typed selectors stay authoritative (`docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`, `docs/509-packet-capture-selector-compiler-boundary.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_selector_contract.py`, wire it into `tools/hygiene.py`, refresh the juicy-lesson / curated-reference surface, and regenerate the generated discovery/version surfaces (`tools/check_packet_capture_selector_contract.py`, `tools/hygiene.py`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## New in 2026-03-08r237

- Keep packet capture summary-first without overloading the learned-network lane: accept `adrs/ADR-0098-packet-capture-summary-review-surface-boundary.md`, add `docs/508-packet-capture-summary-review-surface-boundary.md`, and add the canonical `packet.capture.summary` schema/example so bounded capture has its own evidence-only review/export surface instead of borrowing `net-flow-summary`.
- Tighten the packet-capture, export, incident-bundle, evidence-spine, evidence-posture, tracing, risk-register, runbook, hygiene, and archive-map docs around that boundary so `packet.capture.summary` becomes the ordinary handoff artifact while raw packet payload export stays the stronger explicit exception (`docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, `docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/478-evidence-collection-posture-by-profile.md`, `docs/248-tracing-observability-as-evidence.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_summary_contract.py`, wire it into `tools/hygiene.py`, refresh the juicy-lesson / curated-reference surface, and regenerate the generated discovery/version surfaces (`tools/check_packet_capture_summary_contract.py`, `tools/hygiene.py`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## New in 2026-03-08r236

- Make packet capture implementable without normalizing `.pcap` folklore: accept `adrs/ADR-0097-packet-capture-session-and-summary-first-export-boundary.md`, add `docs/507-packet-capture-session-and-summary-first-export-boundary.md`, and add the canonical `packet.capture.session` schema/example so bounded capture is a typed temporary-authority session with summary-first export by default.
- Tighten the raw-packet, export, incident-bundle, evidence-spine, evidence-posture, tracing, risk-register, runbook, hygiene, and archive-map docs around that contract so packet capture stays lease-shaped and raw packet payload export stays an explicit stronger exception (`docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`, `docs/478-evidence-collection-posture-by-profile.md`, `docs/248-tracing-observability-as-evidence.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/00-index.md`, `README.md`).
- Add `tools/check_packet_capture_session_contract.py`, wire it into `tools/hygiene.py`, refresh the juicy-lesson / curated-reference surface, and regenerate the generated discovery/version surfaces (`tools/check_packet_capture_session_contract.py`, `tools/hygiene.py`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).

## New in 2026-03-08r235

- Fix the raw-packet authority boundary as a narrow cross-profile decision: accept `adrs/ADR-0096-packet-capture-raw-sockets-and-fast-packet-io-boundary.md` and add `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, which separates packet capture / raw sockets / fast packet I/O from ordinary app/service networking and keeps netmap/VALE as a default-off explicit dataplane lane.
- Tighten the egress, diagnostics, BPF-risk, netgraph/netmap, device-authority, risk-register, hygiene, and runbook docs around that boundary so DNS evidence and bounded learn/audit do not quietly fall back to packet-capture folklore (`docs/201-network-egress-as-capability.md`, `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`, `docs/384-kernel-extensibility-bpf-and-jit-risk.md`, `docs/400-netgraph-and-netmap-as-derived-network-fabrics.md`, `docs/459-outbound-network-posture-by-profile.md`, `docs/476-device-authority-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Add a lightweight guardrail that keeps packet-capture / raw-packet authority distinct from ordinary networking across the core docs (`tools/check_packet_capture_boundary.py`, `tools/hygiene.py`).
- Refresh the juicy-lesson / curated-reference surface and regenerate discovery/version surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-08r234

- Fix the learn/audit network-policy lane as a bounded convergence contract: accept `adrs/ADR-0095-network-learn-audit-convergence-contract.md` and add `docs/505-network-learn-audit-convergence-contract.md`, which makes learn sessions explicitly time- and event-bounded, keeps `net-flow-summary` evidence-only, and preserves `net-egress-policy` as the only authoritative enforcement surface.
- Tighten the existing learned-network-policy, outbound-network, evidence-spine, risk-register, hygiene, and runbook docs around that contract so “observe first” cannot quietly become a standing permissive mode (`docs/328-learned-network-policies-from-flow-receipts.md`, `docs/459-outbound-network-posture-by-profile.md`, `docs/229-evidence-spine-overview.md`, `docs/266-open-questions-and-risk-register.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Add a typed `net.flow.summary` artifact plus a lightweight guardrail that keeps bounded-session metadata, example digest joins, and doc wiring aligned (`spec/net.flow.summary.schema.json`, `spec/examples/net.flow.summary.json`, `tools/check_learn_net_contract.py`, `tools/hygiene.py`).
- Refresh the juicy-lesson / curated-reference surface with current learn/audit-policy references, then regenerate discovery/version surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-08r233

- Decide the DNS-evidence privacy/explainability boundary without adding a new product-profile knob: accept `adrs/ADR-0094-dns-receipt-detail-and-export-posture-by-profile.md` and add `docs/504-dns-receipt-detail-and-export-posture-by-profile.md`, which makes `net-flow-receipt` the normal export surface, keeps detailed DNS receipts local-first and bounded, and differentiates A–D mainly by how much qname detail may leave the box.
- Tighten the outbound-network, DNS-mediation, product-profile, telemetry-boundary, and risk-register docs so DNS evidence posture is now a compiled consequence of `network_egress` + `evidence` + `evidence_exports` rather than an open-ended implementation folkway (`docs/459-outbound-network-posture-by-profile.md`, `docs/305-dns-mediation-and-hostname-binding.md`, `docs/411-product-profiles-as-compilation-target.md`, `docs/503-telemetry-is-not-a-product-profile-default-boundary.md`, `docs/266-open-questions-and-risk-register.md`, `docs/99-llm-runbook.md`).
- Refresh the juicy-lesson / curated-reference surface with the DNS privacy and qname-minimization research inputs that motivated the narrower posture, then regenerate discovery/version surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-08r232

- Reduce entropy in the product-profile artifact by removing the overlapping `telemetry` default key and explicitly collapsing observability posture onto `evidence`, `evidence_exports`, and `network_egress` instead (`adrs/ADR-0093-no-separate-telemetry-product-profile-key.md`, `docs/503-telemetry-is-not-a-product-profile-default-boundary.md`, `docs/501-product-profile-default-vocabulary-boundary.md`, `spec/product.profile.schema.json`, `spec/examples/product.profiles.json`).
- Tighten the profile core docs and decided risk item so future observability/export work lands on the existing posture surfaces instead of growing a second overlapping review vocabulary (`docs/411-product-profiles-as-compilation-target.md`, `docs/266-open-questions-and-risk-register.md`, `docs/110-juicy-os-lessons.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`).
- Refresh generated discovery/version surfaces and archive maps for the tightened product-profile vocabulary (`docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-08r231

- Turn the official foreign support-bundle intake path into a typed, checkable spec surface by adding constrained specialization schemas for the canonical `content.import.plan` / `content.import.receipt` workflow instead of leaving the path example-only (`spec/content.import.support-bundle.plan.schema.json`, `spec/content.import.support-bundle.receipt.schema.json`, `docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md`, `docs/266-open-questions-and-risk-register.md`).
- Keep that decision narrow by explicitly treating the new support-bundle schemas as constrained shapes of the generic import lane rather than inventing new authority kinds, and wire the boundary through the existing support-bundle docs (`docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `spec/examples/content.import.support-bundle.plan.json`, `spec/examples/content.import.support-bundle.receipt.json`).
- Add a lightweight guardrail that keeps the typed support-bundle intake schemas, examples, and docs aligned so the official path cannot drift back into host-open folklore or example-only ambiguity (`tools/check_support_bundle_import_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`).
- Refresh generated discovery/version surfaces and archive maps for the typed support-bundle intake contract (`docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-08r230

- Fix the product-profile default-key boundary as a checkable contract: accept an ADR that keeps `product.profiles.defaults` a flat symbolic compilation-target map, explicitly allowlists the default-key vocabulary in schema, and keeps structured policy in dedicated specs instead of a second profile options tree (`adrs/ADR-0091-product-profile-default-vocabulary-boundary.md`, `docs/501-product-profile-default-vocabulary-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the profile artifact around that decision by turning `spec/product.profile.schema.json` into an explicit allowlist for the v0 default vocabulary and by wiring the product-profile core doc to the new boundary (`spec/product.profile.schema.json`, `spec/examples/product.profiles.json`, `docs/411-product-profiles-as-compilation-target.md`, `docs/110-juicy-os-lessons.md`).
- Add a lightweight guardrail that mechanically checks alignment across the schema allowlist, the profile example, and the canonical default-key registry doc (`tools/check_profile_default_vocabulary.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh generated discovery/version surfaces and archive maps for the decided profile-vocabulary boundary (`docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

# Index

## New in 2026-03-07r228

- `docs/499-fuzz-target-classes-and-flake-aware-promotion-gate-boundary.md`
- `adrs/ADR-0089-fuzz-target-classes-and-flake-aware-promotion-boundary.md`
- `docs/266-open-questions-and-risk-register.md`
- `docs/274-continuous-fuzzing-farm.md`
- `docs/275-root-cause-certificates-and-bisection.md`
- `docs/166-test-receipts-and-promotion-gates.md`
- `docs/229-evidence-spine-overview.md`
- `docs/411-product-profiles-as-compilation-target.md`
- `docs/98-archive-hygiene.md`
- `docs/99-llm-runbook.md`
- `docs/110-juicy-os-lessons.md`
- `docs/32-curated-references.md`
- `docs/412-product-profile-matrix.md`
- `docs/414-doc-catalog.md`
- `docs/415-risk-register-index.md`
- `docs/418-artifact-index.md`
- `docs/420-context-pack.md`
- `docs/00-index.md`

## New in 2026-03-07r227

- Fix the support-bundle intake boundary as a checkable contract: accept an ADR that keeps foreign support bundles on the safe-open import lane, records the execution boundary in `content.import.plan` / `content.import.receipt`, and stages deeper incident reproduction inside disposable workspaces instead of direct host-open folklore (`adrs/ADR-0088-safe-open-support-bundle-intake-and-repro-boundary.md`, `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the existing content-import lane with a tiny execution contract (`isolation`, `network`, `lifetime`) and canonical support-bundle import examples so timeline-first preview and no-network disposable intake are mechanically representable (`spec/content.import.plan.schema.json`, `spec/content.import.receipt.schema.json`, `spec/examples/content.import.support-bundle.plan.json`, `spec/examples/content.import.support-bundle.receipt.json`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/220-operational-time-travel-debugging.md`, `docs/267-sanitization-portal-and-disposable-sandboxes.md`, `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`).
- Add a lightweight guardrail that mechanically checks the safe-open support-bundle intake join points and prevents drift across schemas, examples, docs, and the decided risk item (`tools/check_safe_open_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`).

## New in 2026-03-07r225

- Make store retention / garbage collection posture a checkable product-shape decision: accept an ADR that keeps retention profile-shaped, separates soft `keep_generations` preference from hard `rollback_floor_generations`, and makes `store.gc.receipt.rollback_coverage` the compact answer to whether cleanup preserved recovery coverage (`adrs/ADR-0086-store-retention-and-gc-posture-by-profile.md`, `docs/496-store-retention-and-gc-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the existing GC lane by extending `store.gc.plan` / `store.gc.receipt` with rollback-floor / rollback-coverage fields, and by reframing roots/pins, boot-environment, profile, and evidence docs so retention preference stops masquerading as a hard safety floor (`spec/store.gc.plan.schema.json`, `spec/store.gc.receipt.schema.json`, `spec/examples/store.gc.plan.json`, `spec/examples/store.gc.receipt.json`, `docs/175-pins-roots-and-garbage-collection.md`, `docs/404-zfs-boot-environments-as-system-generations.md`, `docs/426-store-gc-plans-and-receipts.md`, `docs/229-evidence-spine-overview.md`, `docs/411-product-profiles-as-compilation-target.md`).
- Thread that decision into anti-drift product defaults by adding the stable `store_retention` profile knob plus A/B/C/D notes/invariants, so the archive cannot slide back into silent rollback-loss or hidden cleanup semantics (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`).
- Add a lightweight guardrail that mechanically checks the store-retention join points and prevents drift across product profiles, GC plan/receipt schemas, rollback coverage example wiring, and the core docs (`tools/check_store_gc_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons + curated references with current official Nix GC-roots and OpenZFS hold/bookmark pointers, then regenerate generated discovery surfaces and version stamps (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`).

## New in 2026-03-07r224

- Fix the frontend-authoring boundary as a checkable contract: accept an ADR that keeps compiled canonical JSON Spec/policy objects authoritative, makes `frontend.compile.receipt` explicitly evidence-only, and blesses JSON + HuJSON as the in-tree v0 authoring path while richer frontends remain adapter lanes (`adrs/ADR-0085-frontend-source-compile-receipt-and-canonical-ir-boundary.md`, `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Add a typed schema/example for `frontend.compile.receipt`, plus a canonical HuJSON→`trust-policy` example that binds source/compiler provenance to a real compiled output digest (`spec/frontend.compile.receipt.schema.json`, `spec/examples/frontend.compile.receipt.json`, `spec/examples/trust.policy.hujson`, `spec/examples/trust.policy.json`).
- Reframe the frontend / evaluator / evidence docs so source text stays authoring context, compile evidence stays evidence-only, and the blessed in-tree path remains conservative (`docs/79-derive-spec-frontends.md`, `docs/83-evaluator-minimalism.md`, `docs/149-human-policy-hujson-and-canonicalization.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).
- Add a lightweight guardrail that mechanically checks the frontend compile boundary and prevents schema/example drift across the canonical HuJSON source, compile receipt, and compiled trust-policy example (`tools/check_frontend_compile_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## New in 2026-03-07r223

- Fix the authority-budget boundary as a checkable contract: accept an ADR that keeps `authority.budget` authoritative, makes `authority.budget.check` explicitly evidence-only, and makes `authority.exception` the authoritative timeboxed field-scoped waiver for the generic component-runtime budget lane (`adrs/ADR-0084-authority-budgets-and-exception-boundary.md`, `docs/494-authority-budget-policy-check-and-exception-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the generic authority-budget lane around that decision by adding typed schemas/examples for `authority.budget`, `authority.budget.check`, and `authority.exception`, and by narrowing the canonical v0 dimension set to filesystem / network / devices / trust / observability instead of silently absorbing every privileged lane (`spec/authority.budget.schema.json`, `spec/authority.budget.check.schema.json`, `spec/authority.exception.schema.json`, `spec/examples/authority.budget.json`, `spec/examples/authority.budget.check.json`, `spec/examples/authority.exception.json`).
- Reframe the authority-budget / descriptor / evidence docs so component-runtime least-authority budgets stop overlapping with kernel-mutation, network-topology, firmware, reset, workload-identity, and operator-session authority lanes (`docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/297-component-descriptors-and-compiled-runtime-manifests.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`).
- Add a lightweight guardrail that mechanically checks the authority-budget join points, keeps the v0 dimension set stable, and prevents schema/example drift across budget/check/exception artifacts (`tools/check_authority_budget_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## New in 2026-03-07r222

- Fix the temporary-authority boundary as a checkable contract: accept an ADR that keeps lane-specific grant / lease / session objects authoritative, makes `lease.issue.receipt` and `lease.use.receipt` explicitly evidence-only, and requires `lease.envelope.target` / `lease.issue.receipt.target` to point at the authoritative temporary-authority object rather than a later action receipt (`adrs/ADR-0083-temporary-authority-grant-lease-and-use-boundary.md`, `docs/493-temporary-authority-grant-lease-and-use-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the generic lease lane around that decision by adding `authority_semantics` to `lease.issue.receipt` and `lease.use.receipt`, rewiring the canonical examples so `lease.envelope` + `lease.issue.receipt` point at `portal-grant`, and moving later action evidence to `lease.use.receipt.related` (`spec/lease.envelope.schema.json`, `spec/lease.issue.receipt.schema.json`, `spec/lease.use.receipt.schema.json`, `spec/examples/portal.grant.json`, `spec/examples/lease.envelope.json`, `spec/examples/lease.issue.receipt.json`, `spec/examples/lease.use.receipt.json`, `spec/examples/export.receipt.json`).
- Reframe the lease / evidence docs so grants, lease joins, issuance evidence, use evidence, and later action receipts stop overlapping (`docs/249-lease-registry-and-cross-lane-revocation.md`, `docs/252-lease-envelope-and-cross-lane-joins.md`, `docs/449-lease-issue-and-use-receipts.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Add a lightweight guardrail that mechanically checks the temporary-authority join points and prevents drift across grant/lease/session authority objects, lease envelopes, lease issue receipts, and lease use receipts (`tools/check_lease_authority_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## New in 2026-03-07r221

- Fix attestation result authority as a checkable contract: accept an ADR that keeps `attestation.receipt` explicitly evidence-only, keeps `attestation.admission.policy` as the action→requirement map, and requires authoritative action receipts to summarize attestation decisions via `attestation_verification` instead of treating verifier output as silent authority (`adrs/ADR-0082-attestation-results-evidence-and-admission-issue-boundary.md`, `docs/492-attestation-results-evidence-and-admission-issue-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the attestation-admission lane around that decision by adding `authority_semantics` to `attestation.receipt`, adding `attestation_verification` summaries to `secret-receipt`, `breakglass-receipt`, and `workload-identity-issue-receipt`, and wiring the canonical examples to `attestation.requirement` + `attestation.admission.policy` digests (`spec/attestation.receipt.schema.json`, `spec/secret.receipt.schema.json`, `spec/breakglass.receipt.schema.json`, `spec/workload.identity.issue.receipt.schema.json`, `spec/examples/attestation.requirement.json`, `spec/examples/attestation.admission.policy.json`, `spec/examples/attestation.receipt.json`, `spec/examples/secret.receipt.json`, `spec/examples/breakglass.grant.json`, `spec/examples/breakglass.receipt.json`, `spec/examples/secret.grant.json`, `spec/examples/workload.identity.issue.receipt.json`).
- Reframe the attestation / identity / secrets / recovery docs so verifier evidence, gate policy, and issued authority no longer overlap (`docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/388-remote-attestation-admission-and-enrollment.md`, `docs/181-workload-identity-and-secretless-deploys.md`, `docs/223-secrets-and-key-management-as-evidence.md`, `docs/236-breakglass-and-recovery-mode.md`, `docs/229-evidence-spine-overview.md`, `docs/440-attestation-admission-policy-diff-as-review-surface.md`, `docs/110-juicy-os-lessons.md`).
- Add a lightweight guardrail that mechanically checks the attestation-admission join points and prevents drift across requirements, admission policy, verifier receipts, and consuming authority receipts (`tools/check_attestation_admission_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## New in 2026-03-07r220

- Fix vulnerability verification as a checkable contract: accept an ADR that keeps `vuln.query.receipt` deterministic, makes `vuln-gate-receipt` explicitly evidence-only, and binds the optional vulnerability-verification lane to `release.authority.policy` plus a single `vulnerability_verification` summary on publish receipts (`adrs/ADR-0081-vulnerability-verification-evidence-and-publish-gate-boundary.md`, `docs/491-vulnerability-verification-evidence-and-publish-gate-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the vulnerability lane around that decision by adding `authority_semantics` to `vuln-gate-receipt`, wiring vulnerability-verification requirements into `release.authority.policy`, and collapsing publish-time vulnerability joins into `release.publish.receipt.vulnerability_verification` (`spec/vuln.gate.receipt.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`, `spec/examples/vuln.gate.receipt.json`, `spec/examples/release.authority.policy.json`, `spec/examples/release.publish.receipt.json`).
- Reframe the vulnerability / SBOM / VEX / authority docs so query receipts, gate receipts, and publication authority no longer overlap (`docs/60-vulnerability-intel-and-gates.md`, `docs/338-vulnerability-snapshots-query-receipts-and-openvex.md`, `docs/168-sboms-and-vex-as-evidence.md`, `docs/229-evidence-spine-overview.md`, `docs/260-release-authority-policy-and-key-management.md`, `docs/110-juicy-os-lessons.md`).
- Add a lightweight guardrail that mechanically checks the vulnerability-verification join points and prevents drift across vuln gate policy, query receipts, gate receipts, release authority policy, and publish receipts (`tools/check_vulnerability_verification_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## New in 2026-03-07r219

- Fix witness trust as a checkable contract: accept an ADR that makes `witness.policy` the authoritative roster/quorum/shortfall surface, keeps `log.checkpoint.receipt` evidence-only, and binds witness-policy evaluation to release transparency and release authority without letting monitor config or receipt contents silently redefine trust (`adrs/ADR-0080-witness-policy-and-roster-quorum-boundary.md`, `docs/490-witness-policy-and-roster-quorum-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the transparency lane around that decision by adding typed witness-policy schemas/examples, binding checkpoint receipts to `witness_policy_digest` + `quorum_verdict`, replacing inline witness quorum knobs with `witness_policy_digest` joins in monitor/release authority policy, and extending `release.publish.receipt.transparency_verification` to summarize the pinned witness-policy result (`spec/witness.policy.schema.json`, `spec/examples/witness.policy.json`, `spec/log.checkpoint.receipt.schema.json`, `spec/transparency.monitor.policy.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`, `spec/examples/log.checkpoint.receipt.json`, `spec/examples/transparency.monitor.policy.json`, `spec/examples/transparency.monitor.snapshot.json`, `spec/examples/release.authority.policy.json`, `spec/examples/release.transparency.entry.json`, `spec/examples/release.publish.receipt.json`).
- Reframe the transparency / witness / authority docs so witness networks remain coordination surfaces while witness trust becomes a portable review surface (`docs/257-release-capsules-and-transparency.md`, `docs/259-transparency-monitors-and-witness-gossip.md`, `docs/260-release-authority-policy-and-key-management.md`, `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`, `docs/488-release-transparency-evidence-and-monitor-gate-boundary.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Add a lightweight guardrail that mechanically checks the witness-policy join points and prevents drift across witness policy, checkpoint receipts, monitor policy, release authority policy, and publish receipts (`tools/check_witness_policy_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## New in 2026-03-07r218

- Fix workflow verification as a checkable contract: accept an ADR that keeps `supplychain-layout-policy` as a workflow-constraint policy, makes `supplychain-verify-receipt` explicitly evidence-only, and binds the optional workflow-verification lane to `release.authority.policy` plus a single `supplychain_verification` summary on publish receipts (`adrs/ADR-0079-supplychain-verification-evidence-and-publish-gate-boundary.md`, `docs/489-supplychain-verification-evidence-and-publish-gate-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the supply-chain workflow-verification lane around that decision by adding `authority_semantics` to `supplychain-verify-receipt`, wiring workflow-verification requirements into `release.authority.policy`, and collapsing publish-time workflow joins into `release.publish.receipt.supplychain_verification` (`spec/supplychain.verify.receipt.schema.json`, `spec/supplychain.layout.policy.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`, `spec/examples/supplychain.verify.receipt.json`, `spec/examples/supplychain.layout.policy.json`, `spec/examples/release.authority.policy.json`, `spec/examples/release.publish.receipt.json`).
- Reframe the attestation / workflow / authority docs so provenance, layout verification, verifier summaries, and publication authority no longer overlap (`docs/202-in-toto-layouts-and-step-policy.md`, `docs/71-attestations-dsse-in-toto-slsa.md`, `docs/31-provenance-and-sbom.md`, `docs/229-evidence-spine-overview.md`, `docs/260-release-authority-policy-and-key-management.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Add a lightweight guardrail that mechanically checks the workflow-verification join points and prevents drift across layout policy, verification receipts, release authority policy, and publish receipts (`tools/check_supplychain_verification_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## New in 2026-03-07r217

- Fix release transparency as a checkable contract: accept an ADR that keeps `release.publish.receipt` authoritative, makes `release.transparency.entry` / `log.checkpoint.receipt` / `transparency.monitor.snapshot` explicitly evidence-only, and binds the release-transparency lane to the governing `release.authority.policy` plus a single `transparency_verification` summary on publish receipts (`adrs/ADR-0078-release-transparency-evidence-and-monitor-gate-boundary.md`, `docs/488-release-transparency-evidence-and-monitor-gate-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the release-transparency lane around that decision by removing the vague `policy_digest` field from `release.transparency.entry`, requiring `authority_policy_digest`, adding checkpoint-receipt joins and monitor summary status, and collapsing publish-time transparency joins into `release.publish.receipt.transparency_verification` (`spec/release.transparency.entry.schema.json`, `spec/log.checkpoint.receipt.schema.json`, `spec/transparency.monitor.snapshot.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`, `spec/examples/release.transparency.entry.json`, `spec/examples/log.checkpoint.receipt.json`, `spec/examples/transparency.monitor.snapshot.json`, `spec/examples/release.authority.policy.json`, `spec/examples/release.publish.receipt.json`).
- Reframe the release-authority / transparency docs so publication authority, append-only evidence, witnessed checkpoints, and monitor state no longer overlap (`docs/257-release-capsules-and-transparency.md`, `docs/259-transparency-monitors-and-witness-gossip.md`, `docs/260-release-authority-policy-and-key-management.md`, `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Add a lightweight guardrail that mechanically checks the release-transparency join points and prevents drift across authority policy, transparency entries, checkpoint receipts, monitor snapshots, and publish receipts (`tools/check_release_transparency_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## New in 2026-03-07r216

- Fix keyless publisher identity as a checkable contract: accept an ADR that keeps `publisher.identity.receipt` as **identity evidence only**, adds a bundle-first/offline-verification boundary for `sigstore-keyless`, and lets `release.authority.policy` / `release.publish.receipt` carry supplemental identity-evidence rules and decisions without weakening threshold publish authority (`adrs/ADR-0077-keyless-identity-evidence-and-offline-verification-boundary.md`, `docs/487-keyless-identity-evidence-and-offline-verification-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the keyless lane around that decision by updating `publisher.identity.receipt`, `release.authority.policy`, and `release.publish.receipt` schemas/examples so portable keyless evidence binds `sigstore_bundle_digest` + `verification_roots_digest` and publish receipts can explain whether identity evidence was accepted or rejected (`spec/publisher.identity.receipt.schema.json`, `spec/release.authority.policy.schema.json`, `spec/release.publish.receipt.schema.json`, `spec/examples/publisher.identity.receipt.json`, `spec/examples/release.authority.policy.json`, `spec/examples/release.publish.receipt.json`, `spec/examples/pki.trust.bundle.json`).
- Reframe the identity / authority docs so publisher identity, bundle-first verification, release authority, and the evidence spine no longer overlap or imply that CI identity is itself release authority (`docs/290-keyless-signing-and-publisher-identity-receipts.md`, `docs/333-sigstore-bundles-and-offline-verification.md`, `docs/260-release-authority-policy-and-key-management.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Add a lightweight guardrail that mechanically checks the keyless-identity join points and prevents drift across identity receipts, bundle/trust-root bindings, release authority policy, and release publish receipts (`tools/check_keyless_identity_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## New in 2026-03-07r215

- Fix execution-integrity authority as a checkable contract: accept an ADR that keeps `exec.integrity.policy` / `exec.integrity.plan` / `exec.integrity.receipt` as the authoritative lane, binds execution-integrity planning to `runtime_manifest_digest` + `stratum_stack_digest` + `mount_view_digest`, keeps `exec-verify-snapshot` / `exec-verify-event` as backend observations, and narrows interpreters/loaders/writable bytes into one operable rule (`adrs/ADR-0076-exec-integrity-authority-and-verified-execution-boundary.md`, `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the verified-exec lane around that decision by updating authoritative plan/receipt schemas/examples, retargeting `exec.verify.policy.diff` to authoritative `exec.integrity.policy` objects, and switching change sets to `apply-exec-integrity` (`spec/exec.integrity.plan.schema.json`, `spec/exec.integrity.receipt.schema.json`, `spec/exec.verify.policy.diff.schema.json`, `spec/examples/exec.integrity.plan.json`, `spec/examples/exec.integrity.receipt.json`, `spec/examples/exec.verify.policy.diff.json`, `spec/change.set.schema.json`, `spec/examples/change.set.json`).
- Reframe the evidence + review docs so policy intent, activation receipts, backend observations, and drift review no longer overlap or contradict each other (`docs/289-exec-integrity-policy-and-verified-execution.md`, `docs/233-verified-execution-as-evidence.md`, `docs/442-exec-verify-policy-diff-as-review-surface.md`, `docs/229-evidence-spine-overview.md`, `docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/97-non-negotiable-behaviors.md`, `docs/110-juicy-os-lessons.md`).
- Add a lightweight guardrail that mechanically checks the execution-integrity join points and prevents drift across policy/plan/receipt/runtime-composition bindings, change-set ops, and the core docs (`tools/check_exec_integrity_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## New in 2026-03-07r214

- Make multi-origin runtime composition a checkable contract: accept an ADR that fixes `stratum.manifest` + `stratum.stack` + `mount.view` as the official runtime-composition lane, requires exactly one ABI anchor per stack, forbids silent host-library fallback, and binds runtime manifests/evidence to `stratum_stack_digest` + `mount_view_digest` (`adrs/ADR-0075-stratum-stack-and-runtime-composition-boundary.md`, `docs/485-stratum-stack-and-runtime-composition-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Add typed schemas/examples plus a lightweight guardrail that mechanically checks the runtime-composition join points and prevents drift across strata, compiled mount views, and runtime manifests (`spec/stratum.manifest.schema.json`, `spec/stratum.stack.schema.json`, `spec/mount.view.schema.json`, `spec/examples/stratum.manifest.json`, `spec/examples/stratum.stack.json`, `spec/examples/mount.view.json`, `spec/runtime.manifest.schema.json`, `spec/examples/runtime.manifest.json`, `tools/check_strata_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing runtime-composition docs so mount views, strata, and component/runtime manifests explicitly inherit the accepted boundary instead of leaving multi-origin userlands as folklore (`docs/264-mount-namespaces-and-union-views.md`, `docs/295-strata-and-multi-origin-userlands.md`, `docs/297-component-descriptors-and-compiled-runtime-manifests.md`, `docs/110-juicy-os-lessons.md`).
- Regenerate discovery/version surfaces and refresh the top-level archive map for the accepted runtime-composition boundary (`docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-07r213

- Make origin-label handling a checkable contract: accept an ADR that fixes `content.origin` as the authoritative provenance object, keeps filesystem quarantine/origin labels pointer-only, and requires `content.import.receipt` to say whether metadata was preserved, rehydrated, cleared-by-policy, or laundering-suspected (`adrs/ADR-0074-origin-label-authority-and-anti-laundering-boundary.md`, `docs/484-origin-label-authority-and-anti-laundering-boundary.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the provenance / metadata lane so imports, exports, removable-media ingestion, query/index guidance, and non-negotiable behavior docs explicitly inherit the accepted authority boundary instead of leaving xattr-vs-CAS semantics implicit (`spec/content.import.receipt.schema.json`, `spec/examples/content.origin.json`, `spec/examples/content.import.plan.json`, `spec/examples/content.import.receipt.json`, `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`, `docs/251-export-policies-and-support-bundle-portal.md`, `docs/279-usb-quarantine-and-removable-media-workflow.md`).
- Add a lightweight guardrail that mechanically checks the provenance-authority join points and prevents drift across `content.origin`, import receipts, and the new authority doc (`tools/check_content_origin_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official provenance-label / portal / extended-attribute pointers, then regenerate discovery/version surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-07r212

- Make destructive reprovisioning a checkable contract: accept an ADR that fixes the official destructive reset/reseed lane as `reset.authorization` + `reset.receipt`, bound to `disk.layout.plan`, install payload digests, explicit target selectors, and profile-shaped authority signals instead of vague “signed reset bundles/markers” (`adrs/ADR-0073-destructive-reprovisioning-and-reset-authority.md`, `docs/483-destructive-reprovisioning-and-reset-authority.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `destructive_reprovision` profile knob, tightening the install/recovery and evidence docs to inherit the new boundary, and wiring typed reset artifacts into the archive’s shared install/recovery story (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/309-installation-and-recovery-as-derived-operations.md`, `docs/310-disk-layout-plans-and-receipts.md`, `docs/250-breakglass-and-recovery-workflows.md`, `docs/229-evidence-spine-overview.md`, `docs/473-installation-and-recovery-posture-by-profile.md`).
- Add typed schemas/examples plus a lightweight guardrail that mechanically checks the destructive-reprovision join keys and prevents drift across reset authorization, reset receipts, disk-layout evidence, and profile defaults (`spec/reset.authorization.schema.json`, `spec/reset.receipt.schema.json`, `spec/examples/reset.authorization.json`, `spec/examples/reset.receipt.json`, `tools/check_reset_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official Chromium OS recovery / developer-mode physical-presence lessons, then regenerate discovery/version surfaces (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-07r211

- Make boot code admission a checkable contract: accept an ADR that binds `boot.manifest`, `boot.override.policy`, `boot.override.receipt`, `boot.attestation`, and `kmod.load.plan` / `kmod.load.receipt` into one constrained kernel-code admission story, and limit normal mutable boot overrides to `next-entry`, `boot-mode`, and `console-profile` (`adrs/ADR-0072-boot-code-admission-and-constrained-overrides.md`, `docs/482-boot-code-admission-and-constrained-overrides.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten the boot + kernel-mutation lane so manifests carry policy digests, attestation exposes verified digests, kmod plan/receipt examples bind back to `boot_manifest_digest`, and the existing loader/manifest docs explicitly inherit the accepted boundary (`spec/boot.manifest.schema.json`, `spec/boot.attestation.schema.json`, `spec/kmod.load.plan.schema.json`, `spec/kmod.load.receipt.schema.json`, `spec/boot.override.policy.schema.json`, `spec/boot.override.receipt.schema.json`, `spec/examples/boot.manifest.json`, `spec/examples/boot.attestation.json`, `spec/examples/kmod.load.plan.json`, `spec/examples/kmod.load.receipt.json`, `spec/examples/boot.override.policy.json`, `spec/examples/boot.override.receipt.json`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/277-loader-verification-and-boot-config-constraints.md`, `docs/313-boot-manifests-and-eventlog-replay.md`, `docs/284-bootenv-switching-as-evidence.md`, `docs/229-evidence-spine-overview.md`).
- Add a lightweight guardrail that mechanically checks the boot-admission join keys and prevents example/schema drift across manifest, override, attestation, and kmod receipts (`tools/check_boot_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons and regenerate discovery/version surfaces for the accepted boot boundary (`docs/110-juicy-os-lessons.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r210

- Make the human-scale debugging handoff contract explicit: accept an ADR that fixes the official support handoff as `incident.timeline` + `incident.bundle` + `bundle.plan` + `bundle.payload.manifest` + `bundle.build.receipt`, keeps `tar.zst` as the canonical payload format, and keeps `zip` as an explicit compatibility adapter (`adrs/ADR-0071-support-bundle-contract-and-timeline-first-handoff.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/266-open-questions-and-risk-register.md`).
- Tighten incident/support bundle docs and examples so the default handoff is timeline-first and digest-bound instead of a mystery tarball (`docs/216-incident-snapshots-and-support-bundles.md`, `docs/419-incident-timelines-as-derived-artifacts.md`, `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/229-evidence-spine-overview.md`, `spec/incident.bundle.schema.json`, `spec/bundle.build.receipt.schema.json`, `spec/examples/incident.bundle.json`, `spec/examples/bundle.build.receipt.json`, `spec/examples/bundle.payload.manifest.json`).
- Add a lightweight guardrail that keeps the official support handoff contract wired and prevents example/schema drift on timeline-first support bundles (`tools/check_support_bundle_contract.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons + curated references with current official support-bundle / diagnostics pointers, then regenerate discovery surfaces and version stamps (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r209

- Make trust-bundle posture a checkable product-shape decision: accept an ADR that keeps fleet trust roots purpose-scoped and diff-gated with shadow trust blocking in official lanes, keeps workstation extra roots visible and trusted-UI-mediated, keeps general-OS system trust preferred with explicit local override, and makes fixed-purpose offline/strongly-approved trust bundles the production default for factory/regulatory shapes (`adrs/ADR-0070-trust-bundle-posture-by-profile.md`, `docs/480-trust-bundle-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `trust_bundles` profile knob, tightening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into invisible workstation root injection, app-shipped shadow trust in official fleet lanes, or ad-hoc live production CA edits (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing trust-bundle lane docs so artifact, shadow-trust, and trust-bundle-diff guidance explicitly inherit the new A/B/C/D boundary instead of leaving trust-store posture implicit (`docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `docs/327-shadow-trust-and-system-ca-governance.md`, `docs/434-pki-trust-bundle-diff-as-review-surface.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official p11-kit trust-module, SPIFFE trust-bundle, FreeBSD `certctl`, and cert-manager trust-manager pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r208

- Make hardware-compatibility posture a checkable product-shape decision: accept an ADR that keeps fleet preflight blocking and cohort-aware for boot-critical/remote-management-floor failures, keeps workstation boot-floor failures trusted-UI-blocking with explicit consent for warnings, keeps general-OS preflight preferred with explicit override, and makes approved-hardware admission the production default for factory/regulatory shapes (`adrs/ADR-0069-hardware-compatibility-posture-by-profile.md`, `docs/479-hardware-compatibility-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `hardware_compatibility` profile knob, tightening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into blind fleet switches, surprise workstation hardware regressions, or faux-supported factory bundles (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing hardware inventory / compatibility docs so inventory refresh, preflight strength, and support-claim semantics explicitly inherit the new A/B/C/D boundary instead of leaving gate strength implicit (`docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official FreeBSD device-inspection/devmatch, systemd hwdb, fwupd hardware-ID, and Fuchsia driver-binding pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r207

- Make network-topology posture a checkable product-shape decision: accept an ADR that keeps fleet host topology activation-first and commit-confirmed with maintenance leases, keeps workstation risky host-topology changes trusted-UI-visible and rollbackable, keeps general-OS derived networking preferred with explicit local-admin fallback, and keeps production topology sealed/offline-windowed for factory/regulatory shapes (`adrs/ADR-0068-network-topology-posture-by-profile.md`, `docs/477-network-topology-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Turn that into anti-drift profile defaults by extending `spec/examples/product.profiles.json` and `tools/check_product_profiles.py`, and wire the accepted boundary through the product-profile meta-doc, desktop viability checklist, runbook, and hygiene docs (`docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`).
- Tighten the networking lanes so host topology, substrate mapping, and authority-budget docs now inherit the A/B/C/D boundary explicitly instead of leaving host-topology mutation implicit (`docs/322-network-topology-and-firewall-as-derived-operations.md`, `docs/64-networking-modes-mapping.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`).
- Refresh juicy lessons + curated references and regenerate generated discovery surfaces + version stamps (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r206

- Make evidence-collection posture a checkable product-shape decision: accept an ADR that keeps fleet evidence bounded but always on, keeps workstation evidence locally useful and user-exportable without ambient support telemetry, keeps general-OS local retention viable without hidden collector dependencies, and makes bundled/redacted evidence the production default for factory/regulatory shapes (`adrs/ADR-0067-evidence-collection-posture-by-profile.md`, `docs/478-evidence-collection-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Turn that into anti-drift profile defaults by extending `spec/examples/product.profiles.json` and `tools/check_product_profiles.py`, and wire the accepted boundary through the product-profile meta-doc, desktop viability checklist, runbook, and hygiene docs (`docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/99-llm-runbook.md`, `docs/98-archive-hygiene.md`).
- Tighten the evidence lanes so the evidence spine, structured event log, incident bundle, inspect-tree diagnostics, and flight recorder docs now inherit the A/B/C/D collection boundary explicitly (`docs/229-evidence-spine-overview.md`, `docs/215-structured-event-log-as-evidence.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/302-structured-diagnostics-inspect-trees.md`, `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`).
- Refresh juicy lessons + curated references and regenerate generated discovery surfaces + version stamps (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r205

- Make device-authority posture a checkable product-shape decision: accept an ADR that keeps fleet service compartments compiled-minimal and lease-expanded, keeps workstation raw sensitive devices in the trusted host with portal-first app access, preserves explicit raw-device compatibility fallback for general-OS viability, and makes compiled-minimal sealed device authority the production default for factory/regulatory shapes (`adrs/ADR-0066-device-authority-posture-by-profile.md`, `docs/476-device-authority-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `device_authority` profile knob, tightening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into ambient raw-device authority for fleet/workstation shapes or faux-sealed production device posture (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing device-authority lanes so device grants and devfs-view docs explicitly inherit the new A/B/C/D boundary instead of leaving raw device-node posture implicit (`docs/278-device-grants-and-devfs-rulesets.md`, `docs/323-devfs-views-plans-and-receipts.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official FreeBSD jails/devfs and Qubes device-security pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r204

- Make kernel-mutation posture a checkable product-shape decision: accept an ADR that keeps fleet kernel mutation activation-first and maintenance-leased, keeps workstation risky host-kernel mutation trusted-UI-visible, preserves explicit local-admin fallback for general-OS viability, and makes preload-only plus lockdown the production default for factory/regulatory shapes (`adrs/ADR-0065-kernel-mutation-posture-by-profile.md`, `docs/475-kernel-mutation-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `kernel_mutation` profile knob, tightening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into ambient runtime sysctl folklore, silent workstation host mutation, or faux-lockdown production claims (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing kernel-mutation lanes so sysctls, kmods, lockdown, and drift surfaces explicitly inherit the new A/B/C/D boundary instead of leaving runtime mutation posture implicit (`docs/318-kernel-tunables-and-sysctls-as-evidence.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/230-lockdown-levels-and-securelevel.md`, `docs/429-sysctl-diff-as-drift-surface.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official FreeBSD/OpenBSD securelevel, sysctl, and module-path pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r203

- Make high-risk approval posture a checkable product-shape decision: accept an ADR that keeps fleet shared-trust mutations digest-bound/role-separated/quorum-shaped by default, keeps workstation personal-risk actions trusted-UI user-consent-first, keeps general-OS single-principal local-admin viability without hidden reviewer dependencies, and requires offline/OOB-capable role-separated quorum for factory/regulatory production mutations (`adrs/ADR-0064-high-risk-approval-posture-by-profile.md`, `docs/474-high-risk-approval-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `high_risk_approvals` profile knob, tightening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into requester-self-approval for fleet/factory shared-trust mutations or reviewer-theater defaults for workstation/general-OS basics (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing approval lanes so two-person integrity, multiparty approvals, and release authority explicitly inherit the new A/B/C/D boundary instead of leaving quorum posture implicit (`docs/107-two-person-integrity.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`, `docs/260-release-authority-policy-and-key-management.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official TUF, Uptane, Vault control-group, and GitHub deployment-protection pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r202

- Make installation-and-recovery posture a checkable product-shape decision: accept an ADR that keeps fleet install/recovery target-device-bound and additive by default, keeps workstation destructive storage changes trusted-UI-guided and encrypted-root-first, keeps general-OS guided/classic install choice explicit, and requires target-bound offline-capable recovery plus signed reset authority for factory/regulatory shapes (`adrs/ADR-0063-installation-and-recovery-posture-by-profile.md`, `docs/473-installation-and-recovery-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `installation_recovery` profile knob, tightening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into wrong-disk automation, surprise workstation wipes, hidden destructive compatibility paths, or ad-hoc factory reset folklore (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing install/recovery lanes so the shared workflow docs explicitly inherit the new A/B/C/D boundary instead of leaving destructive authority and recovery-media expectations implicit (`docs/309-installation-and-recovery-as-derived-operations.md`, `docs/310-disk-layout-plans-and-receipts.md`, `docs/360-derived-recovery-images-and-minimal-userspace.md`).
- Refresh juicy lessons + curated references with the accepted boundary and current official OpenBSD `bsd.rd`, FreeBSD `bsdinstall`, systemd-repart, and ZFSBootMenu install/recovery pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r201

- Make update-delivery and release posture a checkable product-shape decision: accept an ADR that keeps fleet updates health-gated and rollout-shaped, keeps workstation apply/reboot trusted-UI-visible and deferrable, keeps general-OS transactional viability free of hidden coordinator requirements, and requires approved offline bundles or mirror kits with quarantine→promote as the factory/regulatory production default (`adrs/ADR-0062-update-delivery-and-release-posture-by-profile.md`, `docs/472-update-delivery-and-release-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by tightening A–D update notes/invariants/forbidden lanes and extending the product-profile guardrail so the archive cannot slide back into surprise workstation host updates, coordinator-dependent general-OS viability, opaque fleet updater folklore, or online-only factory delivery paths (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing update lanes so health-gated updates, rollout/assignment guidance, offline bundles, air-gap mirror kits, and channel lessons explicitly inherit the new A/B/C/D delivery boundary instead of leaving profile defaults implicit (`docs/112-health-gated-updates.md`, `docs/177-fleet-coordinated-rollouts.md`, `docs/138-offline-signed-update-bundles.md`, `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`, `docs/89-update-channel-lessons-freebsd-update.md`).
- Refresh juicy lessons with the accepted boundary so “bytes authority vs rollout/assignment/finalization vs offline carrier” stays discoverable and amnesia-resistant (`docs/110-juicy-os-lessons.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).


## New in 2026-03-06r200

- Make firmware-update posture a checkable product-shape decision: accept an ADR that keeps fleet firmware mutation policy-gated and maintenance-shaped, keeps workstation firmware apply trusted-UI-visible and consent-first, keeps general-OS firmware handling user-choice with explicit adapters, and requires offline-staged firmware workflows for factory/regulatory shapes by default (`adrs/ADR-0061-firmware-update-posture-by-profile.md`, `docs/471-firmware-update-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by sharpening A–D firmware notes/invariants/forbidden lanes and extending the product-profile guardrail so the archive cannot slide back into fleet updater folklore, silent workstation firmware changes, or online-only factory firmware paths (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing firmware lane docs so platform-provenance and capsule guidance explicitly inherit the new product-shape default instead of leaving A/B/C/D posture implicit (`docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `docs/336-uefi-capsules-esrt-and-fwupd-practice-notes.md`, `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`, `docs/221-firmware-updates-as-artifacts.md`).
- Refresh firmware lessons + curated references with the accepted boundary and current official UEFI 2.11 / LVFS / NIST firmware-resiliency pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).


## New in 2026-03-06r199

- Make workload-identity / credential-issuance posture a checkable product-shape decision: accept an ADR that keeps fleet service identity short-lived/digest-bound and headless, keeps workstation AppVM/dev-service identity separate from human login/account authority, keeps general-OS static-token flows adapter-shaped, and forbids shipped static shared production secrets in factory/regulatory shapes by default (`adrs/ADR-0060-workload-identity-and-credential-issuance-posture-by-profile.md`, `docs/470-workload-identity-and-credential-issuance-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `workload_identity` profile knob, sharpening A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into token sprawl, human/workload identity confusion, or shipped production shared secrets (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing identity lane docs so workload identity, PKI lifecycle, and dynamic service identity explicitly inherit the new product-shape default instead of leaving A/B/C/D posture implicit (`docs/181-workload-identity-and-secretless-deploys.md`, `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/240-dynamic-service-identities.md`).
- Refresh workload-identity lessons + curated references with the accepted boundary and current official SPIFFE/SPIRE, Kubernetes bound-token, and Vault dynamic-credential pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).


## New in 2026-03-06r198

- Make platform-provenance / attestation-admission posture a checkable product-shape decision: accept an ADR that keeps fleet measured posture receipted and available for sensitive admissions, keeps workstation posture visible/exportable without making remote attestation a surprise hard dependency for ordinary local use, keeps general-OS attestation optional/exportable with explicit gates, and requires retained measured posture for production/factory-sensitive admissions by default (`adrs/ADR-0059-platform-provenance-and-attestation-admission-posture-by-profile.md`, `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by refining the stable `platform_provenance` profile knob, sharpening A–D notes/invariants, and extending the product-profile guardrail so the archive cannot slide back into attestation theater, verifier-dependent workstation breakage, or production evidence-without-gating (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing attestation lane docs so evidence, admission policy, and admission-policy diffs explicitly inherit the new product-shape default instead of leaving A/B/C/D posture implicit (`docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/388-remote-attestation-admission-and-enrollment.md`, `docs/440-attestation-admission-policy-diff-as-review-surface.md`).
- Refresh attestation lessons + curated references with the accepted boundary and current official measured-boot / Keylime / Trusted Launch pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r197

- Make trustworthy-time posture a checkable product-shape decision: accept an ADR that requires authenticated quorum/LKGT posture for fleet expiry-sensitive gates, makes workstation degraded time visible and gates sensitive actions, keeps authenticated time preferred with explicit fallback in general OS, and requires bounded offline signed-time or authenticated-quorum bootstrap for factory/regulatory shapes (`adrs/ADR-0058-trustworthy-time-posture-by-profile.md`, `docs/468-trustworthy-time-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `time_authority` profile knob, refining A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into silent unauthenticated time fallback or airgap-time waiver folklore (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing time lane so the BSD-friendly backend doc explicitly inherits the product-shape default instead of leaving fleet/workstation/factory posture implicit (`docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`).
- Refresh time lessons + curated references with the accepted boundary and current official NTS / Roughtime pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r196

- Make operator-access posture a checkable product-shape decision: accept an ADR that keeps fleet operator access JIT/certificate-based and role-shell-first, makes workstation admin local-presence-first with remote shell admin exceptional, keeps general-OS static-key remote admin adapter-shaped, and forbids standing vendor/admin keys in factory/regulatory images by default (`adrs/ADR-0057-operator-access-posture-by-profile.md`, `docs/467-operator-access-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `operator_access` profile knob, refining A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into permanent bastions, standing workstation remote admin, or shipped factory maintenance keys (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing operator-access lane so the headless SSH/role-shell doc explicitly inherits the new product-shape default instead of leaving workstation/general-OS/factory posture implicit (`docs/311-operator-access-leases-and-ssh-certs.md`).
- Refresh operator-access lessons + curated references with accepted posture and current official SSH-cert / doas / session-recording pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r195

- Make export-boundary posture a checkable product-shape decision: accept an ADR that keeps fleet evidence export brokered/ticketed/encrypted, makes workstation sharing recipient-visible and redaction-aware, keeps general-OS adapter fallback explicit, and requires minimal redacted strongly approved export for factory/regulatory shapes (`adrs/ADR-0056-export-boundary-posture-by-profile.md`, `docs/466-export-boundary-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `evidence_exports` profile knob, refining A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into ambient upload folklore or invisible remembered support export authority (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing export lane so the portal + diff docs explicitly inherit the product-shape default instead of leaving approval severity purely implicit (`docs/251-export-policies-and-support-bundle-portal.md`, `docs/433-export-policy-diff-as-review-surface.md`).
- Refresh export lessons + curated references with the accepted boundary and current official support/export pointers (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r194

- Make data-at-rest posture a checkable product-shape decision: accept an ADR that encrypts mutable state by default for fleet hosts, makes lost-device/login-bounded user state the workstation default, keeps encryption preferred with explicit compatibility fallback for general OS, and requires encrypted production state plus attested/quorum maintenance unlock for factory/regulatory shapes (`adrs/ADR-0055-data-at-rest-posture-by-profile.md`, `docs/465-data-at-rest-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Thread that decision into anti-drift product defaults by adding the stable `data_at_rest` profile knob, refining A–D notes/invariants/forbidden lanes, and extending the product-profile guardrail so the archive cannot slide back into image-baked unlock secrets or ambient workstation auto-unlock (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Tighten the existing ZFS encryption lane so substrate capability does not masquerade as product policy: file/URL key locations stay adapter territory unless mediated by explicit broker/evidence workflow (`docs/409-zfs-encryption-and-key-management.md`).
- Refresh encryption/home-state lessons + curated references so the accepted boundary stays discoverable and current (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Close the remaining schema/example coverage hole for portable-home, AppVM-storage, and restore artifacts so `check_spec_example_coverage.py` stays green (`spec/examples/home.attach.receipt.json`, `spec/examples/home.unlock.receipt.json`, `spec/examples/home.lock.receipt.json`, `spec/examples/appvm.storage.plan.json`, `spec/examples/appvm.storage.receipt.json`, `spec/examples/restore.plan.json`, `spec/examples/restore.receipt.json`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r193

- Make backup / restore posture a checkable product-shape decision: accept an ADR that treats fleet hosts as replaceable state-replication systems, keeps workstation recovery explicit via exports or home replication, leaves general-OS backup choice open, and requires replication plus restore drills for factory/regulatory shapes (`adrs/ADR-0054-backup-and-restore-posture-by-profile.md`, `docs/464-backup-and-restore-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Turn that decision into anti-drift product defaults by refining the stable `backups` profile knob, wiring backup/recovery notes + invariants into A–D, and extending the profile guardrail so recovery posture cannot quietly slide back into full-host image folklore or mystery sync (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh backup/recovery wiring, juicy lessons, and curated references so the accepted boundary stays discoverable and current (`docs/316-backups-and-restores-as-derived-operations.md`, `docs/317-restore-drills-and-continuous-recovery-testing.md`, `docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Close an existing hygiene hole by adding the missing portable-home, AppVM-storage, and restore artifact schemas named by the archive (`spec/home.attach.receipt.schema.json`, `spec/home.unlock.receipt.schema.json`, `spec/home.lock.receipt.schema.json`, `spec/appvm.storage.plan.schema.json`, `spec/appvm.storage.receipt.schema.json`, `spec/restore.plan.schema.json`, `spec/restore.receipt.schema.json`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r192

- Make human identity / home-state posture a checkable product-shape decision: accept an ADR that keeps fleet hosts on operator-account defaults, makes portable login-mounted homes the workstation default, keeps whole-home AppVM mounts exceptional, preserves host-account compatibility in general OS, and keeps production/factory identities separate (`adrs/ADR-0053-human-identity-and-home-state-posture-by-profile.md`, `docs/463-human-identity-and-home-state-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Reduce entropy in the product profile artifact by replacing the workstation-only `portable_homes` knob with a stable cross-profile `home_identity` default, refining profile invariants/forbidden lanes and extending the profile guardrail so home-state drift is caught mechanically (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh portable-home/AppVM-storage wiring and current references so the accepted boundary stays discoverable (`docs/269-portable-home-areas-and-user-records.md`, `docs/270-appvm-storage-private-volatile-and-home-areas.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r191

- Make private-key / crypto-operation posture a checkable product-shape decision: accept an ADR that keeps fleet key use headless and brokered, workstation key use presence-gated and vault-preferred, general-OS compatibility explicit/adapter-shaped, and appliance/factory key use offline-or-quorum by default (`adrs/ADR-0052-private-key-and-crypto-op-posture-by-profile.md`, `docs/462-private-key-and-crypto-op-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Turn that decision into anti-drift product defaults by adding a stable `private_keys` profile knob and extending the profile guardrail so the archive cannot slide back into file-key sprawl or ambient signing authority (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh crypto-lane wiring, workstation viability, juicy lessons, and curated references so split-key / non-exportable patterns stay discoverable and current (`docs/306-crypto-operations-portal-and-split-keys.md`, `docs/392-crypto-key-policies-and-nonexportable-handles.md`, `docs/410-desktop-viability-checklist.md`, `docs/411-product-profiles-as-compilation-target.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Regenerate generated discovery surfaces and version stamps (`docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r190

- Make remote assistance a checkable product-shape decision: accept an ADR that keeps fleet support operator/TTY-shaped, workstation support visible and secure-attention-gated for control, general-OS support explicit/leased, and appliance support absent by default outside maintenance-shaped workflows (`adrs/ADR-0051-remote-assistance-posture-by-profile.md`, `docs/461-remote-assistance-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Turn that decision into anti-drift product defaults by adding a stable `remote_assistance` profile knob and extending the profile guardrail so the archive cannot slide back into stealthy or ambient remote-support posture (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh remote-assistance wiring, workstation viability, juicy lessons, and curated references; also normalize duplicated tail numbering in the risk register before regenerating the generated discovery surfaces and version stamps (`docs/291-remote-assistance-sessions-as-evidence.md`, `docs/410-desktop-viability-checklist.md`, `docs/411-product-profiles-as-compilation-target.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/420-context-pack.md`, `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/00-index.md`, `CHANGELOG.md`).

## New in 2026-03-06r189

- Make inbound exposure a checkable product-shape decision: accept an ADR that keeps listener exposure brokered across A–D, makes loopback the low-friction default, and allows trusted-UI consent for non-local exposure only where a human product shape exists and the approval lands in a lease or durable policy object (`adrs/ADR-0050-inbound-listen-posture-by-profile.md`, `docs/460-inbound-listen-posture-by-profile.md`, `docs/266-open-questions-and-risk-register.md`).
- Turn that decision into anti-drift product defaults by adding `network_ingress` profile knobs and extending the profile guardrail so inbound-listen posture drift is caught mechanically (`spec/examples/product.profiles.json`, `tools/check_product_profiles.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh the listen-broker wiring and workstation checklist so loopback-first local development, non-local exposure, and low-traffic activation stay coherent across A–D (`docs/286-inbound-listen-broker-and-firewall-leases.md`, `docs/411-product-profiles-as-compilation-target.md`, `docs/410-desktop-viability-checklist.md`).
- Refresh juicy lessons + curated references with current socket-activation, PF-anchor/authpf, and opt-in remote-support pointers; then regenerate generated discovery surfaces and version stamps (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/412-product-profile-matrix.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-06r188

- Make outbound-network posture a checkable profile truth instead of a lesson-only aspiration: accept an ADR that keeps egress brokered across A–D, only allows interactive approvals where the product shape includes a human, and requires brokered DNS whenever hostname policy is the review surface (`adrs/ADR-0049-outbound-network-posture-by-profile.md`, `docs/459-outbound-network-posture-by-profile.md`, `spec/examples/product.profiles.json`).
- Turn that decision into anti-drift product defaults by adding `network_egress` + `dns_resolution` profile knobs and extending the profile guardrail so egress / DNS posture drift is caught mechanically (`tools/check_product_profiles.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons + curated references, then regenerate generated discovery surfaces and version stamps (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/00-index.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `README.md`, `CHANGELOG.md`).

- Make removable-media / USB posture a checkable profile truth instead of a lesson-only aspiration: accept an ADR that bans trusted-plane automount by default, sets quarantine-first posture across A–D, and makes device-domain use explicit per profile (`adrs/ADR-0048-removable-media-and-usb-posture-by-profile.md`, `docs/458-removable-media-and-usb-posture-by-profile.md`, `spec/examples/product.profiles.json`).
- Turn that decision into anti-drift product defaults by adding `removable_media` + `usb_isolation` profile knobs and extending the profile guardrail so automount/device-isolation drift is caught mechanically (`tools/check_product_profiles.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

- Make the workstation runtime boundary explicit: for profile **B**, the host is trusted UI/brokers and general interactive apps are **AppVM-first**. Capture the decision in an accepted ADR and a focused wiring doc, and thread it through the desktop viability/app-compartment docs (`adrs/ADR-0047-workstation-host-ui-and-appvm-boundary.md`, `docs/457-workstation-host-ui-and-appvm-boundary.md`, `docs/410-desktop-viability-checklist.md`, `docs/268-desktop-appvms-and-portalized-apps.md`).
- Turn that into a checkable compilation-target default by refining the workstation profile posture, forbidding host-side general app execution by default, and narrowing the remaining desktop open question to implementation details (`spec/examples/product.profiles.json`, `docs/411-product-profiles-as-compilation-target.md`, `docs/412-product-profile-matrix.md`, `docs/266-open-questions-and-risk-register.md`).
- Add a profile-drift guardrail so the archive cannot quietly slide back into an ambiguous host-app model (`tools/check_product_profiles.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Refresh juicy lessons + curated references, then regenerate generated discovery surfaces and version stamps (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/00-index.md`, `docs/420-context-pack.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `README.md`, `CHANGELOG.md`).















## New in 2026-03-04r185

- Eliminate spec-example drift warnings by validating long-lived *variant* examples via thin wrapper schemas (`microvm.stop.plan.force`, `microvm.stop.receipt.denied`). The wrappers `$ref` the base contracts and pin the variant semantics so examples remain mechanically checkable without expanding the core surface (`spec/microvm.stop.plan.force.schema.json`, `spec/microvm.stop.receipt.denied.schema.json`, `docs/98-archive-hygiene.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r184

- Stabilize the microVM “why” surface by introducing a central reason-code registry for lifecycle receipts, capturing the governance rule in an accepted ADR, and enforcing it with a hygiene check so example receipts can't invent ad-hoc codes (`docs/456-microvm-receipt-reason-code-registry.md`, `adrs/ADR-0046-microvm-reason-code-registry.md`, `tools/check_microvm_reason_code_registry.py`, `tools/hygiene.py`, `docs/455-microvm-launch-plans-and-receipts.md`, `docs/99-llm-runbook.md`).
- Add an explicit denied stop receipt example that demonstrates the two-code pattern (`denied-by-policy` + `force-stop-denied`) and is mechanically guarded against drift (`spec/examples/microvm.stop.plan.force.json`, `spec/examples/microvm.stop.receipt.denied.json`).
- Refresh curated references with high-signal cues for stable error vocabularies (gRPC status codes; systemd symbolic exit-status names) and extend juicy lessons so the registry stays discoverable (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r183

- Make microVM lifecycle receipts operationally deterministic by requiring non-empty `reasons[]` with stable `reasons[].code` on non-success outcomes (denied/failed/timeout); capture the rule in an ADR and enforce it with a hygiene guardrail (`adrs/ADR-0045-microvm-receipt-reason-codes.md`, `spec/microvm.launch.receipt.schema.json`, `spec/microvm.stop.receipt.schema.json`, `tools/check_microvm_receipt_reason_requirements.py`, `docs/455-microvm-launch-plans-and-receipts.md`).
- Extend juicy lessons and the LLM runbook with the new invariant so it stays discoverable and amnesia-resistant (`docs/110-juicy-os-lessons.md`, `docs/99-llm-runbook.md`).
- Refresh curated references with high-signal cues for structured, machine-readable error detail envelopes and stable reason-code vocabularies (`docs/32-curated-references.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r182

- Make microVM launches more forensic and spec-able by recording attached host↔guest IO crossings in the receipt: add `assigned.io_channels` (vsock/virtio-console/nmdm/stdio), update the example receipt, and capture the decision in an ADR so A–D behavior doesn’t drift (`spec/microvm.launch.receipt.schema.json`, `spec/examples/microvm.launch.receipt.json`, `adrs/ADR-0044-microvm-io-channels-in-receipts.md`, `docs/455-microvm-launch-plans-and-receipts.md`, `docs/110-juicy-os-lessons.md`).
- Refresh curated references with concrete vsock semantics pointers (CID/port model, well-known CIDs) so cross-backend implementers stay aligned (`docs/32-curated-references.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r181

- Make microVM plan identity mechanically implementable: define `plan_digest = sha256(utf8(JCS(plan)))` and capture the rule in an ADR (`adrs/ADR-0043-microvm-plan-digest-sha256.md`, `docs/455-microvm-launch-plans-and-receipts.md`, `spec/microvm.launch.receipt.schema.json`, `spec/microvm.stop.receipt.schema.json`).
- Add an amnesia-resistor guardrail: `tools/check_microvm_example_plan_digests.py` verifies receipt examples actually bind the computed plan digest, and update the microVM lifecycle examples to use real sha256 digests (no `...` placeholders) so drift is caught early (`spec/examples/microvm.launch.plan.json`, `spec/examples/microvm.launch.receipt.json`, `spec/examples/microvm.stop.plan.json`, `spec/examples/microvm.stop.receipt.json`, `tools/hygiene.py`).
- Refresh curated references with RFC 8785 JCS implementation pointers (keeps cross-language implementers aligned) and extend juicy lessons with a durable “content identity must be checkable” rule of thumb (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`, `docs/99-llm-runbook.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r180

- Make microVM **stop** spec-able (like launch) by introducing `microvm.stop.plan` + `microvm.stop.receipt` (schemas + examples) and wiring stop into the control-plane and evidence-spine docs so terminations are auditable and queryable across A–D (`spec/microvm.stop.plan.schema.json`, `spec/examples/microvm.stop.plan.json`, `spec/microvm.stop.receipt.schema.json`, `spec/examples/microvm.stop.receipt.json`, `docs/29-vm-control-plane.md`, `docs/229-evidence-spine-overview.md`).
- Decide stop semantics conservatively: Plan→Receipt, bounded `graceful` vs explicit `force`, idempotent `already-stopped`, and optional `expect_running_plan_digest` safety guard (`adrs/ADR-0042-microvm-stop-semantics.md`, `docs/455-microvm-launch-plans-and-receipts.md`).
- Extend juicy lessons and curated references so “no silent kills” and backend stop primitives stay discoverable (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r179

- Decide strict microVM launch idempotency: `derive-vmmd` is strict-idempotent by `(instance_id, plan_digest)` (retries are safe; implicit replacement is denied) and capture the rule in an ADR so A–D behavior does not fork (`adrs/ADR-0041-microvm-instance-idempotency.md`, `docs/455-microvm-launch-plans-and-receipts.md`, `docs/29-vm-control-plane.md`).
- Extend the microVM juicy lessons to make “no surprise restarts” a stable rule of thumb for fleet/workstation UX (`docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r178

- Make the `derive-vmmd` runtime boundary spec-able by introducing a digest-bound Plan→Receipt join key for microVM launches: `microvm.launch.plan` + `microvm.launch.receipt` (schema + examples) and wire it into the evidence spine and control-plane docs (`docs/455-microvm-launch-plans-and-receipts.md`, `docs/229-evidence-spine-overview.md`, `docs/29-vm-control-plane.md`, `spec/microvm.launch.plan.schema.json`, `spec/microvm.launch.receipt.schema.json`).
- Add a juicy lesson that makes “launch is evidence” a stable rule of thumb for runtime isolation/forensics (`docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-03-04r177

- Decide the microVM orchestration boundary in v0: keep `derive-vmmd` **host-local** (verify → enforce → receipt) and treat distributed scheduling/reconciliation as an external, killable adapter concern (`adrs/ADR-0040-microvm-orchestration-host-local.md`, `docs/266-open-questions-and-risk-register.md`).
- Add an amnesia-resistor convention for the risk register: tag decided items with **[DECIDED]** and exclude them from generated “top open questions” surfaces; add a warning check to keep decided items pinned to ADRs (`docs/266-open-questions-and-risk-register.md`, `tools/gen_context_pack.py`, `tools/gen_risk_register_index.py`, `tools/check_open_questions_decisions.py`, `docs/420-context-pack.md`, `docs/415-risk-register-index.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r176

- Add a killable ecosystem interop lane for standard attestations by documenting an in-toto/SLSA export adapter and introducing a typed export report artifact: `attestation.adapter.intoto.report` (schema + example) (keeps DeriveBSD receipts as source of truth while enabling downstream verifier tooling) (`docs/454-intoto-slsa-adapter-lane.md`, `spec/attestation.adapter.intoto.report.schema.json`, `spec/examples/attestation.adapter.intoto.report.json`).
- Wire the new lane into adapter discipline, the evidence spine, juicy lessons, and curated references (adds current SLSA v1.2 pointers) so the interop remains discoverable and amnesia-resistant (`docs/402-adapter-lanes-and-strangler-discipline.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.


## New in 2026-02-28r175

- Make Capsicum capability-set drift mechanically reviewable by introducing typed preopen map artifacts and a compact diff surface: `preopen.map` + `preopen.map.diff` (schemas + examples) with a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/453-preopen-map-diff-as-review-surface.md`, `spec/preopen.map.schema.json`, `spec/examples/preopen.map.json`, `spec/preopen.map.diff.schema.json`, `spec/examples/preopen.map.diff.json`).
- Wire `preopen.map.diff` into the canonical diff registry, drift bundle posture guidance, and the evidence spine so “what handles/rights changed?” stays explainable and gateable without forks; refresh Capsicum launcher + descriptor docs with schema pointers (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/294-oblivious-sandboxing-launchers.md`, `docs/297-component-descriptors-and-compiled-runtime-manifests.md`).
- Extend the canonical risk-flag vocabulary with stable preopen-map drift reason codes (`preopen-map-egress-added`, `preopen-map-handle-added`, `preopen-map-rights-broadened`) and update curated references with Capsicum primitives (`cap_enter(2)`, `cap_rights_limit(2)`) (`spec/examples/risk.flag.registry.json`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.


## New in 2026-02-28r174

- Make sysctl drift explainable without bulk inventory by introducing a bounded observation artifact: `sysctl.snapshot` (schema + example) plus a tight wiring doc. Drift checks can capture snapshots and bundles can include them without shipping raw command output (`docs/452-sysctl-snapshot-as-evidence-artifact.md`, `spec/sysctl.snapshot.schema.json`, `spec/examples/sysctl.snapshot.json`).
- Tighten sysctl drift evidence by allowing `sysctl.event` to point at the snapshot digest (`snapshot_digest`), and wire snapshots into the evidence spine + kernel knobs lane (`spec/sysctl.event.schema.json`, `spec/examples/sysctl.event.json`, `docs/229-evidence-spine-overview.md`, `docs/318-kernel-tunables-and-sysctls-as-evidence.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r173

- Make policy evaluator code drift mechanically reviewable by introducing a typed policy module diff surface: `policy.module.diff` (schema + example) plus a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/451-policy-module-diff-as-review-surface.md`, `spec/policy.module.diff.schema.json`, `spec/examples/policy.module.diff.json`).
- Wire `policy.module.diff` into the canonical diff surface registry, drift bundle posture guidance, the evidence spine, and the policy-module juicy lesson so changes in policy-module authority (hostcalls/limits) stay explainable and gateable without forks (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `spec/examples/risk.flag.registry.json`).
- Refresh wiring/version stamps (`docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r172

- Add a guardrail that keeps per-diff review-surface docs uniform and mechanically jumpable: `tools/check_diff_review_docs.py` enforces Tier placement, requires the canonical `Registry→Diff→Gate` token, and requires schema+example pointers; wire it into `python3 tools/hygiene.py` and document the invariant in archive hygiene (`tools/check_diff_review_docs.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`).
- Entropy-reducing refactor: add an explicit “The artifacts” schema/example block to the adapter-kill and impurity-waiver diff wiring docs so reviewers can jump directly to contracts (`docs/444-adapter-kill-policy-diff-as-review-surface.md`, `docs/445-impurity-waiver-policy-diff-as-review-surface.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r171

- Make `/dev` authority drift mechanically reviewable by introducing a typed devfs view diff surface: `devfs.view.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/450-devfs-view-diff-as-review-surface.md`, `spec/devfs.view.diff.schema.json`, `spec/examples/devfs.view.diff.json`).
- Wire `devfs.view.diff` into the canonical diff surface registry, drift bundle posture guidance, and the evidence spine; extend the canonical risk-flag vocabulary with stable `/dev` exposure reason codes (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `spec/examples/risk.flag.registry.json`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r170

- Complete Broker→Lease→Receipt evidence by introducing generic lease issuance + use receipts: `lease.issue.receipt` and `lease.use.receipt` (schemas + examples) plus a tight wiring doc (keeps temporary authority explainable and bundle-friendly without forks) (`docs/449-lease-issue-and-use-receipts.md`, `spec/lease.issue.receipt.schema.json`, `spec/examples/lease.issue.receipt.json`, `spec/lease.use.receipt.schema.json`, `spec/examples/lease.use.receipt.json`).
- Update the lease registry and evidence spine to treat issuance/use as first-class evidence (and fix a small lease-envelope reference miswire); update the pattern catalog to point at the canonical receipts (`docs/249-lease-registry-and-cross-lane-revocation.md`, `docs/229-evidence-spine-overview.md`, `docs/397-pattern-catalog.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r169

- Make exported support bundles self-describing by introducing a typed bundle payload member manifest artifact: `bundle.payload.manifest` (schema + example) and a tight wiring doc (turns “what was in the bundle?” into queryable evidence) (`docs/448-bundle-payload-manifest-as-evidence-artifact.md`, `spec/bundle.payload.manifest.schema.json`, `spec/examples/bundle.payload.manifest.json`).
- Tighten bundle build receipts to optionally bind the payload manifest digest (`bundle.build.receipt.output.payload_manifest_digest`) and refresh the deterministic export lane doc + evidence spine so plan→bytes→members stays replayable without forks (`spec/bundle.build.receipt.schema.json`, `spec/examples/bundle.build.receipt.json`, `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/229-evidence-spine-overview.md`).
- Update curated references with the OCI image digest/manifest model pointer and refresh wiring/version stamps; regenerate generated discovery surfaces (`docs/32-curated-references.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-02-28r168

- Make offline mirror kits self-describing by introducing a typed kit manifest artifact: `mirror.kit.manifest` (schema + example) and a tight wiring doc for evidence/receipt binding (keeps air-gap imports explainable and resumable without forks) (`docs/447-mirror-kit-manifest-as-evidence-artifact.md`, `spec/mirror.kit.manifest.schema.json`, `spec/examples/mirror.kit.manifest.json`).
- Tighten mirror-kit import receipts to record the kit manifest digest when present (`mirror.import.receipt.source.kit_manifest_digest`), and refresh the air-gap mirror-kit lane doc + juicy lesson so operators can always answer "what exactly was on that kit?" with receipts (`spec/mirror.import.receipt.schema.json`, `spec/examples/mirror.import.receipt.json`, `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r167

- Make trust-policy drift mechanically reviewable by introducing a typed diff surface: `trust.policy.diff` (schema + example) with a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/446-trust-policy-diff-as-review-surface.md`, `spec/trust.policy.diff.schema.json`, `spec/examples/trust.policy.diff.json`).
- Wire `trust.policy.diff` into the canonical diff registry, drift bundle posture guidance, and the evidence spine; extend the canonical risk-flag vocabulary with a stable trust-policy drift reason code (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `spec/examples/risk.flag.registry.json`).
- Refresh wiring/version stamps (`docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r166

- Make “known impurity” non-ambient by introducing an explicit impurity waiver policy and a gateable diff surface: `impurity.waiver.policy` + `impurity.waiver.policy.diff` (schema + examples) with a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/445-impurity-waiver-policy-diff-as-review-surface.md`, `spec/impurity.waiver.policy.schema.json`, `spec/impurity.waiver.policy.diff.schema.json`, `spec/examples/impurity.waiver.policy.json`, `spec/examples/impurity.waiver.policy.diff.json`).
- Wire `impurity.waiver.policy.diff` into the canonical diff registry, drift bundle posture guidance, the evidence spine, and the determinism-check lane; extend the canonical risk-flag vocabulary with impurity waiver drift reason codes and add the primary Nix impurity reference to curated references (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/367-reproducible-generations-and-determinism-checks.md`, `spec/examples/risk.flag.registry.json`, `docs/32-curated-references.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r165

- Add an amnesia-resistor guardrail that keeps the meta-engineering "design law" docs discoverable: `tools/check_meta_doc_discoverability.py` requires every numbered doc >=397 to be linked from `docs/00-index.md` or `docs/110-juicy-os-lessons.md`; wire the check into `python3 tools/hygiene.py` and document the invariant in archive hygiene (`tools/check_meta_doc_discoverability.py`, `tools/hygiene.py`, `docs/98-archive-hygiene.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces (product profile matrix, context pack, doc catalog, risk index, artifact index).
## New in 2026-02-28r164

- Make adapter lanes *actually killable* by introducing an explicit adapter posture policy and a gateable diff surface: `adapter.kill.policy` + `adapter.kill.policy.diff` (schema + examples) with a tight wiring doc mapping it to Adapter→Shadow→Replace + Registry→Diff→Gate (`docs/444-adapter-kill-policy-diff-as-review-surface.md`, `spec/adapter.kill.policy.schema.json`, `spec/adapter.kill.policy.diff.schema.json`, `spec/examples/adapter.kill.policy.json`, `spec/examples/adapter.kill.policy.diff.json`).
- Wire `adapter.kill.policy.diff` into the canonical diff registry, drift bundle posture guidance, and the evidence spine so “interop toggles” stay explainable and gateable without forks; update adapter lane discipline and the killability juicy lesson (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/402-adapter-lanes-and-strangler-discipline.md`, `docs/110-juicy-os-lessons.md`).
- Extend the canonical risk-flag vocabulary with adapter kill/phase reason codes and refresh discovery/version wiring (`spec/examples/risk.flag.registry.json`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r163

- Make measured boot event logs explainable and replayable by introducing a typed canonical event log artifact: `boot.eventlog.canon` (schema + example) plus a tight wiring doc for bundle/export posture and verifier ergonomics (`docs/443-boot-eventlog-canon-as-evidence-artifact.md`, `spec/boot.eventlog.canon.schema.json`, `spec/examples/boot.eventlog.canon.json`).
- Flesh out the measured-boot lane to treat `boot.eventlog.canon` as the canonical object behind `boot.attestation.tpm.eventlog_digest`, and add an explicit `eventlog_canon` identifier to `boot.attestation` evidence for deterministic replay/verifier behavior (`docs/176-measured-boot-attestation.md`, `docs/313-boot-manifests-and-eventlog-replay.md`, `spec/boot.attestation.schema.json`, `spec/examples/boot.attestation.json`, `spec/examples/boot.manifest.json`).
- Wire the new evidence artifact into discovery and evidence UX surfaces (evidence spine + juicy lessons) and extend curated references with primary TCG CEL/PFP/event-log-processing specs (`docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/00-index.md`).

## New in 2026-02-28r162

- Fix the execution-integrity authority boundary: accept an ADR that keeps `exec.integrity.policy` / `exec.integrity.plan` / `exec.integrity.receipt` as the authoritative lane, binds execution-integrity planning to `runtime_manifest_digest` + `stratum_stack_digest` + `mount_view_digest`, keeps `exec-verify-snapshot` / `exec-verify-event` as backend observations, and narrows interpreters/loaders/writable bytes into one operable rule (`adrs/ADR-0076-exec-integrity-authority-and-verified-execution-boundary.md`, `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`).
- Rewire the verified-exec drift surface and activation plumbing around the authoritative lane by tightening `exec.verify.policy.diff`, switching change sets to `apply-exec-integrity`, and adding a guardrail that prevents future drift across policy/plan/receipt/runtime-composition joins (`spec/exec.integrity.plan.schema.json`, `spec/exec.integrity.receipt.schema.json`, `spec/exec.verify.policy.diff.schema.json`, `spec/examples/exec.integrity.plan.json`, `spec/examples/exec.integrity.receipt.json`, `spec/examples/exec.verify.policy.diff.json`, `spec/change.set.schema.json`, `spec/examples/change.set.json`, `tools/check_exec_integrity_contract.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).
- Extend the canonical risk-flag vocabulary with verified-exec drift reason codes (disable/relax/exception) and refresh wiring/version stamps (`spec/examples/risk.flag.registry.json`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r161

- Make incident/support bundle **plan drift** mechanically reviewable by introducing a typed bundle plan diff surface: `bundle.plan.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/441-bundle-plan-diff-as-review-surface.md`, `spec/bundle.plan.diff.schema.json`, `spec/examples/bundle.plan.diff.json`).
- Wire `bundle.plan.diff` into the canonical diff surface registry (keeps review surfaces discoverable and gateable) and update the bundle export lane + juicy lessons to reference the stable diff surface (`docs/430-diff-surface-registry.md`, `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/110-juicy-os-lessons.md`).
- Refresh wiring/version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r160

- Add a guardrail that keeps the canonical risk-flag registry wired to real review surfaces: `tools/check_risk_flag_typical_sources.py` validates that each `typical_sources` entry in `risk.flag.registry` points at a real schema under `spec/` and that any `*.diff` sources are listed in the canonical diff surface registry (`docs/430-diff-surface-registry.md`).
- Wire the new check into `python3 tools/hygiene.py` and document the invariant in archive hygiene guidance (`docs/98-archive-hygiene.md`).
- Refresh discovery/version stamps (`docs/00-index.md`, `README.md`, `docs/110-juicy-os-lessons.md`) and regenerate generated discovery surfaces.

## New in 2026-02-28r159

- Make attestation admission policy drift mechanically reviewable by introducing a typed diff surface: `attestation.admission.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/440-attestation-admission-policy-diff-as-review-surface.md`, `spec/attestation.admission.policy.diff.schema.json`, `spec/examples/attestation.admission.policy.diff.json`).
- Wire the new diff surface into the canonical diff registry, drift bundle posture-diff guidance, the evidence spine, and the Keylime/admission juicy lesson so “what is attestation-gated?” stays explainable and gateable without forks (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Extend the open-questions register with the remaining admission-policy drift/gate questions and refresh discovery/version wiring (`docs/266-open-questions-and-risk-register.md`, `docs/00-index.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-02-28r158

- Make kernel module policy drift mechanically reviewable by introducing a typed module policy diff surface: `kmod.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/439-kmod-policy-diff-as-review-surface.md`, `spec/kmod.policy.diff.schema.json`, `spec/examples/kmod.policy.diff.json`).
- Wire `kmod.policy.diff` into the canonical diff surface registry and drift bundle posture-diff guidance, and update the evidence spine + kernel module lane + juicy lessons so “privileged code allowlists” stay explainable and gateable without forks (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/110-juicy-os-lessons.md`, `docs/266-open-questions-and-risk-register.md`).
- Extend the canonical risk-flag vocabulary with kmod policy drift reason codes (e.g. `kmod-policy-runtime-load-enabled`) and refresh discovery/version stamps + regenerate generated discovery surfaces (`spec/examples/risk.flag.registry.json`, `docs/00-index.md`, `README.md`).

## New in 2026-02-28r157

- Make time-source posture drift mechanically reviewable by introducing a typed time source policy diff surface: `time.source.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/438-time-source-policy-diff-as-review-surface.md`, `spec/time.source.policy.diff.schema.json`, `spec/examples/time.source.policy.diff.json`).
- Extend the canonical risk-flag vocabulary with time authority drift reason codes (e.g. `time-quorum-relaxed`, `time-bootstrap-relaxed`) and wire the new diff surface into the canonical diff registry, drift bundle guidance, and the evidence spine (`spec/examples/risk.flag.registry.json`, `docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Refresh discovery/version stamps and regenerate generated discovery surfaces (`docs/00-index.md`, `README.md`).

## New in 2026-02-28r156

- Harden discovery-surface drift control by extending `python3 tools/check_discovery.py` to require that the newest `## New in <version>` block is the **first** such block in `docs/00-index.md`, and that the index carries a valid `Last updated:` stamp matching the current version.
- Update archive hygiene guidance to reflect the new invariant (`docs/98-archive-hygiene.md`) and bump version stamps / regenerate generated discovery surfaces.

## New in 2026-02-28r155

- Add an incremental guardrail that ties the canonical diff surface registry to the canonical `risk_flags` vocabulary: diff wiring docs must declare a `## Risk flags` section (or be explicitly allowlisted) so gates and review UI have a stable jump-to reason-code surface (`tools/check_diff_wiring_risk_flags.py`, `tools/baselines/diff_wiring_missing_risk_flags.txt`, `docs/98-archive-hygiene.md`, `docs/430-diff-surface-registry.md`).
- Refactor the sandbox/sysctl/export diff wiring docs to declare their minimal starter `risk_flags` sets (keeps posture drift gateable without forks): `docs/432-sandbox-profile-diff-as-review-surface.md`, `docs/429-sysctl-diff-as-drift-surface.md`, `docs/433-export-policy-diff-as-review-surface.md`.


## New in 2026-02-28r154

- Add a Tier C optional lane describing **split secrets brokers** (Split GPG / Split SSH style): keep private keys in a more trusted compartment and delegate bounded crypto operations via Broker→Lease→Receipt; interop via Adapter→Shadow→Replace (`docs/437-split-secrets-brokers.md`).
- Wire the new lane into the juicy lessons discovery surface and curated references (keeps citations centralized) (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`).
- Update the open-questions/risk register entry for the crypto operations portal to include split-secrets workflow questions (`docs/266-open-questions-and-risk-register.md`).


## New in 2026-02-27r153

- Make boot-critical closure drift mechanically reviewable by introducing a typed boot manifest diff surface: `boot.manifest.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/436-boot-manifest-diff-as-review-surface.md`, `spec/boot.manifest.diff.schema.json`, `spec/examples/boot.manifest.diff.json`).
- Extend the canonical diff surface registry and drift bundle guidance to include `boot.manifest.diff` as a posture diff attachment (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`) and wire it into the evidence spine and measured-boot lesson so “what did we boot?” stays explainable (`docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`).
- Extend the canonical risk-flag vocabulary with boot-drift reason codes (`bootloader-changed`, `kernel-image-changed`, `cmdline-profile-changed`) and refresh version stamps + regenerate generated discovery surfaces (`spec/examples/risk.flag.registry.json`, `README.md`, `CHANGELOG.md`).



## New in 2026-02-27r152

- Add a canonical risk-flag vocabulary registry (`risk.flag.registry`) so `risk_flags` reason codes used by diff summaries and gates stay explicit, stable, and profile-aware without forks (`docs/435-risk-flags-registry-and-gate-vocabulary.md`, `spec/risk.flag.registry.schema.json`, `spec/examples/risk.flag.registry.json`).
- Add a drift guardrail (`tools/check_risk_flag_registry.py`) wired into `python3 tools/hygiene.py` to prevent ad-hoc risk-flag strings (requires canonical kebab-case ids in spec examples and in gate docs lines mentioning `risk_flags`).
- Entropy-reducing refactor: normalize existing diff examples + gate docs to canonical kebab-case risk flags (keeps review surfaces mechanically gateable); update curated references with primary policy engine pointers used by the new doc, bump version stamps, and regenerate generated discovery surfaces.


## New in 2026-02-27r151

- Entropy-reducing refactor: extend the canonical diff surface registry to include a per-diff wiring doc pointer (so every `*.diff` review surface has a direct jump-to for gate semantics + bundle attachment): `docs/430-diff-surface-registry.md`.
- Add a new guardrail check (`tools/check_diff_surface_registry_wiring.py`) and wire it into `python3 tools/hygiene.py`; document the invariant in archive hygiene (`docs/98-archive-hygiene.md`).
- Extend the “registries + diffs + gates” juicy lesson with the canonical diff registry discipline (`docs/110-juicy-os-lessons.md`), bump version stamps, and regenerate generated discovery surfaces (`docs/00-index.md`).


## New in 2026-02-27r150

- Make trust root drift mechanically reviewable by introducing a typed trust bundle diff artifact: `pki.trust.bundle.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/434-pki-trust-bundle-diff-as-review-surface.md`, `spec/pki.trust.bundle.diff.schema.json`, `spec/examples/pki.trust.bundle.diff.json`).
- Wire `pki.trust.bundle.diff` into the canonical diff surface registry, drift bundle guidance, the evidence spine, and the trust roots juicy lesson; extend the trust bundle open-question block with default gating questions (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`, `docs/110-juicy-os-lessons.md`, `docs/266-open-questions-and-risk-register.md`).
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.



## New in 2026-02-27r149

- Make data-egress boundary drift mechanically reviewable by introducing a typed export policy diff artifact: `export.policy.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles (`docs/433-export-policy-diff-as-review-surface.md`, `spec/export.policy.diff.schema.json`, `spec/examples/export.policy.diff.json`).
- Update the canonical diff surface registry and drift bundle guidance to include export boundary diffs (`docs/430-diff-surface-registry.md`, `docs/395-drift-bundles-and-review-summaries.md`) and wire export diffs into the evidence spine (`docs/229-evidence-spine-overview.md`).
- Extend the export portal juicy lesson (#122) with export boundary drift discipline and add the primary sosreport upstream reference to curated references (`docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`); capture remaining export boundary drift questions in the risk register (`docs/266-open-questions-and-risk-register.md`).



## New in 2026-02-27r148

- Make sandbox posture changes mechanically reviewable by introducing a typed sandbox profile diff artifact: `sandbox.profile.diff` (schema + example) and a tight wiring doc mapping it to Registry→Diff→Gate + drift bundles: `docs/432-sandbox-profile-diff-as-review-surface.md`, `spec/sandbox.profile.diff.schema.json`, `spec/examples/sandbox.profile.diff.json`.
- Update the canonical diff surface registry to include `sandbox.profile.diff` (`docs/430-diff-surface-registry.md`) and refactor drift bundle guidance to eliminate redundant lists while still calling out posture diffs (`docs/395-drift-bundles-and-review-summaries.md`).
- Wire sandbox profile diffs into evidence + discovery surfaces (`docs/229-evidence-spine-overview.md` + juicy lesson #225 in `docs/110-juicy-os-lessons.md`), update this discovery surface (`docs/00-index.md`), bump version stamps, and regenerate generated discovery surfaces.

## New in 2026-02-27r147

- Add a juicy-lessons citation guardrail (`tools/check_juicy_lesson_references.py`) that blocks *new* uncataloged external URLs in `docs/110-juicy-os-lessons.md` without forcing retroactive churn (uses a baseline allowlist under `tools/baselines/`; documented in `docs/98-archive-hygiene.md`).
- Add a conservative Tier C stabilization lane note + typed receipt artifact for explicit determinism normalizers: `build.stabilizer.receipt` (schema + example) and a tight mapping doc (`docs/431-build-stabilizers-and-determinism-normalizers.md`).
- Extend curated references with primary reproducible-builds normalization sources (SOURCE_DATE_EPOCH + strip-nondeterminism + OSS-Rebuild stabilizers).
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## New in 2026-02-27r146

- Add a canonical diff surface registry (`docs/430-diff-surface-registry.md`) so the set of typed `*.diff` review surfaces stays explicit and stable as the archive grows (reduces review-surface entropy; improves drift bundle UX).
- Add a new guardrail check (`tools/check_diff_surface_registry.py`) and wire it into `python3 tools/hygiene.py`, preventing new `*.diff` schemas from landing without being listed in the registry (documented in `docs/98-archive-hygiene.md`).
- Refactor drift bundle guidance to reference the canonical registry (reduces duplication and keeps the review funnel stable): `docs/395-drift-bundles-and-review-summaries.md`.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## New in 2026-02-27r145

- Make kernel knob posture drift reviewable by introducing a typed sysctl plan diff artifact: `spec/sysctl.diff.schema.json`, `spec/examples/sysctl.diff.json`, plus a tight wiring doc mapping the lane to Plan→Receipt + Registry→Diff→Gate and drift bundles (`docs/429-sysctl-diff-as-drift-surface.md`).
- Wire `sysctl.diff` into the review funnel and evidence spine (`docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`), extend juicy lesson #183 with “planned sysctl diffs” (`docs/110-juicy-os-lessons.md`), and refresh the kernel mutation control open question block (`docs/266-open-questions-and-risk-register.md`).
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## New in 2026-02-27r144

- Make platform posture drift reviewable by introducing a typed firmware inventory diff surface: `fw.inventory.diff` (schema + example) and a tight wiring doc (`docs/428-fw-inventory-diff-as-drift-surface.md`). This turns firmware/UEFI posture changes (including Secure Boot digest summaries) into a gateable, exportable diff artifact.
- Wire `fw.inventory.diff` into the review funnel and evidence spine (`docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`) and extend juicy lesson #187 with “firmware posture diffs” (`docs/110-juicy-os-lessons.md`).
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## New in 2026-02-27r143

- Add a release-scope stamp guardrail: `tools/check_release_last_updated.py` requires docs mentioned in the newest `CHANGELOG.md` entry to carry the current release `Last updated:` stamp.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## New in 2026-02-27r142

- Make `/etc` drift a first-class, typed diff surface by introducing `etc.config.diff` (schema + example) and a tight wiring doc that maps it to Registry→Diff→Gate + drift bundles: `docs/427-etc-config-diff-as-a-drift-surface.md`, `spec/etc.config.diff.schema.json`, `spec/examples/etc.config.diff.json`.
- Wire `/etc` drift diffs into the review funnel and evidence spine (`docs/395-drift-bundles-and-review-summaries.md`, `docs/229-evidence-spine-overview.md`) and add a juicy lesson subchapter on `/etc` drift discipline (`docs/110-juicy-os-lessons.md`).
- Extend curated references with the FreeBSD `etcupdate(8)` primary reference (keeps citations centralized): `docs/32-curated-references.md`.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.

## New in 2026-02-27r141

- Make store retention *explainable* by adding typed GC artifacts: `store.gc.plan` and `store.gc.receipt` (schemas + examples) and a tight doc that maps GC to Plan→Receipt + policy gates (`docs/426-store-gc-plans-and-receipts.md`).
- Close a paper-artifact gap by adding typed pin receipts used by GC roots: `spec/pin.add.receipt.schema.json`, `spec/pin.rm.receipt.schema.json` plus examples (matches RFC-0110 and `docs/175-pins-roots-and-garbage-collection.md`).
- Wire GC receipts into the evidence spine and extend GC ergonomics with “retention as evidence” (`docs/229-evidence-spine-overview.md`, `docs/175-pins-roots-and-garbage-collection.md`, `docs/110-juicy-os-lessons.md`).
- Extend curated references with primary Nix GC docs (keeps citations centralized): `docs/32-curated-references.md`.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.


## New in 2026-02-27r140

- Add a drift guardrail: `tools/check_doc_patterns.py` requires meta docs (>=397) to declare `**Patterns:**` near the top (explicit mapping to the pattern catalog; stable review surface).
- Refactor the meta-doc range (>=397) to include `**Patterns:**` metadata and tighten `docs/397-pattern-catalog.md` + `docs/99-llm-runbook.md` to treat explicit pattern mapping as part of the archive contract.
- Wire the new check into `python3 tools/hygiene.py` and document it in `docs/98-archive-hygiene.md`.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.


## New in 2026-02-27r139

- Add an optional TPM-sealed secrets lane with typed, diffable PCR policies: `docs/425-tpm-sealed-secrets-and-pcr-policies.md`, `spec/tpm.pcr.policy.schema.json`, `spec/examples/tpm.pcr.policy.json`.
- Add a release drift guardrail: `tools/check_release_curated_references.py` ensures numbered docs mentioned in the newest `CHANGELOG.md` entry do not introduce external URLs without also adding them to `docs/32-curated-references.md` (keeps citations centralized for new work).
- Wire the new guardrail into `python3 tools/hygiene.py` and document it in `docs/98-archive-hygiene.md`; update curated references with TPM sealing + PCR measurement sources.
- Extend juicy lesson #59 with TPM-sealed secrets as a high-leverage optional lane (`docs/110-juicy-os-lessons.md`).
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.


## New in 2026-02-27r138

- Add a schema drift guardrail: `tools/check_schema_kind_matches_filename.py` enforces that dotted-kind schemas keep a stable schema naming discipline (e.g. `spec/mirror.import.receipt.schema.json` declares kind `mirror.import.receipt`) (prevents kind/filename mismatch drift).
- Wire the new check into `python3 tools/hygiene.py` and document it in `docs/98-archive-hygiene.md`.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.


## New in 2026-02-27r137

- Add a changelog-format guardrail (`tools/check_changelog_format.py`) and normalize CHANGELOG spacing to keep release notes compact and diff-friendly.
- Document the new guardrail in `docs/98-archive-hygiene.md` and keep the hygiene wrapper wired.
- Bump version stamps, update this discovery surface (`docs/00-index.md`), and regenerate generated discovery surfaces.


## New in 2026-02-27r136

- Make bundle-min builds first-class evidence by adding the typed `bundle.build.receipt` artifact (schema + example) and wiring it into deterministic export + incident bundle guidance (`docs/253-bundle-plans-and-deterministic-exports.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/229-evidence-spine-overview.md`).
- Reduce drift by unifying the bundle include-knob surface: `spec/incident.bundle.schema.json` now defines `#/$defs/include_knobs`, and `spec/bundle.plan.schema.json` references it (keeps selection plans aligned with bundle include knobs).
- Extend juicy lesson #99 with the plan+build-receipt discipline, bump version stamps, and regenerate generated discovery surfaces (`docs/110-juicy-os-lessons.md`, `docs/414-doc-catalog.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`).


## New in 2026-02-27r135

- Make offline mirror kits concrete as typed **Plan→Receipt** artifacts for quarantine-first imports and policy-gated promotion: add `mirror.import.plan`/`mirror.import.receipt`/`mirror.promote.plan`/`mirror.promote.receipt` (schemas + examples) and update `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`.
- Add a drift guardrail to prevent “paper artifacts”: `tools/check_changelog_artifact_mentions.py` ensures docs referenced by the newest `CHANGELOG.md` entry don't mention non-existent typed artifacts; wired into `tools/hygiene.py` and documented in `docs/98-archive-hygiene.md`.
- Extend curated references with the Uptane Standard and add a new juicy lesson on offline update ergonomics (`docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).
- Bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`).


## New in 2026-02-27r134

- Add an optional forward-secure event log sealing lane (tamper-evident local evidence) by introducing the typed `event.seal.receipt` artifact and wiring it into the evidence docs: `docs/424-forward-secure-event-log-sealing.md`, `spec/event.seal.receipt.schema.json`, `spec/examples/event.seal.receipt.json`, plus updates to `docs/215-structured-event-log-as-evidence.md`, `docs/229-evidence-spine-overview.md`, and `docs/110-juicy-os-lessons.md`.
- Reduce refresh friction by extending the context pack generator to include a compact “Recent changes” section sourced from `CHANGELOG.md` (Markdown + JSON), and regenerate `docs/420-context-pack.md` + `docs/_generated/context_pack.json` (`tools/gen_context_pack.py`).
- Update curated references with official FSS/digest-chain sources and bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `README.md`, `CHANGELOG.md`).


## New in 2026-02-27r133

- Make the “reproducible generations” lane concrete by adding typed Plan→Receipt artifacts for determinism checks: `docs/367-reproducible-generations-and-determinism-checks.md`, `spec/repro.check.plan.schema.json`, `spec/repro.check.receipt.schema.json`, `spec/examples/repro.check.plan.json`, `spec/examples/repro.check.receipt.json`.
- Wire determinism receipts into the review funnel by adding `repro.check.receipt` as an optional drift-bundle attachment (`docs/395-drift-bundles-and-review-summaries.md`) and regenerate the artifact index so `kind → schema → example` stays current (`docs/418-artifact-index.md`, `docs/_generated/artifact_index.json`).
- Bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `README.md`, `CHANGELOG.md`).

## New in 2026-02-27r132

- Add **persist sets** as a stable diff surface for “what is allowed to persist” (impermanence/stateless-root lesson): `docs/423-persist-sets-and-ephemeral-root.md`, `spec/persist.set.registry.schema.json`, `spec/examples/persist.set.registry.json`.
- Strengthen anti-amnesia release wiring: `tools/check_discovery.py` now enforces that any numbered docs mentioned in the newest `CHANGELOG.md` entry are linked from the appropriate discovery surface (index vs juicy lessons) *and* appear in the matching “New in …” section.
- Update discovery wiring + curated references for the new lane, and bump version stamps (`docs/00-index.md`, `docs/110-juicy-os-lessons.md`, `docs/32-curated-references.md`, `docs/98-archive-hygiene.md`, `README.md`).

## New in 2026-02-27r131

- Add an **invariant registry** as a stable diff surface (Registry → Diff → Gate): `docs/422-invariant-registry-and-design-invariants.md`, `spec/invariant.registry.schema.json`, `spec/examples/invariant.registry.json`.
- Fix a quiet “must-read drift” hole: normalize the runbook’s mandatory refresh list and harden the context pack generator to extract **all** backticked items (so `docs/01-glossary.md` and `docs/02-derive-core.md` can’t disappear from the generated pack).
- Add a new guardrail to prevent accidental refresh-path erosion: `tools/check_must_read_set.py` (wired into `tools/hygiene.py`).

## New in 2026-02-27r130

- Add a research **disposable workspace** lane (Template → Lease → Dispose) translated from Qubes TemplateVM/DisposableVM into DeriveBSD patterns and evidence surfaces: `docs/421-disposable-workspaces-and-template-microvms.md`.
- Add a guardrail that keeps **external URLs** for meta docs (>=397) centralized in `docs/32-curated-references.md`: new check `tools/check_curated_references.py` wired into `tools/hygiene.py`.
- Tighten version stamp discipline: extend `tools/check_version.py` to also validate the top-level `Last updated:` tags on `README.md`, `docs/110-juicy-os-lessons.md`, and `docs/00-index.md`.

## New in 2026-02-27r129

- Add a generated **context pack** (Markdown + JSON) as a first-class “amnesia resistor”, so a single file captures current version, must-read set, A–D summary, and top risks: `docs/420-context-pack.md`, `docs/_generated/context_pack.json`, `tools/gen_context_pack.py`.
- Wire the context pack into discovery + hygiene: `tools/check_generated_docs.py` validates it, and `tools/check_discovery.py` requires it to be linked from this index.

## New in 2026-02-27r128

- Add a typed **incident timeline** artifact (`incident.timeline`) as a human-scale orientation surface for incidents (schema + example + doc): `docs/419-...`, `spec/incident.timeline.schema.json`.
- Wire timelines into the evidence spine and support bundle story: incident bundles can include an `incident.timeline` digest, and causality graphs now explicitly pair with timeline views.
- Refresh structured output contract with a canonical domain output example for incident timelines (`docs/87-structured-output-contract.md`).

## New in 2026-02-27r127

- Make A–D **profile naming** mechanically stable: canonical ids live in `spec/examples/product.profiles.json`, and a single alias map lives in `spec/product.profile_aliases.json`.
- Strengthen doc metadata guardrails: meta docs can list either A–D or canonical ids; tools normalize and detect duplicates.
- Improve the generated profile matrix and context pack so “what profile is this?” is always answerable.

## New in 2026-02-27r126

- Add a generated **artifact index** (Markdown + JSON) that maps `kind` → canonical schema → example(s), to make typed outputs discoverable and reduce LLM/human navigation friction (`docs/418-artifact-index.md`, `docs/_generated/artifact_index.json`, `tools/gen_artifact_index.py`).
- Fix a drift hole: `tools/check_generated_docs.py` now actually checks the risk register index outputs (and also validates the new artifact index), so generated discovery surfaces can't silently stale.
- Add a lightweight **spec example coverage** guardrail and wire it into hygiene, ensuring every plan/receipt/event/report/registry/diff schema has a matching example (`tools/check_spec_example_coverage.py`, `tools/hygiene.py`).

## New in 2026-02-27r125

- Add a typed **platform provenance report** (`platform-report`) and a tight doc that binds platform/firmware lifecycle into the evidence model (`docs/417-...`, `spec/platform.report.schema.json`).
- Treat firmware lifecycle as derived ops using the existing `fw.update.*` artifacts, and refresh the structured output contract to include the new domain output (`docs/87-...`).
- Tighten curated references for firmware/UEFI tooling (fwupd/LVFS, FreeBSD fwget/efivar, DICE) and add a new juicy lesson item tying it together.

## New in 2026-02-27r124

- Add a first-class **policy trace** artifact (schema + example) and a doc that binds `derive explain-policy` to stable JSON traces (`docs/416-...`, `spec/policy.trace.schema.json`).

This is a living design archive for **DeriveBSD**: a hypervisor-centric, BSD-native, planned-from-scratch successor to Nix-like systems.

We keep it small by:
- **one concept per file**
- proposals in **RFCs**, decisions in **ADRs**
- **links/citations** instead of copying external text

## Reading paths

### 0) Running the archive (humans + LLMs)
- LLM runbook (invariants + must-read + output contract): `docs/99-llm-runbook.md`
- Context pack (generated short refresh + JSON pack): `docs/420-context-pack.md`, `docs/_generated/context_pack.json`
- Product profiles as compilation targets (A–D, no forks): `docs/411-product-profiles-as-compilation-target.md`
- Product profiles artifact (example): `spec/examples/product.profiles.json`
- Product profiles matrix (generated): `docs/412-product-profile-matrix.md`
- Removable-media / USB posture by profile: `docs/458-removable-media-and-usb-posture-by-profile.md`
- Outbound-network posture by profile: `docs/459-outbound-network-posture-by-profile.md`
- Packet capture / raw sockets / fast packet I/O boundary: `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`
- Packet capture session + summary-first export boundary: `docs/507-packet-capture-session-and-summary-first-export-boundary.md`
- Packet capture summary review surface: `docs/508-packet-capture-summary-review-surface-boundary.md`
- Packet capture selector compiler boundary: `docs/509-packet-capture-selector-compiler-boundary.md`
- Packet capture local-artifact metadata and retention boundary: `docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md`
- Packet capture stronger export approval evidence boundary: `docs/515-packet-capture-strong-export-approval-evidence-boundary.md`
- Packet capture stronger export transport boundary: `docs/516-packet-capture-strong-export-transport-boundary.md`
- Packet capture stronger export recipient-digest confirmation boundary: `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`
- Packet capture stronger export remote-object continuity boundary: `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`
- Packet capture stronger export remote-validator continuity boundary: `docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`
- Packet capture stronger export remote-protection posture boundary: `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`
- Packet capture stronger export remote-locator continuity boundary: `docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`
- Remote assistance posture by profile: `docs/461-remote-assistance-posture-by-profile.md`
- Private-key / crypto-operation posture by profile: `docs/462-private-key-and-crypto-op-posture-by-profile.md`
- Operator-access posture by profile: `docs/467-operator-access-posture-by-profile.md`
- Trustworthy-time posture by profile: `docs/468-trustworthy-time-posture-by-profile.md`
- Platform provenance / attestation-admission posture by profile: `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`
- Firmware-update posture by profile: `docs/471-firmware-update-posture-by-profile.md`
- Human identity / home-state posture by profile: `docs/463-human-identity-and-home-state-posture-by-profile.md`
- Backup / restore posture by profile: `docs/464-backup-and-restore-posture-by-profile.md`
- Data-at-rest posture by profile: `docs/465-data-at-rest-posture-by-profile.md`
- Doc catalog (generated nav map + JSON index): `docs/414-doc-catalog.md`, `docs/_generated/doc_catalog.json`
- Risk register index (generated summary + JSON): `docs/415-risk-register-index.md`, `docs/_generated/risk_register.json`
- Artifact index (generated schema→kind→example + JSON): `docs/418-artifact-index.md`, `docs/_generated/artifact_index.json`
- Context pack generator (memory prosthetic): `tools/gen_context_pack.py`


### 1) The Derive pipeline (Spec → Lock → Plan → Artifact)
- Vision + glossary: `docs/00-vision.md`, `docs/01-glossary.md`
- Day-0 behaviors: `docs/97-non-negotiable-behaviors.md`
- The pipeline contract: `docs/02-derive-core.md`
- Spec authoring frontends (compile-to-IR): `docs/79-derive-spec-frontends.md`, `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`, ADR-0023
- Store + hashing: `docs/03-store.md`, `docs/56-store-layout-and-digests.md`
- Long-term source availability (SWHID fallback): `docs/403-swhid-fallback-and-long-term-source-availability.md`
- Closure proofs: `docs/90-closure-proof.md`, `docs/92-verification-matrix.md`
- Policy decision records: `docs/93-policy-decision-records.md`
- Policy trace format + explain surfaces: `docs/416-policy-trace-format-and-explain-surfaces.md`
- Platform provenance + firmware lifecycle as derived ops: `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`, `spec/platform.report.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`
- DevShells (developer UX parity): `docs/159-devshells.md`, `adrs/ADR-0039-devshells-first-class.md`
- Sandbox + hardening: `docs/04-sandbox.md`, `docs/45-build-sandbox-jails.md`, `docs/49-capsicum-casper-hardening.md`, `docs/325-rootless-jails-and-unprivileged-compartments.md`
- Hostile builders: `docs/91-hostile-builders.md`
- Trust + caches: `docs/46-cache-trust-model.md`, `docs/61-channel-metadata-tuf-inspired.md`, `docs/127-uptane-director-targets.md`, `adrs/ADR-0009-artifact-verification.md`
  - immutable objects + revocable name indirection (Amoeba lesson): `docs/345-amoeba-bullet-server-and-capability-directories.md`
  - optional full TUF metadata adapter (interop + delegations): `docs/203-full-tuf-metadata-adapter.md`
  - optional transparency evidence: `docs/131-sigsum-lightweight-transparency.md`, `docs/132-scitt-ledger-receipts.md`, `docs/324-transparent-key-directories-and-minimal-tlogs.md`
  - optional cache witness quorums (reproducibility corroboration): `docs/190-cache-witness-quorums-trustix.md`
- Trust policy as data: `docs/57-namespaces-channels-trust.md`, `spec/trust.policy.schema.json` (+ drift review surface: `docs/446-trust-policy-diff-as-review-surface.md`, `spec/trust.policy.diff.schema.json`)
- Shadow trust prevention (system CA governance): `docs/327-shadow-trust-and-system-ca-governance.md`
- Publisher identity receipts (keyless signing, optional): `docs/290-keyless-signing-and-publisher-identity-receipts.md`, `docs/333-sigstore-bundles-and-offline-verification.md`, `docs/487-keyless-identity-evidence-and-offline-verification-boundary.md`, `spec/publisher.identity.receipt.schema.json`, `spec/sigstore.bundle.schema.json`
- Provenance + SBOM: `docs/31-provenance-and-sbom.md`, `docs/71-attestations-dsse-in-toto-slsa.md`, `docs/75-sbom-formats-spdx-cyclonedx.md`
- Supply-chain workflow policy (in-toto layouts, optional): `docs/202-in-toto-layouts-and-step-policy.md`
- SBOM + VEX evidence objects (policy-bound inventory + exploitability): `docs/168-sboms-and-vex-as-evidence.md`
- Vulnerability intelligence + gates (optional; snapshot + receipts): `docs/60-vulnerability-intel-and-gates.md`, `docs/338-vulnerability-snapshots-query-receipts-and-openvex.md`
- Artifact knowledge graph (GUAC-style) + supply-chain queries: `docs/334-artifact-knowledge-graph-and-supply-chain-queries.md`
- Tests as evidence (optional policy gate): `docs/166-test-receipts-and-promotion-gates.md`
- Fuzzing as evidence (optional long-running gate): `docs/274-continuous-fuzzing-farm.md`
- Fuzz target classes + flake-aware promotion boundary: `docs/499-fuzz-target-classes-and-flake-aware-promotion-gate-boundary.md`
- Policy: `docs/30-policy-engine.md`, `docs/85-policy-engine-options-and-traces.md`
- Process topology / least authority: `docs/96-process-topology.md`
- Unit manifests as component declarations (capability-first, contract-bound): `docs/344-derive-unit-manifests-and-capability-routing.md`
- Hermetic component test realms (realm-builder-style; tests as routed capabilities): `docs/354-realm-builder-style-hermetic-component-tests.md`
- Wasm component model / WIT as a standard contract language (digestable interfaces): `docs/356-wasm-component-model-and-wit-contracts.md`
- Contract registries + API diff gates (interfaces are versioned surfaces): `docs/370-contract-registries-and-api-diff-gates.md`
- Parser surface registry + fuzz gates (treat “new parser” as first-class drift): `docs/376-parser-surface-registry-and-fuzz-gates.md`
- Surface registries as a meta-pattern (keep drift gateable as the system grows): `docs/379-surface-registry-pattern.md`
- Pattern catalog (keep new subsystems in a small set of reusable shapes): `docs/397-pattern-catalog.md`
- Spec schema conventions + evolution (keep artifacts legible as the archive grows): `docs/407-spec-schema-conventions-and-evolution.md`
- v0 cutline + feature tiers (keep the project shippable): `docs/401-v0-cutline-and-feature-tiers.md`
- Adapter lanes + strangler discipline (interop without forever-legacy): `docs/402-adapter-lanes-and-strangler-discipline.md`
- Drift bundles (one review attachment that summarizes all drift surfaces): `docs/395-drift-bundles-and-review-summaries.md`, `spec/drift.bundle.schema.json`
- Closure diffs (make “new code ingestion” reviewable): `docs/396-closure-diffs-and-new-code-surfaces.md`, `spec/closure.diff.schema.json`
- Deprecation policies + removal receipts (no silent breaks): `docs/385-deprecation-policies-and-removal-receipts.md`, `spec/deprecation.notice.schema.json`
- Safe boundary APIs (kernel boundary is also a contract surface): `docs/361-safe-crossing-apis-and-boundary-bugs-lessons-from-tock.md`
- Userspace driver/kernel-subsystem testing lane (rump kernels lesson): `docs/355-rump-kernels-and-userspace-driver-testing.md`
- Kernel extensibility (BPF/JIT risk) is authority (lease-gated, brokered, diffable): `docs/384-kernel-extensibility-bpf-and-jit-risk.md`
- Promise profiles (reviewable least-authority declarations): `docs/232-service-promise-profiles.md`, `docs/271-promise-profile-vocabulary-and-lint.md`, `spec/sandbox.profile.schema.json`
- Learned promise profiles (observation mode; tighten-by-running): `docs/326-learned-promise-profiles-and-observation-mode.md`
- Denial-driven policy suggestions (denials → reviewable policy patches): `docs/378-denial-driven-policy-suggestions.md`
- Policy tests as artifacts (suites + reports + mutation, optional): `docs/393-policy-tests-suites-and-mutation.md`, `spec/policy.test.suite.schema.json`, `spec/policy.test.report.schema.json`
- Policy analysis as evidence (automated reasoning, optional high-assurance lane): `docs/394-policy-analysis-and-automated-reasoning.md`
- Learned network policies (audit mode; flows → reviewable diffs): `docs/328-learned-network-policies-from-flow-receipts.md`
- Network learn/audit convergence contract (bounded session + evidence summary + review-before-enforce): `docs/505-network-learn-audit-convergence-contract.md`
- Learned resource budgets (observation mode; usage → reviewable diffs): `docs/329-learned-resource-budgets-and-observation-mode.md`
- Oblivious sandboxing launchers (Capsicum by default; preopen maps as artifacts): `docs/294-oblivious-sandboxing-launchers.md`, `docs/180-capability-mode-dynamic-linking.md`
- Exec integrity policy + verified execution (no unverified code runs, optional backend): `docs/289-exec-integrity-policy-and-verified-execution.md`, `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`, `spec/exec.integrity.policy.schema.json`, `spec/exec.integrity.plan.schema.json`, `spec/exec.integrity.receipt.schema.json`, `spec/exec.verify.policy.diff.schema.json`
- Outbound-network posture by profile (A–D defaults): `docs/459-outbound-network-posture-by-profile.md`
- Private-key / crypto-operation posture by profile (A–D defaults): `docs/462-private-key-and-crypto-op-posture-by-profile.md`
- Human identity / home-state posture by profile (A–D defaults): `docs/463-human-identity-and-home-state-posture-by-profile.md`
- Data-at-rest posture by profile (A–D defaults): `docs/465-data-at-rest-posture-by-profile.md`
- Remote assistance posture by profile (A–D defaults): `docs/461-remote-assistance-posture-by-profile.md`
- Network egress broker + flow receipts (outbound is a lease, not ambient): `docs/281-network-egress-broker-and-consent.md`, `spec/net.egress.policy.schema.json`, `spec/net.egress.grant.schema.json`, `spec/net.flow.receipt.schema.json`
  - DNS mediation + hostname binding (optional receipt lane): `docs/305-dns-mediation-and-hostname-binding.md`, `spec/net.dns.query.receipt.schema.json`
  - DNS receipt detail/export posture by profile (keep qname detail local-first and bounded): `docs/504-dns-receipt-detail-and-export-posture-by-profile.md`
- Inbound listen broker + firewall leases (listening is a lease, not ambient): `docs/286-inbound-listen-broker-and-firewall-leases.md`, `spec/net.listen.policy.schema.json`, `spec/net.listen.grant.schema.json`, `spec/net.listen.receipt.schema.json`
- Relay-backed publish sessions for temporary service sharing (bounded B/C share path; durable ingress stays on `net.listen.*`): `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`, `spec/net.publish.session.schema.json`
- Publish-session audience binding and publicness posture (B/C human sharing stays audience-bound by default; `public-link` / `public-webhook` are explicit exception postures): `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`, `spec/net.publish.session.schema.json`
- Publish-session end conditions and no-auto-resume posture (temporary shares are reboot-cleared and must be recreated as a new session with fresh authority): `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md`, `spec/net.publish.session.schema.json`
- Publish-session session-scoped locator posture (public/org/support relay locators stay session-scoped; `tailnet-device-name` is the only stable-name exception): `docs/565-publish-session-session-scoped-locator-posture-boundary.md`, `spec/net.publish.session.schema.json`
- Publish-session tailnet reverse-forward posture (private tailnet/device-name sharing stays `reverse-forward` shaped instead of borrowing URL-share vocabulary): `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md`, `spec/net.publish.session.schema.json`
- Publish-session audience-bound human-share relay-url posture (`organization-users` and `named-recipients` stay `relay-url` shaped instead of borrowing support-peer or tailnet vocabulary): `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md`, `spec/net.publish.session.schema.json`
- Publish-session relay remote-locator posture (`relay.remote_locator.kind` now follows access model so URI/session/device grammar cannot contradict the chosen share shape): `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md`, `spec/net.publish.session.schema.json`
- Publish-session relay remote-locator-value posture (`relay.remote_locator.value` now follows locator kind so non-URI lanes cannot hide URI-looking value text): `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md`, `spec/net.publish.session.schema.json`
- Publish-session audience-bound share binding-hint posture (`provider-identity` / `organization-users` shares name `identity_provider_hint`, and `named-recipients` shares name `recipient_hint`): `docs/573-publish-session-audience-bound-shares-require-binding-hints.md`, `spec/net.publish.session.schema.json`
- Publish-session redacted locator + separate secret handoff posture (usable secrets stay off locator/evidence surfaces): `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md`, `spec/net.publish.session.schema.json`
- Publish-session secret handoff lifetime posture (share secrets die with session authority): `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md`, `spec/net.publish.session.schema.json`
- Publish-session secret consumption posture (`single-use-secret` versus `shared-secret` stays explicit): `docs/568-publish-session-secret-consumption-semantics-boundary.md`, `spec/net.publish.session.schema.json`
- Publish-session support-peer authority join posture (`support-peer` shares require `authority.trigger = support-session` plus `authority.support_session_digest`): `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md`, `spec/net.publish.session.schema.json`
- Host network topology + firewall substrate as derived operations (links/routes/pf root ruleset are receipted): `docs/322-network-topology-and-firewall-as-derived-operations.md`, `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`, `spec/net.topology.event.schema.json`
- Optional netgraph/netmap fabrics (graph-shaped datapaths + VALE fast path): `docs/400-netgraph-and-netmap-as-derived-network-fabrics.md`
- Workload identity + secretless deploys (SPIFFE/SPIRE-shaped, optional lane): `docs/181-workload-identity-and-secretless-deploys.md`, `spec/workload.identity.lease.schema.json`, `spec/workload.identity.issue.receipt.schema.json`, `spec/workload.identity.grant.schema.json`
- Desktop viability checklist (constraints to keep profile B possible): `docs/410-desktop-viability-checklist.md`
- Disposable workspaces (Template → Lease → Dispose; Qubes lessons, optional lane): `docs/421-disposable-workspaces-and-template-microvms.md`
- Portals / mediated dynamic access: `docs/179-portals-and-powerbox.md`
- Persistent file capabilities (bookmarks): `docs/198-persistent-file-capabilities-bookmarks.md`
- Intent routing (plumber-style): `docs/199-intent-routing-and-plumbing.md`
- Data transfer portals (clipboard / drag&drop): `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- Workstation cross-domain data-transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- Notification portal (non-observing): `docs/206-notification-portal-non-observing.md`
- Input authority (secure attention + HID risk): `docs/207-input-authority-secure-attention-and-hid-risk.md`
- Screen sharing + remote control (screencast + injected input): `docs/208-screencast-and-remote-desktop-portals.md`
- Camera + audio capture portals: `docs/209-camera-and-audio-capture-portals.md`
- Portal sessions + permission store: `docs/210-portal-sessions-and-permission-store.md`
- Location portal: `docs/211-location-portal.md`
- Printing portal: `docs/212-printing-portal.md`
- Sanitization portal (open safely; disposable sandbox transform): `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- Origin labels + quarantine attributes (imports): `docs/280-origin-labels-and-quarantine-attributes.md`
- Information-flow labels + explicit declassification (optional lane): `docs/381-information-flow-labels-and-declassification.md`
- Attribute-indexed metadata + live queries (BFS lesson): `docs/293-attribute-indexed-metadata-and-live-queries.md`
- Evidence queries over fact tables (osquery-shaped ergonomics, but derived and receipted): `docs/399-evidence-queries-and-fact-tables.md`
- Portable home areas + embedded user records (optional lane): `docs/269-portable-home-areas-and-user-records.md`
- AppVM storage contract (template/private/volatile + optional home areas): `docs/270-appvm-storage-private-volatile-and-home-areas.md`
- Toolchain trust hardening (optional DDC lane): `docs/191-diverse-double-compiling-and-bootstrappable-toolchains.md`
  - optional Zig toolchain wedge for cross-compiling C/C++ dependencies: `docs/398-zig-toolchain-wedge-and-cross-compilation.md`

### 2) Host systems (atomic switch, ZFS generations)
- Activation + switching: `docs/06-system-activation.md`, `docs/86-host-activation-rcd-and-service-jails.md`, `docs/404-zfs-boot-environments-as-system-generations.md`
- Service supervision + compiled service DB: `docs/214-service-supervision-health-as-evidence.md`, `docs/114-service-manifests-smf-lessons.md`, `docs/173-compiled-service-database-bundles.md`, `docs/235-process-contracts-and-service-ownership.md`, `docs/239-service-lifecycle-restarters-and-repo.md`, `docs/349-supervision-trees-and-restart-strategies.md`, `docs/352-crash-only-and-roc-for-system-services.md`, `docs/238-portal-activated-services-and-socket-activation.md`, `docs/240-dynamic-service-identities.md`, `docs/342-minix-self-healing-and-reincarnation.md`
- State datasets + migrations as evidence: `docs/217-state-datasets-and-migrations-as-evidence.md`, `spec/statedb.schema.json`, `spec/state.snapshot.schema.json`, `spec/state.migration.plan.schema.json`, `spec/state.migration.receipt.schema.json`
- Persist sets + ephemeral root (explicit persistence boundary; diffable + gateable): `docs/423-persist-sets-and-ephemeral-root.md`, `spec/persist.set.registry.schema.json`
  - checkpoint boundaries + durable identities (orthogonal persistence lessons): `docs/347-orthogonal-persistence-and-checkpointed-systems.md`
- Optional activation broker (restart-safe handle escrow): `docs/196-capability-activation-and-escrow.md`
- ZFS boot environments: `docs/69-host-generations-bectl.md`, `docs/284-bootenv-switching-as-evidence.md`, `docs/27-vm-storage-zfs.md`, `docs/126-zfs-send-distribution.md`
- Health-gated updates + boot assessment: `docs/112-health-gated-updates.md`, `docs/241-boot-try-counters-and-boot-assessment.md`, `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`, `spec/boot.health.gate.policy.schema.json`, `spec/boot.health.report.schema.json`, `spec/boot.bless.receipt.schema.json`
- Slot-based A/B update mental model (Android/ChromeOS lessons): `docs/359-slot-based-updates-and-boot-assessment-lessons.md`

- Installation + recovery as derived operations (installer/recovery images as artifacts; install as change sets): `docs/309-installation-and-recovery-as-derived-operations.md`, `docs/250-breakglass-and-recovery-workflows.md`
- Derived recovery images + minimal userspace (repair ergonomics as artifacts): `docs/360-derived-recovery-images-and-minimal-userspace.md`
- Disk layout plans/receipts (partitioning as evidence): `docs/310-disk-layout-plans-and-receipts.md`, `spec/disk.layout.plan.schema.json`, `spec/disk.layout.receipt.schema.json`
- Hardware inventory + driver binding as evidence (privacy-safe, digest-first): `docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `spec/hw.inventory.receipt.schema.json`
- Hardware compatibility gates (preflight before switching generations): `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `spec/hw.compat.report.schema.json`
- Hardware support matrices (bundled approved-hardware catalogs for release/reset admission): `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`, `spec/hw.support.matrix.schema.json`
- Firmware inventory + updates + UEFI variable writes as evidence (no platform drift folklore): `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `docs/336-uefi-capsules-esrt-and-fwupd-practice-notes.md`, `docs/337-secure-boot-certificate-rotation-and-fleet-trust.md`, `spec/fw.inventory.receipt.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`, `spec/uefi.var.set.plan.schema.json`, `spec/uefi.var.set.receipt.schema.json`

- Operator access as leases (SSH certs; session evidence; optional TTY recording): `docs/311-operator-access-leases-and-ssh-certs.md`, `spec/operator.session.schema.json`, `docs/292-terminal-session-recording-as-evidence.md`
- Operator-access posture by profile (A–D defaults): `docs/467-operator-access-posture-by-profile.md`
- Trustworthy-time posture by profile (A–D defaults): `docs/468-trustworthy-time-posture-by-profile.md`
- Platform provenance / attestation-admission posture by profile (A–D defaults): `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`
- Firmware-update posture by profile (A–D defaults): `docs/471-firmware-update-posture-by-profile.md`
- Data at rest (ZFS encryption + key management lanes, A–D viable): `docs/409-zfs-encryption-and-key-management.md` (see also: `docs/146-zfs-native-encryption-for-generations.md`)
- Data-at-rest posture by profile (A–D defaults): `docs/465-data-at-rest-posture-by-profile.md`
- Optional OCI host transport (bootc lessons): `docs/133-bootable-oci-host-images-bootc-lessons.md`
- Secure boot hooks (optional): `docs/51-secure-boot-integration.md`, `docs/244-bootchain-revocation-and-allowlists.md`, `docs/245-boot-measurement-phases-and-pcr-separation.md`, `docs/337-secure-boot-certificate-rotation-and-fleet-trust.md`
- Measured boot + posture receipts (optional, explainable): `docs/176-measured-boot-attestation.md`, `docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/313-boot-manifests-and-eventlog-replay.md`, `docs/332-tpm-attestation-in-practice-pcr-registry-uki-keylime.md`, `spec/boot.manifest.schema.json`, `spec/boot.attestation.schema.json`
- Unified boot capsules (single signed/measurable boot payload): `docs/358-unified-boot-capsules-and-measured-boot-receipts.md`
- Measured launch / DRTM lane (late launch integrity, optional): `docs/390-measured-launch-and-drtm-trenchboot-lane.md`
- Attester provisioning receipts (optional, makes enrollment auditable/operable): `docs/314-attester-provisioning-and-key-lifecycle-receipts.md`, `spec/attester.provision.receipt.schema.json`

### 3) Hypervisor-centric runtime (microVM-first)
- Direction + rationale: `docs/22-scope-and-direction.md`, `docs/23-hypervisor-centric-derivebsd.md`
- MicroVM artifact target: `docs/24-microvm-artifact-target.md`, `docs/73-artifact-target-framework.md`
- Optional ABI compatibility adapter lane (Linux emulation vs microVMs): `docs/408-abi-compatibility-lanes-linuxulator-vs-microvms.md`
- Runtime manifest + bundle format: `docs/33-runtime-manifest-schema.md`, `docs/34-microvm-bundle-format.md`, `docs/128-image-registry-imgadm-lessons.md`
- Optional verified lazy rootfs mounts (on-demand): `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`
- Accepted lazy-mount authority / fallback / evidence boundary: `docs/527-verified-lazy-tree-mount-materialization-and-evidence-boundary.md`
- Optional P2P distribution/swarm caches (fleet rollout acceleration): `docs/301-p2p-distribution-and-swarm-caches.md`
- Control plane: `docs/29-vm-control-plane.md`
- Launch plans + receipts (runtime join key; receipts even on denial): `docs/455-microvm-launch-plans-and-receipts.md`, `spec/microvm.launch.plan.schema.json`, `spec/microvm.launch.receipt.schema.json`
- bhyve backend mapping: `docs/40-bhyve-config-mapping.md`, `docs/25-hypervisor-backends.md`
- IO/control channels: `docs/72-bhyve-io-channels.md`
- Runtime blast-radius contract: `docs/94-runtime-blast-radius-contract.md`
- Optional confidential microVMs (TEE-backed isolation + attestable receipts): `docs/330-confidential-microvms-and-tee-attestation-as-evidence.md`, `docs/331-tee-attestation-in-practice-snp-tdx-and-verifier-services.md`, `spec/tee.attestation.reference.schema.json`, `spec/tee.attestation.evidence.schema.json`, `spec/tee.attestation.receipt.schema.json`
- Networking: `docs/26-virtual-networking-pf.md`, `docs/67-pf-anchors-per-instance.md`, `docs/64-networking-modes-mapping.md`, `docs/322-network-topology-and-firewall-as-derived-operations.md`
- Device isolation domains (driver VMs): `docs/204-device-isolation-domains.md`
- Device grants + /dev authority (devfs rulesets): `docs/278-device-grants-and-devfs-rulesets.md`
- Devfs views as derived operations (plans/receipts/events for `/dev` exposure): `docs/323-devfs-views-plans-and-receipts.md`, `spec/devfs.view.plan.schema.json`
- USB quarantine + removable media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- Removable-media / USB posture by profile (A–D defaults): `docs/458-removable-media-and-usb-posture-by-profile.md`
- Outbound-network posture by profile (A–D defaults): `docs/459-outbound-network-posture-by-profile.md`
- Private-key / crypto-operation posture by profile (A–D defaults): `docs/462-private-key-and-crypto-op-posture-by-profile.md`
- Resource governance (limits + optional budget capabilities): `docs/65-resource-governance.md`, `docs/143-resource-controls-rctl-racct-cpuset.md`, `docs/193-resource-budget-capabilities.md`, `docs/247-resource-budgets-and-limits-as-evidence.md`, `docs/285-hierarchical-resource-limits-compilation.md`
  - QoS/accounting discipline (isolation + exposure + responsibility): `docs/346-nemesis-isolation-exposure-responsibility.md`
- Rollout + rollback: `docs/35-workload-rollout-rollback.md`

### 4) “Explainability” surfaces (why/what/where-from)
- Explainability contract: `docs/95-explainability-contract.md`
- Policy replay + counterfactual explanations: `docs/312-policy-replay-and-counterfactual-explanations.md`
- Structured outputs: `docs/87-structured-output-contract.md`, `docs/38-structured-outputs.md`
- Diff + review workflows: `docs/66-diff-and-review-workflows.md`
- Repro capsules: `docs/39-repro-capsules.md`
- Observability evidence (DTrace/audit): `docs/120-observability-explainability-dtrace.md`, `docs/248-tracing-observability-as-evidence.md`, `docs/52-host-auditing-openbsm.md`
- Structured diagnostics (Inspect-style trees) as queryable state: `docs/302-structured-diagnostics-inspect-trees.md`
- Diagnostics query plane (selectors + snapshots; Archivist-style): `docs/372-inspect-style-structured-introspection.md`
- Flight recorder tracing + budgeted diagnostics (always-on, bounded): `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`
- Evidence vault (write-once, content-addressed history for receipts/traces): `docs/350-venti-fossil-write-once-archive-store.md`
- Observability as capability (no ambient debug authority): `docs/192-observability-as-capability.md`
- Structured event journal (typed logs as evidence): `docs/215-structured-event-log-as-evidence.md`
- Optional event sealing receipts (tamper-evident local evidence): `docs/424-forward-secure-event-log-sealing.md`, `spec/event.seal.receipt.schema.json`
- Durable attestation / posture timelines (time series of verifier receipts, retention budgeted): `docs/315-durable-attestation-and-posture-timelines.md`, `spec/attestation.receipt.schema.json`
- Remote attestation admission policy (make “what is gated?” reviewable, optional): `docs/388-remote-attestation-admission-and-enrollment.md`, `spec/attestation.admission.policy.schema.json`, `spec/attestation.requirement.schema.json`
- Attestation result vs issued-authority boundary (verifier evidence stays evidence-only; action receipts stay authoritative): `docs/492-attestation-results-evidence-and-admission-issue-boundary.md`, `spec/attestation.receipt.schema.json`, `spec/secret.receipt.schema.json`, `spec/breakglass.receipt.schema.json`, `spec/workload.identity.issue.receipt.schema.json`
- Incident snapshots + support bundles (shareable context as evidence): `docs/216-incident-snapshots-and-support-bundles.md`
- Incident timelines (human-scale orientation surface): `docs/419-incident-timelines-as-derived-artifacts.md`, `spec/incident.timeline.schema.json`
- Hardware inventory receipts + hardware compat reports (supportability without SSH; preflight safety): `docs/319-hardware-inventory-and-driver-binding-as-evidence.md`, `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`, `spec/hw.inventory.receipt.schema.json`, `spec/hw.compat.report.schema.json`
- Hardware support matrices (approved-hardware catalogs that travel with release/reset bundles): `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`, `spec/hw.support.matrix.schema.json`
- Time-travel snapshots as leases ("previous versions" without ambient snapshot exposure): `docs/300-time-travel-snapshots-as-leases.md`
- Export policies + support-bundle portal (user/policy-mediated sharing): `docs/251-export-policies-and-support-bundle-portal.md`
- Remote assistance sessions as evidence (screen share + control without backdoors): `docs/291-remote-assistance-sessions-as-evidence.md`, `spec/support.session.schema.json`
- Terminal session recording as evidence (TTY I/O logs, optional): `docs/292-terminal-session-recording-as-evidence.md`, `spec/tty.session.recording.schema.json`
- Bundle plans + deterministic exports (selection+transforms as evidence): `docs/253-bundle-plans-and-deterministic-exports.md`
- Export transparency logs (prove what left the system, optional): `docs/254-export-transparency-logs.md`
- Release capsules + transparency (single verifiable release handle): `docs/257-release-capsules-and-transparency.md`
- Transparency monitors + witness gossip (alerts as evidence): `docs/259-transparency-monitors-and-witness-gossip.md`
- Witness networks + checkpoint cosigning (split-view defense as an operable parameter): `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`, `spec/log.checkpoint.receipt.schema.json`
- Release authority policy (threshold publishing + emergency halts): `docs/260-release-authority-policy-and-key-management.md`
- Rollout privacy constraints (cohort hygiene): `docs/261-rollout-privacy-and-cohort-hygiene.md`
- Policy-constrained transports (ticketing uploads as evidence, optional): `docs/255-policy-constrained-transports.md`
- Consent UX contract (uniform approvals across GUI/TTY/OOB): `docs/256-consent-ux-contract.md`
- Multiparty approvals + separation of duties (quorum approvals as evidence): `docs/288-multiparty-approvals-and-separation-of-duties.md`

- Causality graphs (minimal evidence index): `docs/246-causality-graphs-and-minimal-evidence-bundles.md`
- Crash artifacts + symbolication as evidence (crash reports, dumps, build-id symbols): `docs/224-crash-artifacts-and-symbolication-as-evidence.md`, `spec/crash.report.schema.json`
- State snapshot + migration receipts (what schema changed, and why): `docs/217-state-datasets-and-migrations-as-evidence.md`
- Backups + restores as derived operations (state replication + rehearsed recovery as evidence): `docs/316-backups-and-restores-as-derived-operations.md`, `docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md`, `docs/317-restore-drills-and-continuous-recovery-testing.md`, `docs/464-backup-and-restore-posture-by-profile.md`, `spec/backup.plan.schema.json`, `spec/backup.receipt.schema.json`, `spec/restore.drill.receipt.schema.json`
- Configuration transactions + receipts (commit-confirmed for risky changes): `docs/218-configuration-transactions-and-receipts.md`
- /etc drift diffs as a stable review surface (gateable; attach to drift bundles): `docs/427-etc-config-diff-as-a-drift-surface.md`
- Change sets + apply engine (unify multi-step transitions): `docs/219-change-sets-and-apply-engine.md`
- Kernel tunables + sysctls as evidence (no mystery knobs; drift is a fact): `docs/318-kernel-tunables-and-sysctls-as-evidence.md`, `spec/sysctl.plan.schema.json`, `spec/sysctl.receipt.schema.json`, `spec/sysctl.event.schema.json`
- Kernel module policy + loading as evidence (treat kmods as executable code): `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `spec/kmod.policy.schema.json`, `spec/kmod.load.plan.schema.json`, `spec/kmod.load.receipt.schema.json`, `spec/kmod.event.schema.json`
- Secrets and key management as evidence (brokered creds, no inline secrets): `docs/223-secrets-and-key-management-as-evidence.md`
- Crypto operations portal (split keys; sign/decrypt by lease + receipts): `docs/306-crypto-operations-portal-and-split-keys.md`, `spec/crypto.op.request.schema.json`, `spec/crypto.op.receipt.schema.json`
- Private-key / crypto-operation posture by profile: `docs/462-private-key-and-crypto-op-posture-by-profile.md`
- Crypto key policies (non-exportable default; quorum + presence hooks): `docs/392-crypto-key-policies-and-nonexportable-handles.md`, `spec/crypto.key.policy.schema.json`
- Crypto surface registry + diff gates (protocol/suite/library drift is reviewable): `docs/391-crypto-surface-registry-and-agility-gates.md`, `spec/crypto.registry.schema.json`, `spec/crypto.diff.schema.json`
- PKI + trust bundles as evidence (trust-store is a versioned object; CA injection is digest-pinned): `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `spec/pki.trust.bundle.schema.json`, `spec/pki.issue.plan.schema.json`, `spec/pki.issue.receipt.schema.json`
- Sealed secrets + attested unsealing (TPM policy lane, optional): `docs/272-sealed-secrets-attested-unsealing.md`
- Platform posture + attestation receipts as evidence (reusable verifier results): `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- Firmware updates as artifacts (inventory + plans + receipts): `docs/221-firmware-updates-as-artifacts.md`
- Debugging by lease (record/replay capsules): `docs/194-debugging-by-lease-and-replay-capsules.md`
- Deterministic concurrency lane (optional; shrink replay capsules, tame heisenbugs): `docs/377-deterministic-concurrency-lane.md`
- Chaos experiments + fault injection as leases (optional; resilient-by-practice): `docs/389-chaos-experiments-and-fault-injection-as-leases.md`, `spec/chaos.experiment.plan.schema.json`, `spec/chaos.experiment.receipt.schema.json`
- Automated bisection + root-cause certificates (optional): `docs/275-root-cause-certificates-and-bisection.md`
- Lease envelope + cross-lane joins (unified temporary authority metadata): `docs/252-lease-envelope-and-cross-lane-joins.md`
- Operational time-travel debugging (replay capsules in change/incident workflows): `docs/220-operational-time-travel-debugging.md`
- Deterministic redaction transforms: `docs/195-deterministic-redaction-transforms.md`
- Time + entropy authority for determinism and replay: `docs/197-time-and-rng-authority.md`
- Time discipline + trustworthy timestamps as evidence: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`
- Time sources in practice (chrony NTS + Roughtime quorum): `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`
- Trustworthy-time posture by profile: `docs/468-trustworthy-time-posture-by-profile.md`
- Platform provenance / attestation-admission posture by profile: `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`
- Firmware-update posture by profile: `docs/471-firmware-update-posture-by-profile.md`
- Time monitors + lie detection (treat time like a transparency problem): `docs/308-time-monitors-and-lie-detection.md`
- Evidence spine overview (receipts everywhere): `docs/229-evidence-spine-overview.md`
- Capability activation + escrow (restart-safe authority, socket-activation generalized): `docs/196-capability-activation-and-escrow.md`

### 5) Mile-high directions (brainstorm → RFCs)

These are intentionally **short**: they capture promising paradigms and where they plug into the pipeline.

- Roadmap / idea inventory: `docs/99-mile-high-directions.md`
- Feature-harvest rubric (keep “ecosystem steals” disciplined): `docs/296-feature-harvest-rubric.md`
- “Deployments are commits” (ZFS-native): `docs/100-deployments-are-commits.md`
- CAS everywhere (beyond “binary cache”): `docs/101-cas-everywhere.md`
- Emergency patch mode (graft-like, auditable): `docs/102-emergency-grafts.md`
- Breakglass + recovery mode (repair without destroying evidence): `docs/236-breakglass-and-recovery-mode.md` (RFC-0168)
- Verified execution at runtime (optional MAC/veriexec): `docs/103-runtime-verified-execution.md`
- Builder strategy (jail builds + optional microVM builders): `docs/104-builder-tiers.md`
- Compatibility view for foreign binaries (libmap/hints): `docs/105-compat-view-foreign-binaries.md`
- Strata and multi-origin userlands (explicit composition of adapter trees): `docs/295-strata-and-multi-origin-userlands.md`
- Blast-radius diffs as first-class review: `docs/106-blast-radius-diff.md`
- Drift bundles as the default review attachment (link all diffs + evidence): `docs/395-drift-bundles-and-review-summaries.md`
- Authority graphs + `authority.diff` as a review substrate: `docs/366-capability-graphs-and-authority-diff-surfaces.md`
- Trust boundary graphs + threat diffs (new boundary = reviewable artifact): `docs/380-trust-boundary-graphs-and-threat-diff.md`
- Two-person integrity (separate approvals): `docs/107-two-person-integrity.md`
- Ports/pkg adapter lane (breadth without chaos): `docs/108-ports-pkg-adapter-lane.md`
- Repo signing UX lessons (pkg-style ergonomics): `docs/109-repo-signing-ux.md`
- Juicy OS lessons index: `docs/110-juicy-os-lessons.md`
- Feature flags as typed inputs (USE lessons): `docs/262-feature-flags-and-constraints.md`
- Flake-style input graphs + registries (composition lessons): `docs/263-flake-style-input-graphs-and-registries.md`
- Filesystem views as capabilities (Plan 9 union lessons): `docs/264-mount-namespaces-and-union-views.md`
- Portable service bundles (attach/detach ops tooling lane): `docs/265-portable-service-bundles.md`
- Open questions + risk register (what to decide next): `docs/266-open-questions-and-risk-register.md`
- Sanitization portal (Dangerzone-style disposable transform): `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- Desktop AppVMs + portalized apps (Qubes/Flatpak stance): `docs/268-desktop-appvms-and-portalized-apps.md`
- Consent ledgers + permission review UI: `docs/369-consent-ledgers-and-permission-review-ui.md`
- Permission center + authority introspection (review/revoke/explain in one place): `docs/371-permission-center-and-authority-introspection.md`
- Portable home areas + embedded user records (systemd-homed lesson): `docs/269-portable-home-areas-and-user-records.md`
- AppVM storage: template + private + volatile (+ optional home areas): `docs/270-appvm-storage-private-volatile-and-home-areas.md`
- Packaged base sets (pkgbase lessons): `docs/111-packaged-base-pkgbase.md`
- Health-gated updates (boot success gate): `docs/112-health-gated-updates.md`, `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`
- Signed revertible patchsets (syspatch-style): `docs/113-syspatch-style-patchsets.md`
- Service manifests as derived graphs (SMF lessons): `docs/114-service-manifests-smf-lessons.md`
- Compartmentalized control planes (Qubes lessons): `docs/115-compartmentalized-control-planes.md`
- Witness rebuilders + deep diffs: `docs/116-witness-rebuilders-diffoscope.md`
- Reproducible generations + determinism check lane: `docs/367-reproducible-generations-and-determinism-checks.md`
- Impurity waiver policy + gateable diff surface (keep “known impurity” non-ambient): `docs/445-impurity-waiver-policy-diff-as-review-surface.md`
- Pledge/unveil mindset (ergonomics): `docs/117-pledge-unveil-mindset.md`
- pledge/unveil-style promises compiled to Derive profiles: `docs/368-pledge-unveil-style-promises-and-derive-profiles.md`
- Distributed unprivileged builds (pbulk lessons): `docs/118-distributed-builds-pbulk.md`
- Store/image distribution adapters (casync/CernVM-FS): `docs/119-casync-cvmfs-distribution.md`
- Verified lazy rootfs + on-demand mounts (composefs/eStargz/Nydus): `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`
- Verified lazy tree mount / materialization / evidence boundary: `docs/527-verified-lazy-tree-mount-materialization-and-evidence-boundary.md`
- P2P distribution + swarm caches (Dragonfly lesson): `docs/301-p2p-distribution-and-swarm-caches.md`
- Observability as explainability (DTrace): `docs/120-observability-explainability-dtrace.md`
- Jailed hypervisor workers (bhyve-in-jail): `docs/121-jailed-hypervisor-workers.md`
- System extensions for immutable bases: `docs/122-system-extensions.md`
- Ignition-style first boot provisioning: `docs/123-ignition-style-firstboot.md`
- virtio-9p as a restricted file channel: `docs/124-virtio-9p-injection-channel.md`
- Per-jail hardening knobs (secadm mindset): `docs/125-hardening-knobs-per-jail.md`
- ZFS send/recv distribution lane: `docs/126-zfs-send-distribution.md`
- Uptane “director” role (bytes vs assignment): `docs/127-uptane-director-targets.md`
- Image registry lessons (SmartOS imgadm/IMGAPI): `docs/128-image-registry-imgadm-lessons.md`
- Template microVMs and disposable instances (Qubes disk model): `docs/129-template-microvms-and-disposables.md`
- ZFS bookmarks and redaction bookmarks (sanitized replication): `docs/130-zfs-bookmarks-and-redaction.md`
- Sigsum transparency lane (lightweight): `docs/131-sigsum-lightweight-transparency.md`
- SCITT ledger receipts (publication evidence): `docs/132-scitt-ledger-receipts.md`
- Bootable OCI host images (bootc lessons): `docs/133-bootable-oci-host-images-bootc-lessons.md`
- Declarative image pipelines (apko/melange/Wolfi lessons): `docs/134-declarative-image-pipelines-apko-melange.md`
- Cross-compartment RPC policy (qrexec lessons): `docs/135-qrexec-style-rpc-policy.md`
- Remote execution API builder pools (REAPI lessons): `docs/136-remote-execution-api-builder-pools.md`
- Anti-rollback rollback indices (Verified Boot lesson): `docs/137-anti-rollback-rollback-index.md`
- Offline signed update bundles (RAUC/fwup lessons): `docs/138-offline-signed-update-bundles.md`
- Air-gap mirror kits + sneakernet updates (offline happy path): `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`
- Mirror kit manifest (self-describing offline kit index): `docs/447-mirror-kit-manifest-as-evidence-artifact.md`
- Bandwidth-efficient deltas (OSTree static deltas): `docs/139-bandwidth-efficient-deltas.md`
- Capability routing manifests (Fuchsia lessons): `docs/140-capability-routing-manifests.md`
- Component descriptors → compiled runtime manifests (single source of “how it runs”): `docs/297-component-descriptors-and-compiled-runtime-manifests.md`
- Build records (`.buildinfo` lessons) + witness rebuilders: `docs/141-build-records-buildinfo-and-rebuilders.md`
- Trustworthy time inputs (Roughtime + LKGT): `docs/142-trustworthy-time-roughtime.md`
- Trustworthy time: NTS + Roughtime + LKGT wiring: `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`
- Policy-derived resource budgets (rctl/racct/cpuset): `docs/143-resource-controls-rctl-racct-cpuset.md`
- Authority budgets + permission drift alarms (stop capability creep early): `docs/298-authority-budgets-and-permission-drift-alarms.md`
- Routing isolation via multiple FIBs (setfib): `docs/144-routing-isolation-fibs-setfib.md`
- Optional unikernel lane (Solo5/rump lessons): `docs/145-unikernel-lane-rump-solo5.md`
- Optional CHERI lane (capability hardware memory safety + compartmentalization): `docs/387-cheri-capability-hardware-and-memory-safety-lane.md`
- ZFS native encryption for state/generations (key-use evidence): `docs/146-zfs-native-encryption-for-generations.md`
- Minimal privilege escalation rules (doas-style): `docs/147-doas-minimal-privilege-escalation.md`
- Reproducibility variation harness (reprotest/diffoscope/stabilizers): `docs/148-reproducibility-variation-harness-reprotest.md`
- Human-editable policy sources (HuJSON) + canonical signing (JCS): `docs/149-human-policy-hujson-and-canonicalization.md`
- Frontend source / compile receipt / canonical IR boundary: `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`, `spec/frontend.compile.receipt.schema.json`
- Derive unit source / compile receipt / runtime boundary: `docs/500-derive-unit-source-compile-receipt-and-runtime-boundary.md`, `spec/derive.unit.compile.receipt.schema.json`
- Support-bundle intake typed plan / receipt shapes: `docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md`, `spec/content.import.support-bundle.plan.schema.json`, `spec/content.import.support-bundle.receipt.schema.json`
- Telemetry is not a product-profile default boundary: `docs/503-telemetry-is-not-a-product-profile-default-boundary.md`
- DNS receipt detail / export posture by profile: `docs/504-dns-receipt-detail-and-export-posture-by-profile.md`
- Network learn/audit convergence contract: `docs/505-network-learn-audit-convergence-contract.md`, `spec/net.flow.summary.schema.json`
- Jail profiles as derived allowlists (allow.* knobs + devfs rulesets): `docs/150-jail-profiles-and-allowlist-knobs.md`
- Factotum-style credential broker (protocol-agnostic agent): `docs/151-factotum-style-credential-broker.md`
- Store view minimization (hide non-required store paths from builders): `docs/152-store-view-minimization.md`
- sandboxfs-accelerated store views (optional performance optimization): `docs/167-sandboxfs-accelerated-storeviews.md`
- Store immutability invariants (prevent post-build mutation / TOCTOU): `docs/153-store-immutability-and-toc-tou.md`
- SBOM + VEX as evidence objects (inventory + exploitability context): `docs/168-sboms-and-vex-as-evidence.md`
- Jobsets + build farms (Hydra lessons): `docs/169-jobsets-and-build-farms.md`
- Remote cache threat model (poisoning + verification): `docs/170-remote-cache-threat-model.md`
- VNET jails as network compartments (separate per-domain stacks): `docs/171-vnet-jails-network-compartments.md`
- Hypervisor device backend isolation (hardening lane): `docs/172-device-backend-isolation-bhyve.md`
- Compiled service database + bundles (s6-rc lessons): `docs/173-compiled-service-database-bundles.md`
- Specialisations/variants within a generation (safe-mode, role-mode): `docs/174-specialisations-and-variants.md`
- Pins/roots and garbage collection (retention ergonomics): `docs/175-pins-roots-and-garbage-collection.md`
- Receipted store GC plans/receipts (retention as evidence): `docs/426-store-gc-plans-and-receipts.md`, `spec/store.gc.plan.schema.json`, `spec/store.gc.receipt.schema.json`
- Measured boot + remote attestation lane (optional): `docs/176-measured-boot-attestation.md`
- Fleet-coordinated staged rollouts (optional): `docs/177-fleet-coordinated-rollouts.md`
- Sigstore keyless signing adapter (optional): `docs/178-sigstore-keyless-signing-adapter.md`
- Portals / powerbox broker (mediated capability acquisition): `docs/179-portals-and-powerbox.md`
- ScreenCast + RemoteDesktop portals (screen sharing + remote control): `docs/208-screencast-and-remote-desktop-portals.md`
- Camera + audio capture portals (AV devices as leased streams): `docs/209-camera-and-audio-capture-portals.md`
- Capability mode + dynamic linking strategy: `docs/180-capability-mode-dynamic-linking.md`
- Workload identity + secretless deploys (SPIFFE/SPIRE-shaped lane): `docs/181-workload-identity-and-secretless-deploys.md`
- Capability leases + revocation (revocable grants): `docs/182-capability-leases-and-revocation.md`
- Lease registry + cross-lane revocation (unify all temporary authority): `docs/249-lease-registry-and-cross-lane-revocation.md`
- Object-capability RPC lane (capability-carrying crossings): `docs/183-object-capability-rpc.md`
  - Contract channels as policy inputs (Singularity lesson): `docs/339-singularity-manifests-and-contract-channels.md`
  - FD-first capability IPC (Doors lesson): `docs/341-doors-lightweight-capability-rpc.md`
  - File-shaped broker APIs (Inferno lesson): `docs/340-inferno-styx-and-distributed-namespaces.md`
  - Capability-kernel lessons (KeyKOS/EROS): `docs/343-keykos-eros-capability-kernel-lessons.md`
- Attenuating delegation tokens (Macaroons/Biscuit lane): `docs/184-attenuating-delegation-tokens.md`
- Portal consent receipts (auditable interactive ask): `docs/185-portal-consent-and-audit-receipts.md`
- Policy modules as WebAssembly (sandboxed extensibility lane): `docs/186-policy-modules-wasm.md`
- Policy module diff as a review surface (gateable policy-code drift): `docs/451-policy-module-diff-as-review-surface.md`
- Witnessed transparency checkpoints (split-view defense): `docs/187-witnessed-transparency-checkpoints.md`
- Debugging by lease (record/replay capsules): `docs/194-debugging-by-lease-and-replay-capsules.md`
- Automated bisection + root-cause certificates (optional): `docs/275-root-cause-certificates-and-bisection.md`
- Lease envelope + cross-lane joins (unified temporary authority metadata): `docs/252-lease-envelope-and-cross-lane-joins.md`
- Deterministic redaction transforms: `docs/195-deterministic-redaction-transforms.md`
- Time + entropy authority for determinism and replay: `docs/197-time-and-rng-authority.md`
- Time discipline + trustworthy timestamps as evidence: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`
- Evidence spine overview (receipts everywhere): `docs/229-evidence-spine-overview.md`
- Capability activation + escrow (restart-safe authority, socket-activation generalized): `docs/196-capability-activation-and-escrow.md`
- DevShells (nix-shell parity): `docs/159-devshells.md`
- Overlay transforms (Nix overlay analogue): `docs/160-overlay-transforms.md`
- Module + options layer (NixOS-ish composition): `docs/161-module-and-options-layer.md`
- User environments (Home-Manager analogue): `docs/162-user-environments.md`
  - Activation plans/receipts (profiles, generations, atomic switch): `docs/386-userenv-activation-plans-and-receipts.md`, `spec/userenv.activate.plan.schema.json`, `spec/userenv.activate.receipt.schema.json`
- CHERI capability lane (optional hardening): `docs/163-cheri-capability-lane.md`
- CHERI temporal revocation vs authority revocation (design with indirection): `docs/250-cheri-temporal-revocation-and-indirection.md`
- Split crypto domains (split-GPG lesson): `docs/164-split-crypto-domains.md`
- FreeBSD pkg repository adapter (optional compatibility lane): `docs/165-freebsd-pkg-repo-adapter.md`
- Test receipts as evidence (promotion gates): `docs/166-test-receipts-and-promotion-gates.md`

### 6) Tests + promotion gates
- Conformance/regression harness: `docs/88-conformance-tests-kyua-atf.md`
- Test receipts as evidence: `docs/166-test-receipts-and-promotion-gates.md`
- Scenario tests (multi-machine): `docs/188-scenario-tests-multimachine.md`
- Interactive VM test driver + artifact capture: `docs/405-interactive-vm-tests-and-artifact-capture.md`
- Model checking as evidence: `docs/287-formal-model-checking-and-invariants.md` (starter models in `docs/models/`).

### 7) Authority graphs
- Capability routing manifests (Fuchsia lessons): `docs/140-capability-routing-manifests.md`
- Genode init + nested capability distribution lessons: `docs/375-genode-init-and-capability-routing-lessons.md`
- Component descriptors → compiled runtime manifests (single source of “how it runs”): `docs/297-component-descriptors-and-compiled-runtime-manifests.md`
- Capability graph lint/viz: `docs/189-capability-graph-lint-and-viz.md`
- Authority diff schema + review workflows: `docs/374-authority-diff-schema-and-review-workflows.md`

### 7.1) Observability and budgets as authority
- Observability authority as leased grants: `docs/192-observability-as-capability.md`
- Delegable resource budgets as grants (optional): `docs/193-resource-budget-capabilities.md`

### 8) Cache and toolchain trust (optional high-assurance lanes)
- Cache witness quorums (Trustix-style): `docs/190-cache-witness-quorums-trustix.md`
- DDC + bootstrappable toolchains: `docs/191-diverse-double-compiling-and-bootstrappable-toolchains.md`
- Proof artifacts and formal verification lanes (proofs as supply-chain evidence): `docs/373-proof-artifacts-and-formal-verification-lanes.md`

## Where to add new work

- New proposal → `rfcs/` (draft first)
- Accepted decision → `adrs/` (append-only)
- Consolidated “current truth” → `docs/` (short, updated)

## References

Start at: `docs/32-curated-references.md`
## New in 2026-02-27r123 (risk register index + risk lint)

- Add a generated **risk register index** (markdown + JSON) so `docs/266` stays scannable and machine-usable (`docs/415-risk-register-index.md`, `docs/_generated/risk_register.json`, `tools/gen_risk_register_index.py`).
- Add a simple **risk register lint** and wire into hygiene to keep failure modes explicit (`tools/check_risk_register.py`, `tools/hygiene.py`).
- Extend generated-doc guardrails + discovery wiring to cover the new risk index (`tools/check_generated_docs.py`, `tools/check_discovery.py`, `docs/98-archive-hygiene.md`, `docs/99-llm-runbook.md`).

## New in 2026-02-27r122 (doc catalog + generated-doc guardrail)

- Added a generated doc catalog + JSON index as a navigation/memory prosthetic: `docs/414-doc-catalog.md`, `docs/_generated/doc_catalog.json`, generator `tools/gen_doc_catalog.py`
- Extended generated-doc checks to cover the doc catalog outputs (prevents silent drift): `tools/check_generated_docs.py`

## New in 2026-02-27r121 (profile matrix + doc metadata guardrail + ZFS replication robustness)

- Add a generated **A–D product profile matrix** doc plus a generator + stale-check so profile defaults/invariants stay mechanically visible and don't drift (`docs/412-product-profile-matrix.md`, `tools/gen_product_profile_matrix.py`, `tools/check_generated_docs.py`).
- Add a lightweight **doc metadata** guardrail for the meta-engineering doc range (>=397): new docs must declare Tier/Profiles/Pillars near the top; wire check into hygiene (`tools/check_doc_metadata.py`, `tools/hygiene.py`).
- Add a tight ZFS replication operations doc focused on **resume tokens**, **bookmarks**, and **encryption-aware** replication, and wire it into backup/distribution lanes + profile defaults (`docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md`, `docs/316-backups-and-restores-as-derived-operations.md`, `docs/126-zfs-send-distribution.md`, `spec/examples/product.profiles.json`).

## New in 2026-02-27r120 (profiles + at-rest encryption + desktop viability + anti-amnesia tooling)

- [99 LLM runbook](99-llm-runbook.md)
- [411 Product profiles as compilation targets](411-product-profiles-as-compilation-target.md)
- [458 Removable media and USB posture by profile](458-removable-media-and-usb-posture-by-profile.md)
- [459 Outbound network posture by profile](459-outbound-network-posture-by-profile.md)
- [461 Remote assistance posture by profile](461-remote-assistance-posture-by-profile.md)
- [462 Private-key and crypto-operation posture by profile](462-private-key-and-crypto-op-posture-by-profile.md)
- [463 Human identity and home-state posture by profile](463-human-identity-and-home-state-posture-by-profile.md)
- [464 Backup and restore posture by profile](464-backup-and-restore-posture-by-profile.md)
- [465 Data-at-rest posture by profile](465-data-at-rest-posture-by-profile.md)
- [468 Trustworthy-time posture by profile](468-trustworthy-time-posture-by-profile.md)
- [469 Platform provenance and attestation-admission posture by profile](469-platform-provenance-and-attestation-admission-posture-by-profile.md)
- [471 Firmware-update posture by profile](471-firmware-update-posture-by-profile.md)
- [409 ZFS encryption and key management](409-zfs-encryption-and-key-management.md)
- [410 Desktop viability checklist](410-desktop-viability-checklist.md)

## New in 2026-02-27r119 (schema conventions + ABI compatibility lane)

- [407 Spec schema conventions and evolution](407-spec-schema-conventions-and-evolution.md)
- [408 ABI compatibility lanes: Linux emulation vs microVMs](408-abi-compatibility-lanes-linuxulator-vs-microvms.md)

## New in 2026-02-27r118 (interactive VM tests + UAPI fuzz descriptors)

- [405 Interactive VM tests and artifact capture](405-interactive-vm-tests-and-artifact-capture.md)
- [406 UAPI fuzz descriptors and conformance](406-uapi-fuzz-descriptors-and-conformance.md)

## New in 2026-02-27r117 (SWHID source archival + ZFS BE generation contract)

- [403 SWHID fallback + long-term source availability](403-swhid-fallback-and-long-term-source-availability.md)
- [404 ZFS boot environments as system generations](404-zfs-boot-environments-as-system-generations.md)

## New in 2026-02-27r116 (v0 cutline + killable adapters)

- [401 v0 cutline and feature tiers](401-v0-cutline-and-feature-tiers.md)
- [402 Adapter lanes and strangler discipline](402-adapter-lanes-and-strangler-discipline.md)

## New in 2026-02-27r115 (netgraph + netmap/VALE derived fabrics)

- [400 Netgraph and netmap as derived network fabrics](400-netgraph-and-netmap-as-derived-network-fabrics.md)

## New in 2026-02-27r114 (pattern catalog + Zig toolchain wedge + evidence queries)

- [397 DeriveBSD pattern catalog](397-pattern-catalog.md)
- [398 Zig toolchain wedge and cross compilation](398-zig-toolchain-wedge-and-cross-compilation.md)
- [399 Evidence queries and fact tables](399-evidence-queries-and-fact-tables.md)

## New in 2026-02-27r113 (drift bundles + closure diffs)

- [395 Drift bundles and review summaries](395-drift-bundles-and-review-summaries.md)
- [396 Closure diffs and new code surfaces](396-closure-diffs-and-new-code-surfaces.md)

## New in 2026-02-27r112 (policy test suites + mutation testing + policy analysis lane)

- Policy tests as first-class artifacts: introduce `policy.test.suite` + `policy.test.report` schemas and document the regression/mutation testing posture (`docs/393-policy-tests-suites-and-mutation.md`, `spec/policy.test.suite.schema.json`, `spec/policy.test.report.schema.json`, and examples).
- Add an optional policy analysis lane (automated reasoning complements tests for high-assurance authorization) (`docs/394-policy-analysis-and-automated-reasoning.md`).
- Wire the new lane into discovery surfaces and meta-engineering guardrails (design rubric + principles + references) (`docs/348-design-review-rubric-and-feature-intake.md`, `docs/12-design-principles.md`, `docs/32-curated-references.md`, `docs/110-juicy-os-lessons.md`).

## New in 2026-02-27r111 (crypto drift surfaces + key policies + blast-radius crypto section)

- Make crypto drift reviewable with `crypto.registry` + `crypto.diff` (protocols/suites/blessed libraries/key policies as first-class surfaces): `docs/391-crypto-surface-registry-and-agility-gates.md`, `spec/crypto.registry.schema.json`, `spec/crypto.diff.schema.json`
- Introduce `crypto.key.policy` to standardize non-exportable key definitions (backend binding, subject selectors, quorum/presence hooks): `docs/392-crypto-key-policies-and-nonexportable-handles.md`, `spec/crypto.key.policy.schema.json`
- Extend blast-radius diffs to optionally include a `crypto` section (umbrella report can carry crypto drift): `spec/blast_radius.diff.schema.json`, `spec/examples/blast_radius.diff.json`, `docs/106-blast-radius-diff.md`
- Wire crypto surfaces into the meta-engineering guardrails (design rubric + surface registry pattern + design principles): `docs/348-design-review-rubric-and-feature-intake.md`, `docs/379-surface-registry-pattern.md`, `docs/12-design-principles.md`

## New in 2026-02-27r110 (CHERI lane + attestation admission policy + chaos leases + measured launch)

- [387 CHERI: capability hardware and a memory-safety lane](387-cheri-capability-hardware-and-memory-safety-lane.md)
- [388 Remote attestation: admission and enrollment](388-remote-attestation-admission-and-enrollment.md)
- [389 Chaos experiments and fault injection as leases](389-chaos-experiments-and-fault-injection-as-leases.md)
- [390 Measured launch (DRTM) and late-launch integrity](390-measured-launch-and-drtm-trenchboot-lane.md)

## New in 2026-02-27r109 (kernel extensibility + deprecation lifecycle + userenv activation)

- [384 Kernel extensibility: BPF/JIT risk](384-kernel-extensibility-bpf-and-jit-risk.md)
- [385 Deprecation policies and removal receipts](385-deprecation-policies-and-removal-receipts.md)
- [386 UserEnv activation plans and receipts](386-userenv-activation-plans-and-receipts.md)
- (New schemas) `spec/deprecation.notice.schema.json`, `spec/userenv.activate.plan.schema.json`, `spec/userenv.activate.receipt.schema.json`

## New in 2026-02-27r108 (trust boundaries + info-flow labels)

- [380 Trust boundary graphs and threat diff](380-trust-boundary-graphs-and-threat-diff.md)
- [381 Information-flow labels and declassification](381-information-flow-labels-and-declassification.md)
- [383 Surface ids: namespacing and stability](383-surface-ids-namespacing-and-stability.md)

## New in 2026-02-27r107 (determinism + denial-driven suggestions + surface registries)

- [377 Deterministic concurrency lane](377-deterministic-concurrency-lane.md)
- [378 Denial-driven policy suggestions](378-denial-driven-policy-suggestions.md)
- [379 Surface registry pattern](379-surface-registry-pattern.md)

## New in 2026-02-27r106 (parser registry + fuzz gates)

- [376 Parser surface registry and fuzz gates](376-parser-surface-registry-and-fuzz-gates.md)

## New in 2026-02-27r105 (inspect + proof lanes + authority.diff schema)

- [372 Inspect-style structured introspection](372-inspect-style-structured-introspection.md)
- [373 Proof artifacts and formal verification lanes](373-proof-artifacts-and-formal-verification-lanes.md)
- [374 Authority diff schema and review workflows](374-authority-diff-schema-and-review-workflows.md)
- [375 Genode init and capability-routing lessons](375-genode-init-and-capability-routing-lessons.md)

## New in 2026-02-27r104 (contract registries + permission center)

- [370 Contract registries and API-diff gates](370-contract-registries-and-api-diff-gates.md)
- [371 Permission center and authority introspection](371-permission-center-and-authority-introspection.md)

## New in 2026-02-27r103 (authority graphs + reproducible generations + consent ledger)

- [366 Capability graphs and authority-diff surfaces](366-capability-graphs-and-authority-diff-surfaces.md)
- [367 Reproducible generations and determinism checks](367-reproducible-generations-and-determinism-checks.md)
- [368 Pledge/unveil-style promises and derive profiles](368-pledge-unveil-style-promises-and-derive-profiles.md)
- [369 Consent ledgers and permission review UI](369-consent-ledgers-and-permission-review-ui.md)

## New in 2026-02-27r102 (UAPI registry + driver tiering + hotpatch lane)

- [362 UAPI surface registry and compatibility gates](362-uapi-surface-registry-and-compat-gates.md)
- [363 Driver safety tiering (Rust-first, user-mode by default)](363-driver-safety-tiering-rust-and-user-mode.md)
- [364 Live patching lane (hotpatch capsules)](364-live-patching-lane-hotpatch-capsules.md)
- [365 Userspace filesystem servers (puffs/FUSE)](365-userspace-filesystems-puffs-fuse.md)


## New in 2026-02-25 (release capsules + staged rollouts)
- [257 Release capsules and transparency](257-release-capsules-and-transparency.md)
- [258 Staged rollouts and cohorts](258-staged-rollouts-and-cohorts.md)
- [259 Transparency monitors and witness gossip](259-transparency-monitors-and-witness-gossip.md)
- [260 Release authority policy and key management](260-release-authority-policy-and-key-management.md)
- [261 Rollout privacy and cohort hygiene](261-rollout-privacy-and-cohort-hygiene.md)
- [RFC-0189 Release capsules and transparency](../rfcs/RFC-0189-release-capsules-and-transparency.md)
- [RFC-0190 Staged rollouts and cohorts](../rfcs/RFC-0190-staged-rollouts-and-cohorts.md)
- [RFC-0191 Transparency monitors and alert evidence](../rfcs/RFC-0191-transparency-monitors-and-alert-evidence.md)
- [RFC-0192 Release authority policy](../rfcs/RFC-0192-release-authority-policy.md)
- [RFC-0193 Rollout privacy constraints](../rfcs/RFC-0193-rollout-privacy-constraints.md)

## New in 2026-02-25 (exports: policy + plans + transports + consent + transparency)
- [251 Export policies + support-bundle portal](251-export-policies-and-support-bundle-portal.md)
- [252 Lease envelope and cross-lane joins](252-lease-envelope-and-cross-lane-joins.md)
- [253 Bundle plans and deterministic exports](253-bundle-plans-and-deterministic-exports.md)
- [254 Export transparency logs](254-export-transparency-logs.md)
- [255 Policy-constrained transports](255-policy-constrained-transports.md)
- [256 Consent UX contract](256-consent-ux-contract.md)
- [RFC-0183 Export policies and support-bundle portal](../rfcs/RFC-0183-export-policies-and-support-bundle-portal.md)
- [RFC-0184 Lease envelope and cross-lane joins](../rfcs/RFC-0184-lease-envelope-and-cross-lane-joins.md)
- [RFC-0185 Bundle plans and deterministic exports](../rfcs/RFC-0185-bundle-plans-and-deterministic-exports.md)
- [RFC-0186 Export transparency logs](../rfcs/RFC-0186-export-transparency-logs.md)
- [RFC-0187 Policy-constrained transports](../rfcs/RFC-0187-policy-constrained-transports.md)
- [RFC-0188 Consent UX contract](../rfcs/RFC-0188-consent-ux-contract.md)

## New in 2026-02-25 (evidence spine overview + posture lockdown + explicit A/B lifecycle + boot assessment + confirmable change-sets + service contract handles)
- [229 Evidence spine overview](229-evidence-spine-overview.md)
- [230 Lockdown levels and securelevel](230-lockdown-levels-and-securelevel.md)
- [231 A/B updates and recovery semantics](231-ab-updates-and-recovery-semantics.md)
- [241 Boot try-counters and boot assessment](241-boot-try-counters-and-boot-assessment.md)
- [242 Confirmable change-sets and auto-revert](242-confirmable-change-sets-and-auto-revert.md)
- [243 Service contract handles and membership](243-service-contract-handles-and-membership.md)
- [244 Boot-chain revocation and allowlists](244-bootchain-revocation-and-allowlists.md)
- [245 Boot measurement phases and PCR separation](245-boot-measurement-phases-and-pcr-separation.md)
- [246 Causality graphs and minimal evidence bundles](246-causality-graphs-and-minimal-evidence-bundles.md)
- [RFC-0164 Lockdown levels as a first-class posture output](../rfcs/RFC-0164-lockdown-levels-as-a-first-class-posture-output.md)
- [RFC-0165 A/B update lifecycle on ZFS boot environments](../rfcs/RFC-0165-ab-update-lifecycle-on-zfs-boot-environments.md)
- [RFC-0173 Boot try-counters and boot assessment](../rfcs/RFC-0173-boot-try-counters-and-boot-assessment.md)
- [RFC-0174 Confirmable change-sets and auto-revert](../rfcs/RFC-0174-confirmable-change-sets-and-auto-revert.md)
- [RFC-0175 Service contract handles and membership](../rfcs/RFC-0175-service-contract-handles-and-membership.md)

## New in 2026-02-24 (ops evidence: faults + supervision + events + state + config + change sets + resources)
- [213 Fault management architecture](213-fault-management-architecture.md)
- [214 Service supervision + health as evidence](214-service-supervision-health-as-evidence.md)
- [215 Structured event journal as evidence](215-structured-event-log-as-evidence.md)
- [216 Incident snapshots + support bundles](216-incident-snapshots-and-support-bundles.md)
- [217 State datasets + migrations as evidence](217-state-datasets-and-migrations-as-evidence.md)
- [218 Configuration transactions + receipts](218-configuration-transactions-and-receipts.md)
- [219 Change sets + apply engine](219-change-sets-and-apply-engine.md)
- [220 Operational time-travel debugging](220-operational-time-travel-debugging.md)
- [221 Firmware updates as artifacts](221-firmware-updates-as-artifacts.md)
- [222 Resource governance as evidence](222-resource-governance-as-evidence.md)
- [223 Secrets and key management as evidence](223-secrets-and-key-management-as-evidence.md)
- [224 Crash artifacts and symbolication as evidence](224-crash-artifacts-and-symbolication-as-evidence.md)
- [225 Storage health + scrubbing as evidence](225-storage-health-and-scrubbing-as-evidence.md)
- [226 Platform posture + attestation receipts as evidence](226-platform-posture-and-attestation-results-as-evidence.md)
- [227 Time discipline + trustworthy timestamps as evidence](227-time-discipline-and-trustworthy-timestamps-as-evidence.md)
- [228 PKI + identity lifecycle as evidence](228-pki-and-identity-lifecycle-as-evidence.md)

## New in 2026-02-25 (promise profiles + verified exec as evidence)
- [232 Service promise profiles](232-service-promise-profiles.md)
- [233 Verified execution as evidence](233-verified-execution-as-evidence.md)
- [234 Anykernel + rump kernels](234-anykernel-and-rump-kernels.md)
- [235 Process contracts + service ownership](235-process-contracts-and-service-ownership.md)
- [236 Breakglass + recovery mode](236-breakglass-and-recovery-mode.md)
- [237 Lint reports + contract testing](237-lint-reports-and-contract-testing.md)
- [238 Portal-activated services + socket activation](238-portal-activated-services-and-socket-activation.md)
- [RFC-0166 Service promise profiles](../rfcs/RFC-0166-service-promise-profiles.md)
- (Updated) [RFC-0072 Runtime verified execution](../rfcs/RFC-0072-runtime-verified-execution.md)

## New in 2026-02-25 (bootchain revocation + measured-boot ergonomics + causality graphs)
- [244 Boot-chain revocation and allowlists](244-bootchain-revocation-and-allowlists.md)
- [245 Boot measurement phases and PCR separation](245-boot-measurement-phases-and-pcr-separation.md)
- [246 Causality graphs and minimal evidence bundles](246-causality-graphs-and-minimal-evidence-bundles.md)
- [RFC-0176 Bootchain policy and revocation](../rfcs/RFC-0176-bootchain-policy-and-revocation.md)
- [RFC-0177 Boot measurement phases](../rfcs/RFC-0177-boot-measurement-phases.md)
- [RFC-0178 Causality graphs as evidence](../rfcs/RFC-0178-causality-graphs-as-evidence.md)

## New in 2026-02-25 (sealed secrets + air-gap mirror kits)
- [272 Sealed secrets + attested unsealing (TPM policy lane)](272-sealed-secrets-attested-unsealing.md)
- [273 Air-gap mirror kits + sneakernet updates](273-airgap-mirror-kits-and-sneakernet-updates.md)

## New in 2026-02-25 (fuzzing farm + bisection certificates)
- [274 Continuous fuzzing farm](274-continuous-fuzzing-farm.md)
- [275 Root-cause certificates + bisection](275-root-cause-certificates-and-bisection.md)
- (Updated) [234 Anykernel + rump kernels](234-anykernel-and-rump-kernels.md)
- (Updated) [166 Test receipts + promotion gates](166-test-receipts-and-promotion-gates.md)

## New in 2026-02-25 (kmods + loader verification)
- [276 Kernel module policy + loading as evidence](276-kernel-module-policy-and-loading-as-evidence.md)
- [277 Loader verification + boot config constraints](277-loader-verification-and-boot-config-constraints.md)
- (Updated) [230 Lockdown levels and securelevel](230-lockdown-levels-and-securelevel.md)

## New in 2026-02-25 (remote assistance + terminal session recording)
- [291 Remote assistance sessions as evidence](291-remote-assistance-sessions-as-evidence.md)
- [292 Terminal session recording as evidence](292-terminal-session-recording-as-evidence.md)


## New in 2026-02-26r76 (operator access + policy replay)
- [311 Operator access as leases (SSH certificates + recorded sessions)](311-operator-access-leases-and-ssh-certs.md)
- [312 Policy replay and counterfactual explanations](312-policy-replay-and-counterfactual-explanations.md)


## New in 2026-02-26r80 (kernel mutation as evidence)
- [318 Kernel tunables + sysctls as evidence](318-kernel-tunables-and-sysctls-as-evidence.md)
- (Updated) [276 Kernel module policy + loading as evidence](276-kernel-module-policy-and-loading-as-evidence.md)


## New in 2026-02-26r81 (hardware inventory + compatibility gates)
- [319 Hardware inventory + driver binding as evidence](319-hardware-inventory-and-driver-binding-as-evidence.md)
- [320 Hardware compatibility gates + safe upgrades](320-hardware-compatibility-gates-and-safe-upgrades.md)
- (Updated) [298 Authority budgets + permission drift alarms](298-authority-budgets-and-permission-drift-alarms.md)
- (Updated) [97 Non-negotiable behaviors](97-non-negotiable-behaviors.md)


## New in 2026-02-26r82 (firmware updates + UEFI variable evidence)
- [321 Firmware updates + UEFI variables as evidence](321-firmware-updates-and-uefi-variables-as-evidence.md)
- (New schemas) `spec/fw.inventory.receipt.schema.json`, `spec/fw.update.plan.schema.json`, `spec/fw.update.receipt.schema.json`, `spec/uefi.var.set.plan.schema.json`, `spec/uefi.var.set.receipt.schema.json`
- (Updated) [110 Juicy OS lessons](110-juicy-os-lessons.md)
- (Updated) [266 Open questions and risk register](266-open-questions-and-risk-register.md)
- (Updated) [97 Non-negotiable behaviors](97-non-negotiable-behaviors.md)
- (Updated) [298 Authority budgets + permission drift alarms](298-authority-budgets-and-permission-drift-alarms.md)
- (Updated) [32 Curated references](32-curated-references.md)



## New in 2026-02-26r83 (host networking substrate as evidence)
- [322 Network topology + firewall as derived operations](322-network-topology-and-firewall-as-derived-operations.md)
- (New schemas) `spec/net.topology.plan.schema.json`, `spec/net.topology.receipt.schema.json`, `spec/net.topology.event.schema.json`
- (Updated) [67 pf anchors per instance](67-pf-anchors-per-instance.md)
- (Updated) [64 Networking modes mapping](64-networking-modes-mapping.md)
- (Updated) [97 Non-negotiable behaviors](97-non-negotiable-behaviors.md)
- (Updated) [298 Authority budgets + permission drift alarms](298-authority-budgets-and-permission-drift-alarms.md)
- (Updated) [266 Open questions and risk register](266-open-questions-and-risk-register.md)
- (Updated) [110 Juicy OS lessons](110-juicy-os-lessons.md)
- (Updated) [32 Curated references](32-curated-references.md)


## New in 2026-02-26r84 (devfs views as derived operations)
- [323 Devfs views: plans, receipts, and drift events](323-devfs-views-plans-and-receipts.md)
- (New schemas) `spec/devfs.view.plan.schema.json`, `spec/devfs.view.receipt.schema.json`, `spec/devfs.view.event.schema.json`
- (Updated) [278 Device grants + devfs rulesets](278-device-grants-and-devfs-rulesets.md) (formalize `devfs.view.*` objects)
- (Updated) [297 Component descriptors + compiled runtime manifests](297-component-descriptors-and-compiled-runtime-manifests.md) (add devfs view output)
- (Updated) [97 Non-negotiable behaviors](97-non-negotiable-behaviors.md) (add `/dev` views derived + receipted)
- (Updated) [298 Authority budgets + permission drift alarms](298-authority-budgets-and-permission-drift-alarms.md) (device budgets consume devfs view receipts/events)
- (Updated) [266 Open questions and risk register](266-open-questions-and-risk-register.md) (add `/dev` drift risk item)
- (Updated) [110 Juicy OS lessons](110-juicy-os-lessons.md) (add `/dev` view lesson)


## New in 2026-02-27r101 (capability hygiene + boot capsules + recovery ergonomics)
- [357 Capability attenuation, revocation, and membranes](357-capability-attenuation-revocation-and-membranes.md)
- [358 Unified boot capsules and measured-boot receipts](358-unified-boot-capsules-and-measured-boot-receipts.md)
- [359 Slot-based A/B updates and boot assessment lessons](359-slot-based-updates-and-boot-assessment-lessons.md)
- [360 Derived recovery images and minimal userspace](360-derived-recovery-images-and-minimal-userspace.md)
- [361 Safe crossing APIs and boundary bugs (Tock lessons)](361-safe-crossing-apis-and-boundary-bugs-lessons-from-tock.md)
- (Updated) [12 Design principles](12-design-principles.md) (authority engineering principle)
- (Updated) [348 Design review rubric](348-design-review-rubric-and-feature-intake.md) (attenuation/revocation patterns)
- (Updated) [110 Juicy OS lessons](110-juicy-os-lessons.md) (add 214–218)
- Update the open-questions/risk register entry for the crypto operations portal to include split-secrets workflow questions (`docs/266-open-questions-and-risk-register.md`).

Last updated: 2026-03-19r307