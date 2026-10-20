#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
default_max_bytes=128000000
max_bytes_env=${IOTOX_DATACUBE_MAX_BYTES:-}
max_bytes=${max_bytes_env:-$default_max_bytes}
headroom_bytes=${IOTOX_DATACUBE_HEADROOM_BYTES:-500000}
timestamp=${IOTOX_DATACUBE_TIMESTAMP:-$(TZ=America/New_York date +%Y.%m.%d.%H.%M.%S)}
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT

die() {
    printf 'repository datacube: %s\n' "$*" >&2
    exit 1
}

usage() {
    cat <<'EOF'
Usage:
  tools/make-repository-datacube.sh [--conversation|--public|--seed|--upload] [--no-founding-cubes|--include-founding-cubes] [OUTPUT_DIRECTORY]
  tools/make-repository-datacube.sh --verify ARCHIVE

Builds a clean-commit IoTox repository datacube. The default conversation
profile contains the tracked repository, a cloneable Git bundle, available
matching-commit standalone distribution and validation evidence, and as many
founding revision cubes as fit below the hard size limit. The public profile
omits nested founding cubes for a smaller GitHub/release handoff. The seed
profile is the recommended public repository seed: source snapshot, one-commit
cloneable bundle, no local history, no nested founding cubes. The upload profile
is the full-history provenance handoff: full reachable Git history by default,
no size ceiling unless IOTOX_DATACUBE_MAX_BYTES is set, and no nested founding
cubes unless explicitly requested. No profile pads the result.

Environment:
  IOTOX_DATACUBE_MAX_BYTES       strict upper bound; 0 disables (default: 128000000, upload: 0)
  IOTOX_DATACUBE_HEADROOM_BYTES  reserve while adding optional cubes (500000)
  IOTOX_DATACUBE_HISTORY_MODE    auto, full, or snapshot (default: auto)
  IOTOX_DATACUBE_PROFILE         conversation, public, seed, or upload (default: conversation)
  IOTOX_DATACUBE_INCLUDE_FOUNDING_CUBES  0 or 1 (default: profile-dependent)
  IOTOX_DATACUBE_TIMESTAMP       filename timestamp, YYYY.MM.DD.HH.MM.SS
EOF
}

require_tool() {
    command -v "$1" >/dev/null 2>&1 || die "required tool is missing: $1"
}

require_uint() {
    local name=$1
    local value=$2
    [[ "$value" =~ ^[0-9]+$ ]] || die "$name must be an unsigned integer: $value"
}

archive_paths_are_safe() {
    local archive=$1
    local entry
    while IFS= read -r entry; do
        case "$entry" in
            /* | ../* | */../* | */..)
                die "unsafe path in archive $archive: $entry"
            ;;
        esac
    done < <(unzip -Z1 "$archive")
    if zipinfo -l "$archive" | awk '$1 ~ /^l/ {found = 1} END {exit !found}'; then
        die "symlink entries are not accepted in archive: $archive"
    fi
}

stage_has_no_symlinks() {
    local stage=$1
    local link
    link=$(find "$stage" -type l -print -quit)
    [[ -z "$link" ]] || die "symlink entries are not accepted in a datacube: $link"
}

create_zip() {
    local stage=$1
    local cube_name=$2
    local destination=$3
    (
        cd "$stage"
        zip -q -X -9 -y -r "$destination" "$cube_name"
    )
}

verify_archive() {
    local archive=$1
    local size
    local effective_max_bytes=$max_bytes
    local top
    local extract_root="$work/verify-extract"
    local bare_root="$work/verify-bare.git"
    local limit_label

    [[ -f "$archive" ]] || die "archive does not exist: $archive"
    if [[ -z "$max_bytes_env" ]]; then
        case "$(basename "$archive")" in
            IoTox-upload-repository-datacube-*)
                effective_max_bytes=0
                ;;
        esac
    fi
    size=$(stat -c '%s' "$archive")
    if (( effective_max_bytes > 0 )); then
        (( size < effective_max_bytes )) ||
            die "archive is $size bytes; limit is strictly below $effective_max_bytes"
        limit_label=$effective_max_bytes
    else
        limit_label='unbounded'
    fi
    unzip -tq "$archive" >/dev/null || die "ZIP integrity failed: $archive"
    archive_paths_are_safe "$archive"

    mapfile -t top_entries < <(unzip -Z1 "$archive" | cut -d/ -f1 | LC_ALL=C sort -u)
    [[ ${#top_entries[@]} -eq 1 && -n "${top_entries[0]}" ]] ||
        die "archive must contain exactly one top-level directory"
    top=${top_entries[0]}

    mkdir -p "$extract_root"
    unzip -q "$archive" -d "$extract_root"
    [[ -f "$extract_root/$top/CHATGPT_START_HERE.md" ]] ||
        die "CHATGPT_START_HERE.md is missing"
    [[ -f "$extract_root/$top/SHA256SUMS" ]] || die "SHA256SUMS is missing"
    [[ -f "$extract_root/$top/git/IoTox.bundle" ]] || die "Git bundle is missing"
    [[ -f "$extract_root/$top/git/HISTORY_MODE" ]] || die "Git history mode is missing"
    [[ -f "$extract_root/$top/git/SOURCE_COMMIT" ]] || die "source commit marker is missing"
    [[ -f "$extract_root/$top/repository/CMakeLists.txt" ]] ||
        die "repository source is missing"
    case "$(tr -d '\n' < "$extract_root/$top/git/HISTORY_MODE")" in
        full|snapshot)
            ;;
        *)
            die "unknown Git history mode"
            ;;
    esac

    (
        cd "$extract_root/$top"
        sha256sum -c SHA256SUMS >/dev/null
    ) || die "payload checksum verification failed"

    git init --bare -q "$bare_root"
    git -C "$bare_root" bundle verify "$extract_root/$top/git/IoTox.bundle" >/dev/null 2>&1 ||
        die "Git bundle verification failed"

    printf 'verified=%s\n' "$archive"
    printf 'bytes=%s\n' "$size"
    printf 'limit=%s\n' "$limit_label"
    printf 'top=%s\n' "$top"
}

for tool in git zip unzip zipinfo sha256sum stat find sort awk sed grep cut install \
    tar gzip cp xargs wc basename mktemp date; do
    require_tool "$tool"
done
require_uint IOTOX_DATACUBE_MAX_BYTES "$max_bytes"
require_uint IOTOX_DATACUBE_HEADROOM_BYTES "$headroom_bytes"
if (( max_bytes > 0 )); then
    (( headroom_bytes < max_bytes )) || die "headroom must be smaller than the size limit"
fi
history_mode=${IOTOX_DATACUBE_HISTORY_MODE:-auto}
history_mode_explicit=0
[[ -n "${IOTOX_DATACUBE_HISTORY_MODE:-}" ]] && history_mode_explicit=1
case "$history_mode" in
    auto|full|snapshot)
        ;;
    *)
        die "IOTOX_DATACUBE_HISTORY_MODE must be auto, full, or snapshot: $history_mode"
        ;;
esac
datacube_profile=${IOTOX_DATACUBE_PROFILE:-conversation}
include_founding_cubes=${IOTOX_DATACUBE_INCLUDE_FOUNDING_CUBES:-}

if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    usage
    exit 0
fi

if [[ ${1:-} == --verify ]]; then
    [[ $# -eq 2 ]] || die "--verify requires exactly one archive path"
    verify_archive "$2"
    exit 0
fi

output_args=()
while (($# > 0)); do
    case "$1" in
        --conversation)
            datacube_profile='conversation'
            ;;
        --public)
            datacube_profile='public'
            [[ -n "$include_founding_cubes" ]] || include_founding_cubes=0
            ;;
        --seed)
            datacube_profile='seed'
            [[ -n "$include_founding_cubes" ]] || include_founding_cubes=0
            ;;
        --upload)
            datacube_profile='upload'
            [[ -n "$include_founding_cubes" ]] || include_founding_cubes=0
            ;;
        --no-founding-cubes)
            include_founding_cubes=0
            ;;
        --include-founding-cubes)
            include_founding_cubes=1
            ;;
        --*)
            die "unknown datacube option: $1"
            ;;
        *)
            output_args+=("$1")
            ;;
    esac
    shift
done

case "$datacube_profile" in
    conversation|public|seed|upload)
        ;;
    *)
        die "IOTOX_DATACUBE_PROFILE must be conversation, public, seed, or upload: $datacube_profile"
        ;;
esac
if [[ "$datacube_profile" == seed && "$history_mode_explicit" == 0 ]]; then
    history_mode=snapshot
fi
if [[ "$datacube_profile" == upload ]]; then
    [[ -n "$max_bytes_env" ]] || max_bytes=0
    if [[ "$history_mode_explicit" == 0 ]]; then
        history_mode=full
    fi
fi
require_uint IOTOX_DATACUBE_MAX_BYTES "$max_bytes"
if (( max_bytes > 0 )); then
    (( headroom_bytes < max_bytes )) || die "headroom must be smaller than the size limit"
fi
if [[ -z "$include_founding_cubes" ]]; then
    if [[ "$datacube_profile" == public || "$datacube_profile" == seed || "$datacube_profile" == upload ]]; then
        include_founding_cubes=0
    else
        include_founding_cubes=1
    fi
fi
require_uint IOTOX_DATACUBE_INCLUDE_FOUNDING_CUBES "$include_founding_cubes"
case "$include_founding_cubes" in
    0|1)
        ;;
    *)
        die "IOTOX_DATACUBE_INCLUDE_FOUNDING_CUBES must be 0 or 1: $include_founding_cubes"
        ;;
esac

[[ ${#output_args[@]} -le 1 ]] || die "expected at most one output directory"
[[ "$timestamp" =~ ^[0-9]{4}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}$ ]] ||
    die "invalid timestamp: $timestamp"

git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1 ||
    die "IoTox root is not a Git worktree: $root"
status=$(git -C "$root" status --porcelain=v1 --untracked-files=all)
[[ -z "$status" ]] || {
    printf '%s\n' "$status" >&2
    die "refusing to package a dirty or untracked worktree"
}

sensitive_path_pattern='(^|/)(\.env($|\.)|id_(rsa|ed25519)($|\.)|[^/]*\.(toxsave|identity|ledger|store)$|authority\.plist$|control\.sock$|private[_-]?key($|\.))'
if git -C "$root" rev-list --objects --all |
    sed -n 's/^[0-9a-f][0-9a-f]* //p' |
    grep -Eiq "$sensitive_path_pattern"; then
    git -C "$root" rev-list --objects --all |
        sed -n 's/^[0-9a-f][0-9a-f]* //p' |
        grep -Ei "$sensitive_path_pattern" >&2 || true
    die "sensitive-looking path exists in Git history"
fi
scan_refs_for_private_key_material() {
    local label=$1
    shift
    local key_scan="$work/private-key-paths.$label.txt"
    local key_scan_status=0
    git -C "$root" grep -I -l -E \
        -e '-----BEGIN (OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----' \
        "$@" -- . > "$key_scan" 2>&1 || key_scan_status=$?
    case "$key_scan_status" in
        0)
            cat "$key_scan" >&2
            die "private-key material appears in $label"
            ;;
        1)
            ;;
        *)
            cat "$key_scan" >&2
            die "private-key scan failed for $label"
            ;;
    esac
}

scan_refs_for_private_key_material 'tracked source' HEAD

scan_full_history_for_private_key_material() {
    local object_map="$work/full-history-objects.txt"
    local object_ids="$work/full-history-object-ids.txt"
    local object_types="$work/full-history-object-types.txt"
    local hits="$work/private-key-history-hits.txt"
    local object_id
    local object_type

    : > "$hits"
    git -C "$root" rev-list --objects --all > "$object_map"
    awk '{print $1}' "$object_map" | LC_ALL=C sort -u > "$object_ids"
    git -C "$root" cat-file --batch-check='%(objectname) %(objecttype)' \
        < "$object_ids" > "$object_types"

    while read -r object_id object_type; do
        [[ "$object_type" == blob ]] || continue
        set +e +o pipefail
        git -C "$root" cat-file blob "$object_id" |
            LC_ALL=C grep -a -q -E \
                -e '-----BEGIN (OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----'
        local grep_status=${PIPESTATUS[1]}
        set -e -o pipefail
        if [[ "$grep_status" == 0 ]]; then
            grep -E "^$object_id( |$)" "$object_map" >> "$hits" || true
        fi
    done < "$object_types"

    if [[ -s "$hits" ]]; then
        cat "$hits" >&2
        die "private-key material appears in full reachable Git history"
    fi
}

commit=$(git -C "$root" rev-parse HEAD)
short_commit=$(git -C "$root" rev-parse --short=12 HEAD)
branch=$(git -C "$root" symbolic-ref --short -q HEAD || printf 'detached')
commit_time=$(git -C "$root" show -s --format=%cI HEAD)
output_arg=${output_args[0]:-"$root/DR0Pbox"}
mkdir -p "$output_arg"
output_dir=$(cd "$output_arg" && pwd)
cube_prefix='IoTox-repository-datacube'
if [[ "$datacube_profile" == public ]]; then
    cube_prefix='IoTox-public-repository-datacube'
elif [[ "$datacube_profile" == seed ]]; then
    cube_prefix='IoTox-seed-repository-datacube'
elif [[ "$datacube_profile" == upload ]]; then
    cube_prefix='IoTox-upload-repository-datacube'
fi
cube_name="${cube_prefix}-${timestamp}-${short_commit}"
filename="$cube_name.zip"
archive="$output_dir/$filename"
checksum="$archive.sha256"
[[ ! -e "$archive" && ! -e "$checksum" ]] || die "output already exists: $archive"

stage="$work/stage"
cube="$stage/$cube_name"
mkdir -p "$cube/repository" "$cube/git" "$cube/validation" "$cube/distribution"

git -C "$root" archive --format=tar HEAD | tar -xf - -C "$cube/repository"
full_bundle_probe="$work/full-history.bundle"
source_probe="$work/repository-head.tar.gz"
git -C "$root" bundle create "$full_bundle_probe" --all
git -C "$root" archive --format=tar HEAD | gzip -9 > "$source_probe"
full_bundle_bytes=$(stat -c '%s' "$full_bundle_probe")
source_probe_bytes=$(stat -c '%s' "$source_probe")
bundle_mode='full'
if [[ "$history_mode" == snapshot ]] ||
    { [[ "$history_mode" == auto ]] &&
      (( max_bytes > 0 )) &&
      (( full_bundle_bytes + source_probe_bytes + headroom_bytes >= max_bytes )); }; then
    bundle_mode='snapshot'
fi

if [[ "$bundle_mode" == full ]]; then
    scan_full_history_for_private_key_material
    install -m 0644 "$full_bundle_probe" "$cube/git/IoTox.bundle"
else
    snapshot_repo="$work/source-snapshot-repo"
    mkdir -p "$snapshot_repo"
    git -C "$root" archive --format=tar HEAD | tar -xf - -C "$snapshot_repo"
    git -C "$snapshot_repo" init -q
    git -C "$snapshot_repo" add -A
    GIT_AUTHOR_NAME='IoTox datacube' \
        GIT_AUTHOR_EMAIL='iotox-datacube@example.invalid' \
        GIT_AUTHOR_DATE="$commit_time" \
        GIT_COMMITTER_NAME='IoTox datacube' \
        GIT_COMMITTER_EMAIL='iotox-datacube@example.invalid' \
        GIT_COMMITTER_DATE="$commit_time" \
    git -C "$snapshot_repo" commit -q \
        -m "IoTox datacube source snapshot $short_commit"
    git -C "$snapshot_repo" branch -M main
    git -C "$snapshot_repo" bundle create "$cube/git/IoTox.bundle" HEAD refs/heads/main
fi
printf '%s\n' "$bundle_mode" > "$cube/git/HISTORY_MODE"
printf '%s\n' "$commit" > "$cube/git/SOURCE_COMMIT"

distribution_status='not present on this host'
if [[ -d "$root/dist/standalone" ]]; then
    distribution_commit=''
    if [[ -f "$root/dist/standalone/build-info.txt" ]]; then
        distribution_commit=$(
            sed -n 's/^source-commit=//p' "$root/dist/standalone/build-info.txt" |
                sed -n '1p'
        )
    fi
    if [[ "$distribution_commit" == "$commit" ]]; then
        mkdir -p "$cube/distribution/standalone"
        cp -a "$root/dist/standalone/." "$cube/distribution/standalone/"
        distribution_status='included: standalone binary, licenses, verification, and source inputs'
    elif [[ -n "$distribution_commit" ]]; then
        distribution_status="present but skipped: standalone source-commit $distribution_commit does not match datacube commit $commit"
    else
        distribution_status='present but skipped: standalone build-info.txt did not record source-commit'
    fi
fi

validation_count=0
shopt -s nullglob
validation_sources=(
    "$root"/build/final-matrix-*.log
    "$root"/build/final-matrix-*.exit
    "$root"/build/*-final-matrix.log
    "$root"/build/*-final-matrix.exit
    "$root"/build/fuzzer-smoke*.log
    "$root"/build/fuzzer-smoke*.exit
    "$root"/build/*-fuzzer-smoke.log
    "$root"/build/*-fuzzer-smoke.exit
    "$root"/build/agent-stress*.log
    "$root"/build/agent-stress*.exit
)
for source in "${validation_sources[@]}"; do
    install -m 0644 "$source" "$cube/validation/$(basename "$source")"
    ((validation_count += 1))
done
if [[ -f "$root/build/coverage-report/coverage.xml" ]]; then
    install -m 0644 "$root/build/coverage-report/coverage.xml" "$cube/validation/coverage.xml"
    ((validation_count += 1))
fi
shopt -u nullglob

included_founders=()
skipped_founders=()
mkdir -p "$cube/provenance/founding-cubes"
if [[ "$include_founding_cubes" == 1 ]]; then
    mapfile -d '' -t founding_candidates < <(
        find "$root/DR0Pbox" -maxdepth 1 -type f \
            \( -name 'IoTox-rev*.zip' -o -name 'IoToxsync-rev*.zip' \) \
            -print0 2>/dev/null | LC_ALL=C sort -z
    )
else
    mapfile -d '' -t founding_candidates < <(
        find "$root/DR0Pbox" -maxdepth 1 -type f \
            \( -name 'IoTox-rev*.zip' -o -name 'IoToxsync-rev*.zip' \) \
            -print0 2>/dev/null | LC_ALL=C sort -z
    )
    for candidate in "${founding_candidates[@]}"; do
        skipped_founders+=("$(basename "$candidate") (omitted by $datacube_profile profile)")
    done
    founding_candidates=()
fi

probe_index=0
for candidate in "${founding_candidates[@]}"; do
    unzip -tq "$candidate" >/dev/null || die "founding cube failed ZIP integrity: $candidate"
    archive_paths_are_safe "$candidate"
    candidate_name=$(basename "$candidate")
    target="$cube/provenance/founding-cubes/$candidate_name"
    install -m 0644 "$candidate" "$target"
    probe="$work/probe-$probe_index.zip"
    create_zip "$stage" "$cube_name" "$probe"
    probe_size=$(stat -c '%s' "$probe")
    if (( max_bytes == 0 || probe_size + headroom_bytes < max_bytes )); then
        included_founders+=("$candidate_name")
    else
        rm -f -- "$target"
        skipped_founders+=("$candidate_name (would exceed reserved budget)")
    fi
    ((probe_index += 1))
done

write_metadata() {
    local metadata_archive_limit=$1
    local metadata_archive_limit_label
    local tracked_count
    local tracked_bytes
    local payload_count
    local payload_bytes

    tracked_count=$(git -C "$root" ls-files -z | awk -v RS='\0' 'END {print NR}')
    tracked_bytes=$(git -C "$root" ls-files -z |
        xargs -0 stat -c '%s' | awk '{sum += $1} END {print sum + 0}')
    payload_count=$(find "$cube" -type f \
        ! -name FILE_INDEX.tsv ! -name SHA256SUMS | wc -l)
    payload_bytes=$(find "$cube" -type f \
        ! -name FILE_INDEX.tsv ! -name SHA256SUMS -printf '%s\n' |
        awk '{sum += $1} END {print sum + 0}')
    if (( metadata_archive_limit == 0 )); then
        metadata_archive_limit_label='unbounded by this profile'
    else
        metadata_archive_limit_label="fewer than $metadata_archive_limit bytes"
    fi

    cat > "$cube/CHATGPT_START_HERE.md" <<EOF
# Start here: IoTox repository datacube

This is a shareable source, review, and recovery snapshot of the official IoTox repository. It was
built from a clean Git worktree at commit \`$commit\` on branch \`$branch\`. The owning IoTox
instance and its repository remain authoritative; this cube lets another person, GitHub upload,
ChatGPT session, or future office holder inspect, question, review, and discuss that exact state
without becoming an authority over the project.

## Read in this order

1. \`repository/README.md\` — product surface and present claims.
2. \`repository/docs/roadmap.md\` — completed gates and next milestones.
3. \`repository/docs/ratox-service-implementation-plan.md\` — active Ratox dependency order and gates.
4. \`repository/docs/security-ratox-v1.md\` — focused terminal-service threats and controls.
5. \`repository/docs/architecture.md\` — component and trust boundaries.
6. \`repository/docs/threat-model-draft.md\` — repository-wide adversaries and non-claims.
7. \`repository/docs/evidence/\` — retained genuine-network and ownership evidence.
8. \`repository/BOOTSTRAPROSE.md\` — deep governing design provenance.
9. \`MANIFEST.md\`, \`FILE_INDEX.tsv\`, and \`SHA256SUMS\` — cube contents and integrity.

The plain source snapshot is under \`repository/\`. \`git/IoTox.bundle\` is
cloneable; \`git/HISTORY_MODE\` records whether it carries full reachable local
history or a single exact source-snapshot commit. The seed profile deliberately
uses snapshot mode; other ceiling-bound profiles may also fall back to snapshot
mode when full history is too large. Host-generated evidence and the checksummed source-linked
distribution are separate from source so their evidentiary status stays visible.
Original owner-supplied cubes, when the byte budget allowed them, are nested
under \`provenance/founding-cubes/\` unchanged.

## Snapshot identity

- commit: \`$commit\`
- commit time: \`$commit_time\`
- branch: \`$branch\`
- datacube profile: \`$datacube_profile\`
- worktree at packaging: clean
- archive limit: $metadata_archive_limit_label

## Public posting boundary

This cube is a source/review artifact, not a stable binary release. The committed
\`repository/artifacts/\` tree is historical repository content and may contain
old build products; only \`distribution/standalone/\`, when present and marked
as same-commit in \`MANIFEST.md\`, represents the host's packaged standalone
distribution for this exact source commit. Upload the sibling \`.sha256\` with
the ZIP when publishing the artifact.

## Roadmap headings at packaging

\`\`\`text
$(awk '/^## M[0-9]+/{sub(/^## /, ""); print}' "$root/docs/roadmap.md")
\`\`\`

## Recent commits

\`\`\`text
$(git -C "$root" log -12 --date=short --pretty=format:'%h %ad %s')
\`\`\`

## Good opening prompt

> Treat this datacube as an exact IoTox repository snapshot at the recorded commit. First map what
> is implemented, what is directly evidenced, what remains planned, and the trust boundaries. Cite
> repository paths and commit IDs. Do not strengthen network, security, portability, or release
> claims beyond the included evidence. Then help me reason about the next milestone.

If an interface cannot inspect ZIP contents directly, extract the cube and upload this file together
with the relevant files under \`repository/\`. Nested founding cubes are provenance and do not need
to be opened for ordinary current-state discussion.
EOF

    cat > "$cube/MANIFEST.md" <<EOF
# IoTox repository datacube manifest

| Field | Value |
|---|---|
| Commit | \`$commit\` |
| Branch | \`$branch\` |
| Commit time | \`$commit_time\` |
| Datacube profile | \`$datacube_profile\` |
| Tracked source files | $tracked_count |
| Tracked source bytes | $tracked_bytes |
| Pre-metadata payload files | $payload_count |
| Pre-metadata payload bytes | $payload_bytes |
| Validation files copied | $validation_count |
| Standalone distribution | $distribution_status |
| Git bundle mode | $bundle_mode |
| Full-history bundle bytes | $full_bundle_bytes |
| Compressed source probe bytes | $source_probe_bytes |
| ZIP ceiling | $metadata_archive_limit_label |

## Content classes

- \`repository/\`: every tracked file at the exact commit, exported with \`git archive\`.
  This includes tracked historical \`artifacts/\` when they are part of the
  repository; those files are provenance, not the current same-commit
  standalone distribution.
- \`git/IoTox.bundle\`: a cloneable Git bundle. If \`git/HISTORY_MODE\` is
  \`full\`, it contains all local refs and reachable history. If the mode is
  \`snapshot\`, it contains one exact source-snapshot commit. Snapshot mode is
  deliberate for seed handoffs and may also be selected by strict archive
  ceilings. Clone with \`git clone IoTox.bundle IoTox\`.
- \`distribution/standalone/\`: copied only when the host artifact records this exact source commit;
  status: $distribution_status. Binary portability is not implied.
- \`validation/\`: selected raw matrix, fuzzer, stress, and machine-readable coverage evidence
  available on the packaging host. Canonical claims and commit associations live in
  \`repository/docs/evidence/\` and \`repository/docs/testing.md\`.
- \`provenance/founding-cubes/\`: unchanged owner-supplied source cubes admitted only when the
  selected profile includes them and they fit below the byte ceiling with reserved metadata headroom.

## Included founding cubes
EOF
    if [[ ${#included_founders[@]} -eq 0 ]]; then
        printf '\n- None included.\n' >> "$cube/MANIFEST.md"
    else
        for item in "${included_founders[@]}"; do
            printf '\n- `%s`\n' "$item" >> "$cube/MANIFEST.md"
        done
    fi
    cat >> "$cube/MANIFEST.md" <<'EOF'

## Skipped founding cubes
EOF
    if [[ ${#skipped_founders[@]} -eq 0 ]]; then
        printf '\n- None.\n' >> "$cube/MANIFEST.md"
    else
        for item in "${skipped_founders[@]}"; do
            printf '\n- `%s`\n' "$item" >> "$cube/MANIFEST.md"
        done
    fi
    cat >> "$cube/MANIFEST.md" <<'EOF'

## Exclusions and safety boundary

The source is committed content only. Build trees, dependency build trees, `.sandworm`, `.sandwurm`,
mutable runtime directories, sockets, FIFOs, savedata, identities, ledgers, command stores, received
files, and arbitrary untracked files are not copied. The builder refuses a dirty worktree,
sensitive-looking paths in reachable Git history, private-key PEM markers in the packaged source
snapshot and in full reachable history when a full-history bundle is selected, unsafe archive paths,
and archive symlinks. Included historical cubes are separately integrity-checked but retain their own
historical package contracts.

`SHA256SUMS` covers every payload and metadata file except itself. The outer ZIP has a sibling
`.sha256` file.
EOF

    {
        printf 'bytes\tpath\n'
        (
            cd "$cube"
            find . -type f ! -name FILE_INDEX.tsv ! -name SHA256SUMS \
                -printf '%s\t%P\n' | LC_ALL=C sort -t $'\t' -k2,2
        )
    } > "$cube/FILE_INDEX.tsv"

    (
        cd "$cube"
        find . -type f ! -name SHA256SUMS -print0 |
            LC_ALL=C sort -z |
            xargs -0 sha256sum > SHA256SUMS
    )
}

stage_has_no_symlinks "$cube"
attempt=0
final_candidate=''
while :; do
    rm -f -- "$cube/CHATGPT_START_HERE.md" "$cube/MANIFEST.md" \
        "$cube/FILE_INDEX.tsv" "$cube/SHA256SUMS"
    write_metadata "$max_bytes"
    final_candidate="$work/final-$attempt.zip"
    create_zip "$stage" "$cube_name" "$final_candidate"
    final_size=$(stat -c '%s' "$final_candidate")
    if (( max_bytes == 0 || final_size < max_bytes )); then
        break
    fi
    (( ${#included_founders[@]} > 0 )) ||
        die "mandatory datacube content is $final_size bytes and exceeds the limit"
    last_index=$((${#included_founders[@]} - 1))
    removed=${included_founders[$last_index]}
    rm -f -- "$cube/provenance/founding-cubes/$removed"
    unset 'included_founders[last_index]'
    skipped_founders+=("$removed (removed after exact final compression)")
    ((attempt += 1))
done

verify_archive "$final_candidate" >/dev/null
install -m 0644 "$final_candidate" "$archive"
(
    cd "$output_dir"
    sha256sum "$filename" > "$filename.sha256"
)

printf 'archive=%s\n' "$archive"
printf 'sha256=%s\n' "$checksum"
printf 'bytes=%s\n' "$final_size"
if (( max_bytes > 0 )); then
    printf 'limit=%s\n' "$max_bytes"
    printf 'utilization_percent=%.2f\n' "$(awk -v size="$final_size" -v limit="$max_bytes" \
        'BEGIN {print (size * 100.0) / limit}')"
else
    printf 'limit=unbounded\n'
    printf 'utilization_percent=unbounded\n'
fi
printf 'commit=%s\n' "$commit"
printf 'git_bundle_mode=%s\n' "$bundle_mode"
printf 'full_history_bundle_bytes=%s\n' "$full_bundle_bytes"
printf 'compressed_source_probe_bytes=%s\n' "$source_probe_bytes"
printf 'founding_cubes=%s\n' "${#included_founders[@]}"
printf 'validation_files=%s\n' "$validation_count"
