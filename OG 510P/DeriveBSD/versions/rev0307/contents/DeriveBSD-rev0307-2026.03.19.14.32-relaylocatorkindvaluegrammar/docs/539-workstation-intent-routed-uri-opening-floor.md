# Workstation intent-routed URI opening floor

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/537-workstation-remoted-session-surface-boundary.md` already decided that clipboard, file selection, URL opens, printing, and similar crossings remain broker/portal lanes outside the remoted session surface.
`docs/538-workstation-cross-domain-datatransfer-floor.md` then fixed clipboard/file movement as an explicit transfer act instead of ambient shared state.
This doc makes the next small but expensive cut:
**cross-compartment URI opening is intent-routed and compartment-preserving, and the trusted host is not the default renderer for untrusted external content.**

See also:
- ADR: `adrs/ADR-0129-workstation-intent-routed-uri-opening-floor.md`
- general intent router: `docs/199-intent-routing-and-plumbing.md`
- portals/powerbox overview: `docs/179-portals-and-powerbox.md`
- workstation host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- workstation data-transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- desktop viability checklist: `docs/410-desktop-viability-checklist.md`

## Why this needs a hard decision

Once the session-surface and data-transfer cuts are made, “open this link” becomes the next place ambient authority tries to sneak back in.
If the archive does not choose, people will naturally reach for the easiest thing:

- let the AppVM call a generic host-side opener,
- let the host browser become the fallback for every `http` / `https` link,
- and let `file://` or custom schemes blur the line between URI routing and explicit file transfer.

That would rebuild exactly the kind of invisible privilege expansion the workstation boundary is trying to prevent.

Upstream practice already hints at the right floor:

- portal-style URI opening exists so sandboxed apps can open URIs under user control
- local-file opening is kept distinct from URI open and should stay on explicit file authority lanes
- compartmentalized systems commonly route risky URLs into separate browsing compartments instead of treating the trusted side as the universal browser

## Accepted baseline

For the ordinary workstation lane:

- cross-compartment URI opening is an explicit **intent-routing** act
- the trusted host is **not** the default renderer for ordinary untrusted `http` / `https` content
- `http` / `https` opens from AppVMs resolve to a designated **browsing compartment**
- `mailto` and similar human-identity-bearing schemes resolve to a designated **communications compartment**
- `file://` does **not** bypass the explicit file import/export boundary
- custom schemes are **deny-by-default** unless policy names an explicit trusted target class and handler lane

This keeps the workstation story coherent:
choosing *where* something opens is a brokered routing decision, not an ambient consequence of whatever handler the host happens to have installed.

## Practical routing model

### `http` / `https`

The baseline target is a designated browsing compartment.
That may be:

- a long-lived browser AppVM,
- a policy-selected browsing role,
- or a disposable-capable browser lane for riskier origins.

The important floor is the trust boundary, not the exact UX variant:
**the host does not become the ordinary browser for untrusted external content.**

### `mailto`

Human-identity-bearing schemes such as `mailto` should route to a designated communications compartment.
That keeps account/session authority separated from the caller compartment and avoids recreating host-side “open everything here” convenience paths.

### `file://`

`file://` is not the cross-domain URI-opening primitive.
If a file is already local to the caller compartment, it may open locally.
If the file needs to move or open in another compartment, the act must go through explicit export/import or file-open portal authority first.

That preserves the previous workstation data-transfer cut instead of letting file movement hide inside URI handling.

### Custom schemes

Custom schemes are deny-by-default in the ordinary workstation lane.
A later allowlist may admit tightly bounded handlers, but only when policy can name:

- the scheme,
- the target handler class,
- the allowed target compartment role,
- and the evidence surface for the routing act.

## Artifact decision: reuse the intent-routing lane

DeriveBSD already has a typed routing/evidence substrate:

- `spec/intent.request.schema.json`
- `spec/intent.route.receipt.schema.json`

Use that lane for workstation URI routing instead of inventing a second bespoke “URL open” artifact family.
That means:

- the routing request stays a typed `intent.request`
- the chosen handler and policy decision stay on `intent.route.receipt`
- any file or portal grant lineage remains attached as supporting authority rather than becoming a rival top-level contract

This is the same entropy-reduction move we made for cross-domain clipboard/file transfer.

## What this buys

### 1) No stealth host-browser fallback

The trusted host can still own chooser UI, defaults, and policy without also becoming the place where risky content is rendered by default.
That keeps the trusted UI/control-plane boundary honest.

### 2) A cleaner split between URI routing and file transfer

`file://` no longer acts as a back door around explicit export/import or file-open portals.
URI routing answers “which handler compartment gets this request?”
The data-transfer lane answers “how does data/file authority cross?”

### 3) Better receipts and support surfaces

A support/export surface can answer:

- which compartment asked to open the URI
- what scheme class it was
- which handler compartment was chosen
- which policy/default/consent path was used
- and whether the request was denied or routed

That is much easier to reason about than “something somewhere called an opener.”

## What is explicitly not baseline

The ordinary workstation lane does **not** require:

- ambient `xdg-open`-style host opener behavior from AppVMs
- host-native browsing of untrusted `http` / `https` content as the default route
- `file://` as a hidden cross-domain file-open shortcut
- arbitrary custom URI schemes automatically crossing compartments
- app-chosen handler execution without an intent-routing decision and route receipt

## Future bounded lane

A future richer URI-routing lane may still be useful.
But it should only arrive after an explicit RFC/ADR answers:

- how disposable-vs-persistent browser selection is expressed in policy,
- how chooser/default-app UX stays intelligible,
- how custom schemes avoid becoming covert privilege-escalation hooks,
- how richer handler metadata travels without leaking unnecessary observer state,
- and whether any host-side adapter lane is worth standardizing for profile **C** without weakening **B**.

The baseline chooser/default-app floor itself is now fixed separately in `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`.

Until then, the archive should optimize for the explicit compartment-preserving route.

## Related docs

- `docs/179-portals-and-powerbox.md`
- `docs/199-intent-routing-and-plumbing.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/537-workstation-remoted-session-surface-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- `spec/intent.request.schema.json`
- `spec/intent.route.receipt.schema.json`

Last updated: 2026-03-17r270
