{
  stdenv,
  fetchurl,
  runCommand,
  cmake,
  ninja,
  pkg-config,
  gnutar,
  gzip,
  python3,
  libsodium,
  currentToxcoreSource,
  iotox,
}:
let
  oldArchive = fetchurl {
    url = "https://github.com/TokTok/c-toxcore/releases/download/v0.2.22/c-toxcore-v0.2.22.tar.gz";
    sha256 = "276d447eb94e9d76e802cecc5ca7660c6c15128a83dfbe4353b678972aeb950a";
  };
  cmpArchive = fetchurl {
    url = "https://github.com/TokTok/cmp/archive/52bfcfa17d2eb4322da2037ad625f5575129cece.tar.gz";
    sha256 = "4abfd641dd5ccba04b6e0ced04a79755fa70709290b3ba15dbd4b4a2de345ed0";
  };
  oldToxcoreSource = runCommand "iotox-c-toxcore-source-0.2.22" {
    nativeBuildInputs = [ gnutar gzip ];
  } ''
    mkdir -p "$out/third_party/cmp"
    tar -xzf ${oldArchive} --strip-components=1 -C "$out"
    tar -xzf ${cmpArchive} --strip-components=1 -C "$out/third_party/cmp"
  '';
  mkFixture = version: toxcoreSource: stdenv.mkDerivation {
    pname = "iotox-toxcore-provider-fixture";
    inherit version;
    src = ../tools/provider-upgrade-fixture;
    nativeBuildInputs = [ cmake ninja pkg-config ];
    buildInputs = [ libsodium ];
    cmakeFlags = [
      "-DTOXCORE_SOURCE_DIR=${toxcoreSource}"
    ];
    postInstall = ''
      mv "$out/bin/iotox-toxcore-provider-fixture" \
        "$out/bin/iotox-toxcore-provider-${version}"
    '';
  };
  oldFixture = mkFixture "0.2.22" oldToxcoreSource;
  currentFixture = mkFixture "0.2.23" currentToxcoreSource;
in
runCommand "iotox-toxcore-provider-upgrade-0.2.22-to-0.2.23" {
  nativeBuildInputs = [ python3 ];
  passthru = {
    inherit oldFixture currentFixture;
  };
} ''
  mkdir -p "$out"
  python3 ${../tools/verify-toxcore-provider-upgrade.py} \
    --old ${oldFixture}/bin/iotox-toxcore-provider-0.2.22 \
    --current ${currentFixture}/bin/iotox-toxcore-provider-0.2.23 \
    --iotox ${iotox}/bin/iotox \
    --output "$out/provider-upgrade.json"
''
