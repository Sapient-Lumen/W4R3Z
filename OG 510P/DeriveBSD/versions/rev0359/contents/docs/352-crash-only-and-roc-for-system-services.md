# Crash-only + Recovery-Oriented Computing (ROC) as service discipline

A lot of “reliability” work dies in the gap between:
- elegant architecture, and
- what operators can actually do at 3am.

**Crash-only software** and **Recovery-Oriented Computing (ROC)** are pragmatic lessons:
design your system so the *normal* response to failure is **restart + recover quickly**, with clear state boundaries and evidence.

DeriveBSD is unusually well-positioned to bake this in, because it already:
- separates build artifacts from runtime state (`docs/217-state-datasets-and-migrations-as-evidence.md`)
- treats operations as receipts (`docs/229-evidence-spine-overview.md`)
- wants explicit service ownership (`docs/235-process-contracts-and-service-ownership.md`)

## What to steal

1) **One way down, one way up**
- to stop a service: crash it (terminate)
- to start a service: run recovery
No “restart potpourri” of special stop modes and bespoke reinit scripts.

2) **Micro-reboots instead of full reboots**
Restart *just* the failing component (or its supervisor) whenever possible.

3) **Soft-state bias**
Keep as much state as possible reconstructible (cacheable, replayable).
Durable state must be explicit and versioned (dataset + migrations).

4) **MTTR-first metrics**
Make Mean Time To Repair (MTTR) a first-class performance target.

## DeriveBSD adaptation

### 1) Service contracts must declare recovery semantics
Each service should declare:
- which state datasets it owns (and schema versions)
- recovery steps (rebuild caches, rebind handles, re-register portals)
- what “healthy” means (signals + budgets)

This integrates with the compiled service DB (`docs/173-compiled-service-database-bundles.md`).

### 2) Restart trees with budgets (pair with OTP lesson)
Combine this with supervision trees (`docs/349-supervision-trees-and-restart-strategies.md`):
- restarters do restarts
- policy decides escalation
- budgets limit flapping
- receipts record everything

### 3) Recovery as evidence
Recovery should produce receipts just like activation:
- “recovered from crash” event
- time-to-recover
- datasets migrated / replayed
- capability grants re-established

This makes MTTR measurable and debuggable.

## Non-goals (keep it tight)
- Not “everything is stateless.”
- Not “never reboot.”
- Not “all failures are fine.”
The goal is: **most failures don’t become operator heroics**.

## References
- Crash-Only Software (Candea/Fox): https://dslab.epfl.ch/pubs/crashonly.pdf
- USENIX page (HotOS’03): https://www.usenix.org/conference/hotos-ix/crash-only-software
- ROC draft (Brown et al.): https://roc.cs.berkeley.edu/papers/hpts01-draft.pdf
- Microsoft Research entry (ROC overview): https://www.microsoft.com/en-us/research/publication/recovery-oriented-computing-motivation-definition-principles-and-examples/
