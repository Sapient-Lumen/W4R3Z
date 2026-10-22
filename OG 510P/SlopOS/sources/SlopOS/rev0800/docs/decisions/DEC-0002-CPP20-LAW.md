# DEC-0002 — C++20 implementation and harness law

**Status:** accepted

All active implementation, reference-model, oracle, explorer, trace, vault, proof-
emission, and office-audit machinery is C++20.  CMake is build description, not an
alternative implementation language.  Formal proof source may use Isabelle/HOL.
A transient shell or Python command may assist one construction turn, but it may
not become required project machinery.

The trusted core uses a restricted profile:

- no exceptions or RTTI;
- no allocation during authoritative transitions;
- no virtual dispatch;
- no owning raw pointers;
- no mutable dynamic initialization;
- no implicit narrowing or signed-overflow assumptions;
- no address-derived identity;
- explicit-width serialized values;
- fixed capacities and total error results;
- low-level casts, MMIO, assembly, barriers, and lifetime manipulation eventually
  confined to a named platform boundary with proof obligations.

This choice does not confer language-level memory safety.  The assurance response
is layered: constrained code, two compilers, warnings, sanitizers, bounded
exploration, differential execution, canonical traces, explicit invariants, and a
formal refinement program.  None substitutes for the others.
