# Rev0857 deep audit

## Mission-relevant finding

Security identity text in the sync domain depended on the ambient C++ stream
locale. The raw SHA-256 formatter inserted each byte as an integral hexadecimal
value through `std::ostringstream`. C++ numeric stream output applies locale
`numpunct` grouping to arithmetic types, so a legal grouped locale could insert
separators into hash text. A directory scan could reject the digest it had just
created; equal bytes no longer implied equal identity text across process
configuration.

## Waste and change amplification

The same area had three overlapping ownership problems: four direct OpenSSL
hash loops independently formatted terminal bytes; nested manifest digest
layers materialized complete aggregate strings; and validation returned entire
entries or manifests by value, copying every nested vector before hashing. The
large domain translation unit therefore owned cryptographic formatting,
serialization grammar, validation adaptation, and file I/O at once.

## Refactor

`security_tuple_digest` now owns the exact existing v1 tuple grammar and streams
it into `Sha256DigestBuilder`. `sync_manifest_identity` owns chunk, lineage,
entry-list, entry, version, folder, and mutation identities. Decimal framing
uses fixed buffers and `std::to_chars`; unknown entry kinds fail closed. The
domain validates by const reference and delegates. File scan, existing-file,
range, and staged verification all use the canonical digest builder.

## Semantic and compatibility result

The emitted v1 bytes are unchanged. An independent legacy oracle compares every
identity layer, including binary field contents and maximum counters. The
integrated corpus proves canonical lowercase hashes and byte-preserving transfer
under a hostile global locale. A 20,000-chunk input exercises the streaming
aggregate path without constructing a correspondingly sized tuple material
string.

## Audit result

The new source audit passes **31/31** checks and separately verifies sanitizer
compile and final-link inventory. The final registered structural inventory
passes **45/45**. The audit forbids ambient stream formatting, direct OpenSSL
contexts, unbounded aggregate material strings, and by-value manifest
validation in this boundary; it also binds the new owners, tests, CMake
inventory, sanitizer lanes, and rev0857 release verifier requirements.

## Remaining risk

Manifest validation still traverses attacker-influenced cardinality in-process,
and file hashing remains ordinary principal-process I/O. The extraction does
not create a sandbox, a complete resource budget, or a proof that all identity
domains are globally non-ambiguous. The monolithic sync domain, repetitive
CMake target inventory, and source-spelling audits remain substantial change
amplifiers. The next semantic priority remains object incarnation and causal
operation identity, not additional pathname heuristics.
