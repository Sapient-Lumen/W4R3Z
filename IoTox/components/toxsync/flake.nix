{
  description = "toxsync C++20 range-synchronization laboratory";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      packages = forAllSystems (system:
        let pkgs = import nixpkgs { inherit system; };
        in {
          default = pkgs.callPackage ./nix/package.nix { };
          toxsync = self.packages.${system}.default;
        });

      devShells = forAllSystems (system:
        let pkgs = import nixpkgs { inherit system; };
        in {
          default = pkgs.mkShell {
            packages = with pkgs; [
              cmake
              ninja
              gcc
              clang
              clang-tools
              gdb
              valgrind
              hyperfine
              linuxPackages.perf
              openssl
            ];
            shellHook = ''
              export LC_ALL=C
              export TZ=UTC
              export MALLOC_ARENA_MAX=1
              echo "toxsync C++20 lab: cmake --preset gcc-debug"
            '';
          };
        });

      checks = forAllSystems (system: {
        toxsync = self.packages.${system}.default;
      });
    };
}
