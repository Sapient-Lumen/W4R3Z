# rev0239 Dispatch Preflight, Formation Mandate, and Audit Lock

rev0239 prioritizes unfinished operational risk over new doctrine. The release fixes a concrete inconsistency: the outgoing first-contact request used a 14-day response deadline while the execution record carried 21 days. That mismatch is now impossible to release silently because the execution record contains a `dispatch_preflight` object and both `tools/audit_external_contact_execution_record.py` and `tools/lint_archive.py` recompute the final outgoing body SHA-256 and verify deadline alignment.

The first-contact state remains honest: no named independent counterparty, public channel locator, or sender authority was supplied. The correct state is therefore still no-send. The no-send record may not start a response clock, prepare a no-response shell, substitute for dispatch, create custody, open intake, enable import, support waiver/adverse inference/status claims, or move the live receipt floor.

The formation-review lane now receives a second substantive hardening pass. The review card adds mandate, independent budget, provider-payment-control prohibition, recusal triggers, appeal route, sealed/public evidence boundary, and capture controls. A provider-selected or provider-paid self-certification can no longer masquerade as independent formation audit review.

Two new critical fixtures preserve the corrections:

- `fixtures/negative-tests/external-contact-execution-preflight-deadline-hash-mismatch.json` blocks stale preflight, stale hash, deadline mismatch, and no-response-clock laundering.
- `fixtures/negative-tests/formation-review-card-provider-funded-self-certification.json` blocks provider-controlled reviewer selection, payment, scope, timing, and publication posture.

The live floor remains zero/stayed. rev0239 does not send an external request, stage a live artifact, open response intake, import evidence, claim custody, claim authority, claim status, claim recognition, or create live-floor credit.

Validation path:

```bash
python3 tools/render_external_contact_message.py
python3 tools/audit_external_contact_message_render.py
python3 tools/audit_external_contact_execution_record.py
python3 tools/audit_formation_audit_review_card.py
python3 tools/run_fixture_examples.py
make context-pack
make manifest
make lint
make package-release STAMP=<YYYY.MM.DD.HH.MM> SLUG=dispatch-preflight-formation-mandate-gateforge
```
