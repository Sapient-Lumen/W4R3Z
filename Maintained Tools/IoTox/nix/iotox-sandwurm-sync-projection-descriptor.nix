{ config, lib, pkgs, iotox, toxBootstrap, sandwurmPackage,
  sourceRevision, ... }:
let
  expectedVersion = "0.51.0";
  expectedRevision =
    lib.strings.removeSuffix "\n" (builtins.readFile ../REVISION);
in {
  sandwurm.directCloudHypervisorGuest = {
    hostName = "iotox-sync-projection-descriptor";
    taskId = "iotox-sync-projection-descriptor-qualification";
    profile = "iotox-sync-projection-descriptor-no-network-qualification";
    reviewHint =
      "Production renameat2 entry/exit descriptor retention, ext4 busy-remount refusal, explicit salvage, and three-writer convergence inside KVM";
    authorityMode = "bounded";
    networkClass = "none";
    workspaceGrant = "shared";
    stateGrant = "task-private";
  };

  image.repart.partitions."10-root".repartConfig.SizeMinBytes =
    lib.mkForce "8G";
  image.repart.partitions."10-root".repartConfig.PaddingMinBytes =
    lib.mkForce "512M";

  environment.systemPackages = [
    iotox
    toxBootstrap
    sandwurmPackage
    pkgs.coreutils
    pkgs.e2fsprogs
    pkgs.jq
    pkgs.python3
    pkgs.strace
    pkgs.util-linux
  ];

  systemd.services.sandwurm-guest-receipts = {
    requires = [ "iotox-sync-projection-descriptor.service" ];
    after = [ "iotox-sync-projection-descriptor.service" ];
  };

  systemd.services.iotox-sync-projection-descriptor = {
    description = "Qualify tree-v2 projection descriptor retention";
    wantedBy = [ "multi-user.target" ];
    requires = [ "workspace.mount" ];
    after = [ "local-fs.target" "workspace.mount" ];
    before = [ "sandwurm-guest-receipts.service" ];
    unitConfig.ConditionPathIsMountPoint = "/workspace";
    path = [
      pkgs.coreutils pkgs.e2fsprogs pkgs.jq pkgs.python3 pkgs.strace
      pkgs.util-linux
    ];
    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
      StateDirectory = "iotox-sync-projection-descriptor";
      StateDirectoryMode = "0700";
      StandardOutput = "journal+console";
      StandardError = "journal+console";
    };
    script = ''
      set -euo pipefail
      umask 0077
      receipt_dir=/workspace/guest-receipts/iotox
      private_receipt_dir=/var/lib/iotox-sync-projection-descriptor/evidence
      install -d -m 0700 "$receipt_dir" "$private_receipt_dir"
      receipt="$receipt_dir/sync-projection-descriptor.json"
      private_receipt="$private_receipt_dir/sync-projection-descriptor.json"

      python3 ${../tools/run-sync-projection-descriptor-rehearsal.py} \
        --iotox ${iotox}/bin/iotox \
        --bootstrap ${toxBootstrap}/bin/DHT_bootstrap \
        --strace ${pkgs.strace}/bin/strace \
        --three-writer-helper ${../tools/run-sync-three-writer.py} \
        --recovery-helper ${../tools/run-sync-recovery-rehearsal.py} \
        --storage-helper ${../tools/run-sync-storage-fault-rehearsal.py} \
        --power-cut-helper ${../tools/run-sync-power-cut-rehearsal.py} \
        --state-root /var/lib/iotox-spd/c \
        --evidence "$private_receipt"

      jq -e '
        .schema == "iotox.sync-projection-descriptor.v1" and
        .status == "passed" and
        .filesystem == "ext4" and
        .network_class == "loopback-only-inside-networkless-vm" and
        .node_count_per_cell == 3 and
        .directed_read_write_share_count_per_cell == 6 and
        .cell_count == 2 and
        [.cells[].cell] == [
          "pre-exchange-selected", "post-exchange-unselected"
        ] and
        ([.cells[] | select(
          .syscall != "renameat2" or
          .flag != "RENAME_EXCHANGE" or
          .exchange_count != 1 or
          .descriptor_stage_identity_equal != true or
          .repair_refusal.exit != 4 or
          .repair_refusal.error != "protocol-error" or
          .final_converged_nodes != 3 or
          .final_repair_verified_nodes != 3
        )] | length) == 0 and
        .cells[0].phase == "entry" and
        .cells[0].salvage_reapplied == true and
        .cells[1].phase == "exit" and
        .cells[1].busy_remount_exit_nonzero == true and
        .cells[1].descriptor_unchanged_after_busy_remount == true and
        .cells[1].helper_closed_before_successful_remount == true and
        .cells[1].read_only_remount_succeeded == true and
        .cells[1].read_write_remount_succeeded == true and
        .cells[1].stage_inode_preserved_across_remount == true and
        .cells[1].cold_start_refused == true and
        .cells[1].cold_start_exit == 3 and
        .cells[1].cold_start_control_socket_exposed == false and
        .same_fd_across_ro_rw_remount == false and
        .same_fd_remount_nonclaim_reason == "ext4-refuses-ro-remount-busy" and
        .product_test_seam == false and
        .salvage_is_automatic_merge == false and
        .contains_secrets == false
      ' "$private_receipt" >/dev/null

      version_output="$(${iotox}/bin/iotox --version)"
      test "$version_output" = 'IoTox ${expectedVersion} ${expectedRevision}'
      binary_sha256="$(sha256sum ${iotox}/bin/iotox | cut -d' ' -f1)"
      test "$(jq -r .version "$private_receipt")" = "$version_output"
      test "$(jq -r .binary_sha256 "$private_receipt")" = "$binary_sha256"
      install -m 0600 "$private_receipt" "$receipt"
      sync -f "$receipt"

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
