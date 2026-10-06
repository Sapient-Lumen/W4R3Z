# KeyKOS/EROS lessons: capability kernels, confinement, and revocation by indirection

DeriveBSD already leans heavily into “capabilities as the unit of authority” (Capsicum, portals, leases, attenuating tokens).
Pure capability kernels like **KeyKOS** and **EROS** are worth studying because they show what happens when this idea is taken seriously *end-to-end*:
- no ambient namespaces as authority
- delegation is a first-class primitive
- confinement is something you can *mechanically check*

We do **not** want to rebuild DeriveBSD as a capability microkernel.
But these systems contain a few high-signal lessons that apply directly to DeriveBSD’s broker/portal/policy model.

## Lesson 1: confinement wants a standard packaging/launch mechanism

EROS emphasizes *constructors*: the system’s standard way to instantiate software in a confined form.
The important point is not the exact mechanism — it’s that confinement gets easier when there’s a single,
blessed packaging and launch path.

**DeriveBSD mapping:**
- treat `derive unit` activation and portal-mediated grants as the only supported ways to get new authority
- ensure every unit launch produces a receipt + manifest digest
- bake “confinement checkability” into promise-profile linting (`docs/271-promise-profile-vocabulary-and-lint.md`)

## Lesson 2: revocation is cheapest with indirection

Capability systems repeatedly rediscover the same practical trick:
- don’t hand out raw authority
- hand out a reference to a revocable *proxy* (an indirection cell)

**DeriveBSD mapping:**
- leases are the indirection cell (`docs/182-capability-leases-and-revocation.md`)
- portals return proxy handles (revocable streams / objects)
- persistent file capabilities (“bookmarks”) should usually be proxy-based, not path-based (`docs/198-persistent-file-capabilities-bookmarks.md`)

## Lesson 3: “authority graphs” are a real operational object

Pure capability systems make it natural to ask:
- who can reach what?
- along which delegation edges?

DeriveBSD already has the right bones:
- capability routing manifests (`docs/140-capability-routing-manifests.md`)
- causality graphs (`docs/246-causality-graphs-and-minimal-evidence-bundles.md`)
- authority budgets (`docs/298-authority-budgets-and-permission-drift-alarms.md`)

**Tightening suggestion:** treat the *authority graph* as something we can snapshot and diff:
- “what new delegation edges appeared?”
- “what was revoked?”

## References

- KeyKOS OSR paper (architecture overview): https://pdos.csail.mit.edu/6.828/2008/readings/keykos-osr.pdf
- “EROS: A fast capability system” (Shapiro et al.): https://flint.cs.yale.edu/cs428/doc/eros.pdf
- “Verifying the EROS confinement mechanism” (Shapiro et al.): https://flint.cs.yale.edu/cs428/doc/eros-verify.pdf

Last updated: 2026-02-27
