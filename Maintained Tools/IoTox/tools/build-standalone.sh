#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck source=/dev/null
source "$root/dependencies.lock"

deps_root=${IOTOX_DEPS_DIR:-"$root/.deps"}
prefix=${IOTOX_DEPS_PREFIX:-"$deps_root/prefix"}
build_root=${IOTOX_STANDALONE_BUILD_DIR:-"$root/build/standalone"}
dist=${IOTOX_DIST_DIR:-"$root/dist/standalone"}
jobs=${IOTOX_JOBS:-}
cmake_generator=${IOTOX_CMAKE_GENERATOR:-}
if [[ -z "$jobs" ]]; then
    if command -v nproc >/dev/null 2>&1; then
        jobs=$(nproc)
    else
        jobs=2
    fi
fi
if [[ -z "${CC:-}" ]] &&
   ! command -v cc >/dev/null 2>&1 &&
   ! command -v gcc >/dev/null 2>&1 &&
   ! command -v clang >/dev/null 2>&1; then
    printf '%s\n' 'standalone build requires a C compiler; set CC or run inside the project dev shell' >&2
    exit 2
fi
if [[ -z "${CXX:-}" ]] &&
   ! command -v c++ >/dev/null 2>&1 &&
   ! command -v g++ >/dev/null 2>&1 &&
   ! command -v clang++ >/dev/null 2>&1; then
    printf '%s\n' 'standalone build requires a C++ compiler; set CXX or run inside the project dev shell' >&2
    exit 2
fi
if [[ -z "$cmake_generator" ]]; then
    if command -v ninja >/dev/null 2>&1 || command -v ninja-build >/dev/null 2>&1; then
        cmake_generator=Ninja
    else
        cmake_generator='Unix Makefiles'
    fi
fi
if [[ -f "$build_root/CMakeCache.txt" ]] &&
   ! grep -Fqx "CMAKE_GENERATOR:INTERNAL=$cmake_generator" "$build_root/CMakeCache.txt"; then
    if [[ -n "${IOTOX_STANDALONE_BUILD_DIR:-}" ]]; then
        printf 'standalone build directory uses a different CMake generator: %s\n' "$build_root" >&2
        printf 'set IOTOX_STANDALONE_BUILD_DIR to a fresh directory or choose IOTOX_CMAKE_GENERATOR=%q\n' "$cmake_generator" >&2
        exit 2
    fi
    generator_slug=$(
        printf '%s' "$cmake_generator" |
            tr '[:upper:] ' '[:lower:]-' |
            tr -cd 'a-z0-9._-'
    )
    build_root="$root/build/standalone-$generator_slug"
fi

"$root/tools/fetch-pinned-dependencies.sh"

sodium_source="$deps_root/src/libsodium-${IOTOX_LIBSODIUM_VERSION}"
toxcore_source="$deps_root/src/c-toxcore-${IOTOX_C_TOXCORE_VERSION}"
argon2_source="$deps_root/src/phc-winner-argon2-${IOTOX_ARGON2_VERSION}"
path_scrub_version=path-scrub-v1
sodium_stamp="$prefix/.iotox-libsodium-${IOTOX_LIBSODIUM_VERSION}-${path_scrub_version}"
argon2_stamp="$prefix/.iotox-argon2-${IOTOX_ARGON2_VERSION}-namespaced-blake2-${path_scrub_version}"

path_sanitize_flags=(
    "-ffile-prefix-map=$root=source-snapshot"
    "-fdebug-prefix-map=$root=source-snapshot"
    "-ffile-prefix-map=$deps_root=dependency-cache"
    "-fdebug-prefix-map=$deps_root=dependency-cache"
    "-ffile-prefix-map=$prefix=dependency-prefix"
    "-fdebug-prefix-map=$prefix=dependency-prefix"
    "-ffile-prefix-map=$build_root=standalone-build"
    "-fdebug-prefix-map=$build_root=standalone-build"
)
standalone_c_flags=${IOTOX_STANDALONE_C_FLAGS:-}
standalone_cxx_flags=${IOTOX_STANDALONE_CXX_FLAGS:-}
for flag in "${path_sanitize_flags[@]}"; do
    standalone_c_flags="${standalone_c_flags:+$standalone_c_flags }$flag"
    standalone_cxx_flags="${standalone_cxx_flags:+$standalone_cxx_flags }$flag"
done

if [[ ${IOTOX_CLEAN_STANDALONE:-0} == 1 ]]; then
    rm -rf "$prefix" "$build_root" "$dist"
fi
mkdir -p "$prefix" "$dist"

if [[ ! -f "$sodium_stamp" ]]; then
    sodium_build="$deps_root/build/libsodium-${IOTOX_LIBSODIUM_VERSION}"
    rm -rf "$sodium_build"
    mkdir -p "$sodium_build"
    (
        cd "$sodium_build"
        CFLAGS="${CFLAGS:-}${CFLAGS:+ }$standalone_c_flags" \
        "$sodium_source/configure" \
            --prefix="$prefix" \
            --disable-shared \
            --enable-static \
            --with-pic
        make -j"$jobs"
        make install
    )
    : >"$sodium_stamp"
fi

if [[ ! -f "$argon2_stamp" ]]; then
    # The Argon2 reference archive and libsodium both export generic blake2b
    # names. A fully static final link therefore needs the reference library's
    # private BLAKE2 implementation namespaced at compile time.
    argon2_cflags=(
        -std=c89 -O3 -Wall -Iinclude -Isrc -pthread -march=native
        -Dblake2b=argon2_internal_blake2b
        -Dblake2b_init=argon2_internal_blake2b_init
        -Dblake2b_init_key=argon2_internal_blake2b_init_key
        -Dblake2b_init_param=argon2_internal_blake2b_init_param
        -Dblake2b_update=argon2_internal_blake2b_update
        -Dblake2b_final=argon2_internal_blake2b_final
        -Dblake2b_long=argon2_internal_blake2b_long
    )
    for flag in "${path_sanitize_flags[@]}"; do
        argon2_cflags+=("$flag")
    done
    printf -v argon2_cflags_text '%q ' "${argon2_cflags[@]}"
    make -C "$argon2_source" clean >/dev/null 2>&1 || true
    make -C "$argon2_source" -j"$jobs" \
        ARGON2_VERSION="$IOTOX_ARGON2_VERSION" \
        LIBRARY_REL=lib \
        CFLAGS="$argon2_cflags_text" \
        libargon2.a
    install -d "$prefix/include" "$prefix/lib"
    install -m 0644 "$argon2_source/include/argon2.h" "$prefix/include/argon2.h"
    install -m 0644 "$argon2_source/libargon2.a" "$prefix/lib/libargon2.a"
    : >"$argon2_stamp"
fi

argon2_library="$prefix/lib/libargon2.a"
if [[ ! -f "$argon2_library" ]]; then
    printf 'pinned Argon2 build did not produce %s\n' "$argon2_library" >&2
    exit 3
fi

pkg_paths=("$prefix/lib/pkgconfig" "$prefix/lib64/pkgconfig")
pkg_config_path=$(IFS=:; printf '%s' "${pkg_paths[*]}")
if [[ -n ${PKG_CONFIG_PATH:-} ]]; then
    pkg_config_path="$pkg_config_path:$PKG_CONFIG_PATH"
fi

extra_link_flags=${IOTOX_STANDALONE_LINK_FLAGS:-}
if [[ ${IOTOX_STATIC_CXX_RUNTIME:-0} == 1 ]]; then
    extra_link_flags="${extra_link_flags:+$extra_link_flags }-static-libgcc -static-libstdc++"
fi

PKG_CONFIG_PATH="$pkg_config_path" \
CMAKE_PREFIX_PATH="$prefix${CMAKE_PREFIX_PATH:+;$CMAKE_PREFIX_PATH}" \
cmake -S "$root" -B "$build_root" -G "$cmake_generator" \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_TESTING=OFF \
    -DIOTOX_WARNINGS_AS_ERRORS=ON \
    -DIOTOX_TOXCORE_SOURCE_DIR="$toxcore_source" \
    -DIOTOX_ARGON2_LIBRARY="$argon2_library" \
    -DIOTOX_PROVENANCE_SOURCE_TREE="source-snapshot" \
    -DIOTOX_PROVENANCE_BUILD_TREE="standalone-build" \
    -DCMAKE_C_FLAGS="$standalone_c_flags" \
    -DCMAKE_CXX_FLAGS="$standalone_cxx_flags" \
    -DCMAKE_SKIP_RPATH=ON \
    -DCMAKE_SKIP_BUILD_RPATH=ON \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DCMAKE_EXE_LINKER_FLAGS="$extra_link_flags"

PKG_CONFIG_PATH="$pkg_config_path" \
cmake --build "$build_root" --target iotox --parallel "$jobs"

install -m 0755 "$build_root/iotox" "$dist/iotox"
if command -v patchelf >/dev/null 2>&1; then
    # Nix compiler wrappers may inject a RUNPATH containing the build output
    # placeholder. Keep only resolved Nix-store runtime directories so the
    # public binary does not retain founder-workspace paths.
    sanitized_runpath=$(
        ldd "$dist/iotox" 2>/dev/null |
            awk '
                $2 == "=>" && $3 ~ /^\/nix\/store\// {
                    path=$3
                    sub(/\/[^\/]+$/, "", path)
                    print path
                }
                $1 ~ /^\/nix\/store\// {
                    path=$1
                    sub(/\/[^\/]+$/, "", path)
                    print path
                }
            ' |
            sort -u |
            paste -sd ':' -
    )
    if [[ -n "$sanitized_runpath" ]]; then
        patchelf --set-rpath "$sanitized_runpath" "$dist/iotox"
    else
        patchelf --remove-rpath "$dist/iotox" || true
    fi
fi
if command -v strip >/dev/null 2>&1; then
    strip --strip-all "$dist/iotox" || true
fi

license_dir="$dist/licenses"
mkdir -p "$license_dir"
install -m 0644 "$root/LICENSE.md" "$license_dir/IoTox-MIT.md"
install -m 0644 "$root/THIRD_PARTY.md" "$dist/THIRD_PARTY.md"
install -m 0644 "$toxcore_source/LICENSE" "$license_dir/c-toxcore-GPL-3.0-or-later.txt"
install -m 0644 "$toxcore_source/third_party/cmp/LICENSE" "$license_dir/cmp-MIT.txt"
install -m 0644 "$sodium_source/LICENSE" "$license_dir/libsodium-ISC.txt"
install -m 0644 "$argon2_source/LICENSE" "$license_dir/argon2-Apache-2.0-or-CC0-1.0.txt"
install -m 0644 "$root/third_party/README.md" "$license_dir/EFF-wordlist-provenance.md"

source_commit=${IOTOX_SOURCE_COMMIT:-}
source_date_epoch=${SOURCE_DATE_EPOCH:-}
if [[ -z "$source_commit" ]] &&
   git -C "$root" diff-index --quiet HEAD --; then
    source_commit=$(git -C "$root" rev-parse HEAD)
    if [[ -z "$source_date_epoch" ]]; then
        source_date_epoch=$(git -C "$root" log -1 --format=%ct)
    fi
fi
if [[ -z "$source_date_epoch" ]]; then
    source_date_epoch=1
fi
sbom_arguments=(
    generate
    --root "$root"
    --binary "$dist/iotox"
    --output "$dist/iotox.spdx.json"
    --source-date-epoch "$source_date_epoch"
)
if [[ -n "$source_commit" ]]; then
    sbom_arguments+=(--source-commit "$source_commit")
fi
python3 "$root/tools/generate-sbom.py" "${sbom_arguments[@]}"

{
    printf 'project=IoTox\n'
    printf 'revision=%s\n' "$(tr -d '\n' < "$root/REVISION")"
    printf 'product-binary=iotox\n'
    printf 'c-toxcore=%s\n' "$IOTOX_C_TOXCORE_VERSION"
    printf 'c-toxcore-sha256=%s\n' "$IOTOX_C_TOXCORE_SHA256"
    printf 'c-toxcore-cmp-commit=%s\n' "$IOTOX_CMP_COMMIT"
    printf 'c-toxcore-cmp-sha256=%s\n' "$IOTOX_CMP_SHA256"
    printf 'libsodium=%s\n' "$IOTOX_LIBSODIUM_VERSION"
    printf 'libsodium-sha256=%s\n' "$IOTOX_LIBSODIUM_SHA256"
    printf 'argon2=%s\n' "$IOTOX_ARGON2_VERSION"
    printf 'argon2-sha256=%s\n' "$IOTOX_ARGON2_SHA256"
    printf 'eff-wordlist=%s\n' "$IOTOX_EFF_WORDLIST_VERSION"
    printf 'eff-wordlist-sha256=%s\n' "$IOTOX_EFF_WORDLIST_SHA256"
    printf 'source-commit=%s\n' "${source_commit:-NOASSERTION}"
    printf 'source-date-epoch=%s\n' "$source_date_epoch"
    printf 'compiler-c=%s\n' "${CC:-$(command -v cc || true)}"
    printf 'compiler-cxx=%s\n' "${CXX:-$(command -v c++ || true)}"
    printf 'cmake-generator=%s\n' "$cmake_generator"
    printf 'static-cxx-runtime=%s\n' "${IOTOX_STATIC_CXX_RUNTIME:-0}"
    printf 'extra-link-flags=%s\n' "$extra_link_flags"
    printf 'built-at-utc=%s\n' "$(date -u -d "@$source_date_epoch" +%Y-%m-%dT%H:%M:%SZ)"
    (cd "$dist" && sha256sum iotox)
} >"$dist/build-info.txt"

"$root/tools/verify-standalone.sh" \
    "$dist/iotox" "$dist/iotox.spdx.json" | tee "$dist/verification.txt"

if [[ ${IOTOX_PACKAGE_SOURCES:-0} == 1 ]]; then
    "$root/tools/package-source-inputs.sh"
fi

printf 'standalone-binary=%s\n' "$dist/iotox"
