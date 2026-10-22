# Harbor
Current focus: user-response event capture, reliance/consent/comprehension fences, and registry-derived count audit.

Revision `rev0111` chooses **response-event evidence without reliance-shaped certainty**. This pass closes F106 with a deterministic user-response event bundle, fixture, harness, and checker. It records parent explanation input, response event, capture context, interpretation guard, follow-up action, privacy/retention posture, history trace, and scoped verdicts for inspect, recheck request, export, dismiss, appeal start, share-link copy, acknowledgement, focus, localized acknowledgement, sealed-detail request, agent follow-up, notification opt-out, batch acknowledgement, and automated retry. It rejects click-as-comprehension, checkbox-as-consent, export-as-reliance, dismiss-as-acceptance, appeal-as-repair, share-as-all-read, acknowledgement-as-compliance, scroll/focus-as-understanding, localized scope widening, sealed request-as-permission, recheck-request-as-passed, delivery-as-user-action, response without parent explanation digest, re-identifying analytics, stale response-as-currentness, agent acknowledgement-as-user-consent, irreversible action without undo, unbounded retention, and retry-as-repair.

Rev0111 also performs an audit/refactor: `tools/harbor_executable_surface_registry.py` now exposes a registry-derived executable-slice count phrase, and `tools/check_harbor_executable_surface_registry.py` plus `tools/check_harbor_briefing_focus.py` consume that phrase instead of hardcoding a spelled-out count. `docs/00-meta/datacube-executable-count-audit.md` documents the change. This is maintenance hygiene only, not a schema, release-status API, badge, trust root, conformance suite, or promotion gate.

Harbor now carries 17 executable proof slices: CrossingRecord evidence, transparency/provenance receipt import, verifier disagreement, property/mutation coverage, mutation triage, checker provenance, release-package provenance, artifact handoff/consumer import, post-import local derivation drift, derivative correction propagation, derivative repair retention/expiry, overlapping correction-epoch lineage, cross-cube lineage import, foreign-import revocation, revocation-overlay propagation, user-visible explanation bundles, and user-response event capture. All 17 are deterministic fixtures or checks, not promoted schemas, dashboards, registries, CI APIs, trust roots, signatures, consumer verification APIs, cache APIs, sync-state ledgers, repair attestations, notification guarantees, records-management systems, legal-hold workflows, privacy-erasure APIs, correction-epoch registries, repair ledgers, conflict-resolution engines, foreign revocation APIs, revocation propagation APIs, public badge workflows, explanation APIs, consent systems, reliance ledgers, analytics products, user-identity registries, accessibility conformance claims, localization equivalence guarantees, compliance workflows, mirror/search truth planes, warning-card status engines, artifact-security guarantees, or conformance suites.

## Latest rev0111 pass
- Research synthesis: [`docs/00-meta/research-synthesis-2026-05-26-pass-cxi.md`](docs/00-meta/research-synthesis-2026-05-26-pass-cxi.md)
- Companion evaluation: [`docs/00-meta/slopos-companions-evaluation-2026-05-26-pass-cxi.md`](docs/00-meta/slopos-companions-evaluation-2026-05-26-pass-cxi.md)
- User-response event surface: [`docs/00-meta/datacube-user-response-event-capture.md`](docs/00-meta/datacube-user-response-event-capture.md)
- Executable count audit: [`docs/00-meta/datacube-executable-count-audit.md`](docs/00-meta/datacube-executable-count-audit.md)
- Verification bundle contract: [`docs/40-verification/harbor-user-response-event-bundle-v0.md`](docs/40-verification/harbor-user-response-event-bundle-v0.md)
- Fixture: [`fixtures/harbor-user-response-event-bundle-v0.json`](fixtures/harbor-user-response-event-bundle-v0.json)
- Harness: [`tools/harbor_user_response_event_harness.py`](tools/harbor_user_response_event_harness.py)
- Checker: [`tools/check_harbor_user_response_event_bundle.py`](tools/check_harbor_user_response_event_bundle.py)
- Executable specimen: [`docs/30-architecture/specimen-flow-106-user-response-reliance-event-capture.md`](docs/30-architecture/specimen-flow-106-user-response-reliance-event-capture.md)
- Proof obligations: [`docs/00-meta/datacube-proof-obligations.md`](docs/00-meta/datacube-proof-obligations.md)

Exact current core paths:
- `docs/00-meta/research-synthesis-2026-05-26-pass-cxi.md`
- `docs/00-meta/slopos-companions-evaluation-2026-05-26-pass-cxi.md`
- `docs/00-meta/datacube-user-response-event-capture.md`
- `docs/00-meta/datacube-executable-count-audit.md`
- `docs/40-verification/harbor-user-response-event-bundle-v0.md`
- `fixtures/harbor-user-response-event-bundle-v0.json`
- `tools/harbor_user_response_event_harness.py`
- `tools/check_harbor_user_response_event_bundle.py`
- `docs/30-architecture/specimen-flow-106-user-response-reliance-event-capture.md`

`rev0111` closes `F106`; `F107` is now the single `next` followthrough item. Do not promote consent systems, reliance ledgers, analytics products, user-identity registries, UI telemetry APIs, notification-read guarantees, user-comprehension proof, global repair workflows, legal/compliance workflows, or final SlopOS datacube shape until repeated specimens prove they deserve it.

## Process anchors
- North star: [`docs/00-meta/charter.md`](docs/00-meta/charter.md)
- Embryo-promotion contract: [`docs/00-meta/embryo-promotion-contract.md`](docs/00-meta/embryo-promotion-contract.md)
- Datacube design principles: [`docs/00-meta/datacube-design-principles.md`](docs/00-meta/datacube-design-principles.md)
- Datacube stability rings: [`docs/00-meta/datacube-stability-rings.md`](docs/00-meta/datacube-stability-rings.md)
- Datacube change classes: [`docs/00-meta/datacube-change-classes.md`](docs/00-meta/datacube-change-classes.md)
- Datacube assertion posture: [`docs/00-meta/datacube-assertion-posture.md`](docs/00-meta/datacube-assertion-posture.md)
- Datacube presence semantics: [`docs/00-meta/datacube-presence-semantics.md`](docs/00-meta/datacube-presence-semantics.md)
- Datacube evidence grades: [`docs/00-meta/datacube-evidence-grades.md`](docs/00-meta/datacube-evidence-grades.md)
- Datacube aggregation semantics: [`docs/00-meta/datacube-aggregation-semantics.md`](docs/00-meta/datacube-aggregation-semantics.md)
- Datacube conformance lanes: [`docs/00-meta/datacube-conformance-lanes.md`](docs/00-meta/datacube-conformance-lanes.md)
- Datacube exactness semantics: [`docs/00-meta/datacube-exactness-semantics.md`](docs/00-meta/datacube-exactness-semantics.md)

Run `make check` before trusting the tree. Run `make package-release` to refresh release surfaces and emit the deterministic zip.
