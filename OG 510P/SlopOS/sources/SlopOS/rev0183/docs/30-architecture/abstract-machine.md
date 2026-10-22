# Abstract machine (v0): state, objects, transitions

This is the nucleus for refinement. It should remain small but precise.
Notation is informal here; later versions may become mechanized.

## State
Let machine state `S` include:
- `Objs`: finite map `ObjID -> Obj`
- `Caps`: finite map `CapID -> Cap` (or embedded in per-domain CSpaces)
- `Domains`: set of domain identifiers
- `Threads`: set of thread/vCPU identifiers
- `Maps`: relation capturing authorized memory mappings
- `RunQ`: scheduler state (constrained by chosen concurrency model)
- `NDet`: nondeterminism providers (Clock/Entropy handles); in D-NONDET profiles there is no ambient access; in D-RR replay, reads consume CH-RR `time_tick`/`entropy` events
- `PStore`: persistent store state (optional; D-PERSIST). Abstractly: a set of commits + named roots + epoch metadata sufficient to reconstruct durable capability graphs (CH-CAPSTORE).

## Objects
`Obj` is a tagged union:
- `Domain { cspace, vspace, ... }`
- `Thread { domain, regs, state, ... }`
- `Endpoint { queue, ... }`
- `MemFrame { size, owner, ... }`
- `PageTable { level, entries, owner, ... }`
- `SharedRegion { participants, rights, frames, ... }`
- `View { bindings, mounts, owner, ... }` (optional; explicit name→cap mapping; see `view-objects.md`)
- `Interrupt { routing, owner, ... }`

## Capabilities
`Cap = (obj: ObjID, rights: Rights, meta: Meta)` where:
- `Rights` is a bitset (e.g., {Read, Write, Execute, Map, Derive, Grant})
- `Meta` may include constraints (e.g., range, guard) as designed

### Derivation rule (sketch)
A transition may produce `Cap'` only via an explicit derivation function `derive(Cap, params)` that is monotone in rights (unless the design explicitly allows amplification and then must justify it).
This supports invariant **I-CAP-1**.

## Memory mappings
Represent mapping authority by requiring a capability with `Map` right to create an entry in `Maps`.
Invariant **I-MAP-1** constrains `Maps` so that cross-domain access occurs only through `SharedRegion` objects (I-SHARE-1).

## Ownership discipline (cross-cutting)
Even in UP bring-up mode and the SMP-big-lock baseline, we phrase safety invariants using an explicit **ownership/transfer** discipline:
- Every mutable kernel object has a well-defined owning PD (or is explicitly shared under a declared sharing rule).
- Any transfer of authority (cap mint/delegate) or transfer of ownership (handoff of an object) is an explicit state transition, logged and validated.
- Mapping/memory objects (frames, page tables) have an owner and a permission lattice; writable aliases of privileged memory are forbidden by invariant, not convention.

This is intentionally future-proofing: SMP profiles can then reuse the same invariants by treating ownership transitions as the boundaries where mutual exclusion (big lock or finer-grained locks) must serialize updates.

## Transitions (core)
Transitions are partial functions `step: S × Action -> S` with actions:
- `CreateObj(type, args)`
- `DeleteObj(obj)` (subject to lifecycle constraints)
- `MintCap(src_cap, params)` / `DeriveCap(...)`
- `Map(domain, frame, perms, vaddr)` / `Unmap(...)`
- `Send(ep, msg)` / `Recv(ep)`
- `Schedule(next)`

## Safety theorem shape (goal)
For the chosen action set `A_slice`:
1) (Initialization) `Init` implies invariants `I_slice`
2) (Preservation) For all `a ∈ A_slice`, if `I_slice(S)` and `step(S,a)=S'` then `I_slice(S')`
3) (Security consequence) `I_slice` implies claim properties (e.g., capability integrity and isolation)

This structure keeps “what we prove” aligned with Claim/Invariant registries.

## ACP slice (LLM-assisted control, non-TCB but specified)
We specify the Agent Control Plane validator as a small relation over CH-ACP actions that can only emit kernel actions with explicit authorization. See `docs/70-llm-control/acp-validator-semantics.md`.
