# ADR-0130: Workstation role-bound intent targets and chooser floor

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0129-workstation-intent-routed-uri-opening-floor.md` already decided that cross-compartment URI opening is an explicit intent-routing act, that the trusted host is not the default renderer for untrusted `http` / `https`, and that `http` / `https` plus `mailto` route into designated compartment classes rather than ambient host handlers.

That still left one expensive ambiguity open:

- when the trusted host needs to choose *which* handler compartment gets the request, do we present a broad "open with…" chooser sourced from whatever apps happen to be installed?
- do first-open prompts from untrusted callers silently mutate defaults?
- can a caller steer routing toward an arbitrary handler as long as the host shows a dialog?

If DeriveBSD leaves that unanswered, the archive will drift back toward the classic desktop failure mode:

- sandbox escape by handler proliferation,
- chooser UI that is really ambient authority in disguise,
- and per-launch "just pick an app" prompts that mutate global defaults from untrusted context.

Current practice points toward a narrower floor.
Portal APIs already separate "open this URI" from the backend chooser implementation, and Android's role system shows that some handler classes are safer when the system treats them as explicit roles (browser, SMS, dialer, home) rather than as an unconstrained registry.
Compartmentalized systems such as Qubes also commonly route URL/file opens into named target compartments or disposables instead of letting the source workload discover arbitrary target apps.

We need a small decision that keeps chooser/default-app UX intelligible while preserving the compartment boundary accepted in ADR-0129.

## Decision

For profile **B** (secure workstation), the baseline chooser/default-app floor is now:

1. Cross-compartment intent routing resolves into **trusted host-managed target roles**, not arbitrary app ids supplied by the caller or discovered from the caller's environment.
2. The minimum workstation role set for ordinary URI handling is:
   - `browsing`
   - `communications`
3. The trusted host may present an interactive chooser, but that chooser is limited to:
   - pre-enrolled compartments already authorized for the requested target role,
   - and bounded disposable/persistent variants of that same role.
4. Ordinary first-open prompts from untrusted callers do **not** opportunistically rewrite global defaults. Default-role assignment happens through trusted settings/admin UX, not as a side effect of an untrusted open request.
5. The routing receipt must say **which target role** was used and **how resolution happened** (`role-default`, `trusted-chooser`, or `policy-pinned`) so support/export surfaces can explain why the request landed where it did.
6. Profile **C** may later allow a broader host-native adapter lane or richer handler registries, but that is not the workstation baseline and must not weaken **B**.

## Consequences

- The archive no longer treats chooser/default-app UX as an ambient desktop convenience layer.
- `http` / `https` and `mailto` now have a stable, reviewable answer for both *class* and *target-selection method*.
- The trusted host keeps ownership of chooser/settings UX without allowing untrusted callers to rewrite global routing state.
- Route receipts become more supportable because they can answer both *which handler ran* and *which role-selection path selected it*.

## Profile effects

- **A** should usually keep these roles absent or tightly maintenance-scoped.
- **B** gets a small trusted role vocabulary and a chooser limited to pre-enrolled target compartments or bounded disposable variants.
- **C** may later expose richer chooser/default-app semantics, but only behind an explicit adapter or later ADR.
- **D** should keep these roles minimal, maintenance-shaped, or absent in production/operator images.

## Not decided here

This ADR does **not** decide:

- the full future role taxonomy beyond the minimum `browsing` / `communications` floor,
- the exact storage format for remembered role assignments,
- the exact disposable-vs-persistent policy vocabulary,
- or whether file/document viewer roles should join the same floor later.

Those remain later RFC/ADR topics.

## References / wiring

- intent router overview: `docs/199-intent-routing-and-plumbing.md`
- workstation URI floor: `docs/539-workstation-intent-routed-uri-opening-floor.md`
- new boundary doc: `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`
- workstation host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- desktop viability checklist: `docs/410-desktop-viability-checklist.md`
- evidence objects: `spec/intent.request.schema.json`, `spec/intent.route.receipt.schema.json`
