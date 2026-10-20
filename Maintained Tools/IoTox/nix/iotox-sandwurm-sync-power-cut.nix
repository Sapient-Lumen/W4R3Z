{ config, lib, pkgs, iotox, toxBootstrap, sandwurmPackage,
  sourceRevision, powerCutBoundary ? "pre-exchange-pending", ... }:
let
  expectedVersion = "0.51.0";
  expectedRevision =
    lib.strings.removeSuffix "\n" (builtins.readFile ../REVISION);
  objectCut = builtins.elem powerCutBoundary [
    "receive-staging-partial"
    "cas-install-temporary"
  ];
  prePublicationCut = builtins.elem powerCutBoundary [
    "manifest-install-temporary"
    "branch-record-install-temporary"
    "branch-pointer-update-temporary"
  ];
  postPublicationCut = builtins.elem powerCutBoundary [
    "manifest-install-directory-fsync"
    "branch-record-install-directory-fsync"
    "branch-pointer-update-directory-fsync"
  ];
  publicationCut = prePublicationCut || postPublicationCut;
  workspaceCut = ! objectCut && ! publicationCut;
  powerCutSuffix =
    if powerCutBoundary == "pre-exchange-pending" then "pre"
    else if powerCutBoundary == "post-exchange-pending" then "post"
    else if powerCutBoundary == "receive-staging-partial" then "receive"
    else if powerCutBoundary == "cas-install-temporary" then "cas"
    else if powerCutBoundary == "manifest-install-temporary" then "manifest"
    else if powerCutBoundary == "branch-record-install-temporary" then "record"
    else if powerCutBoundary == "branch-pointer-update-temporary" then "pointer"
    else if powerCutBoundary == "manifest-install-directory-fsync" then "manifest-dir-fsync"
    else if powerCutBoundary == "branch-record-install-directory-fsync" then "record-dir-fsync"
    else "pointer-dir-fsync";
  receiptSchema =
    if postPublicationCut then "iotox.sync-power-cut.v6"
    else if prePublicationCut then "iotox.sync-power-cut.v5"
    else if objectCut then "iotox.sync-power-cut.v4"
    else "iotox.sync-power-cut.v3";
  powerCutTransition =
    if publicationCut then "branch-publication"
    else if objectCut then "object-pipeline"
    else "workspace-exchange";
  publicationPrefixAssertion =
    if powerCutBoundary == "manifest-install-temporary" then
      ''(.publication_before_restart.manifest_state == "absent" and
         .publication_before_restart.branch_record_state == "absent" and
         .publication_before_restart.branch_pointer_state == "prior")''
    else if powerCutBoundary == "branch-record-install-temporary" then
      ''(.publication_before_restart.manifest_state == "exact" and
         .publication_before_restart.branch_record_state == "absent" and
         .publication_before_restart.branch_pointer_state == "prior")''
    else if powerCutBoundary == "branch-pointer-update-temporary" then
      ''(.publication_before_restart.manifest_state == "exact" and
         .publication_before_restart.branch_record_state == "exact" and
         .publication_before_restart.branch_pointer_state == "prior")''
    else if powerCutBoundary == "manifest-install-directory-fsync" then
      ''((.publication_before_restart.manifest_state == "absent" or
          .publication_before_restart.manifest_state == "exact") and
         .publication_before_restart.branch_record_state == "absent" and
         .publication_before_restart.branch_pointer_state == "prior")''
    else if powerCutBoundary == "branch-record-install-directory-fsync" then
      ''(.publication_before_restart.manifest_state == "exact" and
         (.publication_before_restart.branch_record_state == "absent" or
          .publication_before_restart.branch_record_state == "exact") and
         .publication_before_restart.branch_pointer_state == "prior")''
    else
      ''(.publication_before_restart.manifest_state == "exact" and
         .publication_before_restart.branch_record_state == "exact" and
         (.publication_before_restart.branch_pointer_state == "prior" or
          .publication_before_restart.branch_pointer_state == "successor"))'';
  publicationTemporary =
    if builtins.elem powerCutBoundary [
      "manifest-install-temporary"
      "manifest-install-directory-fsync"
    ] then "manifest"
    else if builtins.elem powerCutBoundary [
      "branch-record-install-temporary"
      "branch-record-install-directory-fsync"
    ] then "branch_record"
    else "branch_pointer";
  publicationSchedulerFence =
    if postPublicationCut then "strace-path-filtered-fsync-delay-enter+sigstop"
    else "strace-path-filtered-delay-enter+sigstop";
in {
  assertions = [{
    assertion = builtins.elem powerCutBoundary [
      "pre-exchange-pending"
      "post-exchange-pending"
      "receive-staging-partial"
      "cas-install-temporary"
      "manifest-install-temporary"
      "branch-record-install-temporary"
      "branch-pointer-update-temporary"
      "manifest-install-directory-fsync"
      "branch-record-install-directory-fsync"
      "branch-pointer-update-directory-fsync"
    ];
    message = "IoTox sync power-cut boundary is unsupported";
  }];

  sandwurm.directCloudHypervisorGuest = {
    hostName = "iotox-sync-power-cut-${powerCutSuffix}";
    taskId = "iotox-sync-power-cut-${powerCutSuffix}-qualification";
    authorityMode = "bounded";
    networkClass = "none";
    workspaceGrant = "shared";
    stateGrant = "task-private";
    profile = "iotox-sync-power-cut-${powerCutSuffix}-no-network-qualification";
    reviewHint =
      "One source-linked three-writer tree-v2 transition recovered after host SIGKILL of Cloud Hypervisor and a second boot of the exact crash image";
  };

  image.repart.partitions."10-root".repartConfig.SizeMinBytes =
    lib.mkForce "24G";
  image.repart.partitions."10-root".repartConfig.PaddingMinBytes =
    lib.mkForce "1G";

  environment.systemPackages = [
    iotox
    toxBootstrap
    sandwurmPackage
    pkgs.python3
    pkgs.strace
    pkgs.e2fsprogs
    pkgs.jq
    pkgs.util-linux
  ];

  systemd.services.sandwurm-guest-receipts = {
    requires = [ "iotox-sync-power-cut.service" ];
    after = [ "iotox-sync-power-cut.service" ];
  };

  systemd.services.iotox-sync-power-cut = {
    description = "Arm or recover the IoTox whole-VMM synchronization cut gate";
    wantedBy = [ "multi-user.target" ];
    requires = [ "workspace.mount" ];
    after = [ "local-fs.target" "workspace.mount" ];
    before = [ "sandwurm-guest-receipts.service" ];
    unitConfig.ConditionPathIsMountPoint = "/workspace";
    path = [
      pkgs.coreutils
      pkgs.e2fsprogs
      pkgs.jq
      pkgs.python3
      pkgs.systemd
      pkgs.util-linux
    ];
    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
      StandardOutput = "journal+console";
      StandardError = "journal+console";
    };
    script = ''
      set -euo pipefail
      umask 0077
      receipt_dir=/workspace/guest-receipts/iotox
      install -d -m 0700 "$receipt_dir" /workspace/power-cut

      python3 ${../tools/run-sync-power-cut-rehearsal.py} \
        --iotox ${iotox}/bin/iotox \
        --bootstrap ${toxBootstrap}/bin/DHT_bootstrap \
        --strace ${pkgs.strace}/bin/strace \
        --three-writer-helper ${../tools/run-sync-three-writer.py} \
        --recovery-helper ${../tools/run-sync-recovery-rehearsal.py} \
        --storage-fault-helper ${../tools/run-sync-storage-fault-rehearsal.py} \
        --state-root /var/lib/iotox-sync-power-cut \
        --evidence "$receipt_dir/sync-power-cut.json" \
        --arm-receipt /workspace/power-cut/armed.json \
        --disk-mib 192 \
        --files 16 \
        --file-bytes 4096 \
        --exchange-bytes 33554432 \
        --cut-boundary ${lib.escapeShellArg powerCutBoundary} \
        --timeout 300

      jq -e '
        .schema == ${builtins.toJSON receiptSchema} and
        .status == "passed" and
        .power_cut_recovery == true and
        .power_cut_model == "host-sigkill-cloud-hypervisor-preseeded-crash-image" and
        .power_cut_transition == ${builtins.toJSON powerCutTransition} and
        .cut_boundary_requested == ${builtins.toJSON powerCutBoundary} and
        (.first_boot_id_sha256 | test("^[0-9a-f]{64}$")) and
        (.recovery_boot_id_sha256 | test("^[0-9a-f]{64}$")) and
        .first_boot_id_sha256 != .recovery_boot_id_sha256 and
        .distinct_boot_observed == true and
        (.initial_view_per_node == ["completed", "completed", "prior"] or
         .initial_view_per_node == ["completed", "completed", "completed"]) and
        (${builtins.toJSON powerCutBoundary} != "post-exchange-pending" or
         .initial_view_per_node == ["completed", "completed", "completed"]) and
        (${builtins.toJSON workspaceCut} or
         .initial_view_per_node == ["completed", "completed", "prior"]) and
        .initial_prior_or_completed_only == true and
        (.follower_projection_stage_present_before_restart | type) == "boolean" and
        (${builtins.toJSON workspaceCut} or
         .follower_projection_stage_present_before_restart == false) and
        (.follower_workspace_state_before_restart == "pending" or
         .follower_workspace_state_before_restart == "stable") and
        ((.follower_workspace_state_before_restart == "pending" and
          .follower_workspace_phase_raw_before_restart == 2) or
         (.follower_workspace_state_before_restart == "stable" and
          .follower_workspace_phase_raw_before_restart == 1)) and
        ((.follower_workspace_state_before_restart == "pending" and
          (.follower_projection_orientation_before_restart == "active" or
           .follower_projection_orientation_before_restart == "pending") and
          (${builtins.toJSON powerCutBoundary} != "post-exchange-pending" or
           .follower_projection_orientation_before_restart == "pending")) or
         (.follower_workspace_state_before_restart == "stable" and
          .follower_projection_orientation_before_restart == "active")) and
        (${builtins.toJSON (! objectCut)} or
         (.follower_workspace_state_before_restart == "stable" and
          .follower_workspace_phase_raw_before_restart == 1 and
          .follower_projection_orientation_before_restart == "active" and
          (.expected_object_sha256 | test("^[0-9a-f]{64}$")) and
          .expected_object_bytes == 33554432 and
          .agent_sigstop_at_arm == true and
          (.object_pipeline_before_restart.expected_object_state == "absent" or
           .object_pipeline_before_restart.expected_object_state == "exact") and
          .object_pipeline_before_restart.incoming_temporary_count >= 0 and
          .object_pipeline_before_restart.incoming_temporary_count <= 4 and
          .object_pipeline_before_restart.cas_install_temporary_count >= 0 and
          .object_pipeline_before_restart.cas_install_temporary_count <= 1 and
          .object_pipeline_after_recovery == {
            incoming_temporary_count: 0,
            incoming_temporary_bytes: 0,
            cas_install_temporary_count: 0,
            cas_install_temporary_bytes: 0,
            expected_object_state: "exact"
          })) and
        (${builtins.toJSON (! publicationCut)} or
         (.follower_workspace_state_before_restart == "stable" and
          .follower_workspace_phase_raw_before_restart == 1 and
          .follower_projection_orientation_before_restart == "active" and
          .agent_sigstop_at_arm == true and
          (.marker_sha256 | test("^[0-9a-f]{64}$")) and
          (.publication_target_commitments | keys == ["branch_pointer", "branch_record", "manifest"]) and
          ([.publication_target_commitments.manifest,
            .publication_target_commitments.branch_record] | all(
              (keys == ["bytes", "name_sha256", "sha256"]) and
              (.bytes > 0 and .bytes <= 4194304) and
              (.name_sha256 | test("^[0-9a-f]{64}$")) and
              (.sha256 | test("^[0-9a-f]{64}$")))) and
          (.publication_target_commitments.branch_pointer |
            (keys == ["bytes", "name_sha256", "prior_bytes", "prior_sha256", "sha256"]) and
            (.bytes > 0 and .bytes <= 4194304) and
            (.prior_bytes > 0 and .prior_bytes <= 4194304) and
            (.name_sha256 | test("^[0-9a-f]{64}$")) and
            (.sha256 | test("^[0-9a-f]{64}$")) and
            (.prior_sha256 | test("^[0-9a-f]{64}$")) and
            .sha256 != .prior_sha256) and
          .publication_target_commitments.branch_record.bytes ==
            .publication_target_commitments.branch_pointer.bytes and
          .publication_target_commitments.branch_record.sha256 ==
            .publication_target_commitments.branch_pointer.sha256 and
          .qualification_scheduler_fence == ${builtins.toJSON publicationSchedulerFence} and
          ${publicationPrefixAssertion} and
          ((.publication_before_restart.${publicationTemporary}_temporary_count == 0 and
            .publication_before_restart.${publicationTemporary}_temporary_bytes == 0) or
           (.publication_before_restart.${publicationTemporary}_temporary_count == 1 and
            .publication_before_restart.${publicationTemporary}_temporary_bytes ==
              .publication_target_commitments.${publicationTemporary}.bytes)) and
          ${lib.concatStringsSep " and\n          " (map (name:
            if name == publicationTemporary then "true"
            else "(.publication_before_restart.${name}_temporary_count == 0 and .publication_before_restart.${name}_temporary_bytes == 0)"
          ) [ "manifest" "branch_record" "branch_pointer" ])} and
          .publication_after_recovery == {
            manifest_state: "exact",
            branch_record_state: "exact",
            branch_pointer_state: "successor",
            manifest_temporary_count: 0,
            manifest_temporary_bytes: 0,
            branch_record_temporary_count: 0,
            branch_record_temporary_bytes: 0,
            branch_pointer_temporary_count: 0,
            branch_pointer_temporary_bytes: 0
          })) and
        .identity_preserved == true and
        .branch_count_per_node == [3, 3, 3] and
        .repair_verified_nodes == 3 and
        (.final.digest | test("^[0-9a-f]{64}$")) and
        .final.files == 18 and
        .final.directories == 1 and
        .final.bytes == 33619995 and
        .elapsed_ms > 0 and
        .contains_secrets == false and
        .dishonest_storage_assessed == false
      ' "$receipt_dir/sync-power-cut.json" >/dev/null

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
          contains_secrets: false
        }' >"$receipt_dir/vm-smoke.json"
    '';
  };
}
