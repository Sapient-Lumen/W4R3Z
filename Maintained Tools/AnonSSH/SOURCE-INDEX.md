# AnonSSH 0.2.0: exact source index

This index accompanies the supplied **x86-64 Linux portable binary** from project revision `9831b007cd47ad9d8b1c82c417804fac9a780db2`. It names the selected source inputs and build modifications, rather than substituting project homepages or newer versions.

The **219,052,212-byte `anonssh-sources.tar.gz` is deliberately not published here**. The complete 721-file project source, including all 636 RouterInfo bootstrap files, is provided as the [1.28 MB project-source ZIP](https://github.com/Sapient-Lumen/W4R3Z/releases/download/anonssh-v0.2.0-9831b007cd47/anonssh-project-source-9831b007cd47-public.zip). The repository [source/](https://github.com/Sapient-Lumen/W4R3Z/tree/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/) directory is an 85-file code/docs/manifests browsing copy, not the complete build tree. External source downloads are linked below. [SOURCE-INDEX.json](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/SOURCE-INDEX.json) contains the machine-readable pins, patch hashes, all 196 Rust crate references and dated availability evidence.

**Scope:** This is a source-location and provenance index, not a legal-compliance certification, complete transitive toolchain inventory, or independently verified offline rebuild. The supplied `sources.json`, where retained as historical evidence, describes the omitted archive, not the contents of this publication. See the original [third-party notes](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/THIRD_PARTY.md) for the project’s distribution statements.

## Identify the binary and project source

- [Complete project-source ZIP](https://github.com/Sapient-Lumen/W4R3Z/releases/download/anonssh-v0.2.0-9831b007cd47/anonssh-project-source-9831b007cd47-public.zip): **1,282,767 bytes, 721 files**; SHA-256 `3900dbab90361c71b782a506daff4c77dc6ba904ac54da60ef5a150f96ec9790`. The locally prepared ZIP was compared against all 721 supplied project paths: only the README example-path anonymization differs. Publication delivery is verified separately by the publisher.

- Portable binary SHA-256: `451f1eee963c9d16c27883054df5d3a70659ca8213eaec31ce5136886d521fcd`.
- [Authoritative AnonSSH build expression](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/default.nix), SHA-256 `0a693dcc645bb040d0924c0f6a4d6968dc3150a8121c6c9d3a57f63598e4d82c`.
- [Cargo.lock](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/Cargo.lock), SHA-256 `cae12c3007bdb647653ea78e374c8aeb5d83b7e4c927aad95e53abab69161b42`.
- [AnonSSH Dropbear runtime-helper patch](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/nix/dropbear-runtime-helpers.patch), SHA-256 `f2834c0378c85073db06a595d03ad0ee2dfdb30e766d3c452bedcdb42a78f8b4`.
- [Makefile](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/Makefile), [project README](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/README.md) and [upstream publication instructions](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/PUBLISHING.md) retain the build workflow. The publication instructions describe the original full handoff; this index records the intentionally different source-link publication layout.

The implementation is unchanged. An illustrative personal path in the published README is anonymized. To inspect all AnonSSH modifications, read [default.nix](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/default.nix) and the complete project ZIP, not only an upstream release archive. To build, extract the ZIP and work inside `AnonSSH-0.2.0-9831b007cd47/`; the reduced Git browsing copy omits required bootstrap files.

## Pinned package set

Use Nixpkgs commit [`7dd199b0e2993e37b4775ed66b1c291699608c9f`](https://github.com/NixOS/nixpkgs/tree/7dd199b0e2993e37b4775ed66b1c291699608c9f), reported in the handoff as `26.11pre-git`. [Exact Nixpkgs archive](https://github.com/NixOS/nixpkgs/archive/7dd199b0e2993e37b4775ed66b1c291699608c9f.tar.gz).

`builtins.fetchTarball` pin: `08kxnni9l87i089hy7p9a7yr64w6h9x5m2cc7k2hn455hidm9mm3` (Nix-base32 SHA-256 of the unpacked recursive/NAR source tree, **not** the compressed archive’s byte hash).

The pinned [top-level package selection](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/top-level/all-packages.nix) chooses OpenSSL 3.5.8 and Boost 1.91.0. The [static package-set construction](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/top-level/stage.nix) chooses musl on Linux. The 24 relevant recipe/support files and 15 local Nixpkgs patches checked against this public revision were byte-identical to those supplied in the handoff.

### Reading the hashes

- **Raw SHA-256** hashes the actual downloaded archive bytes and can be checked using `sha256sum`. SRI `sha256-…` and hexadecimal are alternative encodings of SHA-256.
- **Nix tree SHA-256** hashes the fetcher-normalized, unpacked source tree using recursive/NAR serialization. Do not compare it directly to `sha256sum file.tar.gz`. Use the pinned `fetchzip`/`fetchFromGitHub` recipe.
- **Nix patch SHA-256** hashes `fetchpatch`’s normalized patch output, not necessarily the raw HTTP response. The JSON preserves normalization options and separately labels observed raw response hashes.

## Embedded programs, Tor libraries and certificate source

### Tor 0.4.9.14

Embedded Tor executable; six selected static libraries below.

- [Source download](https://dist.torproject.org/tor-0.4.9.14.tar.gz)
- [Official Tor archive](https://archive.torproject.org/tor-package-archive/tor-0.4.9.14.tar.gz) and [EFF Tor mirror](https://tor.eff.org/dist/tor-0.4.9.14.tar.gz), both exact-version locations found in their directory listings. See the availability qualification below.
- Raw SHA-256: `182449ac1c8ff43278da27b69b02040e11d03d0327db6d9126e4190ec6235e4a`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/to/tor/package.nix).

AnonSSH overrides the Nixpkgs Tor 0.4.9.13 source with 0.4.9.14, enables GPL code, disables systemd/seccomp/libcap, replaces buildInputs with six static libraries, sets -static -lgcc, clears postPatch, builds src/app/tor, disables checks. The Nixpkgs patches array is retained.

The AnonSSH override in [default.nix](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/default.nix) is authoritative: the base recipe’s Tor 0.4.9.13 is **not** the selected release. Tor’s six explicit static-library inputs are libevent, OpenSSL, zlib, XZ/liblzma, zstd and scrypt.

### libevent 2.1.13

Tor static library.

- [Source download](https://github.com/libevent/libevent/releases/download/release-2.1.13-stable/libevent-2.1.13-stable.tar.gz)
- Raw SHA-256: `f7e9383b8c0baa81b687e5b5eecc01beefaf1b19b64151d95ed61647fe7a315c`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/li/libevent/package.nix).

### OpenSSL 3.5.8

Tor, i2pd and OpenSSH cryptographic static build input.

- [Source download](https://github.com/openssl/openssl/releases/download/openssl-3.5.8/openssl-3.5.8.tar.gz)
- Raw SHA-256: `a8f84a39918ec6415ce765d9b429d313ba97b8143169c172e734b9514464f5b2`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/development/libraries/openssl/default.nix).

pkgs/top-level/all-packages.nix selects openssl_3_5; static-musl modifications and local patches are in the pinned recipe.

### zlib 1.3.2

Tor, i2pd, OpenSSH and Dropbear static build input.

- [Source download](https://github.com/madler/zlib/releases/download/v1.3.2/zlib-1.3.2.tar.gz)
- [Recipe mirror / alternative](https://www.zlib.net/fossils/zlib-1.3.2.tar.gz)
- Raw SHA-256: `bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/development/libraries/zlib/default.nix).

### XZ Utils / liblzma 5.8.4

Tor static library.

- [Source download](https://github.com/tukaani-project/xz/releases/download/v5.8.4/xz-5.8.4.tar.xz)
- Raw SHA-256: `4ce24038fd4221e0d13bc1a2de7a4db56e90b92b3bf75321f6c14be73f65de4b`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/xz/xz/package.nix).

### Zstandard 1.5.7

Tor static library.

- [Source download](https://github.com/facebook/zstd/archive/refs/tags/v1.5.7.tar.gz)
- Nix tree SHA-256: `sha256-tNFWIT9ydfozB8dWcmTMuZLCQmQudTFJIkSr0aG7S44=`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/tools/compression/zstd/default.nix).
- Exact source tag: `v1.5.7`, constrained by the Nix tree hash above. A tag is not presented as an immutable commit ID.

### scrypt 1.3.3

Tor static libscrypt-kdf input.

- [Source download](https://www.tarsnap.com/scrypt/scrypt-1.3.3.tgz)
- Raw SHA-256: `1c2710517e998eaac2e97db11f092e37139e69886b21a1b2661f64e130215ae9`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/sc/scrypt/package.nix).

### i2pd 2.61.0

Embedded i2pd executable.

- [Source download](https://github.com/PurpleI2P/i2pd/archive/refs/tags/2.61.0.tar.gz)
- Nix tree SHA-256: `sha256-dfCeY64TGRoTMNvKZk5jrhyRc8b8K03KM7YV5w/pbUM=`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/i2/i2pd/package.nix).
- Exact source tag: `2.61.0`, constrained by the Nix tree hash above. A tag is not presented as an immutable commit ID.

AnonSSH uses pkgsStatic.i2pd.override { upnpSupport = false; }; selected inputs are Boost, zlib and OpenSSL, not miniupnpc.

### OpenSSH Portable 10.5p1

Embedded ssh, sftp-server and scp executables.

- [Source download](https://ftp.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-10.5p1.tar.gz)
- [Recipe mirror / alternative](https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-10.5p1.tar.gz)
- Raw SHA-256: `d44d28a839ea9daf969cc69150fde59910b2b39361dad81a3bd6cbd19218db11`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/tools/networking/openssh/default.nix).

First URL resolves the pinned mirror://openbsd entry; second is an official OpenBSD CDN alternative. pkgs.openssh is the plain OpenSSH variant, not HPN or GSSAPI. Its shared recipe is pkgs/tools/networking/openssh/common.nix; static selection disables PAM/FIDO/security-key and keeps LDNS.

### Dropbear 2026.94

Embedded Dropbear server with AnonSSH runtime-helper patch.

- [Source download](https://github.com/mkj/dropbear/archive/refs/tags/DROPBEAR_2026.94.tar.gz)
- Nix tree SHA-256: `sha256-AJ6JvTPhd+Y4xnIIVqbJiU1rkmRmojoZX3pwKV0qrxA=`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/dr/dropbear/package.nix).
- Exact source tag: `DROPBEAR_2026.94`, constrained by the Nix tree hash above. A tag is not presented as an immutable commit ID.

Apply the pinned Nixpkgs pass-path.patch first, then source/nix/dropbear-runtime-helpers.patch via the override in source/default.nix. This is not an unmodified upstream Dropbear binary.

### Java I2P certificate source 2.13.0

Source of embedded reseed certificates; no Java router executable is embedded.

- [Source download](https://github.com/i2p/i2p.i2p/archive/i2p-2.13.0.tar.gz)
- [Recipe mirror / alternative](https://download.i2p2.de/releases/2.13.0/i2psource_2.13.0.tar.bz2)
- [Recipe mirror / alternative](https://files.i2p-projekt.de/2.13.0/i2psource_2.13.0.tar.bz2)
- [Recipe mirror / alternative](https://download.i2p2.no/releases/2.13.0/i2psource_2.13.0.tar.bz2)
- Nix tree SHA-256: `sha256-fCtjCKbvad8Uk+1ir1suJ0MqV8JjAcmOKXJicbUtKls=`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/i2/i2p/package.nix).
- Exact source tag: `i2p-2.13.0`, constrained by the Nix tree hash above. A tag is not presented as an immutable commit ID.

All URLs are the exact ordered alternatives in the pinned fetchzip recipe; hash is the unpacked normalized tree, not any compressed download. AnonSSH copies certificates/ from pkgs.buildPackages.i2p output. Static audit found 35 embedded certificate byte matches in supplied Java I2P source.

## Additional selected dependencies

### libxcrypt 4.5.2

The exact source archive, licensing files and selected recipe/local patch are also available in the [small source supplement](https://github.com/Sapient-Lumen/W4R3Z/releases/download/anonssh-v0.2.0-9831b007cd47/anonssh-source-supplement-20261020.zip).

Selected Dropbear static dependency; crypt/yescrypt symbols observed in the supplied Dropbear payload.

- [Source download](https://github.com/besser82/libxcrypt/releases/download/v4.5.2/libxcrypt-4.5.2.tar.xz)
- Raw SHA-256: `71513a31c01a428bccd5367a32fd95f115d6dac50fb5b60c779d5c7942aec071`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/development/libraries/libxcrypt/default.nix).

This source location extends the original bundle’s inventory. The pinned package set supplies its recipe.

### LDNS 1.9.2

Selected OpenSSH static dependency; LDNS symbols observed in the supplied ssh payload.

- [Source download](https://www.nlnetlabs.nl/downloads/ldns/ldns-1.9.2.tar.gz)
- Raw SHA-256: `b524fa21994b6e834200ceb8c27f1b84bda5982fe35706f058196c079db94d5d`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/ld/ldns/package.nix).

This source location extends the original bundle’s inventory. The pinned package set supplies its recipe.

### Boost 1.91.0

Selected i2pd static dependency; Boost symbols observed in the supplied i2pd payload.

- [Source download](https://archives.boost.io/release/1.91.0/source/boost_1_91_0.tar.bz2)
- Raw SHA-256: `de5e6b0e4913395c6bdfa90537febd9028ea4c0735d2cdb0cd9b45d5f51264f5`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/development/libraries/boost/1.91.nix).

pkgs/top-level/all-packages.nix selects boost = boost191. Build and selected patch logic is in pkgs/development/libraries/boost/generic.nix. This index does not claim every optional Boost sublibrary was linked.

This source location extends the original bundle’s inventory. The pinned package set supplies its recipe.

### musl libc 1.2.6

Selected Linux pkgsStatic C runtime source; included for build provenance, not an independently reconstructed toolchain inventory.

- [Source download](https://musl.libc.org/releases/musl-1.2.6.tar.gz)
- Raw SHA-256: `d585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/mu/musl/package.nix).

pkgs/top-level/stage.nix creates pkgsStatic with musl on Linux. The recipe also fetches BSD-compatible headers and iconv sources and applies patches; consult the full pinned recipe.

This source location extends the original bundle’s inventory. The pinned package set supplies its recipe.

### libedit 20260508-3.1

Selected OpenSSH package build input; not asserted to be linked into each of its three embedded executables.

- [Source download](https://thrysoee.dk/editline/libedit-20260508-3.1.tar.gz)
- Raw SHA-256: `91f42d6571dd8d92faedd1341134ce5abca0c5d0b4b352814186d33f2b11272e`.
- [Pinned recipe](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/li/libedit/package.nix).

The OpenSSH package builds more programs than AnonSSH embeds. libedit propagates ncurses. This index does not classify these as demonstrated dependencies of the shipped ssh/scp/sftp-server payloads.

This source location extends the original bundle’s inventory. The pinned package set supplies its recipe.

## Patches and build modifications

For the modified Dropbear server, use the pinned `DROPBEAR_2026.94` source, then apply Nixpkgs [`pass-path.patch`](https://github.com/NixOS/nixpkgs/blob/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/dr/dropbear/pass-path.patch), followed by the project’s [`nix/dropbear-runtime-helpers.patch`](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/nix/dropbear-runtime-helpers.patch). The latter changes `src/svr-chansession.c` to use validated absolute SFTP/scp helper paths through `ANONSSH_SFTP_SERVER` and `ANONSSH_SCP_SERVER`. [default.nix](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/default.nix) appends the project patch to the upstream package’s patches; it does not replace the package recipe.

The following patch files are selected by the relevant pinned recipes. Exact raw-file or normalized hashes are recorded per patch in the JSON. Conditional patches for unselected OpenSSH HPN/GSSAPI, other Boost versions, Darwin, MinGW or LoongArch are not substituted into this Linux build.

| Component | Selected patch | Hash interpretation |
| --- | --- | --- |
| tor | [disable-monotonic-timer-tests.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/to/tor/disable-monotonic-timer-tests.patch) | Raw file |
| dropbear | [pass-path.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/dr/dropbear/pass-path.patch) | Raw file |
| openssh | [locale_archive.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/tools/networking/openssh/locale_archive.patch) | Raw file |
| openssh | [dont_create_privsep_path.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/tools/networking/openssh/dont_create_privsep_path.patch) | Raw file |
| openssh | [ssh-keysign-8.5.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/tools/networking/openssh/ssh-keysign-8.5.patch) | Raw file |
| openssl | [nix-ssl-cert-file.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/development/libraries/openssl/3.5/nix-ssl-cert-file.patch) | Raw file |
| openssl | [openssl-disable-kernel-detection.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/development/libraries/openssl/3.5/openssl-disable-kernel-detection.patch) | Raw file |
| openssl | [use-etc-ssl-certs.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/development/libraries/openssl/3.5/use-etc-ssl-certs.patch) | Raw file |
| zlib | [export-variable.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/development/libraries/zlib/export-variable.patch) | Raw file |
| zlib | [mingw-shared.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/development/libraries/zlib/mingw-shared.patch) | Raw file |
| zstd | [playtests-darwin.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/tools/compression/zstd/playtests-darwin.patch) | Raw file |
| zstd | [man-fix.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/tools/compression/zstd/man-fix.patch) | Raw file |
| libxcrypt | [fix-symver-on-non-elf.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/development/libraries/libxcrypt/fix-symver-on-non-elf.patch) | Raw file |
| boost | [cmake-paths-188.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/development/libraries/boost/cmake-paths-188.patch) | Raw file |
| libedit | [01-cygwin.patch](https://raw.githubusercontent.com/NixOS/nixpkgs/7dd199b0e2993e37b4775ed66b1c291699608c9f/pkgs/by-name/li/libedit/01-cygwin.patch) | Raw file |
| dropbear | [dropbear-runtime-helpers.patch](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/nix/dropbear-runtime-helpers.patch) | Raw file |
| libevent | [883630f76cbf512003b81de25cd96cb75c6cf0f9.patch](https://github.com/libevent/libevent/commit/883630f76cbf512003b81de25cd96cb75c6cf0f9.patch) | Nix normalized patch |
| boost | [0921b9fd5c776aec7748475c6c10807e0d51bc6d.patch](https://github.com/boostorg/context/commit/0921b9fd5c776aec7748475c6c10807e0d51bc6d.patch) | Nix normalized patch; relative=include |
| boost | [5883212311535a0046031d74d1568ae173c1e35b.patch](https://github.com/boostorg/context/commit/5883212311535a0046031d74d1568ae173c1e35b.patch) | Nix normalized patch; relative=include |
| musl | [300-relative.patch](https://raw.githubusercontent.com/openwrt/openwrt/87606e25afac6776d1bbc67ed284434ec5a832b4/toolchain/musl/patches/300-relative.patch) | Raw download |
| musl | [CVE-2026-6042](https://www.openwall.com/lists/musl/2026/04/03/2/1) | Raw download |
| musl | [CVE-2026-40200.patch](https://www.openwall.com/lists/musl/2026/04/10/3/1) | Raw download |

Patches are not the only modifications: complete `postPatch`, `patchPhase`, configure flags, build phases and install phases remain in the pinned recipes. In particular:

- **tor:** Source/version override, six static libraries, --enable-gpl --disable-systemd --disable-seccomp, -static -lgcc, selected build/install phases, postPatch removed, tests off.
- **dropbear:** Appends runtime-helper patch to the pinned Nixpkgs patches; static server uses zlib and libxcrypt.
- **i2pd:** UPnP disabled; certificates copied from buildPackages.i2p output.
- **openssl:** Pinned postPatch modifies async_posix.h for musl and engine paths for static builds; configure uses no-shared/no-module/no-ct, plus other platform flags. Use complete recipe.
- **zlib:** Pinned postPatch substitutes configure archiver fields and removes gzopen_w from win32/zlib.def; complete recipe retained upstream.
- **xz:** Pinned postPatch substitutes /usr/bin/uname in config.guess.
- **scrypt:** Pinned patchPhase removes command -p from Makefile.in, autotools/Makefile.am, libcperciva/cpusupport/Build/cpusupport.sh and configure; patches test shebangs.
- **openssh:** Pinned postPatch changes install mode 4711 to 0711; static configuration, selected features and /etc/ssh override are in the common and top-level recipes.

musl also fetches compatibility headers and auxiliary sources; libedit propagates ncurses; Boost and the compiler/runtime have further build inputs. Follow the full pinned Nixpkgs graph for these. This index does not claim that every optional build dependency is present in the shipped payloads, or that all toolchain sources have been enumerated.

## Rust source references

[Cargo.lock](https://github.com/Sapient-Lumen/W4R3Z/blob/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/Cargo.lock) contains **196 registry packages**, each with its exact version and registry archive checksum. The JSON lists each crate’s direct `static.crates.io` archive URL, the crates.io API download URL and raw SHA-256. There are no Git-sourced lockfile packages in this handoff. Workspace code is browsable in [source/](https://github.com/Sapient-Lumen/W4R3Z/tree/anonssh-v0.2.0-9831b007cd47/Maintained%20Tools/AnonSSH/source/) and included in the complete project ZIP.

`default.nix` sets `cargoLock.lockFile = ./Cargo.lock`. Preserve the lockfile and use Cargo’s `--locked` option when working with it; a Cargo fetch alone is not the full portable-binary build. The project’s static build is driven by `nix-build default.nix --arg static true` from the extracted complete project directory, as used by its Makefile. Do not attempt the portable build using only the reduced repository browsing copy. That build was not run during this index review.

Static inspection of the supplied omitted archive found 196 matching vendored directories, no package-checksum mismatches and no vendored-file checksum failures. All 196 direct crate download references passed bounded HTTP gzip-prefix probes on 2026-10-20. Those probes did not redownload or checksum the complete crate archives, and the lockfile is not proof that every package was linked into this target.

## What was checked, and what remains qualified

- The supplied raw Tor, libevent, OpenSSH, OpenSSL, scrypt, XZ and zlib archive hashes match the corresponding build-recipe hashes. A previously retrieved libxcrypt source archive was also read and hash-matched. These are independent local byte checks, not just version-string matches.
- All 24 inspected Nixpkgs recipe/support files and all 15 referenced local Nixpkgs patches matched the exact public pinned revision byte-for-byte.
- Source-download availability was tested with bounded read-only requests. A successful archive-prefix probe demonstrates an HTTP response with the expected compression signature, **not** a complete download, checksum validation, signature verification or rebuild. Detailed results and timestamps are in the JSON.
- **Tor:** the official [download page](https://download.torproject.org/tor/) and [archive listing](https://archive.torproject.org/tor-package-archive/) identify 0.4.9.14; the [EFF mirror listing](https://tor.eff.org/dist/) also names that tarball. In this environment the direct dist, archive and EFF requests returned a 195-byte “Site Unavailable” HTML page despite HTTP success statuses. They are not marked download-verified, nor declared globally broken. Obtain the exact release tarball from an available listed location and verify the raw SHA-256 above. No Git snapshot is claimed to share that release-tarball byte hash.
- **Java I2P mirrors:** its primary GitHub source and `files.i2p-projekt.de` alternative passed archive-prefix checks. The `download.i2p2.de` mirror returned HTTP 502 and `download.i2p2.no` returned HTTP 404 during this review. Their recipe references are preserved accurately rather than silently replaced.
- **musl patch:** the Openwall 2026-04-03 patch URL timed out on the first attempt; one bounded retry succeeded. Both outcomes are retained in the JSON.
- libxcrypt, LDNS and Boost are additional dependencies whose symbols were observed in embedded Dropbear, ssh and i2pd respectively, but whose upstream source payloads were absent from the original source bundle. Naming them here does not retroactively make the original bundle exhaustive.

The omitted archive’s SHA-256 is `2f849cd78509f972d22a323b87d94ff325645e0abf37b6f91f43df5ddb8406ff`, recorded only to distinguish the supplied artifact from this publication. It is not a download promise. Required notices, licenses, source availability and any distributor obligations must be assessed separately; this index does not assert they have all been satisfied.

Checked 2026-10-20.
