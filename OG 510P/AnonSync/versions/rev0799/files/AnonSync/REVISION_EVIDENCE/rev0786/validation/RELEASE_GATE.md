# rev0786 release gate

Required publication lanes pass: the full GCC Debug suite, focused GCC
ASan/UBSan authority suite, 20 owner-generation repetitions, five peer-ingress
lifecycle repetitions, strict Clang syntax for every changed C++ translation
unit, six deterministic authority audits, source-diff hygiene, full-source
package preflight, and exact tested-tree/package projection verification.

The optimized GCC Release authority lane also passes 5/5 after the same build
tree was resumed across cloud command-window interruptions. It is recorded as
optional rather than publication-critical. One warning comes from the pinned
SQLite 3.53.3 amalgamation; changed AnonSync C++ is warning-free in the captured
strict lanes.

Publication remains fail-closed: the final directory, manifest file set and
hashes, ZIP paths, ZIP CRC, release-package verifier, and active source
projection must all pass before the archive link is emitted.
