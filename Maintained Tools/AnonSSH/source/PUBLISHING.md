# Publishing AnonSSH

`make package-publication` creates a publication handoff under
`artifacts/publication/`. The ZIP intentionally contains no Git history, local runtime
state, credentials, private keys, build cache, or mutable router profiles.

The ZIP is GitHub-ready publication staging, not a repository-root archive: commit the
contents of `source/`, and upload `release/` separately as release assets. This keeps the
large executable and corresponding-source bundle out of ordinary Git history.

## Handoff layout

- `START-HERE.md` is this guide.
- `REVISION` identifies the exact source commit.
- `HANDOFF.json` describes the archive and supported binary target.
- `HANDOFF-SHA256SUMS` covers every other file in the handoff.
- `source/` is the Git-ready repository tree. Publish its contents as the repository
  root.
- `release/x86_64-linux/` is the complete release bundle. It contains the executable,
  release checksum inventory, manifests, licenses, SPDX SBOM, deterministic test
  reports, and the corresponding-source archive for AnonSSH, its embedded programs,
  Tor's selected static libraries, and the Java I2P reseed-certificate source. All
  source trees and vendored Rust crates are materialized as ordinary files; the archive
  contains no symlinks into the build machine's Nix store or elsewhere.
- `evidence/` contains selected machine-readable gate and mixed-bond compatibility
  evidence. It is supporting material, not required at runtime.

## Recommended GitHub publication

1. Extract the ZIP and verify `HANDOFF-SHA256SUMS` from its top-level directory with
   `sha256sum -c HANDOFF-SHA256SUMS`.
2. Create an empty GitHub repository and publish the contents of `source/` as its first
   commit. The prior development history is deliberately absent.
3. Create a release tag matching `release/x86_64-linux/version.txt` from that commit.
4. Upload the files from `release/x86_64-linux/` as release assets. Do not commit the
   large executable or corresponding-source archive into the ordinary source tree.
5. Keep `SHA256SUMS`, `manifest.json`, `report.json`, `sbom.spdx.json`, `sources.json`,
   `LICENSE`, and `THIRD_PARTY.md` beside the executable and source archive.
6. State accurately that this handoff is unsigned. `SHA256SUMS` detects corruption but
   does not authenticate the publisher.

The package target performs this check itself, but a publisher can independently prove
that the nested source archive contains no symlinks:

```sh
cd release/x86_64-linux
sha256sum -c SHA256SUMS
test "$(tar -tvzf anonssh-sources.tar.gz |
  awk 'substr($1, 1, 1) == "l" { count++ } END { print count + 0 }')" -eq 0
grep -F '"schema":"anonssh.corresponding-sources.v2"' sources.json
```

The included `anonssh` is a static x86-64 Linux executable with no dynamic-library
dependency. It embeds Tor, i2pd, OpenSSH `ssh`/`scp`/`sftp-server`, Dropbear, I2P reseed
certificates, and the curated I2P bootstrap corpus. It does not embed external client
tools such as rsync, Git, Borg, or SSHFS. `THIRD_PARTY.md`, `sbom.spdx.json`, and
`sources.json` distinguish executable payloads, statically linked Tor dependencies, and
the Java I2P certificate source.

## Binary verification

On an x86-64 Linux machine:

```sh
cd release/x86_64-linux
sha256sum -c SHA256SUMS
chmod 755 anonssh
./anonssh --version
./anonssh doctor
./anonssh test --json
```

The binary can then be installed as `anonssh` on `PATH`. First-use and server setup are
documented in `source/README.md`.
