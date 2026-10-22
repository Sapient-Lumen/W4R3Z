# Steward

[SlopOS](../README.md) · [Complete editions](../DOWNLOADS.md#steward)

Steward gives component life an accountable shape. Starting, receiving activation material, becoming ready, serving work, cooling down, and stopping are different moments. Its proposed service fabric makes each moment identifiable and explainable, so an operator can ask what happened to this particular run rather than interpret a generic green light. Within the SlopOS family, Steward’s subject is lifecycle truth.

## A service with a remembered life

The early supervision posture starts from explicit component roots identified by `cid`, not raw process IDs or whatever escaped into a host process tree. A supervised service stays foreground and accountable. Stopping follows a bounded sequence: cooperative request, grace, then escalation. Restart replays the declared manifest and activation rather than recovering some larger, undocumented authority from the surrounding machine. Host service managers can sit beneath a compatibility boundary without defining Steward’s public language. [Supervision posture, rev0023](../sources/Steward/rev0023/docs/30-architecture/supervision-posture-v0.md).

Repeated failure brings out the human purpose. One exit cause describes one run; a repair gate describes the pattern across runs. Cooling down means another automatic attempt may follow. Repair-required means something explicit must change before trying again. The envisioned status surface keeps recent cycles, causes, and quieting history available, with actions such as explain, inspect recent cycles, or attach a failure bundle. Rather than a spinner that never confesses what it is waiting for, the operator gets a reason and a next step. [Repair-gate posture](../sources/Steward/rev0023/docs/30-architecture/repair-gate-posture-v0.md).

This is Steward’s characteristic aesthetic: a service has a legible biography. Its delays and interruptions belong in the interface, not only in logs that someone must reconstruct after the fact. The design makes patience, restraint, and explicit repair possible operational states.

## A concrete executable center

The later lifecycle harness supplies a small `demo.web` component. Its manifest names an image digest, the entry selector `svc/web`, bounded restart settings, readiness requirements, and allowed activation names. The activation set describes the kinds, rights, and origins of material delivered to a fresh instance without publishing raw descriptors or bearer tokens.

An accepted example progresses from manifest and activation set through spawn, activation receipt, material freshness, readiness, and serving. Nearby counterexamples test what must not slip through: readiness before activation receipt, a restart that adds an undeclared `admin/debug` activation, a stale operation aimed at a previous runtime cycle, or a stop request that claims the component is already stopped. Canonical JSON and SHA-256 bind the records, while validators reject duplicate keys, unknown fields, shell command text masquerading as an entry selector, and forbidden raw-handle fields. These are implemented checks derived from record contents. They validate simulated event sequences; they do not spawn or supervise a process. [Lifecycle harness, rev0201](../sources/Steward/rev0201/tools/steward_lifecycle_harness.py).

The latest dependency work carries the same discipline into relationships. A declaration says a component requires something; a condition witness says what was observed from a particular vantage; a gate says allow, block, defer, or degrade; a fallback explains a degraded mode. None alone means the requested operation ran. [Dependency-gate corpus contract](../sources/Steward/rev0201/docs/40-verification/dependency-gate-corpus-v0.md).

The validator follows references between those packets, detects an identifier reused for different canonical content, rejects checks expired at the gate’s decision time, and refuses an allow decision citing an unavailable hard dependency. A degraded decision needs a known active fallback. That is real multi-record semantic validation, but it checks the cited evidence rather than discovering every dependency or calculating a system-wide start order. [Dependency-gate harness](../sources/Steward/rev0201/tools/steward_dependency_gate_harness.py).

## Small enough to belong

Rev0201 organizes this executable work into twenty narrow corpora. Their declared purpose is to make dangerous conflations testable, not to ship a service manager, scheduler, broker, remote administration bus, or shell. The ambition lies in the precision of the contracts those future systems would have to honor. [Minimum proof slice](../sources/Steward/rev0201/docs/40-verification/minimum-steward-proof-slice.md).

Steward also draws a clear constitutional line. SlopOS retains native capability meaning and final compatibility; Steward’s component and activation profiles remain proposals for adoption, not a parallel law imposed on the primary system. [SlopOS crosswalk](../sources/Steward/rev0201/docs/30-architecture/slopos-boundary-crosswalk-v0.md). Its companion map leaves shell intent to Schell, repair surfaces to Helm, crossings to Harbor, appraisal to Ward, object references to ViewFS, and foreign-ground classification to Foundry. A Ward-derived warrant may inform a lifecycle request without becoming ambient administrator mode. [Companion boundary map](../sources/Steward/rev0201/docs/30-architecture/companion-boundary-map-v0.md).

Steward’s promise is a computer that can explain the life of its work without confusing a plan, a receipt, and an accomplished effect.
