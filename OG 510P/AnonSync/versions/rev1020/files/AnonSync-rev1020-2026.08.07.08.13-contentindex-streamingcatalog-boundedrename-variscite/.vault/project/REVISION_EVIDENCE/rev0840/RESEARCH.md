# AnonSync rev0840 research notes

Accessed 2026-07-18. These references informed the implementation and next-work
speculation; they do not imply that AnonSync implements the cited specifications.

## C++ stream locale

The current C++ working draft states that when no locale has been imbued, stream locale
queries use a copy of the global C++ locale in effect at construction. Locale facets can
therefore change numeric punctuation in `std::ostringstream`. Rev0840 demonstrates this
with a custom `numpunct` grouping facet and pins `std::locale::classic()` in the heartbeat
encoder.

- C++ draft, input/output library and locale behavior:
  https://eel.is/c++draft/iostreams.base

## JSON number grammar

RFC 8259 defines JSON numbers from decimal digits with optional sign, fraction, and
exponent components. Thousands separators and grouping characters are not in the
grammar. The preserved rev0839 output containing `7_000` is therefore not interoperable
JSON.

- RFC 8259, The JavaScript Object Notation (JSON) Data Interchange Format:
  https://www.rfc-editor.org/rfc/rfc8259
- ECMA-404, The JSON Data Interchange Syntax:
  https://tc39.es/ecma404/

## Deterministic serialization

RFC 8785 exists because cryptographic hashing/signing requires invariant bytes and JSON
permits multiple serializations of equivalent data. It explicitly calls for output
independent of locale settings. Rev0840 does **not** claim JCS compliance: the heartbeat
uses fixed implementation member order and integer-only numeric fields, but it does not
implement the complete RFC 8785 algorithm.

- RFC 8785, JSON Canonicalization Scheme:
  https://www.rfc-editor.org/rfc/rfc8785

## Interpretation and speculation

The immediate inference is broader than this heartbeat: every persistence, signing, or
wire serializer should state its exact byte contract and pin or bypass ambient locale.
A shared “machine text writer” may be useful, but only after format owners are classified;
a helper that merely imbues streams would hide rather than solve ordering, escaping,
floating-point, size-budget, and schema-version questions.

A stronger future pattern is an owning `Publication<T>` or `Authority<T, Invariant>`
value created only after validation, with the serializer unable to reach the broad live
domain model. The rev0840 heartbeat publication is a concrete local experiment with that
shape, not a general proof that the pattern fits every subsystem.
