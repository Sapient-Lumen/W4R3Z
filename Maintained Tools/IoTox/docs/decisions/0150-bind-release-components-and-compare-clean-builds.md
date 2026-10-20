# ADR 0150: Bind release components and compare clean builds

Date: 2026-08-24

Status: accepted

## Context

The source-linked product already pins and checksums its upstream archives, copies license texts,
and proves incremental binary-hash stability. That is not a machine-readable component inventory,
and rebuilding inside one existing CMake tree does not test build-root leakage. A useful release gate
must remain deterministic, must bind the exact executable, and must not claim that project source
dependencies describe a deployment host's complete runtime closure.

## Decision

- Generate deterministic SPDX 2.3 JSON for every standalone and Nix source-linked executable.
- Bind the exact executable SHA-256 and six package records: IoTox, c-toxcore, its pinned cmp
  submodule, libsodium, Argon2, and the embedded EFF word list.
- Take upstream versions, archive URLs, SHA-256 values, and declared licenses only from the checked-in
  dependency lock. Record the complete clean source commit when one is available.
- Derive the SPDX creation time from `SOURCE_DATE_EPOCH` or the clean source commit, and derive the
  document namespace deterministically from release identity, source identity, and binary digest.
- Strictly verify the exact package, file, checksum, and relationship sets. An extra alias, missing
  dependency, changed executable, or lock drift is a failure.
- Compare standalone distributions produced in distinct empty CMake build roots. Require byte-exact
  equality for the binary, SBOM, provenance record, verifier transcript, notices, and licenses.
  Delete the temporary build roots on every exit.
- Label the result as a same-host, same-toolchain comparison. Independent builders and the deployed
  operating-system closure remain separate release evidence.

## Consequences

The ordinary standalone verifier now refuses a missing or mismatched SBOM, CI exercises a clean
second product build instead of an incremental relink, and the Nix package carries its SBOM at
`share/doc/iotox/iotox.spdx.json`. Release consumers can trace the exact embedded source graph without
confusing MIT original code with the licenses of linked components.

The document is not a vulnerability attestation, VEX statement, license opinion, complete compiler
toolchain inventory, or deployment image SBOM. A distribution must add its libc, C++ runtime, kernel,
service configuration, and other operating-system packages at image assembly time.
