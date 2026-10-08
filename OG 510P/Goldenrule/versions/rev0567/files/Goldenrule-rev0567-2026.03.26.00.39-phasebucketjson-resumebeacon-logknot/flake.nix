{
  description = "Concord (gr_engine + grlab)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        gr-engine = pkgs.rustPlatform.buildRustPackage {
          pname = "gr-engine";
          version = "0.1.0";
          src = self;
          cargoLock.lockFile = ./Cargo.lock;
          cargoBuildFlags = [ "-p" "gr_engine" "--bin" "gr-engine" ];
          doCheck = true;
        };

        grlab = pkgs.stdenvNoCC.mkDerivation {
          pname = "grlab";
          version = "0.1.0";
          src = self;
          nativeBuildInputs = [ pkgs.makeWrapper ];
          installPhase = ''
            mkdir -p $out/lib
            cp -r grlab $out/lib/grlab
            mkdir -p $out/bin
            makeWrapper ${pkgs.python311}/bin/python $out/bin/grlab \
              --set PYTHONPATH $out/lib \
              --set GRLAB_ENGINE_BIN ${gr-engine}/bin/gr-engine \
              --add-flags "-m grlab"
          '';
        };
      in
      {
        packages = {
          inherit gr-engine grlab;
          default = gr-engine;
        };

        apps = {
          default = flake-utils.lib.mkApp { drv = gr-engine; };
          gr-engine = flake-utils.lib.mkApp { drv = gr-engine; };
          grlab = flake-utils.lib.mkApp { drv = grlab; };
        };

        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.cargo
            pkgs.ripgrep
            pkgs.rustc
            pkgs.rustfmt
            pkgs.python311
            pkgs.jq
          ];
        };
      });
}
