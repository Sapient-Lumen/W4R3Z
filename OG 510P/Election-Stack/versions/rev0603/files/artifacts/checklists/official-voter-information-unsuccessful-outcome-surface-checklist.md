# Official voter-information unsuccessful-outcome surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes workable after the route has reached a negative, unmatched, unable-to-process, or rejected result.

## Inventory and review scope

- Identify public routes that can end in no-match, rejected, unable-to-process, closed-window, duplicate/already-completed, or temporary-failure outcomes.
- Distinguish this from pre-submit input validation, in-session waiting, immediate successful confirmation, or longer-lived pending review after acceptance.
- Re-check routes where deadlines, cure windows, ballot requests, or registration corrections make a vague unsuccessful outcome especially risky.

## Outcome meaning and next-step posture

- State in ordinary language what the unsuccessful result means in public terms.
- Distinguish fixable same-route correction from wrong-route, closed-window, temporary-service, duplicate/already-completed, and office-help cases when those differences matter.
- Tell the voter whether to correct and retry, use another official route, wait for a status path, or contact the office.
- Do not leave the voter with a generic “error,” “unable to process,” or “no result” state that has no next-step meaning.

## Retry, reroute, and help continuity

- Preserve enough entered context, field cues, or bounded attempt context that the voter can understand what failed without starting from zero.
- Keep any useful reference number or attempt identifier visible when later help depends on it.
- Identify one authoritative status, correction, or office-help path when the same route should no longer be retried.
- Ensure unsuccessful-outcome posture matches the underlying substantive surface and any pending-review or confirmation language.

## Accessibility and reviewability

- Keep unsuccessful-outcome language, next steps, and help transitions available in accessible text on mobile, at zoom, with keyboard navigation, and with screen readers.
- Do not make the only meaning-bearing distinction a color, icon, or transient toast.
- Keep the message visible long enough that a voter can capture the next step or explain the problem to the office.
- Test project-context unsuccessful outcomes, not just ideal-path submissions.

## Evidence posture

- Preserve only route labels, reviewed unsuccessful-outcome paths, retry/help transition review state, context-preservation review state, and last review time.
- Do not preserve full user submissions, internal adjudication notes, hidden anti-abuse thresholds, or sensitive identifiers when bounded policy reconstruction is sufficient.
