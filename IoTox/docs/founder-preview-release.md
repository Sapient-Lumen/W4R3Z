# Founder-preview release

Status: repeatable local release path, not a stable/no-concern product claim.
Updated 2026-10-01.

IoTox can be cut as a founder-preview build for private operator use and
carefully labeled evaluation. That is different from saying sync is safe as the
only copy of precious data or Ratox is a universally certified SSH replacement.
The release commands keep that difference executable.

## Command trail

Start with the read-only plan:

```sh
tools/iotox-repo.sh release-plan founder-preview
```

Then build and test the selected source. The ordinary local path is:

```sh
tools/iotox-repo.sh doctor
tools/iotox-repo.sh build
tools/iotox-repo.sh test quick
tools/iotox-repo.sh test full gcc-debug
```

Before packaging, require a clean committed worktree and run the release gate
against the exact binary that will be represented by the release:

```sh
tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox
```

The check must report:

```text
iotox-release-check-v1
channel=founder-preview
git-clean=1
diff-check=pass
shell-syntax=pass
ship-check=pass
stable-brake=blocked-as-expected
decision=founder-preview-release-path-ready
```

If the stable brake does not say `blocked-as-expected`, the release page must be
revisited: either the stable channel really graduated, or the founder-preview
boundary became stale.

Package conversation/recovery state only from a clean committed tree. For the
first public/GitHub repository seed, use the seed profile:

```sh
tools/iotox-repo.sh datacube --seed
tools/make-repository-datacube.sh --verify /path/to/IoTox-seed-repository-datacube.zip
```

For the older public profile with automatic history selection under the default
128 MB ceiling, use:

```sh
tools/iotox-repo.sh datacube --public
tools/make-repository-datacube.sh --verify /path/to/IoTox-public-repository-datacube.zip
```

Use `tools/iotox-repo.sh datacube --upload` only when the recipient explicitly
wants full local Git history. Use `tools/iotox-repo.sh datacube --conversation`
when the recipient explicitly wants the richer internal conversation cube with
nested founding-cube provenance.

If standalone source inputs are available on the host, package them after the
same clean-tree check:

```sh
tools/package-source-inputs.sh
```

## Required label

Every founder-preview handoff should carry this label or an equivalent:

```text
IoTox founder-preview. Sync is a working-copy synchronization surface that still
requires versioned recovery custody, restore drills, and recovery runbooks for
precious data. Ratox is a profile-bound self-machine control surface; sudo is
not default-on and must be enabled only through an owner-reviewed profile plus
host sudo/PAM policy. Stable/no-concern shipping remains blocked by
`iotox ship-check all stable`.
```

## What this release path proves

- the repository can name its release channel in one native product command;
- founder-preview sync/Ratox claims remain machine-readable;
- stable/no-concern claims fail closed until the missing gates are closed;
- the repo companion can reproduce the command trail;
- datacube packaging refuses dirty source, sensitive-looking history, unsafe
  archive paths, symlinks, and oversize output; and
- support-bundle planning points at the same release gate.

## What it does not prove

- versioned recovery-custody signoff;
- precious-data readiness;
- storage-media certification; IoTox does not claim or pursue it;
- full Ratox fleet/kernel/security certification;
- sudo policy safety on a target machine;
- Tor/I2P anonymity, reliability, or route diversity beyond the included
  evidence scope;
- binary portability outside the represented build environment; or
- that a datacube alone is a product release claim rather than an exact-state
  handoff object.

## Stable graduation

Stable changes the question from “can the founder evaluate and dogfood this with
the warnings attached?” to “can an ordinary operator ship this without concern?”

That requires `iotox ship-check all stable` and
`tools/iotox-repo.sh release-check stable --iotox /path/to/iotox
--evidence-manifest stable-evidence.manifest` to pass without `--allow-dirty`,
using the stable dossier described in
[`docs/stable-release-evidence.md`](stable-release-evidence.md). Do not update
the release label before those commands and their underlying evidence agree.
