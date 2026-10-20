# Revision packaging

Status: current seed/public/upload/conversation repository-datacube contract. Updated 2026-10-01.

## Seed filename contract

```text
IoTox-seed-repository-datacube-YYYY.MM.DD.HH.MM.SS-COMMIT.zip
```

IoTox rules:

- timestamp is America/New_York local time at final archive creation;
- `COMMIT` is the represented clean source commit prefix;
- the sibling `.sha256` names the same ZIP plus `.sha256`;
- final user link text, sandbox target basename, and archive basename must be identical;
- renaming an already delivered archive is prohibited; and
- the seed profile omits local history and nested founding cubes unless an operator explicitly
  overrides it.

Use the seed profile for GitHub/public review, first repository upload, and ordinary external
discussion. Use the public profile when you want the older automatic history behavior under the size
ceiling. Use the richer upload profile only when the ZIP itself should carry full local provenance:

```text
IoTox-upload-repository-datacube-YYYY.MM.DD.HH.MM.SS-COMMIT.zip
```

The upload profile keeps full reachable Git history by default and has no
default ZIP size ceiling. It still excludes mutable local state, generated
build junk, sockets, identities, and other prohibited material. Use the
conversation profile when the recipient needs the internal recovery/conversation
bundle:

```text
IoTox-repository-datacube-YYYY.MM.DD.HH.MM.SS-COMMIT.zip
```

Historical `Project-Name-rev####-...zip` handoffs counted delivered conversation snapshots. They
remain valid provenance names for old cubes, but they are not the default package contract for this
ordinary Git repository.

## Active repository-datacube shape

`tools/make-repository-datacube.sh` creates one verified ZIP with exactly one commit-addressed top
level directory:

```text
IoTox-seed-repository-datacube-YYYY.MM.DD.HH.MM.SS-COMMIT/
├── CHATGPT_START_HERE.md
├── MANIFEST.md
├── FILE_INDEX.tsv
├── SHA256SUMS
├── repository/                 tracked source from the exact clean commit
├── git/IoTox.bundle            cloneable full-history or source-snapshot bundle
├── git/HISTORY_MODE            `full` or `snapshot`
├── git/SOURCE_COMMIT           original repository commit represented by the source tree
├── distribution/standalone/    optional verified host build and immutable inputs
├── validation/                 selected host-generated validation evidence
└── provenance/founding-cubes/  optional unchanged prior cubes within the size ceiling
```

The public profile uses `IoTox-public-repository-datacube-...`, the upload
profile uses `IoTox-upload-repository-datacube-...`, and the conversation profile uses
`IoTox-repository-datacube-...` for the outer ZIP and internal root.
The internal name and every payload file are covered by the datacube checksums and verifier.

## Included

- tracked source, headers, build files, tools, tests, mocks, and fuzz seeds;
- active and historical documentation, decisions, governance, and research records;
- tracked lightweight validation receipts and summaries;
- optional same-commit distribution/validation artifacts admitted by the datacube builder; bulky
  replay executables, fuzz executables, CTest logs, build trees, and standalone attempts remain
  host-local or ignored unless a future decision promotes a tiny receipt;
- a cloneable Git bundle: for seed, a single exact source-snapshot commit; for
  other profiles, full reachable local history when selected or when it fits
  below the strict ceiling, or a single exact source-snapshot commit when full
  history would make a ceiling-bound archive too large;
- optional verified standalone host artifacts and exact checksummed source inputs;
- the standalone binary's deterministic SPDX 2.3 source-component inventory and strict verification
  marker when a distribution is present;
- optional unchanged founding cubes admitted under the strict archive-size ceiling when the selected
  profile includes them.

## Excluded and prohibited

- a working-tree `.git/` directory;
- untracked compiler trees, caches, dependency work directories, and temporary test state;
- live `.toxsave` identities, RecallRoot phrases, private keys, device identity stores, signed customer
  authority ledgers, rollback guards, command/profile stores, runtime sockets, FIFOs, journals, or
  received files;
- Python bytecode/cache directories, core dumps, editor debris, and unrelated host logs;
- unsafe archive paths, symlink entries, or unverified mutable provider downloads.

## Required construction and verification

1. complete the final compiler, sanitizer, analyzer, and process evidence appropriate to the revision;
2. run `tools/iotox-repo.sh release-plan founder-preview` for a bounded founder-preview handoff, or
   the stable channel only after `iotox ship-check all stable --evidence-manifest PATH` graduates;
3. run `tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox` against the exact
   binary represented by the handoff, preserving the stable/no-concern brake;
4. verify any tracked lightweight receipts, keep bulky replay/build evidence in ignored locations,
   and do not reintroduce prebuilt binaries into the committed source tree unless a future decision
   explicitly promotes a small receipt;
5. require `git diff --check` and a clean committed worktree;
6. run `tools/iotox-repo.sh datacube --seed` for the recommended public/GitHub
   seed, `tools/iotox-repo.sh datacube --public` for automatic history under
   the public ceiling, `tools/iotox-repo.sh datacube --upload` for a full-history
   private provenance handoff, or `tools/iotox-repo.sh datacube --conversation` for a richer
   internal conversation cube;
7. verify the generated ZIP with the same tool's `--verify` mode and `unzip -tq`;
8. copy or rename the verified ZIP to the exact human-facing filename;
9. run the datacube verifier and ZIP integrity test again against that exact final file;
10. publish only the complete final filename as the link text.

The verifier rejects unsafe paths and symlinks, checks the one-root shape and payload digests,
validates the Git bundle, confirms the repository entry point, and enforces the package size ceiling
when the selected profile has one. Upload-profile archives are verified without the default public
size ceiling unless `IOTOX_DATACUBE_MAX_BYTES` is set explicitly.

## Historical hidden datacube layout

Revisions before repository foundation used a lone visible `BOOTSTRAPROSE.md` with source hidden under
`IoTox/.datacube/`. Historical scripts and documents remain for provenance and old-cube verification.
They are not the active rev0051 delivery shape and must not be used to describe a new repository
handoff.
