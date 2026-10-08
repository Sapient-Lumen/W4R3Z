# AnonSync rev0852

## Mission increment

AnonSync's implemented heart is to turn each untrusted observation into the
narrowest process-, thread-, connection-, generation-, lifetime-, type-, policy-,
resource-, and durability-bound capability that may authorize one deterministic
recoverable transition. Owning bytes without owning their interpretation is not
enough: the type relationship used at a retained callback boundary must be
proved before erasure and must remain inseparable from the lifetime it governs.

Rev0852 applies that rule to application policy state behind SQLite's retained
authorizer callback.

## Severe defect corrected

Rev0851 replaced borrowed non-null `void*` policy contexts with
`std::shared_ptr<void>`, correctly owning lifetime and moving custom deleters out
of SQLite's connection mutex. Its public constructor still accepted two
independent values:

1. a C callback that cast `void*` to some application type; and
2. an erased shared owner whose actual element type was invisible.

Any callback could therefore be paired with any shared object. The object would
remain alive, but the callback could interpret its address as an unrelated type,
creating undefined behavior inside an authorization boundary. The state machine
proved *when* memory was alive but not *what* memory the callback was authorized
to interpret.

## Delivered

- Replaced the context-bearing public constructor with
  `make_sync_sqlite_owned_authorizer_policy<Policy>(std::shared_ptr<T>)`.
- Added a C++20 constrained policy concept that requires an object, non-array,
  non-volatile context, a supported callback value, invocation with exact
  `T&`/SQLite argument shape, and an exact `int` result.
- Admitted non-null function pointers and empty structural callables such as
  noncapturing lambdas; rejected null function pointers, member pointers, and
  stateful compile-time adapters.
- Replaced the callback-plus-`shared_ptr<void>` representation with one
  `TypedPolicyCapsuleModel<T, Policy>` containing the exact `shared_ptr<T>` and
  invocation behavior.
- Removed all `shared_ptr<void>`, `static_cast`, and `reinterpret_cast` use from
  the owned policy boundary.
- Preserved genuinely const contexts, aliasing shared pointers, exact stored
  pointer identity, custom deleters, and original ownership control blocks.
- Preserved move-only, non-move-assignable, process-incarnation-bound ownership;
  source validation occurs before capsule transfer, and destruction validates
  before virtual/shared ownership teardown.
- Kept a context-free compatibility lane whose C callback always receives
  `nullptr`; non-null application state has only the typed factory lane.
- Migrated the integrated connection-authority custom-deleter probes and the
  transaction exception cutpoint policy to typed construction.
- Kept the raw compatibility rejection test meaningful with a dedicated raw ABI
  fixture instead of routing a typed callback through the legacy overload.
- Expanded the focused owner corpus from 20 to 30 checks, including compile-time
  negative contracts, const ownership, aliasing, custom deletion, child-local
  construction, and inherited-process fail-stop paths.
- Expanded the existing composed authorizer audit from 35 to 41 checks instead
  of adding an overlapping audit.
- Made both integrated typed consumers and the upgraded audit mandatory in
  release packages from rev0852 onward without invalidating rev0851.
- Corrected exact process-test inventories after the child-local test added one
  reviewed inherited spawn: one raw-fork implementation, 13 consumer
  translation units, 24 wrapper spawn sites, and 31 inherited/fresh-image sites.

## Audit/refactor conclusions

The new boundary has one runtime authority object rather than two values that
must agree by convention. Its type erasure is below the proof edge and retains
the exact ownership object. This is materially safer than merely hiding casts in
a helper because callers cannot form the mismatch through the public API.

The complete clean build again demonstrated a major change amplifier: most of
the wall time is concentrated in the monolithic core and selftest translation
units even though this revision changes a dependency-light boundary. The cube
should continue extracting invariant-owned libraries and reducing recompilation
fan-out. Structural audits are valuable when they inventory dangerous escape
hatches, but exact numeric inventories must be updated as part of the same
change that adds a reviewed site; the first complete registry run caught this
correctly.

## Validation

The final active source passes:

- a complete GCC 14.2 C++20 Debug all-target Ninja build;
- an immediate final dependency-closure build with `ninja: no work to do`;
- all **148/148** registered tests in one uninterrupted invocation;
- all **43/43** registered structural audits;
- **992/992** direct focused GCC Debug checks;
- Clang 17 `-Werror` focused build and **992/992** runtime checks;
- GCC 14 ASan+UBSan with leak detection and **992/992** focused checks;
- **250/250** repeated focused executions;
- **362/362** focused structural checks;
- sealed rev0851 parent ZIP verification at **26/26** and directory verification
  at **22/22**;
- an exact rev0851-to-rev0852 source patch that replays across **276/276** active
  files with zero mismatch; and
- final directory and ZIP verification against exact manifest, projection,
  revision evidence, safe archive paths, and CRC integrity.

Exact commands, logs, audit payloads, lineage, source delta, research, scope, and
active projection are under `REVISION_EVIDENCE/rev0852/`.

## Scope limits

The factory proves callback/context type compatibility and exact result type; it
does not prove policy semantics, purity, determinism, synchronization, or
absence of exceptions. The existing bridge catches policy exceptions and fails
closed, but a throwing policy is still application failure.

A child-created owner is bound to the child process, yet cannot prove that an
arbitrary supplied `shared_ptr` control block was not copied from the parent.
POSIX post-fork restrictions remain important in multithreaded programs.

SQLite exposes no getter for the installed authorizer. Named lifetime claims and
nonce probes prove reviewed installation/acquisition boundaries, while arbitrary
foreign raw replacement between probes remains constrained by source inventory.
The close path assumes the exact typed connection owner has quiesced ordinary
users; general concurrent teardown race freedom is not claimed.

No claim is made for ThreadSanitizer, full-project sanitizer coverage,
sanitation of bundled SQLite, Release-mode all-target behavior, Windows runtime
behavior, arbitrary power-loss cutpoints, hostile-input worker isolation,
distributed convergence, payload confidentiality, anonymity, metadata hiding,
forward secrecy, post-compromise recovery, or secure erasure.
