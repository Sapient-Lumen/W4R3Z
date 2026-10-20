# Repository datacubes

The ordinary official repository and its Git history are the project authority. A repository
datacube is a bounded, read-only handoff object for discussing an exact committed state with another
ChatGPT session, reviewer, future office holder, or public GitHub reader. It does not revive the
historical hidden-root packaging contract and does not transfer project authority.

## Build

Start from a clean worktree after the desired commit. For a rich internal
conversation/recovery cube:

```sh
./tools/make-repository-datacube.sh
```

For the recommended public/GitHub repository seed with no local history:

```sh
./tools/make-repository-datacube.sh --seed
```

For the older public profile that omits nested founding cubes and lets the
tool choose full history only when it fits under the ceiling:

```sh
./tools/make-repository-datacube.sh --public
```

For a full-history provenance handoff that carries full reachable Git history
and does not use the default 128 MB ceiling:

```sh
./tools/make-repository-datacube.sh --upload
```

The default destination is ignored `DR0Pbox/`. The name records the America/New_York timestamp and
12-character commit prefix. A sibling `.sha256` records the outer ZIP digest. To select another
destination:

```sh
./tools/make-repository-datacube.sh /absolute/output/directory
```

The default ceiling is strictly fewer than 128,000,000 bytes. This is deliberately decimal 128 MB,
not 128 MiB. The tool fills available space with meaningful provenance but never with padding. It
always prioritizes the committed source and a cloneable Git bundle, then includes available
same-commit standalone and validation evidence. The `seed` profile uses a
single source-snapshot commit by default and is the preferred first public
repository seed. The `conversation` profile greedily admits unchanged founding
cubes while reserving 500,000 bytes for the final manifests and ZIP variance.
The `public` profile omits nested founding cubes by default so the artifact is
smaller and easier to review while retaining automatic history selection. The
`upload` profile is the full-history provenance handoff: full reachable Git
history by default, no default size ceiling, and no nested founding cubes
unless explicitly requested.
Standalone distribution is copied only when `dist/standalone/build-info.txt` records the same
`source-commit` as the datacube commit; stale host binaries are skipped and named as skipped in the
manifest. If full reachable Git history would make the archive exceed the ceiling, the default
`auto` mode records `git/HISTORY_MODE=snapshot` and embeds a single exact source-snapshot bundle
instead. Force behavior with `IOTOX_DATACUBE_HISTORY_MODE=full|snapshot|auto`.

The defaults can be tightened for another transfer channel:

```sh
IOTOX_DATACUBE_MAX_BYTES=64000000 \
IOTOX_DATACUBE_HEADROOM_BYTES=500000 \
./tools/make-repository-datacube.sh --seed
```

## Contents

Every cube has one versioned root and begins with `CHATGPT_START_HERE.md`. It contains:

- `repository/`: every tracked file at the exact clean commit;
- `git/IoTox.bundle`: a cloneable bundle; `git/HISTORY_MODE` is `snapshot`
  for seed handoffs and otherwise `full` when it contains local refs and
  reachable history, or `snapshot` when the strict size ceiling required a
  single exact source-snapshot commit;
- `distribution/standalone/`: the available binary, licenses, verification record, and exact pinned
  source inputs, when their recorded source commit matches the cube commit;
- `validation/`: selected raw matrix, fuzzer, stress, and XML coverage evidence;
- `provenance/founding-cubes/`: original revision cubes that fit the remaining budget, only when the
  selected profile includes them;
- a manifest, byte/path index, and payload checksums.

Generated build trees, dependency work trees, `.sandworm`, `.sandwurm`, arbitrary untracked files,
and mutable or secret runtime state are excluded. The builder refuses dirty source,
sensitive-looking paths in Git history, private-key PEM markers in the packaged source snapshot
and, when a full-history bundle is selected, in reachable Git history, unsafe nested archive paths,
and archive symlinks.

Validation discovery accepts both the original `final-matrix-*` / `fuzzer-smoke*` names and
milestone-qualified `*-final-matrix` / `*-fuzzer-smoke` names. This keeps the most recent Ratox gate
with the cube without making arbitrary build-tree files part of the handoff. Validation files remain
host evidence with their own hashes; the committed source and Git bundle define repository state.

## Verify and recover

Verify the outer checksum, archive, every inner payload, and Git bundle:

```sh
sha256sum -c IoTox*repository-datacube-*.zip.sha256
./tools/make-repository-datacube.sh --verify \
  IoTox-seed-repository-datacube-YYYY.MM.DD.HH.MM.SS-COMMIT.zip
```

After extraction, recover an ordinary Git repository from the bundle with:

```sh
git clone git/IoTox.bundle IoTox
```

The plain `repository/` tree is intended for immediate inspection. The bundle is the recovery layer;
check `git/HISTORY_MODE` before treating it as historical evidence. Historical cubes are provenance;
another ChatGPT session does not need to recursively open them for ordinary current-state discussion.
