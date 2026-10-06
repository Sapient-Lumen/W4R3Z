# Location portal (geolocation) as capability grants

Location is sensitive:
- it can de-anonymize users
- it’s a strong correlator (time + place)
- it’s often requested “just in case”

A greenfield OS should make location access:
- **explicit** (no ambient API)
- **brokered** (user-visible)
- **coarse-first** (precision is policy-gated)
- **receipted** (auditable)

## Lessons to steal

- XDG Desktop Portal **Location**: sandboxed apps query location via a portal.  
  Reference: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Location.html

## Proposal (DeriveBSD)

### Request parameters
A location request includes:
- desired accuracy class: `none | city | neighborhood | precise`
- max acceptable age (cached fix allowed?)
- whether continuous updates are requested (session) or one-shot fix

### Grant semantics
The broker issues `ui.location.grant` with constraints:
- `accuracy_class` actually granted (may be downgraded)
- allowed cadence (one-shot / periodic)
- TTL / lease_id
- optional “remember” binding (via portal.permission.grant)

### Receipts
Each delivered fix can be recorded as `ui.location.receipt`:
- timestamp (bound to `time.snapshot` if the profile requires secure time proofs)
- accuracy class actually used
- whether the fix was user-approved, remembered, or policy-allowed without prompting

### Policy hooks
- hardened profiles can disable the portal family entirely (lockdown)
- default is **deny** unless explicitly allowed
- “precise” requires an explicit UI prompt even if “coarse” is remembered

## Schemas

- `spec/ui.location.grant.schema.json`
- `spec/ui.location.receipt.schema.json`

## Integration points

- Portal conventions: `docs/210-portal-sessions-and-permission-store.md`
- Secure time proofs for fix timestamps (optional): `docs/200-secure-time-bootstrapping.md`
- Intent routing for “open map / directions”: `docs/199-intent-routing-and-plumbing.md`
