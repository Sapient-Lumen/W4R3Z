# Revision notes: AnonSync rev0864

## Mission increment

Rev0864 corrects a semantic authority defect at the local transport boundary.
The socket harnesses labeled a frame digest “checked” after computing the digest
of received bytes, even though no expected digest was compared. A digest is an
observation; equality with a previously frozen digest is the integrity claim.

## Principal C++ corrections

1. Added `SyncPeerTransportDigestBoundFrame`, a final move-only owner that can be
   constructed only through `bind()`.
2. Required a canonical lowercase 64-hex expected SHA-256, positive frame
   budget, nonempty exact bytes, checked byte-count conversion, and an exact
   sender/receiver digest match.
3. Froze the digest of canonical encoded bytes before transmission in both the
   AF_UNIX socketpair and IPv4 loopback harnesses.
4. Moved exact received bytes into the owner and allowed decode/enqueue only
   after successful binding.
5. Added public encoded-versus-received digest evidence and integrated domain
   assertions that equality is canonical and exact.
6. Added an 11-check focused executable covering binary bytes, move-only
   transfer, malformed expected digests, zero/over-budget inputs, empty frames,
   and mismatch rejection.
7. Added the owner to invariant-owned source inventory, the integrated core,
   sanitizer compile/link sets, CTest, timeout policy, and revision-scoped
   package verification.

## Why the prior behavior was wrong

`sha256(received_bytes)` proves only that a program computed a digest. Without a
second value bound to the intended frame, it cannot detect substitution or
corruption and cannot justify a boolean named `frame_digest_checked`. The old
path therefore violated AnonSync's own maxim by promoting an observation to
transition evidence without the missing relation.

## Compatibility

The wire spelling, SQLite schema, durable identities, manifests, chunks, and
idempotency keys are unchanged. Result structs gain additive
`encoded_frame_digest` fields. Valid local fixture traffic is unchanged except
that digest evidence is now genuine. A mismatch fails before canonical decode or
durable ingress enqueue.

## Strategic audit result

The deeper review finds an assurance inversion: local authority owners and
release evidence are advancing faster than the replicated product they are
supposed to protect. Among 56 available revision notes from rev0805 through
rev0863, 49 still mention convergence and 40 still mention anonymity. Those are
not newly discovered caveats; they are long-lived P0 work.

The current release tree contains 34,549,940 bytes and 3,911 files under
`REVISION_EVIDENCE`, versus 4,768,942 bytes and 160 files under `src`. Fifty
Python audit programs contain 153 `read_text()` calls and 118 direct regex API
uses, but no Python AST import, tree-sitter use, libclang binding, or
`compile_commands.json` consumer. This does not make the audits useless, but it
makes lexical evidence a poor substitute for executable protocol semantics,
type ownership, model checking, property testing, and compiler-derived graphs.

## Validation summary

GCC 14.2 Debug all-target build; one uninterrupted 163/163 CTest campaign;
49/49 registered audits; genuine zero-work final closure; GCC focused 11/11;
Clang 17 `-Werror` focused and integrated-core build plus 11/11 focused runtime;
GCC ASan+UBSan focused 11/11 with leak detection; exact eight-file patch replay
across 314 active files; sealed-parent verification 26/26 ZIP and 22/22
directory.

## Deliberate nonclaim

The expected digest in this revision is frozen by the same local fixture before
transmission. It is not a remotely authenticated commitment. This revision does
not add TLS, Noise, peer certificates, key exchange, anonymity, metadata
protection, a remote daemon, or a whole-protocol convergence proof.
