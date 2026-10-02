{
  stdenv,
  cmake,
  ninja,
  pkg-config,
  toxcoreSource,
  libsodium,
  port ? 33445,
}:
stdenv.mkDerivation {
  pname = "iotox-tox-bootstrap-${toString port}";
  version = "0.2.23";
  src = toxcoreSource;
  nativeBuildInputs = [ cmake ninja pkg-config ];
  buildInputs = [ libsodium ];
  cmakeFlags = [
    "-DBUILD_TOXAV=OFF"
    "-DMUST_BUILD_TOXAV=OFF"
    "-DBOOTSTRAP_DAEMON=OFF"
    "-DDHT_BOOTSTRAP=ON"
    "-DBUILD_FUN_UTILS=OFF"
    "-DBUILD_FUZZ_TESTS=OFF"
    "-DBUILD_MISC_TESTS=OFF"
    "-DAUTOTEST=OFF"
    "-DUNITTEST=OFF"
    "-DENABLE_SHARED=OFF"
    "-DENABLE_STATIC=ON"
  ];
  postPatch = ''
    # This bounded IoTox package exposes one unprivileged, collision-free TCP
    # relay. Upstream's sample additionally binds 443 and 3389, which is
    # inappropriate for an opt-in service and collides with common services.
    # The sample also calls perror unconditionally after successful network
    # initialization, so replace that misleading stale-errno error message.
    substituteInPlace other/DHT_bootstrap.c \
      --replace-fail '#define PORT 33445' '#define PORT ${toString port}' \
      --replace-fail '#define NUM_PORTS 3' '#define NUM_PORTS 1' \
      --replace-fail '{443, 3389, PORT}' '{PORT}' \
      --replace-fail '    perror("Initialization");' \
        '    printf("Networking initialized.\\n");'
  '';
  buildPhase = ''
    runHook preBuild
    cmake --build . --target DHT_bootstrap --parallel "$NIX_BUILD_CORES"
    runHook postBuild
  '';
  installPhase = ''
    runHook preInstall
    install -D -m 0755 DHT_bootstrap "$out/bin/DHT_bootstrap"
    runHook postInstall
  '';
}
