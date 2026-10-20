{ stdenv, lib, cmake, ninja, openssl }:

stdenv.mkDerivation {
  pname = "toxsync";
  version = "0.7.0";
  src = lib.cleanSource ../.;

  nativeBuildInputs = [ cmake ninja ];
  buildInputs = [ openssl ];
  cmakeFlags = [
    "-DTOXSYNC_WARNINGS_AS_ERRORS=ON"
    "-DTOXSYNC_BUILD_TESTS=ON"
    "-DTOXSYNC_BUILD_BENCHMARK=OFF"
    "-DTOXSYNC_CRYPTO_BACKEND=OPENSSL"
    "-DTOXSYNC_ENABLE_SIMD=ON"
  ];

  doCheck = true;
  checkPhase = ''
    runHook preCheck
    ctest --output-on-failure
    runHook postCheck
  '';

  meta = {
    description = "Transport-neutral receiver-side delta synchronization library";
    license = lib.licenses.mit;
    platforms = lib.platforms.unix;
  };
}
