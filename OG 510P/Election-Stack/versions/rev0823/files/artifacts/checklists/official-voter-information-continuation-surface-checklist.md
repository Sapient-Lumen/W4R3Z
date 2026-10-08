# Official voter-information continuation surface checklist

Use this checklist for official voter-information routes that continue the same answer-bearing set after initial page load through **Load more**, **infinite scroll**, **virtualized lists**, or a similar appended-list pattern.

## Scope and route inventory

- [ ] Record which official routes continue the same result set after page load instead of using numbered pagination.
- [ ] Record whether the route uses a visible **Load more** trigger, auto-loading on scroll, virtualization, or a hybrid continuation model.
- [ ] Record what kind of official set is being continued (office directory, location list, FAQ/articles, notice archive, other).

## Set meaning and item identity

- [ ] Review whether the route makes clear that the user is continuing one official set rather than switching topics or silently changing filters.
- [ ] Review whether items remain individually distinguishable as the same office/location/article after more results load.
- [ ] When not all items are present in the DOM, review whether bounded item-position or set-size meaning remains available rather than silently resetting.

## Loading and status visibility

- [ ] Review whether loading, loaded, failure, and end-of-set states are expressed in text rather than spinner-only visuals.
- [ ] Review whether meaningful continuation updates are programmatically announced without forcing a focus hunt.
- [ ] Review whether multi-step DOM updates avoid exposing incoherent intermediate state.

## Focus and keyboard continuity

- [ ] Review whether focus remains logical after continuation is triggered.
- [ ] Review whether keyboard users can continue traversing the extended set without being stranded on stale controls or unexpected focus jumps.
- [ ] Review whether newly inserted results appear in a stable enough order that the route remains understandable after continuation.

## End-of-set and recovery posture

- [ ] Review whether the route distinguishes among end of set, temporary retrieval failure, and unknown total size.
- [ ] Review whether compact/mobile variants preserve continuation meaning instead of collapsing into silent autoload behavior.
- [ ] Review whether a visible overview/help escape remains available when brute-force continuation is not the right resolution path.

## Evidence discipline

- [ ] Preserve a small public digest of the continuation model, announcement posture, end-of-set behavior, and re-findability review.
- [ ] Do not retain individualized scroll histories, replay exhaust, or person-level browsing telemetry merely to prove the continuation mechanism existed.
