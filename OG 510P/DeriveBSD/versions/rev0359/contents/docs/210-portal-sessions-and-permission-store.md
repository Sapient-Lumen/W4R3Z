# Portal sessions + permission store (make “remember my choice” coherent)

Portal-shaped capability acquisition is **usable** only if it supports:

- short-lived **requests** (user interaction completes and the handle disappears)
- long-lived **sessions** (screen share, remote desktop, global shortcuts, etc.)
- *optional* “remember” behavior that is **auditable and revocable**

Older ecosystems often bolt these on inconsistently. A greenfield design can standardize them.

## Lessons to steal

- XDG Desktop Portal **Request**: portal calls return a Request handle; completion is signaled via a Response signal.  
  Reference: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Request.html
- XDG Desktop Portal **Session**: long-lived operations return a Session handle that can be closed.  
  Reference: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.Session.html
- XDG Desktop Portal **PermissionStore**: portals persist grants in a free-form DB keyed by app + resource id.  
  Reference: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.impl.portal.PermissionStore.html

## Proposal (DeriveBSD)

### 1) Requests: “an interaction, then it’s over”
A portal method call emits:
- a canonical **portal.request** (canonical bytes → digest)
- a signed **portal.grant** (allow/deny; includes constraints; may include a lease_id)

The broker must be able to prove *what prompt* the user saw:
- prompt template digest
- UI strings bundle digest (localization-safe)
- capability description digest

(See: `docs/185-portal-consent-and-audit-receipts.md`.)

### 2) Sessions: “capability that stays alive, but can be closed”
Some portals create long-lived streams or handles. Model them as:
- a signed **portal.session** receipt with:
  - `session_id` (stable identifier)
  - `portal` (family name, e.g. `ui.screencast`)
  - `capset_digest` (what authority is live for the session)
  - `expires_at` and/or `lease_id`
  - `close_semantics` (what happens on Close: revoke, drain, detach, etc.)

This makes:
- *policy* able to cap lifetime and scope
- *tooling* able to enumerate “what sessions are live”
- *forensics* able to explain “how did this app get to keep screen share?”

### 3) Permission store: “remember choice, but keep it explainable”
Persisting decisions should not be ad-hoc hidden state.

Introduce **portal.permission.grant** records that are:
- keyed by `(app_identity, portal_family, resource_id, operations[])`
- bound to:
  - a **request shape digest** (what was asked)
  - a **prompt template digest** (what was shown)
  - constraints (TTL, max scope, redaction profile, etc.)
- explicitly **revocable** via `portal.permission.revoke`

These records are implementation-flexible:
- local DB (host state dataset)
- or a signed-log / transparency-backed store for high assurance

But in all cases, policy gates:
- whether “remember” is allowed
- maximum retention
- whether grants auto-expire

## Schemas

- `spec/portal.session.schema.json`
- `spec/portal.permission.grant.schema.json`
- `spec/portal.permission.revoke.schema.json`

## Integration points

- Screen share / remote desktop: `docs/208-screencast-and-remote-desktop-portals.md`
- AV capture: `docs/209-camera-and-audio-capture-portals.md`
- Data transfer portals: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- Notifications: `docs/206-notification-portal-non-observing.md`
- Consent ledger / permission review UI: `docs/369-consent-ledgers-and-permission-review-ui.md`
