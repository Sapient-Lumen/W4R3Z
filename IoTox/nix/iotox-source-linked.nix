{
  lib,
  stdenv,
  fetchurl,
  runCommand,
  cmake,
  gnumake,
  ninja,
  pkg-config,
  perl,
  python3,
  source,
  sourceRevision,
  sourceDateEpoch,
}:
let
  libsodiumSource = fetchurl {
    url = "https://download.libsodium.org/libsodium/releases/libsodium-1.0.22.tar.gz";
    sha256 = "adbdd8f16149e81ac6078a03aca6fc03b592b89ef7b5ed83841c086191be3349";
  };
  toxcoreArchive = fetchurl {
    url = "https://github.com/TokTok/c-toxcore/releases/download/v0.2.23/c-toxcore-0.2.23.tar.gz";
    sha256 = "b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe";
  };
  cmpArchive = fetchurl {
    url = "https://github.com/TokTok/cmp/archive/52bfcfa17d2eb4322da2037ad625f5575129cece.tar.gz";
    sha256 = "4abfd641dd5ccba04b6e0ced04a79755fa70709290b3ba15dbd4b4a2de345ed0";
  };
  argon2Source = fetchurl {
    url = "https://github.com/P-H-C/phc-winner-argon2/archive/refs/tags/20190702.tar.gz";
    sha256 = "daf972a89577f8772602bf2eb38b6a3dd3d922bf5724d45e7f9589b5e830442c";
  };

  libsodium = stdenv.mkDerivation {
    pname = "iotox-libsodium";
    version = "1.0.22";
    src = libsodiumSource;
    configureFlags = [
      "--disable-shared"
      "--enable-static"
      "--with-pic"
    ];
    enableParallelBuilding = true;
  };

  argon2 = stdenv.mkDerivation {
    pname = "iotox-argon2";
    version = "20190702";
    src = argon2Source;
    nativeBuildInputs = [ gnumake ];
    dontConfigure = true;
    buildPhase = ''
      runHook preBuild
      make -j$NIX_BUILD_CORES \
        ARGON2_VERSION=20190702 \
        LIBRARY_REL=lib \
        CFLAGS='-std=c89 -O3 -Wall -g -Iinclude -Isrc -pthread \
          -Dblake2b=argon2_internal_blake2b \
          -Dblake2b_init=argon2_internal_blake2b_init \
          -Dblake2b_init_key=argon2_internal_blake2b_init_key \
          -Dblake2b_init_param=argon2_internal_blake2b_init_param \
          -Dblake2b_update=argon2_internal_blake2b_update \
          -Dblake2b_final=argon2_internal_blake2b_final \
          -Dblake2b_long=argon2_internal_blake2b_long' \
        libargon2.a
      runHook postBuild
    '';
    installPhase = ''
      runHook preInstall
      install -D -m 0644 libargon2.a "$out/lib/libargon2.a"
      install -D -m 0644 include/argon2.h "$out/include/argon2.h"
      runHook postInstall
    '';
  };

  toxcoreSource = runCommand "iotox-c-toxcore-source-0.2.23" { } ''
    mkdir -p "$out/third_party/cmp"
    tar -xzf ${toxcoreArchive} --strip-components=1 -C "$out"
    tar -xzf ${cmpArchive} --strip-components=1 -C "$out/third_party/cmp"
    patch -d "$out" -p1 \
      < ${./patches/c-toxcore-0.2.23-file-transfer-round-robin.patch}
    patch -d "$out" -p1 \
      < ${./patches/c-toxcore-0.2.23-tcp-connect-timeout-120.patch}
  '';
in
stdenv.mkDerivation {
  pname = "iotox-source-linked";
  version = "0.51.0-rev0051";
  src = source;
  nativeBuildInputs = [ cmake ninja pkg-config perl python3 ];
  buildInputs = [ libsodium ];
  cmakeFlags = [
    "-DBUILD_TESTING=OFF"
    "-DIOTOX_WARNINGS_AS_ERRORS=ON"
    "-DIOTOX_TOXCORE_SOURCE_DIR=${toxcoreSource}"
    "-DIOTOX_LINKED_TOXCORE_VARIANT=iotox-file-rr1-tcp-connect120"
    "-DIOTOX_ARGON2_LIBRARY=${argon2}/lib/libargon2.a"
  ];
  postInstall = ''
    if nm -u "$out/bin/iotox" | grep -Eq ' tox_(new|iterate|kill)$'; then
      echo "source-linked IoTox retains unresolved toxcore symbols" >&2
      exit 1
    fi
    if ldd "$out/bin/iotox" | grep -Eiq 'libtoxcore|libsodium|libargon2'; then
      echo "source-linked IoTox retains a transport/security runtime dependency" >&2
      exit 1
    fi
  '';
  postFixup = ''
    install -d "$out/share/doc/iotox"
    python3 "$src/tools/generate-sbom.py" generate \
      --root "$src" \
      --binary "$out/bin/iotox" \
      --output "$out/share/doc/iotox/iotox.spdx.json" \
      --source-date-epoch ${toString sourceDateEpoch} \
      ${lib.optionalString (sourceRevision != "") "--source-commit ${lib.escapeShellArg sourceRevision}"}
    python3 "$src/tools/generate-sbom.py" verify \
      --root "$src" \
      --binary "$out/bin/iotox" \
      --sbom "$out/share/doc/iotox/iotox.spdx.json"
  '';
  passthru = {
    inherit libsodium toxcoreSource;
  };
  meta = {
    description = "IoTox with pinned source-linked transport and security dependencies";
    license = with lib.licenses; [ mit gpl3Plus isc asl20 cc0 ];
    platforms = [ "x86_64-linux" ];
    mainProgram = "iotox";
  };
}
