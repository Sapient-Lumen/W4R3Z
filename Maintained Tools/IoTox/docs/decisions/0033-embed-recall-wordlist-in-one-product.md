# ADR 0033: Embed the pinned RecallRoot word list in the one product binary

**Status:** accepted and implemented in rev0009

## Context

IoTox is intended to install and operate as one product executable. RecallRoot-v1 depends on an
exact 7776-entry word list. Requiring an adjacent mutable data file creates a second operational
artifact, introduces path/version mismatch, and can make sovereign re-entry fail after an
incomplete installation.

## Decision

The attributed pinned EFF long word-list text is compiled into `iotox`. `RecallWordList::embedded`
parses it through the same strict dice-code, word-syntax, uniqueness, and exact-count validator
used for an external file.

The source copy remains under `third_party/` with its provenance and checksum. `--wordlist PATH`
is retained only as an explicit research/interoperability override. Normal owner commands use
the embedded contract.

## Consequences

The recall ceremony needs the executable plus the Argon2/libsodium implementation, not a second
runtime data file. The binary is larger by the word-list text, which is an acceptable trade for
one-product reliability.

Changing a word, order, list, or parsing rule would change the permanent recall contract and
requires a new versioned derivation rather than silently modifying v1.
