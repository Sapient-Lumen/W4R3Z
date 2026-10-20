# Security boundary

Toxsync verifies bytes and linked revision records. It does not decide who is authorized to
control a namespace; the embedding application must bind each namespace to an explicit
publisher key and policy.

Production acceptance order:

1. Decode within configured size and count ceilings.
2. Find the namespace's explicitly trusted Ed25519 publisher key.
3. Verify the HEAD signature and engine/resource policy.
4. Reject stale generations, unexpected gaps, forks, and parent mismatches.
5. Verify the root/index digest before decoding dependent metadata.
6. Fetch immutable pages/chunks into private staging names.
7. Verify every completed object before content-addressed publication.
8. Reconstruct into a private file and require the complete artifact SHA-256.
9. Unpack into a fresh staging directory with treepack path/resource limits.
10. Atomically activate the completed revision through application policy.

Tox friendship and transport encryption do not grant namespace authority. Availability
claims are scheduling hints only. A malicious peer can lie, stall, replay, or send corrupt
bytes; limits, deadlines, retries, cancellation, peer penalties, and final digest checks must
remain active.

The v1 weak checksum and 128-bit matching fingerprint are performance filters, not
publisher authentication. The complete artifact SHA-256 is mandatory.

The pin ledger is local retention policy, not authorization. Garbage collection fails closed
when a pinned root/page cannot be decoded. Conservative reachability may leak storage through
false positives, which is preferable to false deletion.

Ed25519 signing currently uses OpenSSL EVP. The dependency-minimum build intentionally lacks
signing rather than substituting an unaudited implementation. Accelerated and portable
SHA-256/rolling backends must produce identical formats and digests.

Standalone `head-keygen` never replaces an existing filesystem entry. On Unix, each key is created
with `O_EXCL|O_NOFOLLOW`, exact descriptor permissions, and complete-write checking; if the second
file cannot be created, the newly created private half is removed. This protects ordinary operator
mistakes and target-creation races in an owner-controlled directory. A same-UID process that can
mutate that directory is outside this boundary. This is not a substitute for a hardware-backed
production identity. IoTox does not use this standalone key as its namespace trust root.

When retained publication inputs are enabled, they land as one private staging directory followed
by an atomic rename. Exact retry re-derives the revision and accepts an already-landed directory only
when its complete requested entry set, types, sizes, and SHA-256 identities match the new signed
HEAD. A partial, extra, linked, or corrupt retained directory fails closed before HEAD mutation.

Treepack rejects symlinks and special files. Never unpack over a live directory. Store roots,
HEAD state, pin journals, private keys, and staging paths must be owner-controlled real
filesystem locations; a privileged local attacker remains outside the current threat model.
