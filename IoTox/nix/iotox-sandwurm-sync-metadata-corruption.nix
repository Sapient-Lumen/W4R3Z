{ config, lib, pkgs, iotox, toxBootstrap, sandwurmPackage,
  sourceRevision, ... }:
let
  expectedVersion = "0.51.0";
  expectedRevision =
    lib.strings.removeSuffix "\n" (builtins.readFile ../REVISION);
in {
  sandwurm.directCloudHypervisorGuest = {
    hostName = "iotox-sync-metadata-corruption";
    taskId = "iotox-sync-metadata-corruption-qualification";
    profile = "iotox-sync-metadata-corruption-no-network-qualification";
    reviewHint =
      "Three source-linked IoTox nodes refuse and exactly recover five durable tree-v2 metadata corruption families inside KVM";
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
    pkgs.jq
    pkgs.python3
    pkgs.util-linux
  ];

  systemd.services.sandwurm-guest-receipts = {
    requires = [ "iotox-sync-metadata-corruption.service" ];
    after = [ "iotox-sync-metadata-corruption.service" ];
  };

  systemd.services.iotox-sync-metadata-corruption = {
    description = "Qualify exact tree-v2 metadata corruption recovery";
    wantedBy = [ "multi-user.target" ];
    requires = [ "workspace.mount" ];
    after = [ "local-fs.target" "workspace.mount" ];
    before = [ "sandwurm-guest-receipts.service" ];
    unitConfig.ConditionPathIsMountPoint = "/workspace";
    path = [ pkgs.coreutils pkgs.jq pkgs.python3 pkgs.util-linux ];
    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
      StateDirectory = "iotox-sync-metadata-corruption";
      StateDirectoryMode = "0700";
      StandardOutput = "journal+console";
      StandardError = "journal+console";
    };
    script = ''
      set -euo pipefail
      umask 0077
      receipt_dir=/workspace/guest-receipts/iotox
      private_receipt_dir=/var/lib/iotox-sync-metadata-corruption/evidence
      install -d -m 0700 "$receipt_dir"
      install -d -m 0700 "$private_receipt_dir"
      receipt="$receipt_dir/sync-metadata-corruption.json"
      private_receipt="$private_receipt_dir/sync-metadata-corruption.json"
      python3 ${../tools/run-sync-metadata-corruption-rehearsal.py} \
        --iotox ${iotox}/bin/iotox \
        --bootstrap ${toxBootstrap}/bin/DHT_bootstrap \
        --three-writer-helper ${../tools/run-sync-three-writer.py} \
        --recovery-helper ${../tools/run-sync-recovery-rehearsal.py} \
        --state-root /var/lib/iotox-sync-metadata-corruption/campaign \
        --evidence "$private_receipt"

      # This is a guest-local smoke predicate. The source-tree Python
      # verifier remains the mandatory closed-schema evidence authority after
      # Sandwurm returns the receipt to the host.
      jq -e '
        .schema == "iotox.sync-metadata-corruption.v2" and
        .status == "passed" and
        .filesystem == "ext4" and
        .network_class == "loopback-only-inside-networkless-vm" and
        .node_count == 3 and
        .directed_read_write_share_count == 6 and
        .family_count == 5 and
        ([.families[].family] == [
          "branch-pointer", "manifest", "immutable-branch-record",
          "workspace", "maintenance"
        ]) and
        ([.families[] | select(
          .live_repair_refused != true or
          .live_corrupt_bytes_retained != true or
          .startup_refused != true or
          .startup_exit == 0 or
          .startup_corrupt_bytes_retained != true or
          .controlled_shutdown_exit != 0 or
          .exact_restoration_verified != true or
          .original_sha256 == .corrupt_sha256
        )] | length) == 0 and
        (.simultaneous.family_count | type) == "number" and
        (.simultaneous.family_count | floor) ==
          .simultaneous.family_count and
        .simultaneous.family_count == 5 and
        ([.simultaneous.families[].family] == [
          "branch-pointer", "manifest", "immutable-branch-record",
          "workspace", "maintenance"
        ]) and
        .simultaneous.mutation ==
          "all-five-last-byte-xor-01-before-agent-resume" and
        .simultaneous.mutation_fence ==
          "agent-process-group-sigstop-all-tasks" and
        (.simultaneous.stopped_agent_tasks | type) == "number" and
        (.simultaneous.stopped_agent_tasks | floor) ==
          .simultaneous.stopped_agent_tasks and
        .simultaneous.stopped_agent_tasks >= 1 and
        .simultaneous.stopped_agent_tasks <= 4096 and
        .simultaneous.controlled_shutdown_exit == 0 and
        .simultaneous.live_repair_refused == true and
        .simultaneous.live_repair_exit == 4 and
        .simultaneous.live_repair_error == "protocol-error" and
        .simultaneous.live_repair_family == "branch-pointer" and
        .simultaneous.live_all_corrupt_bytes_retained == true and
        .simultaneous.initial_startup_refused == true and
        .simultaneous.initial_startup_exit == 3 and
        .simultaneous.initial_startup_family == "branch-pointer" and
        .simultaneous.initial_startup_all_corrupt_bytes_retained == true and
        ([.simultaneous.restoration_steps[].restored_family] == [
          "branch-pointer", "manifest", "immutable-branch-record", "workspace"
        ]) and
        ([.simultaneous.restoration_steps[].next_refused_family] == [
          "manifest", "immutable-branch-record", "workspace", "maintenance"
        ]) and
        ([.simultaneous.restoration_steps[] | select(
          .startup_exit != 3 or
          .restored_prefix_retained != true or
          .remaining_corrupt_bytes_retained != true
        )] | length) == 0 and
        .simultaneous.final_restored_family == "maintenance" and
        .simultaneous.final_startup_succeeded == true and
        .simultaneous.all_original_bytes_retained_after_recovery == true and
        .simultaneous.identity_preserved == true and
        .simultaneous.worktree_preserved == true and
        .simultaneous.exact_restoration_verified == true and
        .identity_preserved == true and
        .final_branch_count == [3, 3, 3] and
        .final_files == 5 and
        .final_directories == 1 and
        .final_bytes == 16411 and
        .final_repair_verified_nodes == 3 and
        .automatic_signed_metadata_quarantine == false and
        .operator_supplied_exact_restoration == true and
        .power_cut == false and
        .dishonest_storage_assessed == false and
        .contains_secrets == false
      ' "$private_receipt" >/dev/null

      version_output="$(${iotox}/bin/iotox --version)"
      test "$version_output" = 'IoTox ${expectedVersion} ${expectedRevision}'
      binary_sha256="$(sha256sum ${iotox}/bin/iotox | cut -d' ' -f1)"
      test "$(jq -r .version "$private_receipt")" = "$version_output"
      test "$(jq -r .binary_sha256 "$private_receipt")" = "$binary_sha256"
      python3 - "$private_receipt" "$receipt" <<'PY'
      import os
      import pathlib
      import sys

      source = pathlib.Path(sys.argv[1])
      destination = pathlib.Path(sys.argv[2])
      payload = source.read_bytes()
      descriptor = os.open(
          destination,
          os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
          0o600,
      )
      try:
          offset = 0
          while offset < len(payload):
              offset += os.write(descriptor, payload[offset:])
          os.fsync(descriptor)
      except BaseException:
          os.close(descriptor)
          destination.unlink(missing_ok=True)
          raise
      else:
          os.close(descriptor)
      parent = os.open(destination.parent, os.O_RDONLY | os.O_DIRECTORY)
      try:
          os.fsync(parent)
      finally:
          os.close(parent)
      PY
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
