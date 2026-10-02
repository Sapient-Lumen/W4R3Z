{ config, lib, pkgs, iotox, toxBootstrap, resilioSync, sandwurmPackage,
  sourceRevision, ... }:
let
  expectedVersion = "0.51.0";
  expectedRevision =
    lib.strings.removeSuffix "\n" (builtins.readFile ../REVISION);
in {
  sandwurm.directCloudHypervisorGuest = {
    hostName = "iotox-sync-shadow";
    taskId = "iotox-sync-shadow-qualification";
    authorityMode = "bounded";
    networkClass = "none";
    workspaceGrant = "shared";
    stateGrant = "task-private";
    profile = "iotox-resilio-shadow-no-network-qualification";
    reviewHint =
      "Two source-linked IoTox nodes shadowed a real Resilio RW/RO pair for two hours inside KVM";
  };

  environment.systemPackages = [
    iotox
    toxBootstrap
    resilioSync
    sandwurmPackage
    pkgs.python3
  ];

  systemd.services.sandwurm-guest-receipts = {
    requires = [ "iotox-sync-shadow.service" ];
    after = [ "iotox-sync-shadow.service" ];
  };

  systemd.services.iotox-sync-shadow = {
    description = "Qualify IoTox one-writer sync beside Resilio Sync";
    wantedBy = [ "multi-user.target" ];
    requires = [ "workspace.mount" ];
    after = [ "local-fs.target" "workspace.mount" ];
    before = [ "sandwurm-guest-receipts.service" ];
    unitConfig.ConditionPathIsMountPoint = "/workspace";
    path = [ pkgs.coreutils pkgs.jq pkgs.python3 pkgs.systemd ];
    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
      StateDirectory = "iotox-sync-shadow";
      StateDirectoryMode = "0700";
      StandardOutput = "journal+console";
      StandardError = "journal+console";
    };
    script = ''
      set -euo pipefail
      umask 0077
      receipt_dir=/workspace/guest-receipts/iotox
      install -d -m 0700 "$receipt_dir"

      python3 ${../tools/run-sync-shadow.py} \
        --iotox ${iotox}/bin/iotox \
        --bootstrap ${toxBootstrap}/bin/DHT_bootstrap \
        --rslsync ${resilioSync}/bin/rslsync \
        --state-root /var/lib/iotox-sync-shadow \
        --evidence "$receipt_dir/sync-shadow.json" \
        --duration-seconds 7200 \
        --interval-seconds 30 \
        --restart-every-cycles 20 \
        --timeout 180

      jq -e '
        .schema == "iotox.sync-shadow.v1" and
        .status == "passed" and
        .incumbent == "resilio-sync" and
        .duration_floor_seconds == 7200 and
        .elapsed_ms >= 7200000 and
        .cycles >= 9 and
        .node_count == 2 and
        .manual_publish_pull_activate_commands == 0 and
        (.publisher_restarts | type) == "number" and
        (.replica_restarts | type) == "number" and
        (.publisher_replay_evictions | type) == "number" and
        .publisher_replay_evictions > 0 and
        (.canonical_manifest_sha256 | test("^[0-9a-f]{64}$")) and
        (.resilio_binary_sha256 | test("^[0-9a-f]{64}$")) and
        (.iotox_binary_sha256 | test("^[0-9a-f]{64}$")) and
        .contains_secrets == false
      ' "$receipt_dir/sync-shadow.json" >/dev/null

      version_output="$(${iotox}/bin/iotox --version)"
      test "$version_output" = 'IoTox ${expectedVersion} ${expectedRevision}'
      binary_sha256="$(sha256sum ${iotox}/bin/iotox | cut -d' ' -f1)"
      virtualization="$(systemd-detect-virt --vm)"
      test "$virtualization" = kvm
      cgroup_type="$(stat -fc '%T' /sys/fs/cgroup)"
      test "$cgroup_type" = cgroup2fs
      jq -n \
        --arg schema iotox.sandwurm-vm-smoke.v0 \
        --arg status passed \
        --arg role device \
        --arg source_revision ${lib.escapeShellArg sourceRevision} \
        --arg product_revision ${lib.escapeShellArg expectedRevision} \
        --arg version "$version_output" \
        --arg binary_sha256 "$binary_sha256" \
        --arg virtualization "$virtualization" \
        --arg cgroup_type "$cgroup_type" \
        '{
          schema: $schema,
          status: $status,
          role: $role,
          source_revision: $source_revision,
          product_revision: $product_revision,
          version: $version,
          binary_sha256: $binary_sha256,
          virtualization: $virtualization,
          cgroup_type: $cgroup_type,
          network_class: "none",
          package_variant: "pinned-source-linked",
          contains_secrets: false
        }' >"$receipt_dir/vm-smoke.json.tmp"
      mv "$receipt_dir/vm-smoke.json.tmp" "$receipt_dir/vm-smoke.json"
    '';
  };
}
