{ pkgs }:

import ../default.nix {
  inherit pkgs;
  embedRuntimes = false;
}
