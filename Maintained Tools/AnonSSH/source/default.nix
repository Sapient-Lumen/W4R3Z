{ pkgs ? import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/7dd199b0e2993e37b4775ed66b1c291699608c9f.tar.gz";
    sha256 = "08kxnni9l87i089hy7p9a7yr64w6h9x5m2cc7k2hn455hidm9mm3";
  }) { }
, devShell ? false
, static ? false
, releaseSources ? false
, embedRuntimes ? true
}:

assert !static || embedRuntimes;
let
  manifest = builtins.fromTOML (builtins.readFile ./Cargo.toml);
  torLibevent = pkgs.pkgsStatic.libevent;
  torOpenSsl = pkgs.pkgsStatic.openssl;
  torZlib = pkgs.pkgsStatic.zlib;
  torXz = pkgs.pkgsStatic.xz;
  torZstd = pkgs.pkgsStatic.zstd;
  torScrypt = pkgs.pkgsStatic.scrypt;
  torStaticLibraries = [
    torLibevent
    torOpenSsl
    torZlib
    torXz
    torZstd
    torScrypt
  ];
  embeddedI2pd = pkgs.pkgsStatic.i2pd.override { upnpSupport = false; };
  embeddedOpenSsh = pkgs.pkgsStatic.openssh;
  dropbearWithRuntimeHelpers = dropbear: dropbear.overrideAttrs (old: {
    patches = (old.patches or [ ]) ++ [ ./nix/dropbear-runtime-helpers.patch ];
  });
  embeddedDropbear = dropbearWithRuntimeHelpers pkgs.pkgsStatic.dropbear;
  runtimeDropbear = dropbearWithRuntimeHelpers pkgs.dropbear;
  torSystemdOverride =
    if builtins.hasAttr "systemd" pkgs.pkgsStatic.tor.override.__functionArgs
    then { systemd = null; }
    else { systemdLibs = null; };
  embeddedTor = (pkgs.pkgsStatic.tor.override ({
    libseccomp = null;
    libcap = null;
  } // torSystemdOverride)).overrideAttrs (_old: {
    version = "0.4.9.14";
    src = pkgs.fetchurl {
      url = "https://dist.torproject.org/tor-0.4.9.14.tar.gz";
      hash = "sha256-GCRJrByP9DJ42ie2mwIEDhHQPQMn222RJuQZDsYjXko=";
    };
    buildInputs = torStaticLibraries;
    configureFlags = [ "--enable-gpl" "--disable-systemd" "--disable-seccomp" ];
    env.NIX_CFLAGS_LINK = "-static -lgcc";
    postPatch = "";
    buildPhase = ''
      runHook preBuild
      make -j$NIX_BUILD_CORES src/app/tor
      runHook postBuild
    '';
    installPhase = ''
      runHook preInstall
      mkdir -p $out/bin $geoip/share/tor
      install -m 0755 src/app/tor $out/bin/tor
      install -m 0644 src/config/geoip src/config/geoip6 $geoip/share/tor/
      runHook postInstall
    '';
    postInstall = ''
      mkdir -p $geoip/share/tor
    '';
    doCheck = false;
    doInstallCheck = false;
  });
  # Reseed certificates are architecture-independent data.  Taking them from
  # buildPackages avoids evaluating the Java router for cross targets.
  javaI2p = pkgs.buildPackages.i2p;
  i2pCertificates = pkgs.buildPackages.runCommand "anonssh-i2p-certificates" { } ''
    mkdir -p $out
    cp -r ${javaI2p}/certificates $out/
  '';
  i2pBootstrap = ./bootstrap/i2p;
  sourceTree = pkgs.lib.cleanSourceWith {
    src = ./.;
    filter = path: _type:
      let name = builtins.baseNameOf (toString path);
      in !(builtins.elem name [ ".git" "artifacts" "result" "target" ]);
  };
  buildSource = pkgs.lib.cleanSourceWith {
    src = ./.;
    filter = path: _type:
      let
        relative = pkgs.lib.removePrefix "${toString ./.}/" (toString path);
        top = builtins.head (pkgs.lib.splitString "/" relative);
      in relative == toString ./. || builtins.elem top [
        "Cargo.lock"
        "Cargo.toml"
        "LICENSE"
        "Makefile"
        "PUBLISHING.md"
        "README.md"
        "THIRD_PARTY.md"
        "anonssh-bond"
        "anonssh-bond-tokio"
        "anonssh-cli"
        "bootstrap"
        "docs"
        "nix"
        "specs"
      ];
  };
  rustPlatform = if static then pkgs.pkgsStatic.rustPlatform else pkgs.rustPlatform;
  package = rustPlatform.buildRustPackage ({
    pname = "anonssh";
    version = manifest.workspace.package.version;
    src = buildSource;

    cargoLock.lockFile = ./Cargo.lock;
    nativeBuildInputs = pkgs.lib.optionals (!static) [ pkgs.makeWrapper ];
    doCheck = !static && embedRuntimes;

    postInstall = pkgs.lib.optionalString (!static) ''
      wrapProgram $out/bin/anonssh \
        --set ANONSSH_I2PD_BIN ${pkgs.i2pd}/bin/i2pd \
        --set ANONSSH_I2PD_CERTS_DIR ${i2pCertificates}/certificates \
        --set ANONSSH_I2PD_BOOTSTRAP_DIR ${i2pBootstrap} \
        --set ANONSSH_TOR_BIN ${pkgs.tor}/bin/tor \
        --set ANONSSH_SSH_BIN ${pkgs.openssh}/bin/ssh \
        --set ANONSSH_DROPBEAR_BIN ${runtimeDropbear}/bin/dropbear \
        --set ANONSSH_SFTP_SERVER_BIN ${pkgs.openssh}/libexec/sftp-server \
        --set ANONSSH_SCP_BIN ${pkgs.openssh}/bin/scp
    '';

    postFixup = pkgs.lib.optionalString static ''
      if ${pkgs.buildPackages.buildPackages.binutils}/bin/readelf -l $out/bin/anonssh | grep -q INTERP; then
        echo 'static AnonSSH unexpectedly has an ELF interpreter' >&2
        exit 1
      fi
      if ${pkgs.buildPackages.buildPackages.binutils}/bin/readelf -d $out/bin/anonssh | grep -q NEEDED; then
        echo 'static AnonSSH unexpectedly needs a shared library' >&2
        exit 1
      fi
    '';

    meta = {
      description = "Password-recoverable SSH over I2P and Tor";
      license = pkgs.lib.licenses.mit;
      mainProgram = "anonssh";
      platforms = pkgs.lib.platforms.linux;
    };
  } // pkgs.lib.optionalAttrs embedRuntimes {
    ANONSSH_EMBEDDED_TOR_BIN = "${embeddedTor}/bin/tor";
    ANONSSH_EMBEDDED_TOR_VERSION = embeddedTor.version;
    ANONSSH_EMBEDDED_I2PD_BIN = "${embeddedI2pd}/bin/i2pd";
    ANONSSH_EMBEDDED_I2PD_VERSION = embeddedI2pd.version;
    ANONSSH_EMBEDDED_I2PD_CERTS_DIR = "${i2pCertificates}/certificates";
    ANONSSH_EMBEDDED_SSH_BIN = "${embeddedOpenSsh}/bin/ssh";
    ANONSSH_EMBEDDED_SSH_VERSION = embeddedOpenSsh.version;
    ANONSSH_EMBEDDED_DROPBEAR_BIN = "${embeddedDropbear}/bin/dropbear";
    ANONSSH_EMBEDDED_DROPBEAR_VERSION = embeddedDropbear.version;
    ANONSSH_EMBEDDED_SFTP_SERVER_BIN = "${embeddedOpenSsh}/libexec/sftp-server";
    ANONSSH_EMBEDDED_SFTP_SERVER_VERSION = embeddedOpenSsh.version;
    ANONSSH_EMBEDDED_SCP_BIN = "${embeddedOpenSsh}/bin/scp";
    ANONSSH_EMBEDDED_SCP_VERSION = embeddedOpenSsh.version;
  });
  shell = pkgs.mkShell {
    packages = with pkgs; [
      borgbackup
      cargo
      clippy
      gitMinimal
      openssh
      rsync
      rustc
      rustfmt
      sshfs
      unzip
      zip
    ];
  };
  sourceBundle = pkgs.runCommand "anonssh-${manifest.workspace.package.version}-sources" {
    nativeBuildInputs = with pkgs; [ coreutils gnutar gzip ];
  } ''
    set -eu
    root="$TMPDIR/anonssh-sources"
    mkdir -p "$root"
    copy_source() {
      source="$1"
      destination="$2"
      if test -d "$source"; then
        cp -rL "$source" "$destination"
      else
        mkdir -p "$destination"
        cp -L "$source" "$destination/source"
      fi
    }
    copy_source ${sourceTree} "$root/anonssh-${manifest.workspace.package.version}"
    copy_source ${pkgs.path} "$root/nixpkgs-${pkgs.lib.version}"
    copy_source ${package.cargoDeps} "$root/anonssh-rust-dependencies"
    copy_source ${embeddedTor.src} "$root/tor-${embeddedTor.version}"
    copy_source ${embeddedI2pd.src} "$root/i2pd-${embeddedI2pd.version}"
    copy_source ${embeddedOpenSsh.src} "$root/openssh-${embeddedOpenSsh.version}"
    copy_source ${embeddedDropbear.src} "$root/dropbear-${embeddedDropbear.version}"
    copy_source ${torLibevent.src} "$root/libevent-${torLibevent.version}"
    copy_source ${torOpenSsl.src} "$root/openssl-${torOpenSsl.version}"
    copy_source ${torZlib.src} "$root/zlib-${torZlib.version}"
    copy_source ${torXz.src} "$root/xz-${torXz.version}"
    copy_source ${torZstd.src} "$root/zstd-${torZstd.version}"
    copy_source ${torScrypt.src} "$root/scrypt-${torScrypt.version}"
    copy_source ${javaI2p.src} "$root/i2p-java-${javaI2p.version}"

    rust_dependency_entries=0
    for dependency in "$root/anonssh-rust-dependencies"/*; do
      if test -d "$dependency"; then
        if ! test -f "$dependency/Cargo.toml"; then
          echo "vendored Rust dependency is incomplete: $dependency" >&2
          exit 1
        fi
        rust_dependency_entries=$((rust_dependency_entries + 1))
      fi
    done
    if test "$rust_dependency_entries" -eq 0; then
      echo 'corresponding source contains no vendored Rust dependencies' >&2
      exit 1
    fi

    remaining_link="$(find "$root" -type l -print -quit)"
    if test -n "$remaining_link"; then
      echo "corresponding source contains a symlink: $remaining_link" >&2
      exit 1
    fi
    chmod -R u+w "$root"
    find "$root" -print0 | xargs -0 touch -h -d @1
    regular_files="$(find "$root" -type f -print | wc -l | tr -d ' ')"
    mkdir -p "$out"
    tar --sort=name --mtime=@1 --owner=0 --group=0 --numeric-owner \
      -C "$TMPDIR" -czf "$out/anonssh-sources.tar.gz" anonssh-sources
    digest="$(sha256sum "$out/anonssh-sources.tar.gz" | cut -d' ' -f1)"
    printf '{"schema":"anonssh.corresponding-sources.v2","complete":true,"materialized":true,"symlinks":0,"regular_files":%s,"rust_dependency_entries":%s,"archive":"anonssh-sources.tar.gz","sha256":"%s","build_inputs":{"nixpkgs":{"version":"${pkgs.lib.version}","path":"nixpkgs-${pkgs.lib.version}"},"rust_dependencies":{"path":"anonssh-rust-dependencies","format":"Cargo.lock vendor tree"}},"programs":[{"name":"anonssh","version":"${manifest.workspace.package.version}","source_path":"anonssh-${manifest.workspace.package.version}"},{"name":"tor","version":"${embeddedTor.version}","source_path":"tor-${embeddedTor.version}"},{"name":"i2pd","version":"${embeddedI2pd.version}","source_path":"i2pd-${embeddedI2pd.version}"},{"name":"openssh","version":"${embeddedOpenSsh.version}","source_path":"openssh-${embeddedOpenSsh.version}"},{"name":"dropbear","version":"${embeddedDropbear.version}","source_path":"dropbear-${embeddedDropbear.version}"}],"linked_libraries":[{"consumer":"tor","name":"libevent","version":"${torLibevent.version}","source_path":"libevent-${torLibevent.version}"},{"consumer":"tor","name":"openssl","version":"${torOpenSsl.version}","source_path":"openssl-${torOpenSsl.version}"},{"consumer":"tor","name":"zlib","version":"${torZlib.version}","source_path":"zlib-${torZlib.version}"},{"consumer":"tor","name":"xz","version":"${torXz.version}","source_path":"xz-${torXz.version}"},{"consumer":"tor","name":"zstd","version":"${torZstd.version}","source_path":"zstd-${torZstd.version}"},{"consumer":"tor","name":"scrypt","version":"${torScrypt.version}","source_path":"scrypt-${torScrypt.version}"}],"data_sources":[{"consumer":"anonssh","name":"java-i2p-reseed-certificates","version":"${javaI2p.version}","source_path":"i2p-java-${javaI2p.version}"}]}\n' \
      "$regular_files" "$rust_dependency_entries" "$digest" > "$out/sources.json"
  '';
in
if devShell then shell else if releaseSources then sourceBundle else package
