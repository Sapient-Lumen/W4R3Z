# Research notes: locale-free security bytes and streaming digests

Primary sources reviewed online:

- C++ working draft, `num_put` virtual functions:
  https://eel.is/c++draft/facet.num.put.virtuals
- C++ working draft, integer `to_chars`:
  https://eel.is/c++draft/charconv.to.chars
- OpenSSL 3.6 documentation, high-level digest API:
  https://docs.openssl.org/3.6/man3/EVP_DigestInit/

The C++ draft specifies that numeric stream output obtains the stream locale,
uses `numpunct`, and inserts thousands-separator characters according to the
facet's grouping for arithmetic types. The integral hexadecimal conversion is
still an arithmetic conversion, so `std::hex` does not make stream output
locale-independent.

The integer `to_chars` contract instead writes digits in the selected base,
uses lowercase `a` through `z` for digits above nine, emits no redundant leading
zeroes, and throws nothing. It is therefore a more suitable primitive for
security framing where exact byte spelling—not human localization—is the
contract.

OpenSSL's EVP digest interface supports incremental init/update/final operation.
AnonSync already wrapped that lifecycle in `Sha256DigestBuilder`; using the
reviewed owner prevents every caller from separately managing context lifetime,
error checking, final byte count, and hexadecimal rendering.

Implications for AnonSync:

- Locale must never be an implicit input to signatures, hashes, identifiers,
  JSON numbers, protocol framing, or durable evidence.
- Compatibility tests should reconstruct legacy bytes independently rather than
  compare two paths sharing the same serializer.
- Nested identities should stream already-frozen fields into a digest owner;
  allocating one aggregate string per layer multiplies memory and copy cost
  without adding authority.
- A streaming hash does not by itself bound hostile cardinality. Parser and
  validation budgets still need explicit entry, chunk, lineage, and total-byte
  ceilings.
- Extracted identity leaves make future protocol-version review cheaper: domain
  separation, field order, length framing, and terminal representation can be
  audited without reading the entire sync engine.
