# Workstation role-bound intent targets and chooser floor

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

`docs/539-workstation-intent-routed-uri-opening-floor.md` already fixed the *class* boundary: cross-compartment URI opening is an intent-routing act, `http` / `https` stays off the trusted host, `mailto` routes to communications, and `file://` does not bypass explicit file authority lanes.
This doc makes the next small but expensive cut:
**the workstation baseline uses trusted host-managed target roles and a bounded chooser, not arbitrary "open with…" app discovery.**

See also:
- ADR: `adrs/ADR-0130-workstation-role-bound-intent-targets-and-chooser-floor.md`
- intent router: `docs/199-intent-routing-and-plumbing.md`
- workstation URI floor: `docs/539-workstation-intent-routed-uri-opening-floor.md`
- desktop viability checklist: `docs/410-desktop-viability-checklist.md`
- workstation host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- typed remembered-state boundary: `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`

## Why this needs a hard decision

Once URI opening is explicit and compartment-preserving, the next place ambient authority tries to return is the chooser/default-app layer.
If DeriveBSD does not choose, people will naturally reach for the easiest thing:

- enumerate whatever handlers happen to be installed,
- let the source AppVM influence the target set,
- and turn first-open prompts into silent global-default rewrites.

That recreates the same ambient authority in a friendlier-looking UI.
The caller no longer *directly* launches the host browser, but it still steers trusted host policy by making the host act as a registry browser.

Upstream practice suggests a narrower floor:

- OpenURI-style portals already separate the user-facing chooser from the app-side request surface.
- AppChooser-style backends choose from a **provided list**, not from an unrestricted app registry.
- Android's role system shows that some handler classes are safer when the system treats them as a small set of host-managed roles such as browser, dialer, SMS, and home.
- Qubes-style OpenURL/OpenInVM flows commonly target named compartments or disposables instead of letting the source workload discover arbitrary handlers.

## Accepted baseline

For the ordinary workstation lane:

- cross-compartment routing resolves to a **target role**, not directly to an arbitrary caller-selected app id
- the minimum role vocabulary for URI-like routing is:
  - `browsing`
  - `communications`
- the trusted host may present an interactive chooser, but only among:
  - pre-enrolled compartments already authorized for that role,
  - and bounded disposable/persistent variants of that same role
- ordinary first-open prompts do **not** rewrite global defaults from untrusted context
- role/default assignment happens through trusted settings/admin UX, not as a side effect of a caller's `intent.request`
- `intent.route.receipt` must record both:
  - the chosen `target_role`
  - and the `resolution_mode` (`role-default`, `trusted-chooser`, or `policy-pinned`)

This keeps the chooser honest:
choosing a target stays a reviewable trusted-host policy act, not ambient application discovery wearing a dialog box.

## Practical model

### Role slots are small and explicit

The baseline does **not** need a giant handler ontology.
The minimum workstation floor only needs enough vocabulary to keep the previously accepted URI lane coherent:

- `browsing` for untrusted `http` / `https`
- `communications` for `mailto` and similar human-identity-bearing schemes

A future ADR may add more roles, but the baseline should stay intentionally small.

### Chooser scope is bounded

A trusted chooser may still be useful, but only for deciding **which enrolled target compartment for the same role** should receive the request.
Examples:

- persistent browser compartment vs disposable browsing lane
- work-mail compartment vs personal-mail compartment

What the chooser must not become:

- a registry of every installed host or guest app,
- a source-AppVM-controlled handler list,
- or a stealth path that mutates global defaults because the user clicked "always use this" in response to an untrusted prompt

### Settings own remembered defaults

Role assignment and remembered defaults belong in trusted settings/admin UX.
Changes to that remembered state should review through `intent.role.binding.diff`, not by diffing desktop registries or settings blobs.
That makes the important question legible:

> which compartment currently holds the `browsing` or `communications` role, and why?

That answer should come from a stable settings surface and evidence, not from grep'ing app menus or desktop-entry caches. `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md` now fixes that remembered state as typed state via an `intent.role.binding` object.

## Evidence tightening

The existing intent-routing artifacts remain the right lane:

- `spec/intent.request.schema.json`
- `spec/intent.route.receipt.schema.json`

But the route receipt now needs enough detail to explain target selection:

- `target_role` — which role the route resolved through
- `resolution_mode` — whether the route used:
  - `role-default`
  - `trusted-chooser`
  - `policy-pinned`

That makes support/export answers better:

- why did this URL land in *that* browser compartment?
- was the route the stable role default or a one-time chooser decision?
- was the target hard-pinned by policy?

## What is explicitly not baseline

The ordinary workstation lane does **not** require:

- broad "open with…" app discovery across host and guest apps
- caller-provided handler ids for cross-compartment routing
- first-open prompts that rewrite role defaults from untrusted context
- arbitrary custom roles for every application category before the browser/comms floor is working
- generic desktop-entry registries as the authoritative routing truth for profile **B**

## Future bounded lane

A richer chooser/default-app story may still be useful later.
But it should only arrive after an explicit RFC/ADR answers:

- whether more roles are worth standardizing,
- whether document-viewer/editor roles belong in the same baseline,
- and whether profile **C** needs a bounded host-native handler adapter lane.

Until then, the archive should optimize for **small role slots, trusted settings-owned defaults, and bounded chooser scope**.

## Related docs

- `docs/179-portals-and-powerbox.md`
- `docs/199-intent-routing-and-plumbing.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/539-workstation-intent-routed-uri-opening-floor.md`
- `spec/intent.request.schema.json`
- `spec/intent.route.receipt.schema.json`
- `spec/intent.role.binding.schema.json`
- `spec/intent.role.binding.diff.schema.json`

Last updated: 2026-03-17r272
