{ config, lib, pkgs, iotox, toxBootstrap, sandwurmPackage,
  sourceRevision, threeWriter ? {}, ... }:
let
  expectedVersion = "0.51.0";
  expectedRevision =
    lib.strings.removeSuffix "\n" (builtins.readFile ../REVISION);
  hostName = threeWriter.hostName or "iotox-three-writer";
  taskId = threeWriter.taskId or "iotox-three-writer-qualification";
  profile = threeWriter.profile or "iotox-three-writer-no-network-qualification";
  reviewHint = threeWriter.reviewHint or
    "Three source-linked IoTox nodes converged one full-mesh read-write namespace inside KVM";
  capacityFiles = threeWriter.capacityFiles or 512;
  capacityFileBytes = threeWriter.capacityFileBytes or 16384;
  capacityLogicalBytes = capacityFiles * capacityFileBytes;
  maxSyncTreeLanes = threeWriter.maxSyncTreeLanes or 4;
  namespaceMaxSyncTreeLanes =
    threeWriter.namespaceMaxSyncTreeLanes or maxSyncTreeLanes;
  effectiveSyncTreeLanes =
    lib.min maxSyncTreeLanes namespaceMaxSyncTreeLanes;
  shadowCycles = threeWriter.shadowCycles or 24;
  soakSeconds = threeWriter.soakSeconds or 0;
  soakMinimumCycles = threeWriter.soakMinimumCycles or 0;
  effectiveSoakMinimumCycles =
    if soakSeconds > 0 && soakMinimumCycles == 0 then 1 else soakMinimumCycles;
  soakCycleDelaySeconds = threeWriter.soakCycleDelaySeconds or 0;
  soakRestartEvery = threeWriter.soakRestartEvery or 0;
  soakRestartPhase =
    if soakRestartEvery > 0 then "before-edit" else "none";
  soakRestartSettlePolicy = threeWriter.soakRestartSettlePolicy or (
    if soakRestartEvery > 0 then "repair-before-edit" else "none"
  );
  soakFinalBoundaryRestartPolicy =
    threeWriter.soakFinalBoundaryRestartPolicy or "allow";
  soakRepairEvery = threeWriter.soakRepairEvery or 0;
  soakRepairRestartPolicy =
    threeWriter.soakRepairRestartPolicy or "defer";
  syncRepairControlTimeoutMs =
    threeWriter.syncRepairControlTimeoutMs or 120000;
  soakStalledRestartAfter = threeWriter.soakStalledRestartAfter or 0;
  maintenanceLifecycle = threeWriter.maintenanceLifecycle or true;
  runFollowups = threeWriter.runFollowups or true;
  timeoutSeconds = threeWriter.timeoutSeconds or 180;
  soakAssertions = if soakSeconds > 0 || effectiveSoakMinimumCycles > 0 then ''
        .soak_campaign == true and
        .soak_requested_seconds == ${toString soakSeconds} and
        .soak_minimum_cycles == ${toString effectiveSoakMinimumCycles} and
        .soak_cycle_delay_ms == ${toString (soakCycleDelaySeconds * 1000)} and
        .soak_restart_every == ${toString soakRestartEvery} and
        .soak_restart_phase == ${builtins.toJSON soakRestartPhase} and
        .soak_restart_settle_policy == ${builtins.toJSON soakRestartSettlePolicy} and
        .soak_final_boundary_restart_policy == ${builtins.toJSON soakFinalBoundaryRestartPolicy} and
        .soak_repair_every == ${toString soakRepairEvery} and
        .soak_repair_restart_policy == ${builtins.toJSON soakRepairRestartPolicy} and
        .sync_repair_control_timeout_ms == ${toString syncRepairControlTimeoutMs} and
        .soak_stalled_restart_after_ms == ${toString (soakStalledRestartAfter * 1000)} and
        .soak_stalled_cycle_recoveries >= 0 and
        (.soak_stalled_cycle_recovery_events | length) == .soak_stalled_cycle_recoveries and
        .soak_cycles >= ${toString effectiveSoakMinimumCycles} and
        .soak_elapsed_ms >= ${toString (soakSeconds * 1000)} and
        .soak_daemon_restarts >= 0 and
        .soak_restart_settle_passes >= 0 and
        (.soak_restart_settle_cycles | length) == .soak_restart_settle_passes and
        (if .soak_restart_settle_policy == "repair-before-edit" then .soak_restart_settle_passes == .soak_daemon_restarts else .soak_restart_settle_passes == 0 end) and
        .soak_restart_skipped_final_boundary >= 0 and
        (.soak_restart_skipped_cycles | length) == .soak_restart_skipped_final_boundary and
        .soak_repair_passes >= 0 and
        .soak_repair_deferrals >= 0 and
        (.soak_repair_deferred_cycles | length) == .soak_repair_deferrals and
        (if .soak_repair_restart_policy == "defer" then .soak_repair_passes >= .soak_repair_deferrals else true end) and
        .soak_repair_pending == false and
        .soak_delete_cycles >= 0 and
        (.soak_final_sha256 | test("^[0-9a-f]{64}$")) and
        (.soak_agent_high_water_kib | length) == 3 and
        ([.soak_agent_high_water_kib[] | select(. <= 0)] | length) == 0 and
        .soak_contains_secrets == false and
  '' else ''
        .soak_campaign == false and
  '';
  maintenanceAssertions = if maintenanceLifecycle then ''
        .maintenance_lifecycle == true and
        .checkpoint_peer_copies == 2 and
        .gc_candidates > 0 and
        .gc_quarantined == .gc_candidates and
        .gc_restored == .gc_quarantined and
        .pin_unpin_observed == true and
        .cutoff_survivors == 2 and
        .post_cutoff_branch_count == [2, 2] and
        .post_cutoff_source_principals == [1, 1] and
        .retired_writer_reentry_refused == true and
  '' else ''
        .maintenance_lifecycle == false and
  '';
  followupAssertions = if runFollowups then ''
        .recovery_rehearsal == true and
        .recovery_model == "same-vm-independent-backup-not-assessed" and
        .recovery_backup_independence == "not-assessed" and
        .recovery_restore_provenance == "not-assessed" and
        .recovery_operator_provenance == "present" and
        .recovery_operator_provenance_bound == true and
        .recovery_restore_reports_with_provenance == 4 and
        (.recovery_root_devices_differ | length) == 4 and
        (.recovery_backup_system_sha256 | test("^[0-9a-f]{64}$")) and
        (.recovery_backup_generation_sha256 | test("^[0-9a-f]{64}$")) and
        (.recovery_backup_failure_domain_sha256 | test("^[0-9a-f]{64}$")) and
        (.recovery_restore_provenance_sha256 | test("^[0-9a-f]{64}$")) and
        .recovery_files == 33 and
        .recovery_directories == 1 and
        .recovery_bytes == 131099 and
        (.recovery_tree_sha256 | test("^[0-9a-f]{64}$")) and
        .recovery_verifier_matches == 4 and
        (.recovery_verifier_report_sha256 | length) == 4 and
        .recovery_one_node_empty_replacement == true and
        .recovery_one_node_capability_revocations == 2 and
        .recovery_one_node_writer_cutoffs == 2 and
        .recovery_one_node_transport_peer_removals == 2 and
        .recovery_one_node_post_cutoff_checkpoints == 2 and
        .recovery_one_node_survivor_restarts == 2 and
        .recovery_one_node_branch_count == [3, 3, 3] and
        .recovery_all_live_nodes_lost == true and
        .recovery_replacement_nodes == 3 and
        .recovery_replacement_branch_count == [3, 3, 3] and
        .recovery_obsolete_principals_absent == true and
        (.recovery_obsolete_principal_sha256 | length) == 4 and
        (.recovery_replacement_principal_sha256 | length) == 3 and
        .recovery_repair_verified_nodes == 6 and
        .recovery_contains_secrets == false and
        .storage_fault_schema == "iotox.sync-storage-fault.v1" and
        .storage_fault_rehearsal == true and
        .storage_fault_status == "passed" and
        .storage_fault_node_count == 3 and
        .storage_fault_filesystem == "ext4-loop" and
        .storage_fault_disk_mib_per_node == 192 and
        .enospc_live_observed == true and
        .enospc_filler_bytes > 0 and
        .enospc_abrupt_exit != 0 and
        .read_only_start_refused == true and
        .read_only_exit != 0 and
        (.read_only_log_sha256 | test("^[0-9a-f]{64}$")) and
        (.abrupt_exchange_observed == "projection-stage" or
         .abrupt_exchange_observed == "pending-workspace") and
        .abrupt_exchange_bytes == 33554432 and
        .abrupt_exchange_exit != 0 and
        .storage_fault_final_files == 19 and
        .storage_fault_final_directories == 1 and
        .storage_fault_final_bytes == 33620017 and
        (.storage_fault_final_tree_sha256 | test("^[0-9a-f]{64}$")) and
        .storage_fault_repair_verified_nodes == 3 and
        .storage_fault_elapsed_ms > 0 and
        .storage_fault_contains_secrets == false and
        .storage_fault_power_cut == false and
        .storage_fault_dishonest_storage_assessed == false and
  '' else "";
in {
  sandwurm.directCloudHypervisorGuest = {
    inherit hostName taskId profile reviewHint;
    authorityMode = "bounded";
    networkClass = "none";
    workspaceGrant = "shared";
    stateGrant = "task-private";
  };

  # The default repart layout gives its only root partition the exact image
  # floor. Keep explicit filesystem and trailing-copy/GPT headroom. This is an
  # ephemeral qualification image, not a deployment-size claim.
  image.repart.partitions."10-root".repartConfig.SizeMinBytes =
    lib.mkForce "24G";
  image.repart.partitions."10-root".repartConfig.PaddingMinBytes =
    lib.mkForce "1G";

  environment.systemPackages = [
    iotox
    toxBootstrap
    sandwurmPackage
    pkgs.python3
    pkgs.e2fsprogs
    pkgs.util-linux
  ];

  systemd.services.sandwurm-guest-receipts = {
    requires = [ "iotox-three-writer.service" ];
    after = [ "iotox-three-writer.service" ];
  };

  systemd.services.iotox-three-writer = {
    description = "Qualify three full-mesh IoTox writers";
    wantedBy = [ "multi-user.target" ];
    requires = [ "workspace.mount" ];
    after = [ "local-fs.target" "workspace.mount" ];
    before = [ "sandwurm-guest-receipts.service" ];
    unitConfig.ConditionPathIsMountPoint = "/workspace";
    path = [
      pkgs.coreutils pkgs.e2fsprogs pkgs.jq pkgs.python3 pkgs.systemd
      pkgs.util-linux
    ];
    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
      StateDirectory = "iotox-three-writer";
      StateDirectoryMode = "0700";
      StandardOutput = "journal+console";
      StandardError = "journal+console";
    };
    script = ''
      set -euo pipefail
      umask 0077
      receipt_dir=/workspace/guest-receipts/iotox
      install -d -m 0700 "$receipt_dir"

      three_writer_args=(
        --iotox ${iotox}/bin/iotox
        --bootstrap ${toxBootstrap}/bin/DHT_bootstrap
        --state-root /var/lib/iotox-three-writer
        --evidence "$receipt_dir/sync-three-writer.json"
        --fresh-state
        --capacity-files ${toString capacityFiles}
        --capacity-file-bytes ${toString capacityFileBytes}
        --shadow-cycles ${toString shadowCycles}
        --stalled-cycle-restart-after 30
        --max-sync-tree-lanes ${toString maxSyncTreeLanes}
        --namespace-maximum-lanes ${toString namespaceMaxSyncTreeLanes}
        --sync-repair-control-timeout-ms ${toString syncRepairControlTimeoutMs}
        --timeout ${toString timeoutSeconds}
      )
      ${lib.optionalString (soakSeconds > 0 || effectiveSoakMinimumCycles > 0) ''
      three_writer_args+=(
        --soak-seconds ${toString soakSeconds}
        --soak-minimum-cycles ${toString effectiveSoakMinimumCycles}
        --soak-cycle-delay ${toString soakCycleDelaySeconds}
        --soak-restart-every ${toString soakRestartEvery}
        --soak-restart-settle-policy ${soakRestartSettlePolicy}
        --soak-final-boundary-restart-policy ${soakFinalBoundaryRestartPolicy}
        --soak-repair-every ${toString soakRepairEvery}
        --soak-repair-restart-policy ${soakRepairRestartPolicy}
        --soak-stalled-restart-after ${toString soakStalledRestartAfter}
      )
      ''}
      ${lib.optionalString maintenanceLifecycle ''
      three_writer_args+=(--maintenance-lifecycle)
      ''}
      python3 ${../tools/run-sync-three-writer.py} "''${three_writer_args[@]}"

      ${lib.optionalString runFollowups ''
      recovery_receipt="$receipt_dir/sync-recovery-rehearsal.json"
      python3 ${../tools/run-sync-recovery-rehearsal.py} \
        --iotox ${iotox}/bin/iotox \
        --bootstrap ${toxBootstrap}/bin/DHT_bootstrap \
        --three-writer-helper ${../tools/run-sync-three-writer.py} \
        --state-root /var/lib/iotox-sync-recovery \
        --evidence "$recovery_receipt" \
        --backup-system iotox-sandwurm-drill-copy \
        --backup-generation three-writer-recovery-${expectedRevision} \
        --backup-failure-domain same-vm-synthetic-copy \
        --restore-provenance run-sync-recovery-rehearsal \
        --files 32 \
        --file-bytes 4096
      storage_fault_receipt="$receipt_dir/sync-storage-fault.json"
      python3 ${../tools/run-sync-storage-fault-rehearsal.py} \
        --iotox ${iotox}/bin/iotox \
        --bootstrap ${toxBootstrap}/bin/DHT_bootstrap \
        --three-writer-helper ${../tools/run-sync-three-writer.py} \
        --recovery-helper ${../tools/run-sync-recovery-rehearsal.py} \
        --state-root /var/lib/iotox-sync-storage-fault \
        --evidence "$storage_fault_receipt" \
        --disk-mib 192 \
        --exchange-bytes 33554432
      jq -s '.[0] * .[1] * .[2]' \
        "$receipt_dir/sync-three-writer.json" "$recovery_receipt" \
        "$storage_fault_receipt" \
        >"$receipt_dir/sync-three-writer.json.tmp"
      mv "$receipt_dir/sync-three-writer.json.tmp" \
        "$receipt_dir/sync-three-writer.json"
      ''}

      jq -e '
        .schema == "iotox.sync-three-writer.v1" and
        .status == "passed" and
        .node_count == 3 and
        .friendship_edge_count == 3 and
        .directed_read_write_share_count == 6 and
        .source_principals_per_node == 2 and
        .branch_count_per_node == [3, 3, 3] and
        .conflict_alternatives_per_node == [2, 2, 2] and
        .three_way_conflict_observed == true and
        .explicit_resolution_observed == true and
        .automation_record_format == 2 and
        .automation_record_bytes == 4808 and
        .tree_lane_cap == ${toString effectiveSyncTreeLanes} and
        .tree_lane_process_cap == ${toString maxSyncTreeLanes} and
        .tree_lane_namespace_cap == ${toString namespaceMaxSyncTreeLanes} and
        .shadow_cycles == ${toString shadowCycles} and
        (.stalled_cycle_restarts | type) == "number" and
        (.stalled_cycle_restart_events | type) == "array" and
        (.stalled_cycle_restart_events | length) == .stalled_cycle_restarts and
${soakAssertions}
        .capacity_campaign == true and
        .capacity_files == ${toString capacityFiles} and
        .capacity_file_bytes == ${toString capacityFileBytes} and
        .capacity_logical_bytes == ${toString capacityLogicalBytes} and
        (.capacity_digest | test("^[0-9a-f]{64}$")) and
        (.capacity_catchup_ms | type) == "number" and
        .capacity_catchup_ms > 0 and
        (.capacity_repair_ms_per_node | length) == 3 and
        (.capacity_agent_high_water_kib | length) == 3 and
        ([.capacity_agent_high_water_kib[] | select(. <= 0)] | length) == 0 and
        (.capacity_allocated_delta_bytes_per_node | length) == 3 and
        ([.capacity_allocated_delta_bytes_per_node[] | select(. <= 0)] | length) == 0 and
${maintenanceAssertions}${followupAssertions}
        .contains_secrets == false
      ' "$receipt_dir/sync-three-writer.json" >/dev/null

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
