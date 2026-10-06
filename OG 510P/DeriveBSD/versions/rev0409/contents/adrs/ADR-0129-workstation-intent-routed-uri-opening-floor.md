# ADR-0129: Workstation intent-routed URI opening floor

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0127-workstation-remoted-session-surface-boundary.md` and `adrs/ADR-0128-workstation-cross-domain-datatransfer-floor.md` already cut two expensive workstation ambiguities down to size:

- GUI crossing is session-surface-first, not seamless host-native per-window integration.
- Clipboard/file transfer is an explicit brokered lane, not ambient shared state.

One daily-life boundary still remained too fuzzy:

- when an AppVM asks to open a URL, does the trusted host just run its own default browser or handler?
- do `http` / `https` links preserve compartment boundaries, or silently escape into the host for convenience?
- do `file://` and custom schemes sneak around the explicit transfer boundary we just accepted?

If DeriveBSD does not answer this now, the archive will drift toward the weakest answer:

- “just call xdg-open” style behavior will reintroduce ambient handler authority,
- the trusted host will quietly become the default renderer for untrusted web content,
- and URL handling will bypass the explicit compartment and evidence model that the workstation story now depends on.

Current practice points in a narrower direction.
Portal-style OpenURI APIs exist so sandboxed apps can open URIs under user control, and local-file opening stays on a separate file-open path.
Compartmentalized systems also commonly route risky links into separate browsing compartments or disposables rather than treating the trusted side of the system as the universal browser.

We need a small decision that keeps workstation ergonomics real without recreating host-side ambient authority.

## Decision

For profile **B** (secure workstation), the baseline URI-opening floor is now:

1. Cross-compartment URI opening is an explicit **intent-routing** act (`intent.request` → `intent.route.receipt`), not ambient host-side `xdg-open`-style behavior.
2. The trusted host is **not** the default renderer for untrusted external content. Ordinary `http` / `https` opens from AppVMs must resolve to a designated **browsing compartment** (ordinary browser AppVM or disposable-capable browser lane), not to a general host browser.
3. Human-identity-bearing schemes such as `mailto` should resolve to a designated **communications compartment**, not to arbitrary caller-chosen host handlers.
4. `file://` is **not** the cross-domain URI lane. Same-compartment local-file opens may stay local, but any cross-compartment file open still goes through the explicit file import/export / portal path.
5. Custom schemes are **deny-by-default** unless policy names an explicit target class / handler compartment and the resulting route stays receipted.
6. The route receipt remains the evidence surface: it binds the request digest, chosen handler, policy decision digest, and any consent/grant lineage used for the handoff.

## Consequences

- The archive no longer treats URL handling as a vague desktop convenience feature.
- B now has a compartment-preserving answer for the common “click a link” case: opening a URL is a brokered routing act, not a privilege escape into the host.
- The previous file-transfer boundary stays intact because `file://` is not allowed to masquerade as a cross-domain open primitive.
- The trusted host keeps ownership of chooser UI, policy, and receipts without becoming the place where risky web content is rendered by default.

## Profile effects

- **A** should usually deny or tightly scope URI-opening acts outside maintenance/admin lanes.
- **B** gets explicit `http` / `https` routing into a designated browsing compartment and designated-handler routing for a small scheme allowlist.
- **C** may later offer broader host-native defaults or local-handler adapters, but that is not the workstation baseline.
- **D** should keep URI-opening lanes minimal, maintenance-shaped, or absent; production/operator flows should prefer typed import/export or explicit bounded viewers.

## Not decided here

This ADR does **not** decide:

- the exact chooser/default-app UX,
- whether `http` / `https` should prefer a long-lived browser AppVM, a disposable browser, or policy-selected mix in each posture,
- the exact scheme allowlist beyond the default deny posture,
- how app-local deep-link schemes should be standardized,
- or the exact receipt vocabulary for richer routing outcomes.

Those remain later RFC/ADR topics.

## References / wiring

- general intent router: `docs/199-intent-routing-and-plumbing.md`
- workstation host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- workstation session-surface boundary: `docs/537-workstation-remoted-session-surface-boundary.md`
- workstation data-transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- new boundary doc: `docs/539-workstation-intent-routed-uri-opening-floor.md`
- desktop viability checklist: `docs/410-desktop-viability-checklist.md`
- existing evidence objects: `spec/intent.request.schema.json`, `spec/intent.route.receipt.schema.json`
