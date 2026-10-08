{
  description = "GlassTTY development shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python312.withPackages (pythonPackages: with pythonPackages; [
          pip
          virtualenv
          pytest
          jsonschema
        ]);
      in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python
            nodejs_22
            jq
            yq
            ripgrep
            fd
            git
            zip
            unzip
            chromium
          ];

          shellHook = ''
            export GLASSTTY_HOME="''${GLASSTTY_HOME:-$HOME/.local/share/glasstty}"
            export PYTHONPATH="$PWD/daemon/src''${PYTHONPATH:+:$PYTHONPATH}"
            export PATH="$PWD/scripts:$PATH"
            mkdir -p "$GLASSTTY_HOME"
            echo "GlassTTY dev shell ready"
            echo "GLASSTTY_HOME=$GLASSTTY_HOME"
          '';
        };
      });
}
