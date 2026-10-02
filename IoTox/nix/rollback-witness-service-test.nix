{ pkgs, iotoxSourceLinked }:

pkgs.testers.runNixOSTest {
  name = "iotox-rollback-witness-service";
  globalTimeout = 15 * 60;

  nodes = {
    witness = { ... }: {
      networking.firewall.allowedTCPPorts = [ 37177 ];
      virtualisation.memorySize = 1024;
    };
    agent = { ... }: {
      virtualisation.memorySize = 1536;
      users.users.operator = {
        isNormalUser = true;
        uid = 1000;
        extraGroups = [ ];
      };
    };
  };

  testScript = ''
    start_all()
    witness.wait_for_unit("multi-user.target")
    agent.wait_for_unit("multi-user.target")

    witness.succeed("mkdir -p /var/lib/iotox-witness && chmod 0700 /var/lib/iotox-witness")
    key_output = witness.succeed("${iotoxSourceLinked}/bin/iotox witness-service-keygen /var/lib/iotox-witness/service.identity")
    assert "role=witness created=1" in key_output
    server_key = key_output.split("public-key=")[1].split()[0]
    assert len(server_key) == 64

    agent.succeed("mkdir -p /var/lib/iotox && chmod 0700 /var/lib/iotox")
    base = "--state /var/lib/iotox/device.toxsave --identity /var/lib/iotox/device.identity --authority-ledger /var/lib/iotox/authority.ledger --no-default-bootstrap --no-default-relays"
    agent.succeed(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-init --run-ms 100")
    agent.succeed("test -s /var/lib/iotox/device.identity && test ! -e /var/lib/iotox/authority.ledger && test ! -e /var/lib/iotox/authority.ledger.guard")
    agent.succeed("mkdir -p /var/lib/iotox/sync-policy/namespaces /var/lib/iotox/update-sync /var/lib/iotox/notes-sync /var/lib/iotox/update /var/lib/iotox/tree-source && chmod 0700 /var/lib/iotox/sync-policy /var/lib/iotox/sync-policy/namespaces /var/lib/iotox/update-sync /var/lib/iotox/notes-sync /var/lib/iotox/update /var/lib/iotox/tree-source && printf 'enrolled notes revision one\\n' >/var/lib/iotox/notes-source && chmod 0600 /var/lib/iotox/notes-source && printf 'tree revision one\\n' >/var/lib/iotox/tree-source/field.txt && chmod 0600 /var/lib/iotox/tree-source/field.txt")
    agent.succeed(f"systemd-run --unit=iotox-policy-seed --service-type=simple ${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-policy-seed --enable-sync --sync-policy-root /var/lib/iotox/sync-policy")
    agent.wait_for_file("/run/iotox-policy-seed/control.sock")
    identity_output = agent.succeed("${iotoxSourceLinked}/bin/iotox --runtime /run/iotox-policy-seed identity")
    device_key = identity_output.split("device-public-key=")[1].split()[0]
    assert len(device_key) == 64
    agent.succeed(f"${iotoxSourceLinked}/bin/iotox sync-namespace-template updates /var/lib/iotox/update-sync {device_key} >/tmp/updates.namespace")
    seeded = agent.succeed("${iotoxSourceLinked}/bin/iotox --runtime /run/iotox-policy-seed sync-namespace-install /tmp/updates.namespace")
    assert "namespace=updates" in seeded
    agent.succeed(f"${iotoxSourceLinked}/bin/iotox sync-namespace-template notes /var/lib/iotox/notes-sync {device_key} >/tmp/notes.namespace")
    notes_seeded = agent.succeed("${iotoxSourceLinked}/bin/iotox --runtime /run/iotox-policy-seed sync-namespace-install /tmp/notes.namespace")
    assert "namespace=notes" in notes_seeded
    tree_seeded = agent.succeed("${iotoxSourceLinked}/bin/iotox --runtime /run/iotox-policy-seed sync-create tree-notes /var/lib/iotox/tree-source read-write 86400")
    assert "namespace=tree-notes" in tree_seeded
    assert "engine=tree-v2" in tree_seeded
    agent.succeed("${iotoxSourceLinked}/bin/iotox --runtime /run/iotox-policy-seed stop")
    agent.wait_until_succeeds("! systemctl is-active --quiet iotox-policy-seed.service")
    release_output = agent.succeed("${iotoxSourceLinked}/bin/iotox update-signer-keygen /var/lib/iotox/update-release.identity")
    release_key = release_output.split("public-key=")[1].split()[0]
    assert len(release_key) == 64
    agent.succeed(f"${iotoxSourceLinked}/bin/iotox update-policy-template updates iotox-witness-x86_64 /var/lib/iotox/update {release_key} >/var/lib/iotox/update.policy && chmod 0600 /var/lib/iotox/update.policy")
    principal = "11" * 32
    agent.succeed("mkdir -p /var/lib/iotox/ratox-profiles/profiles /var/lib/iotox/ratox-profiles/bindings && chmod 0700 /var/lib/iotox/ratox-profiles /var/lib/iotox/ratox-profiles/profiles /var/lib/iotox/ratox-profiles/bindings")
    agent.succeed("install -d -m 0755 /opt/iotox-test && install -m 0555 ${iotoxSourceLinked}/bin/iotox /opt/iotox-test/iotox-helper && install -m 0555 ${pkgs.bash}/bin/bash /opt/iotox-test/ratox-bash")
    agent.succeed("${iotoxSourceLinked}/bin/iotox --shell /opt/iotox-test/ratox-bash --allow-sudo terminal-profile-shell-template witness-shell operator > /tmp/witness-shell.profile")
    agent.succeed("sed -i 's/^enabled=0$/enabled=1/' /tmp/witness-shell.profile")
    agent.succeed("${iotoxSourceLinked}/bin/iotox terminal-profile-lint /tmp/witness-shell.profile")
    agent.succeed("${iotoxSourceLinked}/bin/iotox --ratox-profile-store /var/lib/iotox/ratox-profiles terminal-profile-install /tmp/witness-shell.profile")
    agent.succeed(f"${iotoxSourceLinked}/bin/iotox --ratox-profile-store /var/lib/iotox/ratox-profiles terminal-profile-bind {principal} witness-shell")

    domain = agent.succeed("${iotoxSourceLinked}/bin/iotox witness-domain-generate").strip()
    assert len(domain) == 32
    enrollment = agent.succeed(f"${iotoxSourceLinked}/bin/iotox witness-authority-enrollment /var/lib/iotox/device.identity /var/lib/iotox/authority.ledger {domain} 1").strip()
    assert len(enrollment) == 352
    enrolled = witness.succeed(f"${iotoxSourceLinked}/bin/iotox witness-service-enroll /var/lib/iotox-witness /var/lib/iotox-witness/service.identity {enrollment}")
    assert "lane=authority position=0 enrolled=1" in enrolled
    application_state = "/var/lib/iotox/.iotox-incarnations/device.toxsave.protocol-incarnation"
    application_enrollment = agent.succeed(f"${iotoxSourceLinked}/bin/iotox witness-incarnation-enrollment /var/lib/iotox/device.identity {application_state} application {domain} 1").strip()
    assert len(application_enrollment) == 352
    application_enrolled = witness.succeed(f"${iotoxSourceLinked}/bin/iotox witness-service-enroll /var/lib/iotox-witness /var/lib/iotox-witness/service.identity {application_enrollment}")
    assert "lane=application-incarnation" in application_enrolled
    assert "enrolled=1" in application_enrolled
    ratox_state = "/var/lib/iotox/ratox/incarnation.state"
    ratox_enrollment = agent.succeed(f"${iotoxSourceLinked}/bin/iotox witness-incarnation-enrollment /var/lib/iotox/device.identity {ratox_state} ratox {domain} 1").strip()
    assert len(ratox_enrollment) == 352
    ratox_enrolled = witness.succeed(f"${iotoxSourceLinked}/bin/iotox witness-service-enroll /var/lib/iotox-witness /var/lib/iotox-witness/service.identity {ratox_enrollment}")
    assert "lane=ratox-incarnation" in ratox_enrolled
    assert "enrolled=1" in ratox_enrolled
    route_set = "/var/lib/iotox/routes.signed"
    route_generation = "/var/lib/iotox/routes.generation"
    primary_route_key = agent.succeed("head -c 64 /run/iotox-init/self/address").strip()
    assert len(primary_route_key) == 64
    bulk_route_key = "22" * 32
    agent.succeed(f"${iotoxSourceLinked}/bin/iotox --identity /var/lib/iotox/device.identity route-set-create {route_set} 1 {primary_route_key} {primary_route_key}:protected:either:1:0:0 {bulk_route_key}:bulk:either:2:0:0")
    route_enrollment = agent.succeed(f"${iotoxSourceLinked}/bin/iotox witness-route-enrollment /var/lib/iotox/device.identity {route_set} {route_generation} {domain} 1").strip()
    assert len(route_enrollment) == 352
    route_enrolled = witness.succeed(f"${iotoxSourceLinked}/bin/iotox witness-service-enroll /var/lib/iotox-witness /var/lib/iotox-witness/service.identity {route_enrollment}")
    assert "lane=route-generation" in route_enrolled
    assert "position=1" in route_enrolled
    assert "enrolled=1" in route_enrolled

    remote = f"--authority-witness-host witness --authority-witness-port 37177 --authority-witness-server-key {server_key} --authority-witness-domain {domain} --authority-witness-epoch 1 --authority-witness-intent /var/lib/iotox/authority.witness-intent --witness-application-incarnation --application-incarnation-witness-intent /var/lib/iotox/.iotox-incarnations/application.witness-intent --witness-ratox-incarnation --ratox-incarnation-witness-intent /var/lib/iotox/ratox/ratox.witness-intent --witness-route-generation --route-witness-intent /var/lib/iotox/route.witness-intent --route-set {route_set} --route-generation-state {route_generation} --witness-terminal-policy --terminal-policy-witness-checkpoint /var/lib/iotox/terminal-policy.checkpoint --terminal-policy-witness-intent /var/lib/iotox/terminal-policy.intent --witness-command-effects --command-effect-witness-checkpoint /var/lib/iotox/command-effect.checkpoint --command-effect-witness-intent /var/lib/iotox/command-effect.intent --witness-sync-policy --sync-policy-witness-checkpoint /var/lib/iotox/sync-policy.checkpoint --sync-policy-witness-intent /var/lib/iotox/sync-policy.intent --witness-update-lifecycle --update-lifecycle-witness-intent /var/lib/iotox/update-lifecycle.intent --witness-sync-guarded-state --enable-sync --sync-policy-root /var/lib/iotox/sync-policy --enable-signed-updates --update-policy /var/lib/iotox/update.policy --enable-ratox-terminal --ratox-profile-store /var/lib/iotox/ratox-profiles --ratox-incarnation-state /var/lib/iotox/ratox/incarnation.state --ratox-helper /opt/iotox-test/iotox-helper --ratox-profile-owner-uid 0"
    terminal_enrollment = agent.succeed(f"${iotoxSourceLinked}/bin/iotox witness-terminal-policy-enrollment {base} {remote}").strip()
    assert len(terminal_enrollment) == 352
    terminal_enrolled = witness.succeed(f"${iotoxSourceLinked}/bin/iotox witness-service-enroll /var/lib/iotox-witness /var/lib/iotox-witness/service.identity {terminal_enrollment}")
    assert "lane=terminal-policy" in terminal_enrolled
    assert "position=1" in terminal_enrolled
    assert "enrolled=1" in terminal_enrolled

    effect_enrollment = agent.succeed(f"${iotoxSourceLinked}/bin/iotox witness-command-effects-enrollment {base} {remote}").strip()
    assert len(effect_enrollment) == 352
    effect_enrolled = witness.succeed(f"${iotoxSourceLinked}/bin/iotox witness-service-enroll /var/lib/iotox-witness /var/lib/iotox-witness/service.identity {effect_enrollment}")
    assert "lane=command-effect" in effect_enrolled
    assert "position=1" in effect_enrolled
    assert "enrolled=1" in effect_enrolled

    sync_enrollment = agent.succeed(f"${iotoxSourceLinked}/bin/iotox witness-sync-policy-enrollment {base} {remote}").strip()
    assert len(sync_enrollment) == 352
    sync_enrolled = witness.succeed(f"${iotoxSourceLinked}/bin/iotox witness-service-enroll /var/lib/iotox-witness /var/lib/iotox-witness/service.identity {sync_enrollment}")
    assert "lane=sync-policy" in sync_enrolled
    assert "position=1" in sync_enrolled
    assert "enrolled=1" in sync_enrolled

    update_enrollment = agent.succeed(f"${iotoxSourceLinked}/bin/iotox witness-update-enrollment {base} {remote}").strip()
    assert len(update_enrollment) == 352
    update_enrolled = witness.succeed(f"${iotoxSourceLinked}/bin/iotox witness-service-enroll /var/lib/iotox-witness /var/lib/iotox-witness/service.identity {update_enrollment}")
    assert "lane=update-lifecycle" in update_enrolled
    assert "position=1" in update_enrolled
    assert "enrolled=1" in update_enrolled

    serve = "systemd-run --unit=iotox-witness --service-type=simple ${iotoxSourceLinked}/bin/iotox witness-service-serve /var/lib/iotox-witness /var/lib/iotox-witness/service.identity 0.0.0.0 37177"
    witness.succeed(serve)
    witness.wait_for_open_port(37177)

    # Namespace enrollment first verifies the enrolled complete policy tree
    # over authenticated TCP. The service is then stopped only long enough to
    # install both independently keyed no-replace namespace records.
    guarded_enrollments = []
    for namespace in ["updates", "notes", "tree-notes"]:
        guarded = agent.succeed(f"${iotoxSourceLinked}/bin/iotox witness-sync-guarded-enrollment {base} {remote} {namespace}").strip()
        assert len(guarded) == 352
        guarded_enrollments.append(guarded)
    witness.succeed("systemctl stop iotox-witness.service")
    witness.wait_until_succeeds("! systemctl is-active --quiet iotox-witness.service")
    for index, guarded in enumerate(guarded_enrollments):
        guarded_enrolled = witness.succeed(f"${iotoxSourceLinked}/bin/iotox witness-service-enroll /var/lib/iotox-witness /var/lib/iotox-witness/service.identity {guarded}")
        expected_lane = "tree-v2-state" if index == 2 else "sync-guarded-state"
        assert f"lane={expected_lane}" in guarded_enrolled
        assert "position=1" in guarded_enrolled
        assert "enrolled=1" in guarded_enrolled
    witness.succeed("mkdir -p /var/lib/iotox-witness-checkpoints /var/lib/iotox-witness-initial && chmod 0700 /var/lib/iotox-witness-checkpoints /var/lib/iotox-witness-initial && cp /var/lib/iotox-witness/*.witness /var/lib/iotox-witness-initial/")
    initial_checkpoint = "/var/lib/iotox-witness-checkpoints/initial.checkpoint"
    checkpointed = witness.succeed(f"${iotoxSourceLinked}/bin/iotox witness-service-checkpoint /var/lib/iotox-witness /var/lib/iotox-witness/service.identity {initial_checkpoint}")
    assert "records=11" in checkpointed
    verified = witness.succeed(f"${iotoxSourceLinked}/bin/iotox witness-service-checkpoint-verify {initial_checkpoint} {server_key}")
    assert "records=11 authenticated=1" in verified
    serve = f"systemd-run --unit=iotox-witness --service-type=simple ${iotoxSourceLinked}/bin/iotox witness-service-serve /var/lib/iotox-witness /var/lib/iotox-witness/service.identity 0.0.0.0 37177 {initial_checkpoint}"
    witness.succeed(serve)
    witness.wait_for_open_port(37177)

    agent.succeed(f"systemd-run --unit=iotox-agent --service-type=simple ${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox {remote}")
    agent.wait_for_file("/run/iotox/control.sock")
    agent.succeed("set -o pipefail; ${iotoxSourceLinked}/bin/iotox recall-generate | ${iotoxSourceLinked}/bin/iotox --runtime /run/iotox authority-bootstrap-recall-stdin")
    agent.succeed("cp /var/lib/iotox/sync-policy.checkpoint /var/lib/iotox/sync-policy-pre-automation.checkpoint")
    automated = agent.succeed("${iotoxSourceLinked}/bin/iotox --runtime /run/iotox sync-auto-publish updates /var/lib/iotox/notes-source 86400")
    assert "namespace=updates" in automated
    published = agent.succeed("${iotoxSourceLinked}/bin/iotox --runtime /run/iotox sync-publish notes /var/lib/iotox/notes-source")
    assert "namespace=notes" in published
    assert "generation=1" in published
    agent.succeed("mkdir /var/lib/iotox/tree-pre-advance && chmod 0700 /var/lib/iotox/tree-pre-advance && cp -a /var/lib/iotox/sync-policy/data/tree-notes /var/lib/iotox/tree-pre-advance/root")
    agent.succeed("printf 'tree revision two\\n' >/var/lib/iotox/tree-source/field.txt && chmod 0600 /var/lib/iotox/tree-source/field.txt")
    tree_published = agent.succeed("${iotoxSourceLinked}/bin/iotox --runtime /run/iotox sync-publish tree-notes /var/lib/iotox/tree-source")
    assert "namespace=tree-notes" in tree_published
    assert "engine=tree-v2" in tree_published
    agent.succeed("${iotoxSourceLinked}/bin/iotox --runtime /run/iotox stop")
    # A transient unit may be collected immediately after its clean exit, so
    # assert the semantic condition instead of matching an ActiveState string.
    agent.wait_until_succeeds("! systemctl is-active --quiet iotox-agent.service")
    agent.succeed("mkdir /var/lib/iotox/post-bootstrap && chmod 0700 /var/lib/iotox/post-bootstrap && cp /var/lib/iotox/authority.ledger /var/lib/iotox/authority.ledger.guard /var/lib/iotox/post-bootstrap/ && cp /var/lib/iotox/.iotox-incarnations/device.toxsave.protocol-incarnation /var/lib/iotox/post-bootstrap/application-incarnation && cp /var/lib/iotox/ratox/incarnation.state /var/lib/iotox/post-bootstrap/ratox-incarnation && cp /var/lib/iotox/routes.signed /var/lib/iotox/post-bootstrap/routes.signed && cp /var/lib/iotox/routes.generation /var/lib/iotox/post-bootstrap/routes.generation && cp /var/lib/iotox/terminal-policy.checkpoint /var/lib/iotox/post-bootstrap/terminal-policy.checkpoint && cp /var/lib/iotox/ratox-profiles/profiles/witness-shell.profile /var/lib/iotox/post-bootstrap/witness-shell.profile && cp /var/lib/iotox/sync-policy.checkpoint /var/lib/iotox/post-bootstrap/sync-policy.checkpoint && cp -a /var/lib/iotox/sync-policy/namespaces /var/lib/iotox/post-bootstrap/sync-namespaces && cp -a /var/lib/iotox/sync-policy/automation /var/lib/iotox/post-bootstrap/sync-automation && cp /var/lib/iotox/notes-sync/published-heads/notes.signed-head /var/lib/iotox/post-bootstrap/notes.signed-head && cp /var/lib/iotox/notes-sync/rollback-guards/notes.rollback-guard /var/lib/iotox/post-bootstrap/notes.rollback-guard && cp -a /var/lib/iotox/sync-policy/data/tree-notes /var/lib/iotox/post-bootstrap/tree-notes-current")

    # Restore the complete pre-publication four-root namespace snapshot (all
    # four roots and the local guard absent) while its derived remote record is
    # still at position two. Freshness must fail before RuntimeTree exists.
    agent.succeed("rm -f /var/lib/iotox/notes-sync/published-heads/notes.signed-head /var/lib/iotox/notes-sync/accepted-heads/notes.accepted-head /var/lib/iotox/notes-sync/activated-revisions/notes.activated-revision /var/lib/iotox/notes-sync/retention/notes.retained-revisions /var/lib/iotox/notes-sync/rollback-guards/notes.rollback-guard")
    agent.fail(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-sync-root-rollback {remote} --run-ms 100")
    agent.succeed("test ! -e /run/iotox-sync-root-rollback")
    agent.succeed("mkdir -p /var/lib/iotox/notes-sync/published-heads /var/lib/iotox/notes-sync/rollback-guards && chmod 0700 /var/lib/iotox/notes-sync/published-heads /var/lib/iotox/notes-sync/rollback-guards && cp /var/lib/iotox/post-bootstrap/notes.signed-head /var/lib/iotox/notes-sync/published-heads/notes.signed-head && cp /var/lib/iotox/post-bootstrap/notes.rollback-guard /var/lib/iotox/notes-sync/rollback-guards/notes.rollback-guard")

    # The tree-v2 lane commits the signed branch frontier plus the signed
    # workspace and maintenance roots. Restoring their complete prior local
    # snapshot while the derived service record remains advanced is rejected
    # before RuntimeTree; exact-current replacement recovers normally.
    agent.succeed("rm -rf /var/lib/iotox/sync-policy/data/tree-notes && cp -a /var/lib/iotox/tree-pre-advance/root /var/lib/iotox/sync-policy/data/tree-notes")
    agent.fail(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-tree-v2-rollback {remote} --run-ms 100")
    agent.succeed("test ! -e /run/iotox-tree-v2-rollback")
    agent.succeed("rm -rf /var/lib/iotox/sync-policy/data/tree-notes && cp -a /var/lib/iotox/post-bootstrap/tree-notes-current /var/lib/iotox/sync-policy/data/tree-notes")

    # Restore the complete valid pre-bootstrap local authority pair while the
    # service remains at position 1. The Agent must fail before RuntimeTree.
    agent.succeed("rm /var/lib/iotox/authority.ledger /var/lib/iotox/authority.ledger.guard")
    agent.fail(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-rollback {remote} --run-ms 100")
    agent.succeed("test ! -e /run/iotox-rollback")

    # Exact-current recovery and service restart preserve the committed head.
    agent.succeed("cp /var/lib/iotox/post-bootstrap/authority.ledger /var/lib/iotox/authority.ledger && cp /var/lib/iotox/post-bootstrap/authority.ledger.guard /var/lib/iotox/authority.ledger.guard")
    agent.succeed(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-current {remote} --run-ms 100")
    agent.succeed("mkdir /var/lib/iotox/post-current && chmod 0700 /var/lib/iotox/post-current && cp /var/lib/iotox/.iotox-incarnations/device.toxsave.protocol-incarnation /var/lib/iotox/post-current/application-incarnation && cp /var/lib/iotox/ratox/incarnation.state /var/lib/iotox/post-current/ratox-incarnation")

    # Restore a complete, correctly signed prior application namespace while
    # authority remains current. Independent lane freshness must reject it
    # before RuntimeTree is created.
    agent.succeed("cp /var/lib/iotox/post-bootstrap/application-incarnation /var/lib/iotox/.iotox-incarnations/device.toxsave.protocol-incarnation")
    agent.fail(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-incarnation-rollback {remote} --run-ms 100")
    agent.succeed("test ! -e /run/iotox-incarnation-rollback")
    agent.succeed("cp /var/lib/iotox/post-current/application-incarnation /var/lib/iotox/.iotox-incarnations/device.toxsave.protocol-incarnation")

    # Ratox has a separately enrolled namespace. Rolling back only that signed
    # record is rejected even though authority and application are current.
    # Application may advance before the later lane refuses; no runtime or
    # network/effect surface is created.
    agent.succeed("cp /var/lib/iotox/post-bootstrap/ratox-incarnation /var/lib/iotox/ratox/incarnation.state")
    agent.fail(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-ratox-rollback {remote} --run-ms 100")
    agent.succeed("test ! -e /run/iotox-ratox-rollback")
    agent.succeed("cp /var/lib/iotox/post-current/ratox-incarnation /var/lib/iotox/ratox/incarnation.state")

    # A reviewed exact generation-two artifact advances route policy through
    # its own pending/committed transaction. Restoring the complete valid
    # generation-one artifact/checkpoint pair must then fail before RuntimeTree.
    route_set_two = "/var/lib/iotox/routes.generation-two.signed"
    agent.succeed(f"${iotoxSourceLinked}/bin/iotox --identity /var/lib/iotox/device.identity route-set-create {route_set_two} 2 {primary_route_key} {primary_route_key}:protected:either:1:0:0 {bulk_route_key}:bulk:either:2:0:0")
    agent.succeed(f"mv {route_set_two} {route_set}")
    agent.succeed(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-route-two {remote} --run-ms 100")
    agent.succeed("mkdir /var/lib/iotox/post-route-two && chmod 0700 /var/lib/iotox/post-route-two && cp /var/lib/iotox/routes.signed /var/lib/iotox/routes.generation /var/lib/iotox/post-route-two/")
    agent.succeed("cp /var/lib/iotox/post-bootstrap/routes.signed /var/lib/iotox/routes.signed && cp /var/lib/iotox/post-bootstrap/routes.generation /var/lib/iotox/routes.generation")
    agent.fail(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-route-rollback {remote} --run-ms 100")
    agent.succeed("test ! -e /run/iotox-route-rollback")
    agent.succeed("cp /var/lib/iotox/post-route-two/routes.signed /var/lib/iotox/routes.signed && cp /var/lib/iotox/post-route-two/routes.generation /var/lib/iotox/routes.generation")

    # The first policy deliberately permits host-authorized sudo. Replacing it
    # with a no-escalation profile is not usable until an explicit remote commit.
    agent.succeed("${iotoxSourceLinked}/bin/iotox --shell /opt/iotox-test/ratox-bash terminal-profile-shell-template witness-shell operator > /tmp/witness-shell-safe.profile")
    agent.succeed("sed -i 's/^enabled=0$/enabled=1/' /tmp/witness-shell-safe.profile")
    agent.succeed("${iotoxSourceLinked}/bin/iotox --ratox-profile-store /var/lib/iotox/ratox-profiles terminal-profile-install /tmp/witness-shell-safe.profile")
    agent.fail(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-terminal-uncommitted {remote} --run-ms 100")
    agent.succeed("test ! -e /run/iotox-terminal-uncommitted")
    committed = agent.succeed(f"${iotoxSourceLinked}/bin/iotox witness-terminal-policy-commit {base} {remote}")
    assert "lane=terminal-policy position=2" in committed
    assert "committed=1" in committed
    agent.succeed(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-terminal-safe {remote} --run-ms 100")
    agent.succeed("mkdir /var/lib/iotox/post-terminal-safe && chmod 0700 /var/lib/iotox/post-terminal-safe && cp /var/lib/iotox/terminal-policy.checkpoint /var/lib/iotox/post-terminal-safe/ && cp /var/lib/iotox/ratox-profiles/profiles/witness-shell.profile /var/lib/iotox/post-terminal-safe/")

    # Restore both the old permissive profile and its matching signed local
    # checkpoint. The remote head remains at safe policy two, so startup fails.
    agent.succeed("cp /var/lib/iotox/post-bootstrap/witness-shell.profile /var/lib/iotox/ratox-profiles/profiles/witness-shell.profile && cp /var/lib/iotox/post-bootstrap/terminal-policy.checkpoint /var/lib/iotox/terminal-policy.checkpoint")
    agent.fail(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-terminal-rollback {remote} --run-ms 100")
    agent.succeed("test ! -e /run/iotox-terminal-rollback")
    agent.succeed("cp /var/lib/iotox/post-terminal-safe/witness-shell.profile /var/lib/iotox/ratox-profiles/profiles/witness-shell.profile && cp /var/lib/iotox/post-terminal-safe/terminal-policy.checkpoint /var/lib/iotox/terminal-policy.checkpoint")

    # Restore the complete enrolled pre-automation policy view and matching
    # checkpoint while the service remains at the post-automation head.
    agent.succeed("rm -rf /var/lib/iotox/sync-policy/automation && cp /var/lib/iotox/sync-policy-pre-automation.checkpoint /var/lib/iotox/sync-policy.checkpoint")
    agent.fail(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-sync-policy-rollback {remote} --run-ms 100")
    agent.succeed("test ! -e /run/iotox-sync-policy-rollback")
    agent.succeed("rm -rf /var/lib/iotox/sync-policy/namespaces /var/lib/iotox/sync-policy/automation && cp -a /var/lib/iotox/post-bootstrap/sync-namespaces /var/lib/iotox/sync-policy/namespaces && cp -a /var/lib/iotox/post-bootstrap/sync-automation /var/lib/iotox/sync-policy/automation && cp /var/lib/iotox/post-bootstrap/sync-policy.checkpoint /var/lib/iotox/sync-policy.checkpoint")

    # The update lane commits the exact canonical signer policy even before
    # lifecycle state exists. An uncommitted policy substitution fails before
    # the runtime tree and is repaired only by restoring the enrolled bytes.
    agent.succeed("cp /var/lib/iotox/update.policy /var/lib/iotox/update.policy.enrolled && sed -i 's/^target=iotox-witness-x86_64$/target=iotox-witness-other/' /var/lib/iotox/update.policy")
    agent.fail(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-update-policy-substitution {remote} --run-ms 100")
    agent.succeed("test ! -e /run/iotox-update-policy-substitution")
    agent.succeed("mv /var/lib/iotox/update.policy.enrolled /var/lib/iotox/update.policy")

    witness.succeed("systemctl stop iotox-witness.service")
    agent.fail(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-unavailable {remote} --run-ms 100")
    agent.succeed("test ! -e /run/iotox-unavailable")

    # Export the advanced complete store checkpoint. Selectively restoring
    # the old authority service record is authentic but now below that floor,
    # so the listener must refuse before binding. Restore the exact current
    # record and relaunch with the newly retained floor.
    witness.succeed("mkdir -p /var/lib/iotox-witness-current && chmod 0700 /var/lib/iotox-witness-current && cp /var/lib/iotox-witness/*.witness /var/lib/iotox-witness-current/")
    current_checkpoint = "/var/lib/iotox-witness-checkpoints/current.checkpoint"
    advanced_checkpoint = witness.succeed(f"${iotoxSourceLinked}/bin/iotox witness-service-checkpoint /var/lib/iotox-witness /var/lib/iotox-witness/service.identity {current_checkpoint}")
    assert "records=11" in advanced_checkpoint
    witness.succeed("cp /var/lib/iotox-witness-initial/*-1.witness /var/lib/iotox-witness/")
    witness.succeed(f"set +e; ${iotoxSourceLinked}/bin/iotox witness-service-serve /var/lib/iotox-witness /var/lib/iotox-witness/service.identity 0.0.0.0 37177 {current_checkpoint} >/tmp/rollback.out 2>/tmp/rollback.err; code=$?; test $code -eq 3; grep -Eq 'behind|forked' /tmp/rollback.err")
    witness.succeed("cp /var/lib/iotox-witness-current/*-1.witness /var/lib/iotox-witness/")
    serve = f"systemd-run --unit=iotox-witness --service-type=simple ${iotoxSourceLinked}/bin/iotox witness-service-serve /var/lib/iotox-witness /var/lib/iotox-witness/service.identity 0.0.0.0 37177 {current_checkpoint}"
    witness.succeed(serve)
    witness.wait_for_open_port(37177)
    wrong_key = ("0" if server_key[0] != "0" else "1") + server_key[1:]
    wrong = f"--authority-witness-host witness --authority-witness-port 37177 --authority-witness-server-key {wrong_key} --authority-witness-domain {domain} --authority-witness-epoch 1"
    agent.fail(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-wrong-key {wrong} --run-ms 100")
    agent.succeed("test ! -e /run/iotox-wrong-key")
    agent.succeed(f"${iotoxSourceLinked}/bin/iotox run {base} --runtime /run/iotox-final {remote} --run-ms 100")
  '';
}
