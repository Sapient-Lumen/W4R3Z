{
  description = "IoTox product and Sandwurm VM qualification profiles";

  inputs = {
    # This is qualification infrastructure, not a product dependency. Public
    # snapshots use a portable sibling path; other operators can replace it
    # with: --override-input sandwurm git+file:/absolute/path/to/sandwurm.
    sandwurm.url = "git+file:../sandwurm";
    nixpkgs.follows = "sandwurm/nixpkgs";
    # A separately locked toolchain builds the optional rescue payload.  It is
    # intentionally not allowed to perturb the product/VM package universe.
    rescue-nixpkgs.url = "nixpkgs";
  };

  outputs = { self, nixpkgs, rescue-nixpkgs, sandwurm }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      rescuePkgs = import rescue-nixpkgs { inherit system; };
      aarch64Pkgs = import nixpkgs {
        inherit system;
        crossSystem = nixpkgs.lib.systems.examples.aarch64-multiplatform;
      };
      # Native AArch64 artifacts are fetched from the locked binary cache for
      # system-emulation gates.  Keeping the guest kernel native avoids a huge
      # cross-NixOS closure while the IoTox harness itself remains cross-built
      # from this exact source tree.
      aarch64NativePkgs = import nixpkgs { system = "aarch64-linux"; };
      rescueAarch64Pkgs = import rescue-nixpkgs {
        inherit system;
        crossSystem = nixpkgs.lib.systems.examples.aarch64-multiplatform;
      };
      unfreePkgs = import nixpkgs {
        inherit system;
        config.allowUnfreePredicate = package:
          nixpkgs.lib.getName package == "resilio-sync";
      };
      sourceRevision = self.rev or self.dirtyRev or "uncommitted";
      releaseSourceRevision = self.rev or "";
      releaseSourceDateEpoch = self.lastModified or 1;
      iotoxSource = nixpkgs.lib.fileset.toSource {
        root = ./.;
        fileset = nixpkgs.lib.fileset.unions [
          ./CMakeLists.txt
          ./REVISION
          ./dependencies.lock
          ./cmake
          ./components/toxsync/include
          ./components/toxsync/src
          ./include
          ./src
          ./tools/generate-sbom.py
        ];
      };
      iotoxTestSource = nixpkgs.lib.fileset.toSource {
        root = ./.;
        fileset = nixpkgs.lib.fileset.unions [
          ./CMakeLists.txt
          ./REVISION
          ./dependencies.lock
          ./cmake
          ./components/toxsync/include
          ./components/toxsync/src
          ./include
          ./src
          ./tests
          ./third_party
        ];
      };
      iotox = pkgs.stdenv.mkDerivation {
        pname = "iotox";
        version = "0.51.0-${nixpkgs.lib.strings.removeSuffix "\n" (builtins.readFile ./REVISION)}";
        src = iotoxSource;
        nativeBuildInputs = [ pkgs.cmake pkgs.ninja ];
        cmakeFlags = [
          "-DBUILD_TESTING=OFF"
          "-DIOTOX_WARNINGS_AS_ERRORS=ON"
        ];
      };
      iotoxSourceLinked = pkgs.callPackage ./nix/iotox-source-linked.nix {
        source = iotoxSource;
        sourceRevision = releaseSourceRevision;
        sourceDateEpoch = releaseSourceDateEpoch;
      };
      ratoxTestHarness = pkgs.stdenv.mkDerivation {
        pname = "iotox-ratox-test-harness";
        version = "0.51.0-${nixpkgs.lib.strings.removeSuffix "\n" (builtins.readFile ./REVISION)}";
        src = iotoxTestSource;
        nativeBuildInputs = [ pkgs.cmake pkgs.ninja ];
        cmakeFlags = [
          "-DBUILD_TESTING=ON"
          "-DIOTOX_WARNINGS_AS_ERRORS=ON"
        ];
        buildPhase = ''
          runHook preBuild
          cmake --build . --target iotox iotox_terminal_pty_fixture iotox_terminal_posix_process_tests iotox_terminal_cgroup_recovery_process_tests
          runHook postBuild
        '';
        installPhase = ''
          runHook preInstall
          install -D -m 0755 iotox "$out/bin/iotox"
          install -D -m 0755 iotox_terminal_pty_fixture "$out/bin/iotox_terminal_pty_fixture"
          install -D -m 0755 iotox_terminal_posix_process_tests "$out/bin/iotox_terminal_posix_process_tests"
          install -D -m 0755 iotox_terminal_cgroup_recovery_process_tests "$out/bin/iotox_terminal_cgroup_recovery_process_tests"
          runHook postInstall
        '';
      };
      ratoxSudoTest = pkgs.callPackage ./nix/ratox-sudo-test.nix {
        inherit ratoxTestHarness;
      };
      ratoxCgroupTest = pkgs.callPackage ./nix/ratox-cgroup-test.nix {
        inherit ratoxTestHarness;
      };
      rescueToyboxSource = pkgs.fetchurl {
        url = "https://github.com/landley/toybox/archive/refs/tags/0.8.14.tar.gz";
        hash = "sha256-CC34z9dhNc48SCDIz0wAgdYUkeCZCv8tpI4h/Ju7JNE=";
      };
      rescueOkshSource = pkgs.fetchurl {
        url = "https://github.com/ibara/oksh/archive/oksh-7.9.tar.gz";
        hash = "sha256-Hckj2hor1S1ANeKuBGPY/tNTM51uaS/3R5JtISU0by4=";
      };
      rescueToybox =
        if rescuePkgs.pkgsStatic.toybox.version == "0.8.14"
        then rescuePkgs.pkgsStatic.toybox
        else throw "IoTox rescue Toybox must remain pinned to 0.8.14";
      rescueOkshBase = rescuePkgs.pkgsStatic.oksh;
      rescueOksh =
        if rescueOkshBase.version == "7.9"
        then rescueOkshBase.overrideAttrs (previous: {
          # Curses bakes its build-time terminfo store path into the otherwise
          # static ELF.  Rescue editing works without it; portability matters
          # more than the optional screen-clear integration here.
          configureFlags = (previous.configureFlags or [ ]) ++ [ "--disable-curses" ];
          patches = (previous.patches or [ ]) ++ [ ./nix/oksh-no-curses.patch ];
        })
        else throw "IoTox rescue oksh must remain pinned to 7.9";
      rescueAarch64Toybox =
        if rescueAarch64Pkgs.pkgsStatic.toybox.version == "0.8.14"
        then rescueAarch64Pkgs.pkgsStatic.toybox
        else throw "IoTox aarch64 rescue Toybox must remain pinned to 0.8.14";
      rescueAarch64OkshBase = rescueAarch64Pkgs.pkgsStatic.oksh;
      rescueAarch64Oksh =
        if rescueAarch64OkshBase.version == "7.9"
        then rescueAarch64OkshBase.overrideAttrs (previous: {
          configureFlags = (previous.configureFlags or [ ]) ++ [ "--disable-curses" ];
          patches = (previous.patches or [ ]) ++ [ ./nix/oksh-no-curses.patch ];
        })
        else throw "IoTox aarch64 rescue oksh must remain pinned to 7.9";
      rescueManifest = pkgs.writeText "iotox-rescue-toolbox.manifest" ''
        format=iotox-rescue-toolbox-v1
        architecture=${system}
        toolchain-nixpkgs-revision=e8be7818e19ada32105a8af937a6a473b38167ca
        shell=oksh
        oksh-version=7.9
        oksh-upstream=https://github.com/ibara/oksh/archive/oksh-7.9.tar.gz
        oksh-sha256=1dc923da1a2bd52d4035e2ae0463d8fed353339d6e692ff747926d2125346f2e
        oksh-curses=disabled-no-terminfo-closure
        utilities=toybox
        toybox-version=0.8.14
        toybox-upstream=https://github.com/landley/toybox/archive/refs/tags/0.8.14.tar.gz
        toybox-sha256=082df8cfd76135ce3c4820c8cf4c0081d61491e0990aff2da48e21fc9bbb24d1
        toybox-shell=excluded-upstream-pending
      '';
      iotoxRescueToolbox = pkgs.runCommand
        "iotox-rescue-toolbox-0.1-${system}" {
          nativeBuildInputs = [
            pkgs.binutils
            pkgs.gnutar
            pkgs.gzip
            pkgs.python3Packages.spdx-tools
          ];
        } ''
          mkdir -p "$out/bin" "$out/share/iotox-rescue/licenses"
          install -m 0555 ${rescueOksh}/bin/oksh "$out/bin/oksh"
          install -m 0555 ${rescueToybox}/bin/toybox "$out/bin/toybox"
          for executable in "$out/bin/oksh" "$out/bin/toybox"; do
            if readelf -l "$executable" | grep -Fq INTERP || \
               readelf -d "$executable" | grep -Fq NEEDED; then
              echo "rescue payload is not static: $executable" >&2
              exit 1
            fi
            if grep -aFq '/nix/store/' "$executable"; then
              echo "rescue payload embeds a Nix store dependency: $executable" >&2
              exit 1
            fi
          done
          applet_count=0
          for applet in $(${rescueToybox}/bin/toybox); do
            case "$applet" in
              sh|toysh)
                echo "refusing pending Toybox shell applet: $applet" >&2
                exit 1
                ;;
              toybox|oksh)
                continue
                ;;
            esac
            ln -s toybox "$out/bin/$applet"
            applet_count=$((applet_count + 1))
          done
          test "$applet_count" -eq 238
          mkdir toybox-source oksh-source
          tar -xzf ${rescueToyboxSource} --strip-components=1 \
            -C toybox-source
          tar -xzf ${rescueOkshSource} --strip-components=1 \
            -C oksh-source
          cp toybox-source/LICENSE \
            "$out/share/iotox-rescue/licenses/toybox-LICENSE"
          cp oksh-source/LEGAL \
            "$out/share/iotox-rescue/licenses/oksh-LEGAL"
          cp oksh-source/CONTRIBUTORS \
            "$out/share/iotox-rescue/licenses/oksh-CONTRIBUTORS"
          install -m 0644 ${rescueManifest} \
            "$out/share/iotox-rescue/manifest"
          printf 'toybox-applets=%s\ncommand-names=%s\n' \
            "$applet_count" "$((applet_count + 2))" \
            >> "$out/share/iotox-rescue/manifest"
          oksh_digest=$(sha256sum "$out/bin/oksh" | cut -d' ' -f1)
          toybox_digest=$(sha256sum "$out/bin/toybox" | cut -d' ' -f1)
          printf 'oksh-elf-sha256=%s\ntoybox-elf-sha256=%s\n' \
            "$oksh_digest" "$toybox_digest" \
            >> "$out/share/iotox-rescue/manifest"
          printf '%s\n' \
            'SPDXVersion: SPDX-2.3' \
            'DataLicense: CC0-1.0' \
            'SPDXID: SPDXRef-DOCUMENT' \
            'DocumentName: iotox-rescue-toolbox-x86_64-linux' \
            'DocumentNamespace: https://iotox.dev/spdx/rescue/0.1/x86_64-linux' \
            'Creator: Tool: IoTox-flake' \
            'Created: 2026-09-02T00:00:00Z' \
            'PackageName: oksh' \
            'SPDXID: SPDXRef-Package-oksh' \
            'PackageVersion: 7.9' \
            'PackageDownloadLocation: NOASSERTION' \
            'PackageSourceInfo: Statically built from oksh 7.9; exact source URL and SHA-256 are in the adjacent IoTox manifest.' \
            'FilesAnalyzed: false' \
            "PackageChecksum: SHA256: $oksh_digest" \
            'PackageLicenseConcluded: ISC' \
            'PackageLicenseDeclared: ISC' \
            'PackageCopyrightText: NOASSERTION' \
            'PackageName: toybox' \
            'SPDXID: SPDXRef-Package-toybox' \
            'PackageVersion: 0.8.14' \
            'PackageDownloadLocation: NOASSERTION' \
            'PackageSourceInfo: Statically built from Toybox 0.8.14; exact source URL and SHA-256 are in the adjacent IoTox manifest.' \
            'FilesAnalyzed: false' \
            "PackageChecksum: SHA256: $toybox_digest" \
            'PackageLicenseConcluded: 0BSD' \
            'PackageLicenseDeclared: 0BSD' \
            'PackageCopyrightText: NOASSERTION' \
            'Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-Package-oksh' \
            'Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-Package-toybox' \
            > "$out/share/iotox-rescue/sbom.spdx"
          pyspdxtools --infile "$out/share/iotox-rescue/sbom.spdx"
        '';
      rescueAarch64Manifest = pkgs.writeText
        "iotox-rescue-toolbox-aarch64.manifest" ''
          format=iotox-rescue-toolbox-v1
          architecture=aarch64-linux
          toolchain-nixpkgs-revision=e8be7818e19ada32105a8af937a6a473b38167ca
          shell=oksh
          oksh-version=7.9
          oksh-upstream=https://github.com/ibara/oksh/archive/oksh-7.9.tar.gz
          oksh-sha256=1dc923da1a2bd52d4035e2ae0463d8fed353339d6e692ff747926d2125346f2e
          oksh-curses=disabled-no-terminfo-closure
          utilities=toybox
          toybox-version=0.8.14
          toybox-upstream=https://github.com/landley/toybox/archive/refs/tags/0.8.14.tar.gz
          toybox-sha256=082df8cfd76135ce3c4820c8cf4c0081d61491e0990aff2da48e21fc9bbb24d1
          toybox-shell=excluded-upstream-pending
        '';
      iotoxRescueToolboxAarch64 = pkgs.runCommand
        "iotox-rescue-toolbox-0.1-aarch64-linux" {
          nativeBuildInputs = [
            pkgs.binutils
            pkgs.gnutar
            pkgs.gzip
            pkgs.python3Packages.spdx-tools
          ];
        } ''
          mkdir -p "$out/bin" "$out/share/iotox-rescue/licenses"
          install -m 0555 ${rescueAarch64Oksh}/bin/oksh "$out/bin/oksh"
          install -m 0555 ${rescueAarch64Toybox}/bin/toybox "$out/bin/toybox"
          for executable in "$out/bin/oksh" "$out/bin/toybox"; do
            readelf -h "$executable" | grep -F 'Machine:' | grep -Fq 'AArch64'
            if readelf -l "$executable" | grep -Fq INTERP || \
               readelf -d "$executable" | grep -Fq NEEDED; then
              echo "aarch64 rescue payload is not static: $executable" >&2
              exit 1
            fi
            if grep -aFq '/nix/store/' "$executable"; then
              echo "aarch64 rescue payload embeds a Nix store dependency: $executable" >&2
              exit 1
            fi
          done
          applet_count=0
          for applet in $(${rescueToybox}/bin/toybox); do
            case "$applet" in
              sh|toysh)
                echo "refusing pending Toybox shell applet: $applet" >&2
                exit 1
                ;;
              toybox|oksh)
                continue
                ;;
            esac
            ln -s toybox "$out/bin/$applet"
            applet_count=$((applet_count + 1))
          done
          test "$applet_count" -eq 238
          mkdir toybox-source oksh-source
          tar -xzf ${rescueToyboxSource} --strip-components=1 -C toybox-source
          tar -xzf ${rescueOkshSource} --strip-components=1 -C oksh-source
          cp toybox-source/LICENSE \
            "$out/share/iotox-rescue/licenses/toybox-LICENSE"
          cp oksh-source/LEGAL \
            "$out/share/iotox-rescue/licenses/oksh-LEGAL"
          cp oksh-source/CONTRIBUTORS \
            "$out/share/iotox-rescue/licenses/oksh-CONTRIBUTORS"
          install -m 0644 ${rescueAarch64Manifest} \
            "$out/share/iotox-rescue/manifest"
          printf 'toybox-applets=%s\ncommand-names=%s\n' \
            "$applet_count" "$((applet_count + 2))" \
            >> "$out/share/iotox-rescue/manifest"
          oksh_digest=$(sha256sum "$out/bin/oksh" | cut -d' ' -f1)
          toybox_digest=$(sha256sum "$out/bin/toybox" | cut -d' ' -f1)
          printf 'oksh-elf-sha256=%s\ntoybox-elf-sha256=%s\n' \
            "$oksh_digest" "$toybox_digest" \
            >> "$out/share/iotox-rescue/manifest"
          printf '%s\n' \
            'SPDXVersion: SPDX-2.3' \
            'DataLicense: CC0-1.0' \
            'SPDXID: SPDXRef-DOCUMENT' \
            'DocumentName: iotox-rescue-toolbox-aarch64-linux' \
            'DocumentNamespace: https://iotox.dev/spdx/rescue/0.1/aarch64-linux' \
            'Creator: Tool: IoTox-flake' \
            'Created: 2026-09-02T00:00:00Z' \
            'PackageName: oksh' \
            'SPDXID: SPDXRef-Package-oksh' \
            'PackageVersion: 7.9' \
            'PackageDownloadLocation: NOASSERTION' \
            'PackageSourceInfo: Statically built from oksh 7.9; exact source URL and SHA-256 are in the adjacent IoTox manifest.' \
            'FilesAnalyzed: false' \
            "PackageChecksum: SHA256: $oksh_digest" \
            'PackageLicenseConcluded: ISC' \
            'PackageLicenseDeclared: ISC' \
            'PackageCopyrightText: NOASSERTION' \
            'PackageName: toybox' \
            'SPDXID: SPDXRef-Package-toybox' \
            'PackageVersion: 0.8.14' \
            'PackageDownloadLocation: NOASSERTION' \
            'PackageSourceInfo: Statically built from Toybox 0.8.14; exact source URL and SHA-256 are in the adjacent IoTox manifest.' \
            'FilesAnalyzed: false' \
            "PackageChecksum: SHA256: $toybox_digest" \
            'PackageLicenseConcluded: 0BSD' \
            'PackageLicenseDeclared: 0BSD' \
            'PackageCopyrightText: NOASSERTION' \
            'Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-Package-oksh' \
            'Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-Package-toybox' \
            > "$out/share/iotox-rescue/sbom.spdx"
          pyspdxtools --infile "$out/share/iotox-rescue/sbom.spdx"
        '';
      ratoxRescueToolboxAarch64UserTest = pkgs.runCommand
        "iotox-ratox-rescue-toolbox-aarch64-user" {
          nativeBuildInputs = [ pkgs.qemu ];
        } ''
          export HOME="$TMPDIR/home"
          mkdir -p "$HOME"
          ${pkgs.qemu}/bin/qemu-aarch64 \
            ${iotoxRescueToolboxAarch64}/bin/oksh -c \
            'printf "aarch64-oksh\\n"' | grep -Fxq aarch64-oksh
          ${pkgs.qemu}/bin/qemu-aarch64 \
            ${iotoxRescueToolboxAarch64}/bin/toybox printf \
            'aarch64-toybox\n' | grep -Fxq aarch64-toybox
          ${pkgs.qemu}/bin/qemu-aarch64 \
            ${iotoxRescueToolboxAarch64}/bin/toybox sha256sum \
            ${iotoxRescueToolboxAarch64}/bin/oksh > digest
          test "$(wc -c < digest)" -gt 64
          ${pkgs.qemu}/bin/qemu-aarch64 \
            ${iotoxRescueToolboxAarch64}/bin/toybox > applets
          test "$(wc -w < applets)" -eq 238
          ! grep -Eq '(^|[[:space:]])(sh|toysh)($|[[:space:]])' applets
          for applet in $(cat applets); do
            test -L "${iotoxRescueToolboxAarch64}/bin/$applet"
          done
          touch "$out"
        '';
      ratoxRescueToolboxTest =
        pkgs.callPackage ./nix/ratox-rescue-toolbox-test.nix {
          inherit ratoxTestHarness iotoxRescueToolbox;
        };
      # Build the product-side harness with the same locked nixpkgs/toolchain
      # as the AArch64 NixOS guest.  The separately locked rescue nixpkgs is
      # reserved for the static capsule itself and cannot perturb the product
      # ABI or turn newer compiler heuristics into a qualification variable.
      ratoxTestHarnessAarch64 = aarch64Pkgs.stdenv.mkDerivation {
        pname = "iotox-ratox-test-harness";
        version = "0.51.0-${nixpkgs.lib.strings.removeSuffix "\n" (builtins.readFile ./REVISION)}-aarch64";
        src = iotoxTestSource;
        nativeBuildInputs = [
          aarch64Pkgs.buildPackages.cmake
          aarch64Pkgs.buildPackages.ninja
        ];
        cmakeFlags = [
          "-DBUILD_TESTING=ON"
          "-DIOTOX_WARNINGS_AS_ERRORS=ON"
        ];
        buildPhase = ''
          runHook preBuild
          cmake --build . --target iotox iotox_terminal_pty_fixture iotox_terminal_posix_process_tests
          runHook postBuild
        '';
        installPhase = ''
          runHook preInstall
          install -D -m 0755 iotox "$out/bin/iotox"
          install -D -m 0755 iotox_terminal_pty_fixture "$out/bin/iotox_terminal_pty_fixture"
          install -D -m 0755 iotox_terminal_posix_process_tests "$out/bin/iotox_terminal_posix_process_tests"
          runHook postInstall
        '';
      };
      ratoxRescueToolboxAarch64BinfmtTest =
        pkgs.callPackage ./nix/ratox-rescue-toolbox-aarch64-test.nix {
          inherit ratoxTestHarness iotoxRescueToolboxAarch64;
        };
      ratoxRescueToolboxAarch64SystemTest =
        pkgs.callPackage ./nix/ratox-rescue-toolbox-aarch64-system-test.nix {
          inherit ratoxTestHarnessAarch64 iotoxRescueToolboxAarch64;
          aarch64Kernel = aarch64NativePkgs.linuxPackages.kernel;
          aarch64Busybox = aarch64NativePkgs.pkgsStatic.busybox;
        };
      protectedStateTest =
        pkgs.callPackage ./nix/protected-state-test.nix {
          inherit iotoxSourceLinked;
        };
      rollbackWitnessServiceTest =
        pkgs.callPackage ./nix/rollback-witness-service-test.nix {
          inherit iotoxSourceLinked;
        };
      toxBootstrap = pkgs.callPackage ./nix/tox-bootstrap.nix {
        inherit (iotoxSourceLinked) libsodium toxcoreSource;
      };
      toxBootstrapSecondary = pkgs.callPackage ./nix/tox-bootstrap.nix {
        inherit (iotoxSourceLinked) libsodium toxcoreSource;
        port = 33446;
      };
      toxBootstrapServiceTest =
        pkgs.callPackage ./nix/tox-bootstrap-service-test.nix {
          inherit toxBootstrap;
        };
      iotoxI2pdSrc = pkgs.fetchFromGitHub {
        owner = "PurpleI2P";
        repo = "i2pd";
        tag = "2.60.0";
        hash = "sha256-oVC31GpygznXbmjQ3qv3XZ58jZ9l6ibBoueuBM5Hk0M=";
      };
      iotoxI2pdLab = pkgs.i2pd.overrideAttrs (_final: _previous: {
        version = "2.60.0";
        src = iotoxI2pdSrc;
      });
      iotoxI2pdSource = pkgs.runCommand "iotox-i2pd-2.60.0-source" { } ''
        cp -R --no-preserve=mode,ownership ${iotoxI2pdSrc} "$out"
      '';
      toxcoreProviderUpgrade = pkgs.callPackage ./nix/toxcore-provider-upgrade.nix {
        inherit (iotoxSourceLinked) libsodium;
        currentToxcoreSource = iotoxSourceLinked.toxcoreSource;
        iotox = iotoxSourceLinked;
      };
      mkGuest = { role, routeMode ? "none" }: nixpkgs.lib.nixosSystem {
        inherit system;
        specialArgs = {
          iotox = iotoxSourceLinked;
          inherit role routeMode sourceRevision toxBootstrap;
          providerOldFixture = toxcoreProviderUpgrade.oldFixture;
          providerCurrentFixture = toxcoreProviderUpgrade.currentFixture;
          sandwurmPackage = sandwurm.packages.${system}.sandwurm;
        };
        modules = [
          sandwurm.nixosModules.directCloudHypervisorGuest
          ./nix/iotox-sandwurm-guest.nix
        ];
      };
      mkThreeWriterGuest = threeWriter: nixpkgs.lib.nixosSystem {
        inherit system;
        specialArgs = {
          iotox = iotoxSourceLinked;
          inherit sourceRevision toxBootstrap threeWriter;
          sandwurmPackage = sandwurm.packages.${system}.sandwurm;
        };
        modules = [
          sandwurm.nixosModules.directCloudHypervisorGuest
          ./nix/iotox-sandwurm-three-writer.nix
        ];
      };
      threeWriterGuest = mkThreeWriterGuest {};
      mkThreeWriterNearCeilingGuest = cap: mkThreeWriterGuest {
        hostName = "iotox-three-writer-nc-cap${toString cap}";
        taskId = "iotox-three-writer-near-ceiling-cap-${toString cap}";
        profile = "iotox-three-writer-near-ceiling-cap-${toString cap}";
        reviewHint =
          "Three source-linked IoTox nodes attempt a 3500-file full-mesh read-write namespace inside KVM with ${toString cap} tree lanes";
        capacityFiles = 3500;
        capacityFileBytes = 16384;
        maxSyncTreeLanes = cap;
        namespaceMaxSyncTreeLanes = cap;
        shadowCycles = 0;
        maintenanceLifecycle = false;
        runFollowups = false;
        timeoutSeconds = 1800;
      };
      threeWriterNearCeilingCap1Guest = mkThreeWriterNearCeilingGuest 1;
      threeWriterNearCeilingCap4Guest = mkThreeWriterNearCeilingGuest 4;
      threeWriterNearCeilingCap8Guest = mkThreeWriterNearCeilingGuest 8;
      threeWriterNearCeilingCap16Guest = mkThreeWriterNearCeilingGuest 16;
      threeWriterNearCeilingCap32Guest = mkThreeWriterNearCeilingGuest 32;
      threeWriterNearCeilingCap64Guest = mkThreeWriterNearCeilingGuest 64;
      threeWriterSoakSmokeGuest = mkThreeWriterGuest {
        hostName = "iotox-three-writer-soak-smoke";
        taskId = "iotox-three-writer-soak-smoke";
        profile = "iotox-three-writer-soak-smoke";
        reviewHint =
          "Three source-linked IoTox nodes run a short writable soak with restart and repair cells inside KVM";
        capacityFiles = 128;
        capacityFileBytes = 4096;
        shadowCycles = 4;
        soakSeconds = 30;
        soakMinimumCycles = 3;
        soakRestartEvery = 2;
        soakRestartSettlePolicy = "repair-before-edit";
        soakRepairEvery = 2;
        soakRepairRestartPolicy = "defer";
        syncRepairControlTimeoutMs = 120000;
        timeoutSeconds = 300;
      };
      threeWriterSoak24hGuest = mkThreeWriterGuest {
        hostName = "iotox-three-writer-soak-24h";
        taskId = "iotox-three-writer-soak-24h";
        profile = "iotox-three-writer-soak-24h";
        reviewHint =
          "Three source-linked IoTox nodes run the 24-hour writable synchronization graduation soak inside KVM";
        capacityFiles = 512;
        capacityFileBytes = 16384;
        shadowCycles = 24;
        soakSeconds = 86400;
        soakMinimumCycles = 288;
        soakCycleDelaySeconds = 240;
        soakRestartEvery = 24;
        soakRestartSettlePolicy = "repair-before-edit";
        soakFinalBoundaryRestartPolicy = "skip-if-floor-satisfied";
        soakRepairEvery = 12;
        soakRepairRestartPolicy = "defer";
        syncRepairControlTimeoutMs = 120000;
        soakStalledRestartAfter = 600;
        timeoutSeconds = 900;
      };
      mkSyncPowerCutGuest = powerCutBoundary: nixpkgs.lib.nixosSystem {
        inherit system;
        specialArgs = {
          iotox = iotoxSourceLinked;
          inherit sourceRevision toxBootstrap powerCutBoundary;
          sandwurmPackage = sandwurm.packages.${system}.sandwurm;
        };
        modules = [
          sandwurm.nixosModules.directCloudHypervisorGuest
          ./nix/iotox-sandwurm-sync-power-cut.nix
        ];
      };
      syncPowerCutGuest = mkSyncPowerCutGuest "pre-exchange-pending";
      syncPowerCutPostExchangeGuest =
        mkSyncPowerCutGuest "post-exchange-pending";
      syncPowerCutReceiveStagingGuest =
        mkSyncPowerCutGuest "receive-staging-partial";
      syncPowerCutCasInstallGuest =
        mkSyncPowerCutGuest "cas-install-temporary";
      syncPowerCutManifestInstallGuest =
        mkSyncPowerCutGuest "manifest-install-temporary";
      syncPowerCutBranchRecordInstallGuest =
        mkSyncPowerCutGuest "branch-record-install-temporary";
      syncPowerCutBranchPointerUpdateGuest =
        mkSyncPowerCutGuest "branch-pointer-update-temporary";
      syncPowerCutManifestDirectoryFsyncGuest =
        mkSyncPowerCutGuest "manifest-install-directory-fsync";
      syncPowerCutBranchRecordDirectoryFsyncGuest =
        mkSyncPowerCutGuest "branch-record-install-directory-fsync";
      syncPowerCutBranchPointerDirectoryFsyncGuest =
        mkSyncPowerCutGuest "branch-pointer-update-directory-fsync";
      syncMetadataCorruptionGuest = nixpkgs.lib.nixosSystem {
        inherit system;
        specialArgs = {
          iotox = iotoxSourceLinked;
          inherit sourceRevision toxBootstrap;
          sandwurmPackage = sandwurm.packages.${system}.sandwurm;
        };
        modules = [
          sandwurm.nixosModules.directCloudHypervisorGuest
          ./nix/iotox-sandwurm-sync-metadata-corruption.nix
        ];
      };
      syncProjectionDescriptorGuest = nixpkgs.lib.nixosSystem {
        inherit system;
        specialArgs = {
          iotox = iotoxSourceLinked;
          inherit sourceRevision toxBootstrap;
          sandwurmPackage = sandwurm.packages.${system}.sandwurm;
        };
        modules = [
          sandwurm.nixosModules.directCloudHypervisorGuest
          ./nix/iotox-sandwurm-sync-projection-descriptor.nix
        ];
      };
      syncShadowGuest = nixpkgs.lib.nixosSystem {
        inherit system;
        specialArgs = {
          iotox = iotoxSourceLinked;
          inherit sourceRevision toxBootstrap;
          resilioSync = unfreePkgs.resilio-sync;
          sandwurmPackage = sandwurm.packages.${system}.sandwurm;
        };
        modules = [
          sandwurm.nixosModules.directCloudHypervisorGuest
          ./nix/iotox-sandwurm-sync-shadow.nix
        ];
      };
    in {
      nixosModules.toxBootstrap = import ./nix/iotox-tox-bootstrap-service.nix;

      packages.${system} = {
        default = iotoxSourceLinked;
        inherit iotox iotoxSourceLinked toxBootstrap toxBootstrapSecondary
          toxcoreProviderUpgrade;
        iotox-rescue-toolbox = iotoxRescueToolbox;
        iotox-rescue-toolbox-aarch64 = iotoxRescueToolboxAarch64;
        iotox-i2pd-lab = iotoxI2pdLab;
        iotox-i2pd-source = iotoxI2pdSource;
      };

      nixosConfigurations = {
        iotox-sandwurm-client = mkGuest { role = "client"; };
        iotox-sandwurm-device = mkGuest { role = "device"; };
        iotox-sandwurm-client-direct-udp = mkGuest {
          role = "client";
          routeMode = "direct-udp";
        };
        iotox-sandwurm-device-direct-udp = mkGuest {
          role = "device";
          routeMode = "direct-udp";
        };
        iotox-sandwurm-client-forced-tcp = mkGuest {
          role = "client";
          routeMode = "forced-tcp";
        };
        iotox-sandwurm-device-forced-tcp = mkGuest {
          role = "device";
          routeMode = "forced-tcp";
        };
        iotox-sandwurm-client-tox-tor = mkGuest {
          role = "client";
          routeMode = "tox-tor";
        };
        iotox-sandwurm-device-tox-tor = mkGuest {
          role = "device";
          routeMode = "tox-tor";
        };
        iotox-sandwurm-client-tox-i2p = mkGuest {
          role = "client";
          routeMode = "tox-i2p";
        };
        iotox-sandwurm-device-tox-i2p = mkGuest {
          role = "device";
          routeMode = "tox-i2p";
        };
        iotox-sandwurm-client-tox-i2p-construction = mkGuest {
          role = "client";
          routeMode = "tox-i2p-construction";
        };
        iotox-sandwurm-device-tox-i2p-construction = mkGuest {
          role = "device";
          routeMode = "tox-i2p-construction";
        };
        iotox-sandwurm-three-writer = threeWriterGuest;
        iotox-sandwurm-three-writer-near-ceiling-cap-1 =
          threeWriterNearCeilingCap1Guest;
        iotox-sandwurm-three-writer-near-ceiling-cap-4 =
          threeWriterNearCeilingCap4Guest;
        iotox-sandwurm-three-writer-near-ceiling-cap-8 =
          threeWriterNearCeilingCap8Guest;
        iotox-sandwurm-three-writer-near-ceiling-cap-16 =
          threeWriterNearCeilingCap16Guest;
        iotox-sandwurm-three-writer-near-ceiling-cap-32 =
          threeWriterNearCeilingCap32Guest;
        iotox-sandwurm-three-writer-near-ceiling-cap-64 =
          threeWriterNearCeilingCap64Guest;
        iotox-sandwurm-three-writer-soak-smoke =
          threeWriterSoakSmokeGuest;
        iotox-sandwurm-three-writer-soak-24h =
          threeWriterSoak24hGuest;
        iotox-sandwurm-sync-power-cut = syncPowerCutGuest;
        iotox-sandwurm-sync-power-cut-post-exchange =
          syncPowerCutPostExchangeGuest;
        iotox-sandwurm-sync-power-cut-receive-staging =
          syncPowerCutReceiveStagingGuest;
        iotox-sandwurm-sync-power-cut-cas-install =
          syncPowerCutCasInstallGuest;
        iotox-sandwurm-sync-power-cut-manifest-install =
          syncPowerCutManifestInstallGuest;
        iotox-sandwurm-sync-power-cut-branch-record-install =
          syncPowerCutBranchRecordInstallGuest;
        iotox-sandwurm-sync-power-cut-branch-pointer-update =
          syncPowerCutBranchPointerUpdateGuest;
        iotox-sandwurm-sync-power-cut-manifest-directory-fsync =
          syncPowerCutManifestDirectoryFsyncGuest;
        iotox-sandwurm-sync-power-cut-branch-record-directory-fsync =
          syncPowerCutBranchRecordDirectoryFsyncGuest;
        iotox-sandwurm-sync-power-cut-branch-pointer-directory-fsync =
          syncPowerCutBranchPointerDirectoryFsyncGuest;
        iotox-sandwurm-sync-metadata-corruption =
          syncMetadataCorruptionGuest;
        iotox-sandwurm-sync-projection-descriptor =
          syncProjectionDescriptorGuest;
        iotox-sandwurm-sync-shadow = syncShadowGuest;
      };

      checks.${system} = {
        iotox-package = iotox;
        iotox-source-linked = iotoxSourceLinked;
        inherit toxBootstrapServiceTest;
        toxcore-provider-upgrade = toxcoreProviderUpgrade;
        ratox-sudo-vm = ratoxSudoTest;
        ratox-cgroup-vm = ratoxCgroupTest;
        ratox-rescue-toolbox-vm = ratoxRescueToolboxTest;
        ratox-rescue-toolbox-aarch64-user =
          ratoxRescueToolboxAarch64UserTest;
        ratox-rescue-toolbox-aarch64-binfmt-vm =
          ratoxRescueToolboxAarch64BinfmtTest;
        ratox-rescue-toolbox-aarch64-system-vm =
          ratoxRescueToolboxAarch64SystemTest;
        protected-state-fscrypt-vm = protectedStateTest;
        rollback-witness-service-vm = rollbackWitnessServiceTest;
      };

      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.cmake
          pkgs.clang
          pkgs.clang-tools
          pkgs.gcc
          pkgs.git
          pkgs.libargon2
          pkgs.libsodium
          pkgs.ninja
          pkgs.pkg-config
          pkgs.python3
          pkgs.python3Packages.gcovr
        ];
        LD_LIBRARY_PATH = nixpkgs.lib.makeLibraryPath [
          pkgs.libargon2
          pkgs.libsodium
        ];
      };
    };
}
