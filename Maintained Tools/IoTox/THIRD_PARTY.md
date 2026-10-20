# Third-party notices

IoTox's original source is offered under MIT. A source-linked standalone binary also contains or
links the pinned components below, which retain their own licenses. This summary is informational;
the corresponding license texts are copied into `dist/standalone/licenses/` by the standalone build.

| Component | Version | License | Source |
|---|---:|---|---|
| c-toxcore | 0.2.23 | GPL-3.0-or-later | <https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23> |
| cmp | `52bfcfa17d2eb4322da2037ad625f5575129cece` | MIT | <https://github.com/TokTok/cmp> |
| libsodium | 1.0.22 | ISC | <https://download.libsodium.org/libsodium/releases/> |
| Argon2 reference implementation | 20190702 | Apache-2.0 OR CC0-1.0 | <https://github.com/P-H-C/phc-winner-argon2> |
| EFF large word list | 2016-07-18 | EFF publication terms; see bundled provenance | <https://www.eff.org/dice> |

The exact URLs and SHA-256 digests used by the build are recorded in `dependencies.lock` and the
generated `build-info.txt`. Distributing a combined binary requires compliance with c-toxcore's GPL
terms, including the applicable corresponding-source obligations. The repository's MIT grant does
not override those obligations. Official CI enables `IOTOX_PACKAGE_SOURCES=1` so its artifact also
contains the exact repository commit and pinned upstream archives used by the build; this supports,
but does not replace, release-specific compliance review.

The standalone artifact also carries deterministic SPDX 2.3 JSON binding these six source/data
components to the exact executable SHA-256. It deliberately excludes the deployment-specific libc,
C++ runtime, kernel, service image, and other operating-system packages; the image assembler must add
that runtime closure rather than treating the source-component SBOM as complete deployment inventory.

c-toxcore 0.2.22 is additionally pinned as a test-only savedata/rolling-upgrade fixture. It is built
only by provider qualification checks and the Sandwurm rolling laboratory, is not linked into IoTox,
and is not a distributed product component (ADRs 0152 and 0153).

## Optional rescue deployment payload

The separately built `iotox-rescue-toolbox` package is not linked into `iotox` and is not part of the
six-component product SBOM above. A deployment distributing it also carries:

| Component | Version | License | Source |
|---|---:|---|---|
| oksh | 7.9 | Predominantly public domain; portability files retain BSD/ISC notices | <https://github.com/ibara/oksh/releases/tag/oksh-7.9> |
| Toybox | 0.8.14 | 0BSD | <https://landley.net/toybox/> |

Its output includes `share/iotox-rescue/manifest` plus Toybox's `LICENSE` and oksh's `LEGAL` and
`CONTRIBUTORS` files. The exact upstream archive hashes are in `dependencies.lock`. Those files do
not replace review of copyright/license headers in the complete oksh source or deployment-specific
inventory. ADR 0287 owns the decision to keep this payload separate and to exclude
Toybox's pending shell.
