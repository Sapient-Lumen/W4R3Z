# Redress lane appeal receipts

`redresslane.py` gives moderation pressure a visible counter-surface. A block can be lifted, narrowed, or converted to watch-only only when signed redress evidence binds to the same profile, service, action, subject key, scope, request, and moderation report digest.

Receipt kinds:

- subject countersign
- moderator acknowledgement
- witness observation
- remediation proof
- hard-negative scan

The lane rejects replay, bad signatures, expired/future receipts, receipt refusal, profile/service/scope/request/subject/action drift, quarantine-report drift, rollback, same-sequence forks, previous-link mismatch, and live hard negatives.

Redress is not an override button. It is local evidence that may release a local side-effect block.
