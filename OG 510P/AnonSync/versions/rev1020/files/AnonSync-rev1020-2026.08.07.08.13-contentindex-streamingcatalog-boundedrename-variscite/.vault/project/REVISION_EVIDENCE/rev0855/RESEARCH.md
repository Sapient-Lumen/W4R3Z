# Rev0855 research and speculation

No new external source is required to justify the rev0855 C++ correction: the
defects are directly executable in the parent source and are proved by the new
compile-time and process/thread tests.

The broader architectural speculation remains:

- separate an encrypted, content-addressed data plane from a compact
  authenticated control plane;
- represent every accepted transition as a frozen authority capsule carrying
  object incarnation, causal context, key/schema epoch, policy, limits, and
  durability evidence;
- make the reference convergence model the protocol specification and generated
  history oracle, not prose adjacent to implementation;
- treat authentication, confidentiality, anonymity, metadata resistance,
  forward secrecy, and post-compromise recovery as separate properties with
  separate adversaries and tests; and
- treat local SQLite correctness as one component of a cross-resource crash
  state machine covering database transactions, sidecars, manifests, atomic
  files, directory barriers, receipts, and downstream effects.

Rev0855 reinforces one design rule for that destination: a compatibility mode
must be a narrower type, not a runtime switch on an authority-bearing owner.
