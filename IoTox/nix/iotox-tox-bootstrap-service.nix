{ config, lib, pkgs, ... }:

let
  cfg = config.services.iotox.toxBootstrap;
  stateDirectory = "iotox-tox-bootstrap";
  statePath = "/var/lib/${stateDirectory}";
  familyArgument = if cfg.addressFamily == "ipv4" then "--ipv4" else "--ipv6";
  bootstrapArguments = lib.optionals (cfg.bootstrapPeer != null) [
    cfg.bootstrapPeer.address
    (toString cfg.bootstrapPeer.port)
    cfg.bootstrapPeer.publicKey
  ];
  packageExecutable =
    if cfg.package == null then
      "/invalid/iotox-tox-bootstrap-package-not-configured"
    else
      "${cfg.package}/bin/DHT_bootstrap";
  command = lib.escapeShellArgs (
    [ packageExecutable familyArgument ]
    ++ bootstrapArguments
  );
  stateCheck = pkgs.writeShellScript "iotox-tox-bootstrap-state-check" ''
    set -eu
    check_regular() {
      path=$1
      bytes=$2
      if [ -L "$path" ] || [ ! -f "$path" ]; then
        echo "refusing unsafe bootstrap state path: $path" >&2
        exit 1
      fi
      if [ "$(${pkgs.coreutils}/bin/stat -c %s -- "$path")" -ne "$bytes" ]; then
        echo "refusing malformed bootstrap state file: $path" >&2
        exit 1
      fi
      if [ "$(${pkgs.coreutils}/bin/stat -c %a -- "$path")" != 600 ]; then
        echo "refusing bootstrap state file without mode 0600: $path" >&2
        exit 1
      fi
    }
    if [ -e key ] || [ -L key ]; then
      check_regular key 64
    fi
    if [ -e PUBLIC_ID.txt ] || [ -L PUBLIC_ID.txt ]; then
      check_regular PUBLIC_ID.txt 64
      if ! ${pkgs.gnugrep}/bin/grep -Eq '^[0-9A-F]{64}$' PUBLIC_ID.txt; then
        echo "refusing malformed bootstrap public identity" >&2
        exit 1
      fi
    fi
  '';
in
{
  options.services.iotox.toxBootstrap = {
    enable = lib.mkEnableOption
      "an explicitly owner-operated c-toxcore bootstrap and TCP relay";

    package = lib.mkOption {
      type = lib.types.nullOr lib.types.package;
      default = null;
      description = ''
        Source-pinned package containing bin/DHT_bootstrap. This is explicit
        because the module never downloads or silently selects a daemon.
      '';
    };

    addressFamily = lib.mkOption {
      type = lib.types.enum [ "ipv4" "ipv6" ];
      default = "ipv4";
      description = "Wildcard address family used by the upstream daemon.";
    };

    bootstrapPeer = lib.mkOption {
      default = null;
      description = ''
        Optional existing Tox node used to join the DHT. Null starts an
        isolated node; it does not invent or download a community endpoint.
      '';
      type = lib.types.nullOr (lib.types.submodule {
        options = {
          address = lib.mkOption {
            type = lib.types.strMatching "[^[:space:]]+";
            description = "Operator-reviewed bootstrap address.";
          };
          port = lib.mkOption {
            type = lib.types.ints.between 1 65535;
            description = "Operator-reviewed bootstrap UDP port.";
          };
          publicKey = lib.mkOption {
            type = lib.types.strMatching "[0-9A-Fa-f]{64}";
            description = "Exact Tox public key of the bootstrap peer.";
          };
        };
      });
    };

    openFirewall = lib.mkOption {
      type = lib.types.bool;
      default = false;
      description = ''
        Open TCP and UDP port 33445. This is false by default so importing the
        module never turns a machine into public infrastructure implicitly.
      '';
    };

    memoryMax = lib.mkOption {
      type = lib.types.str;
      default = "256M";
      description = "systemd MemoryMax value for the daemon cgroup.";
    };

    cpuQuota = lib.mkOption {
      type = lib.types.str;
      default = "50%";
      description = "systemd CPUQuota value for the daemon cgroup.";
    };

    tasksMax = lib.mkOption {
      type = lib.types.ints.between 1 4096;
      default = 64;
      description = "Maximum task count for the daemon cgroup.";
    };

    restartSec = lib.mkOption {
      type = lib.types.ints.between 1 3600;
      default = 5;
      description = "Bounded delay before restart after process failure.";
    };
  };

  config = lib.mkIf cfg.enable {
    assertions = [
      {
        assertion = cfg.package != null;
        message =
          "services.iotox.toxBootstrap.package must name a reviewed pinned package";
      }
    ];

    networking.firewall.allowedTCPPorts =
      lib.optionals cfg.openFirewall [ 33445 ];
    networking.firewall.allowedUDPPorts =
      lib.optionals cfg.openFirewall [ 33445 ];

    systemd.services.iotox-tox-bootstrap = {
      description = "Owner-operated IoTox Tox bootstrap and TCP relay";
      documentation = [
        "https://github.com/TokTok/c-toxcore"
      ];
      wantedBy = [ "multi-user.target" ];
      after = [ "network-online.target" ];
      wants = [ "network-online.target" ];
      serviceConfig = {
        Type = "simple";
        ExecStartPre = stateCheck;
        ExecStart = command;
        Restart = "on-failure";
        RestartSec = "${toString cfg.restartSec}s";
        DynamicUser = true;
        StateDirectory = stateDirectory;
        StateDirectoryMode = "0700";
        WorkingDirectory = statePath;
        UMask = "0077";
        MemoryMax = cfg.memoryMax;
        CPUQuota = cfg.cpuQuota;
        TasksMax = cfg.tasksMax;
        LimitNOFILE = 4096;
        NoNewPrivileges = true;
        PrivateDevices = true;
        PrivateTmp = true;
        ProtectClock = true;
        ProtectControlGroups = true;
        ProtectHome = true;
        ProtectHostname = true;
        ProtectKernelLogs = true;
        ProtectKernelModules = true;
        ProtectKernelTunables = true;
        ProtectSystem = "strict";
        RestrictAddressFamilies = [ "AF_INET" "AF_INET6" "AF_UNIX" ];
        RestrictNamespaces = true;
        RestrictRealtime = true;
        RestrictSUIDSGID = true;
        LockPersonality = true;
        MemoryDenyWriteExecute = true;
        CapabilityBoundingSet = "";
        AmbientCapabilities = "";
        SystemCallArchitectures = "native";
      };
    };
  };
}
