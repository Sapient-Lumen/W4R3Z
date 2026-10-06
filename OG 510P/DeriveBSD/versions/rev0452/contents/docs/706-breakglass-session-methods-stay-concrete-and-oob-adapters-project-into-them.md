# Breakglass session methods stay concrete and OOB adapters project into them

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

## What changed

The breakglass method vocabulary is now intentionally small and concrete.

- `breakglass.grant.scope.allowed_methods` now allows only `console`, `serial`, and `ssh`
- `breakglass.receipt.session.method` now records only `console`, `serial`, or `ssh`
- `oob` is no longer a first-class breakglass access/session method

## Why this matters

“Out-of-band” is a useful adjective for approvals and maintenance ceremony, but it is too blurry to be a good authority noun.
It can refer to at least three different things:

- how an approval reached the box,
- which remote-presence adapter provided the console path,
- or how the machine booted into recovery in the first place.

Those are not the same implementation problem, and collapsing them into one breakglass `method` value makes receipts, profile defaults, and later adapter work harder to reason about.

## Accepted boundary

### 1) Breakglass methods are concrete access surfaces

For the reviewed emergency lane, the method vocabulary is now:

- `console`
- `serial`
- `ssh`

That is the authority-visible surface.

### 2) OOB approval stays allowed, but it is not the session method

The archive still supports offline / OOB approval ceremony where product posture requires it.
But approval transport is not the same thing as the session surface that actually exercised breakglass.

### 3) Adapter stacks project into those concrete methods

The first adapter mapping is deliberately boring:

- BMC KVM / HTML5 remote console projects to `console`
- Serial-over-LAN projects to `serial`
- virtual-media-assisted recovery remains bootstrap plumbing until it yields an actual `console`, `serial`, or `ssh` session, or else belongs to a separate install/reset lane

That keeps remote-presence compatibility real without turning every management stack into a distinct breakglass authority kind.

### 4) Richer adapter evidence is follow-on work, but the baseline receipt is now intentionally thin

This cut still does **not** standardize a full BMC / virtual-media / remote-presence evidence artifact family.
But the archive no longer leaves the baseline receipt fuzzy either.

richer adapter/runtime detail still stays redacted side evidence instead of quietly widening `breakglass.receipt`.
That includes launch/runtime data such as console URLs, ports, session ids/tokens, plugin choices, image locators, or copied console-entry hints (`docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md`).

The first follow-on cut was pre-session bootstrap exactness in `docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md`; the next one now explicitly freezes the baseline receipt as adapter-thin rather than reopening generic `oob` session vocabulary or vendor-specific runtime fields.

## First spec cut

The first implementation-shaped cut is narrow:

- remove `oob` from `spec/breakglass.grant.schema.json`
- remove `oob` from `spec/breakglass.receipt.schema.json`
- teach the nearby breakglass docs that OOB approvals remain valid while session methods stay concrete and adapter-projected

That is enough to stop drift without pretending the full adapter evidence UX is finished.

## Related docs

- ADR: `adrs/ADR-0296-breakglass-session-methods-stay-concrete-and-oob-adapters-project-into-them.md`
- breakglass lane: `docs/236-breakglass-and-recovery-mode.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- product defaults: `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`
- risk register: `docs/266-open-questions-and-risk-register.md`
- follow-on bootstrap join cut: `docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md`
- guardrail: `tools/check_breakglass_method_boundary.py`

## References

- DMTF Redfish `VirtualMedia` schema index entry: https://redfish.dmtf.org/redfish/schema_index
- Intel Serial-over-LAN setup guide: https://www.intel.com/content/www/us/en/support/articles/000059471/server-products.html
- Supermicro BMC remote-presence feature overview: https://www.supermicro.com/en/solutions/management-software/bmc-resources

Last updated: 2026-03-23r438
