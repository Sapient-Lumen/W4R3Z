# Official voter-information copy/share surface checklist

Use this quickcheck when an election office offers copy/share controls on public voter-information routes and needs those handoffs to stay truthful.

## Inventory and scope

- Identify official routes that expose `Copy`, `Copy link`, `Share`, `Send`, or similar handoff controls.
- Re-check routes where the copied/shared artifact may differ materially from the full current page (for example, a share-safe canonical URL, bounded status summary, shortlink, office contact block, or citation-safe snapshot).
- Distinguish this from generic share-safe URL posture, generic button/link semantics, or generic permission-gated capability posture alone.

## Artifact truthfulness

- State what each control actually hands off instead of leaving the artifact class implicit.
- Do not let a control that copies only a phone number, office block, summary, or shortlink masquerade as a full official page record.
- If the current live route is not safely forwardable, substitute a safer canonical pointer, citation-safe snapshot, or bounded public summary instead of copying the unsafe route.
- Keep the ordinary help or recovery lane visible when the route cannot safely offer direct forwarding.

## Success, cancel, and failure posture

- Do not announce copy success until the clipboard write has actually succeeded or a truthful fallback confirms the handoff.
- Distinguish successful handoff from unsupported browser, blocked policy, user cancel, missing share target, or failed transmission.
- Do not treat merely opening a share sheet as proof that the share completed.
- Provide a visible fallback when clipboard or native share support is unavailable.

## Authority and recovery context

- Preserve enough office, route, freshness, or help context in the copied/shared artifact that it remains checkable later.
- Keep the handoff compact; do not assume all share targets will preserve long text or rich formatting.
- Review whether a portable record, citation-safe snapshot, or safer public page should be offered instead when exactness matters.
- Ensure copy/share controls do not leak secret-bearing, personalized, or stale local-only state.

## Accessibility and reviewability

- Keep copy/share controls operable with keyboard, touch, zoom, and screen readers.
- Keep success/failure/cancel status available in durable accessible text rather than only in transient decorative toasts.
- Test constrained and unsupported environments instead of assuming native share or clipboard support exists.
- Verify that fallback links or text remain understandable on mobile and in embedded browsers.

## Evidence posture

- Preserve only reviewed control inventories, artifact classes, success/failure/cancel posture, share-safe substitution review, authority-context minimum review, and last review time.
- Do not preserve recipient identities, share-target telemetry, copied secret URLs, raw clipboard payload captures, or individualized sharing analytics when bounded policy reconstruction is sufficient.
