# Disposable workspaces and template microVMs (Template → Lease → Dispose)

**Tier:** D (Research)  
**Profiles:** A, B, C  
**Pillars:** isolation, operability, reproducibility
**Patterns:** Broker→Lease→Receipt, Capsule, Adapter→Shadow→Replace  

Some tasks are *too risky* to run in a long-lived environment (opening random documents, browsing, inspecting untrusted artifacts,
running unknown tools, etc.). A strong operational pattern is to make “do it in an ephemeral compartment” the default, while still
keeping exports and evidence explainable.

This borrows the **TemplateVM / DisposableVM** shape from Qubes OS, but translates it into DeriveBSD’s
**Spec → Lock → Plan → Artifact → Activate** workflow, with receipts and stable review surfaces.

References:
- Qubes OS: DisposableVMs: https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-disposables.html
- Qubes OS: Templates (TemplateVMs): https://doc.qubes-os.org/en/latest/user/templates/templates.html

## The core translation (DeriveBSD shape)

### 1) Template as a derived artifact (immutable base)
Model a **template** as a normal derived image with explicit inputs:

- a base set digest (kernel/userland/toolchain split, if applicable)
- a closure of packages (or a “pkg lane” adapter set)
- a *template policy* (what services are allowed inside the template, what update lanes can modify it)

The template image remains immutable; updates happen by producing a *new template digest* and switching via normal generation/promotion rules.

### 2) Disposable instances as leased activations (no persistence by default)
A disposable workspace is not “a new kind of system”. It is:

- a `microvm.spec` (or jail spec) that **pins** a template digest
- an activation that issues a **lease** (TTL + policy + identity binding)
- a mandatory “brokered export” story for anything that should outlive the compartment

Pattern mapping (see `docs/397-pattern-catalog.md`):
- **Broker → Lease:** the workspace broker issues time-bounded authority to a disposable instance.
- **Plan → Receipt:** launching and exporting produce receipts that can be audited and bundled.
- **Registry → Diff → Gate:** template updates and policy changes remain reviewable (diffable) and promotable (gated).

Concretely, the evidence spine should be able to answer:
- *Which template digest did this instance run?*
- *What authority did it hold, for how long, and why?*
- *What did it export, and through which broker decisions?*

### 3) Exports are explicit, deterministic, and receipted
Persistence happens only through **declared exports**, never ambient shared state.

Examples of exports:
- a derived artifact build output (already a content-addressed store object)
- an “export bundle” (support bundle / incident bundle / investigation bundle)
- a user file export via portals/powerbox (policy-bound, recorded)

The export surfaces should include:
- the disposable instance lease id
- the template digest
- the broker decisions (portal grants, device leases, network policy)
- deterministic digests for exported bundles

## Activation sketch (optional lane)

This is intentionally an **optional lane**: profile B benefits most, but A/C can use it for “risky admin shells” or “untrusted tooling.”

A plausible CLI shape (illustrative, not normative):

- `derive workspace run --template <digest> --ttl 30m --policy <policy-digest>`
  - returns a lease id
  - writes a launch receipt (inputs, template digest, policy digest, resource budgets)
  - streams evidence events (lease snapshots, portal grants, device leases)

- `derive workspace export <lease-id> --bundle support`
  - emits a deterministic bundle artifact + receipt
  - can be required by policy before disposal (“no silent exits” for privileged lanes)

- `derive workspace dispose <lease-id>`
  - revokes the lease and destroys the instance
  - emits a revoke event and a disposal receipt

## UX constraints (don’t break pillars)

- **Reproducibility:** the template digest must be enough to reproduce the environment (within allowed impurity policy).
- **Isolation:** no ambient authority sharing; cross-compartment access is brokered and revocable.
- **Supply-chain:** template creation uses the same provenance + signature gates as any other artifact.
- **Operability/forensics:** “what happened in that disposable session?” must be answerable via receipts + bundle export.

## Why this is valuable even outside desktops

- **A (fleet host):** disposable “break-glass” admin shells; risky forensics tooling runs isolated and export-bundled.
- **B (workstation):** default for browser / document viewers / unknown tools; aligns with portal-driven UX.
- **C (general OS):** “safe sandbox” lane without forcing a desktop model.
- **D (appliance/regulatory):** test labs / compliance probes run as disposable compartments with deterministic evidence exports.

