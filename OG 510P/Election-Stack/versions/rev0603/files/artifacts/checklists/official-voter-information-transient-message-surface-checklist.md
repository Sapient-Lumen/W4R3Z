# Official voter-information transient-message surface checklist

Use this checklist for official voter-information routes where **outcomes, warnings, result counts, no-result states, or next-step cues are announced through transient toasts, snackbars, inline status bars, or other short-lived message layers**.

## Semantics and durability review

- [ ] Record which routes use transient alerts/status messages and what each message class is expected to communicate.
- [ ] Review whether each message is advisory, urgent, or action-requiring and whether the chosen `status`/`alert`/dialog posture tells the truth about that urgency.
- [ ] Review whether any governing meaning appears only in the transient message instead of remaining visible in durable route text.
- [ ] Review whether result counts, no-result states, pending states, and warnings stay inspectable after the announcement moment passes.
- [ ] Review whether messages that really require a decision or rich interaction have moved into a more durable inline or dialog pattern rather than remaining a toast.

## Timing, announcement, and focus review

- [ ] Review whether live-region containers exist before content updates so announcements fire reliably.
- [ ] Review whether ordinary transient messages announce without stealing focus or changing context unnecessarily.
- [ ] Review whether auto-dismiss timing leaves enough time to read and understand the message.
- [ ] Review whether stacked/replaced messages can cause a decisive message to vanish before the voter perceives it.
- [ ] Review whether notification frequency stays bounded enough that repeated messages do not become noise.

## Fallback and evidence review

- [ ] Review whether compact/mobile layouts preserve the same outcome meaning without clipping it into a vanishing overlay.
- [ ] Preserve a small public digest of which message classes were reviewed, how severity was assigned, whether the same meaning remains visible after dismissal, and when the review occurred.
- [ ] Do not retain per-user toast telemetry, session replay, or giant client event streams merely to prove that a transient message once appeared.
