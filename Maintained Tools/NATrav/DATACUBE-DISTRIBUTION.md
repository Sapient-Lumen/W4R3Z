# Self-Carrying NATrav Executable

NATrav's primary publishable binary is one static executable that runs
`natrav-node` directly and also carries the complete clean tracked repository,
documentation, tests, build machinery, and the C++ source needed to reproduce
its Datacube container. Git history, credentials, local runtime state, caches,
generated test evidence, VM images, and packet captures are not embedded.

The Datacube kernel is the bounded launcher and source-inspection layer inside
the executable. It verifies and streams the indexed static node into a sealed
private Linux memfd, then replaces itself with that node using `fexecve` while
preserving the original argument vector and environment. It writes no extracted
executable to disk. After replacement, Datacube is absent from the running
node and owns no traversal policy.

## Release Assets

`make natrav-datacube-release` writes these ignored artifacts under
`dist/v<version>/`:

- `natrav-v<version>-x86_64-linux-<commit>`: the primary directly executable
  NATrav binary, including source and documentation;
- `Datacube-MAIN-rev<revision>-NATrav-v<version>-x86_64-linux-<commit>.zip`: the canonical
  two-member `BOOTSTRAPROSE.md` plus `datacube` pair;
- `NATrav-v<version>-x86_64-linux-datacube-<commit>.manifest.json`: identities,
  sizes, source relation, and node relation;
- `SHA256SUMS`: checksums for the publishable assets.

The Datacube-mandated `Datacube-MAIN-rev<revision>-` prefix binds the upstream
lineage; the remainder independently binds NATrav's version, platform, and Git
commit. The ZIP, executable, manifest, and checksum inventory are appropriate GitHub
Release assets. The repository itself may be public with all tracked files at
the release commit. Do not commit release binaries, Datacube archives, Nix
results, credentials, `.sandworm/`, `authcreds/`, `target/`, `artifacts/`, VM
disks, packet captures, or local rollout logs.

## Build

The build requires a clean tree, the repo's Nix environment, and a selected
Datacube MAIN archive. By default it discovers the pointer in a sibling
`../datacube-science` checkout. An explicit archive is preferable in automation:

```sh
make doctor
make natrav-datacube-release \
  DATACUBE_MAIN_ARCHIVE=../datacube-science/subjects/Datacube-MAIN-rev1227-2026.10.23.03.59-shared-transaction-projection-traits.zip
make validate-natrav-datacube-release \
  NATRAV_EXECUTABLE=dist/v0.52.0/natrav-v0.52.0-x86_64-linux-<commit>
```

The build performs these checks before publishing:

1. Verify the selected Datacube archive against its canonical pointer when the
   sibling checkout supplies one.
2. Materialize the Datacube source and apply the carried auditable descendant
   patch. The patch scopes Python-path rejection to the Datacube C++ source
   tree, makes project admission/metadata language-agnostic, makes NATrav the
   default execution target, and moves Datacube operations under an explicit
   `datacube` namespace.
   The descendant executable inherits the verified parent's linked revision unless an
   explicit Datacube-compatible revision is supplied for a deliberate fork.
   Rev1227's flat extension requires its historical
   `CPP20_ONLY_NO_PYTHON_ACTIVE_TOOLING` constructor-admission token. NATrav
   separately declares its mixed-language set there, while the patched
   per-tree metadata authoritatively marks the project language-agnostic and
   the Datacube source C++20-only.
3. Rebuild the patched static Datacube runtime twice and require byte identity.
   Build or admit a static `natrav-node`, require version 0.52.0 and the exact
   production-envelope response, and stage only tracked NATrav files.
4. Reject secret-bearing names, high-confidence secret content, links, special
   files, dirty release trees, and bounded-format count/size violations. NATrav's
   envelope permits 32,768 entries, 512 MiB raw per tree, and a 1 GiB release
   executable; narrower path, metadata, and decoded-index limits remain security
   controls.
5. Build a draft executable to derive the native bootstrap prose commitment,
   then build the final executable twice and require byte identity.
6. Verify Datacube source identity, linked-pair identity, full project
   materialization, independent file checksums, the re-extracted node, and
   direct execution of that node through the final executable.

## Run NATrav

The downloaded file is the NATrav binary. No extraction or installation step is
required on Linux x86-64:

```sh
chmod 0555 natrav-v0.52.0-x86_64-linux-<commit>
./natrav-v0.52.0-x86_64-linux-<commit> version
./natrav-v0.52.0-x86_64-linux-<commit> serve-config config.json
```

Every argument other than the reserved first argument `datacube` belongs to
`natrav-node`. The direct binary therefore has the same CLI contract as the
standalone Nix-built node.

The `datacube` namespace is deliberately smaller than upstream Datacube. NATrav
retains only project/source inspection, exact materialization, source relation,
bootstrap, and linked release-custody operations. Historical checkpoint
delegation, `DATACUBE_ARCHIVE_ROOT` fallback execution, reusable agents,
mutation plans, and candidate construction are rejected at a dedicated route
allowlist and omitted from help.

## Inspect Carried Source

The explicit `datacube` namespace exposes source and documentation without
changing the default product behavior:

```sh
./natrav-v0.52.0-x86_64-linux-<commit> datacube project-summary
./natrav-v0.52.0-x86_64-linux-<commit> datacube \
  project-find 'birthday-one-hard'
./natrav-v0.52.0-x86_64-linux-<commit> datacube \
  project-read docs/TRAVERSAL_PORTFOLIO.md
```

Materialize the complete project into a fresh target beneath an existing
operation root:

```sh
mkdir -p work
./natrav-v0.52.0-x86_64-linux-<commit> datacube project-materialize \
  --operation-root "$(pwd -P)/work" NATrav \
  0000000000000000000000000000000000000000000000000000000000000001
cd work/NATrav
sha256sum -c NATRAV_DATACUBE_FILES.sha256
```

Materialized files are intentionally read-only. Make a writable copy before
development. `LICENSE` grants the carried project under MIT; third-party
components retain their own notices and licenses.

## Boundaries

The current executable is Linux x86-64 and requires `/proc/self/exe`,
`memfd_create`, sealing, and `fexecve`. The node is static and portable across
ordinary compatible hosts, but privileged traversal mechanisms still depend on
the host kernel, network, policy, and credentials described by the production
envelope. The executable proves exact bytes and relations, not who published
them, universal reachability, independent custody, or the truth of claims made
by those bytes.

The executable kernel source is a declared descendant of canonical Datacube MAIN rev1227,
not a byte-identical copy. The external manifest records the canonical parent
archive, parent executable and source identities, and the exact descendant patch
digest. The patch and resulting C++ source are both carried for inspection.

The executable is also the sole portable NATrav source handoff. The former
source-only `tar.zst` generator was retired because it duplicated the carried
project, used a separate 128 MiB ceiling, and created a second publication truth.
