#!/usr/bin/env bash
# Fetch Nicotine+ upstream source lanes for the next cube revision.
# Output: one directory containing individual source-tree directories, archives, metadata, and hashes.
# Upload the resulting .zip or .tar.gz to ChatGPT for rev0003.
set -euo pipefail

repo_url="https://github.com/nicotine-plus/nicotine-plus.git"
out_root="${1:-Nicotine+DEV-rev0003-upstream-sources-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$out_root"/{source-trees,archives,pypi,metadata,logs}

log() { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$out_root/logs/fetch.log"; }
run() { log "+ $*"; "$@" 2>&1 | tee -a "$out_root/logs/fetch.log"; }

log "Fetching metadata from $repo_url"
if command -v git >/dev/null 2>&1; then
  run git ls-remote --heads --tags "$repo_url" > "$out_root/metadata/ls-remote-heads-tags.txt" || true
else
  log "git not found; curl-only archive downloads will be attempted."
fi

# Direct GitHub archive URLs are useful even when cloning is slow. They create source snapshots,
# but only git clones/worktrees give exact commit metadata without extra API calls.
if command -v curl >/dev/null 2>&1; then
  log "Downloading GitHub source archives for stable, 3.3.x, and master lanes"
  curl -fL --retry 3 --retry-delay 2 -o "$out_root/archives/github-tag-3.3.10.tar.gz" \
    "https://github.com/nicotine-plus/nicotine-plus/archive/refs/tags/3.3.10.tar.gz" || true
  curl -fL --retry 3 --retry-delay 2 -o "$out_root/archives/github-branch-3.3.x.tar.gz" \
    "https://github.com/nicotine-plus/nicotine-plus/archive/refs/heads/3.3.x.tar.gz" || true
  curl -fL --retry 3 --retry-delay 2 -o "$out_root/archives/github-branch-master.tar.gz" \
    "https://github.com/nicotine-plus/nicotine-plus/archive/refs/heads/master.tar.gz" || true

  log "Downloading public GitHub API metadata for issues/PRs/milestones/releases"
  curl -fL --retry 3 --retry-delay 2 -o "$out_root/metadata/github-releases.json" \
    "https://api.github.com/repos/nicotine-plus/nicotine-plus/releases?per_page=100" || true
  curl -fL --retry 3 --retry-delay 2 -o "$out_root/metadata/github-milestones-open.json" \
    "https://api.github.com/repos/nicotine-plus/nicotine-plus/milestones?state=open&per_page=100" || true
  curl -fL --retry 3 --retry-delay 2 -o "$out_root/metadata/github-issues-open-page1.json" \
    "https://api.github.com/repos/nicotine-plus/nicotine-plus/issues?state=open&per_page=100&page=1" || true
  curl -fL --retry 3 --retry-delay 2 -o "$out_root/metadata/github-pulls-open-page1.json" \
    "https://api.github.com/repos/nicotine-plus/nicotine-plus/pulls?state=open&per_page=100&page=1" || true
fi

if command -v git >/dev/null 2>&1; then
  log "Creating full git clone and individual worktree directories"
  run git clone --origin upstream "$repo_url" "$out_root/git-full" || true
  if [ -d "$out_root/git-full/.git" ]; then
    (
      cd "$out_root/git-full"
      git fetch --tags --prune upstream '+refs/heads/*:refs/remotes/upstream/*' 2>&1 | tee -a "../logs/fetch.log" || true
      git remote show upstream > "../metadata/remote-show-upstream.txt" 2>&1 || true
      git branch -a --verbose --no-abbrev > "../metadata/branches-verbose.txt" 2>&1 || true
      git tag --list --sort=-v:refname > "../metadata/tags-version-sorted.txt" 2>&1 || true

      # Stable/current release baseline.
      git worktree add -f "../source-trees/github-tag-3.3.10" "3.3.10" 2>&1 | tee -a "../logs/fetch.log" || true
      # Release-candidate / supported 3.3.x line.
      git worktree add -f "../source-trees/github-branch-3.3.x" "upstream/3.3.x" 2>&1 | tee -a "../logs/fetch.log" || true
      # Future/default development line.
      git worktree add -f "../source-trees/github-branch-master" "upstream/master" 2>&1 | tee -a "../logs/fetch.log" || true

      for d in ../source-trees/*; do
        [ -d "$d/.git" ] || [ -f "$d/.git" ] || continue
        name="$(basename "$d")"
        git -C "$d" rev-parse HEAD > "../metadata/${name}.commit.txt" 2>&1 || true
        git -C "$d" status --short > "../metadata/${name}.status.txt" 2>&1 || true
        git -C "$d" log -1 --format=fuller > "../metadata/${name}.commit-fuller.txt" 2>&1 || true
      done
    )
  fi
fi

# PyPI artifacts for release provenance. This is optional but useful for comparing tag/sdist/wheel.
if command -v python3 >/dev/null 2>&1; then
  log "Attempting PyPI release-artifact download for nicotine-plus==3.3.10"
  python3 -m pip download --no-deps --dest "$out_root/pypi" 'nicotine-plus==3.3.10' 2>&1 | tee -a "$out_root/logs/fetch.log" || true
fi

# Extract direct archives into individual directories if git worktrees were not created.
if command -v tar >/dev/null 2>&1; then
  for archive in "$out_root"/archives/*.tar.gz; do
    [ -f "$archive" ] || continue
    base="$(basename "$archive" .tar.gz)"
    dest="$out_root/source-trees/${base}"
    if [ ! -d "$dest" ]; then
      mkdir -p "$dest.tmp"
      tar -xzf "$archive" -C "$dest.tmp" --strip-components=1 2>>"$out_root/logs/fetch.log" || true
      if [ -n "$(find "$dest.tmp" -mindepth 1 -maxdepth 1 2>/dev/null | head -n 1)" ]; then
        mv "$dest.tmp" "$dest"
      else
        rm -rf "$dest.tmp"
      fi
    fi
  done
fi

# Hash all files for later verification.
if command -v sha256sum >/dev/null 2>&1; then
  (cd "$out_root" && find . -type f -not -path './SHA256SUMS' -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS)
elif command -v shasum >/dev/null 2>&1; then
  (cd "$out_root" && find . -type f -not -path './SHA256SUMS' -print0 | sort -z | xargs -0 shasum -a 256 > SHA256SUMS)
fi

cat > "$out_root/README-FOR-REV0003.md" <<'EOF'
# Nicotine+ upstream source bundle for rev0003

Please upload this whole archive to ChatGPT. For rev0003, it should be unpacked under:

`sources/upstream-current-and-future/`

Expected source lanes:

- `source-trees/github-tag-3.3.10/` — current stable tag baseline.
- `source-trees/github-branch-3.3.x/` — supported 3.3.x / 3.3.11 release-candidate lane.
- `source-trees/github-branch-master/` — future 3.4.0.dev1/default development lane.
- `pypi/` — PyPI 3.3.10 sdist/wheel provenance, if pip download succeeded.
- `metadata/` — ls-remote, branch/tag, release, milestone, issue, and PR snapshots.
- `SHA256SUMS` — content verification.

Do not edit these directories after fetching; create a new bundle if you need a fresher snapshot.
EOF

# Package. Prefer zip because it is easy to upload and inspect; fallback to tar.gz.
if command -v zip >/dev/null 2>&1; then
  zip_path="${out_root}.zip"
  rm -f "$zip_path"
  zip -qr "$zip_path" "$out_root"
  log "Created $zip_path"
else
  tar_path="${out_root}.tar.gz"
  rm -f "$tar_path"
  tar -czf "$tar_path" "$out_root"
  log "Created $tar_path"
fi

log "Done. Upload ${out_root}.zip or ${out_root}.tar.gz for rev0003."
