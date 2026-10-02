{ pkgs, ratoxTestHarness }:

pkgs.testers.runNixOSTest {
  name = "iotox-ratox-sudo";

  nodes.machine = { ... }: {
    users.groups.operator.gid = 1000;
    users.users.operator = {
      isNormalUser = true;
      uid = 1000;
      group = "operator";
      extraGroups = [ "wheel" "video" ];
      home = "/home/operator";
      initialPassword = "iotox-test-password";
    };
    users.groups.operator-nopasswd.gid = 1001;
    users.users.operator-nopasswd = {
      isNormalUser = true;
      uid = 1001;
      group = "operator-nopasswd";
      home = "/home/operator-nopasswd";
    };
    security.sudo = {
      enable = true;
      wheelNeedsPassword = true;
      # Retain the original deterministic noninteractive set-ID branch under
      # a separate fixture account while the real operator crosses PAM and a
      # password prompt through the production PTY.
      extraRules = [{
        users = [ "operator-nopasswd" ];
        commands = [{
          command = "ALL";
          options = [ "NOPASSWD" ];
        }];
      }];
    };
    environment.systemPackages = [ pkgs.coreutils pkgs.sudo ];
  };

  testScript = ''
    start_all()
    machine.wait_for_unit("multi-user.target")
    machine.succeed("su - operator -c '${ratoxTestHarness}/bin/iotox terminal-shell-discover' | grep -F 'user=operator uid=1000 gid=1000'")
    machine.succeed("su - operator -c '${ratoxTestHarness}/bin/iotox host-capabilities' | grep -F 'privilege-escalation-prerequisite=available-host-policy-pending'")
    machine.succeed("su - operator -c '${ratoxTestHarness}/bin/iotox host-capabilities' | grep -F 'sudo-mechanism=setuid-root'")
    machine.succeed("su - operator -c '${ratoxTestHarness}/bin/iotox --allow-sudo terminal-profile-shell-template owner-admin' > /tmp/owner-admin.profile")
    machine.succeed("grep -F 'identity=account:1000:1000' /tmp/owner-admin.profile")
    machine.succeed("grep -F 'confinement=compatibility' /tmp/owner-admin.profile")
    machine.succeed("grep -F 'allow-privilege-escalation=1' /tmp/owner-admin.profile")
    noninteractive = machine.succeed("su - operator-nopasswd -c '${ratoxTestHarness}/bin/iotox_terminal_posix_process_tests --sudo-qualification ${ratoxTestHarness}/bin/iotox ${ratoxTestHarness}/bin/iotox_terminal_pty_fixture /run/wrappers/bin/sudo /run/current-system/sw/bin/id'")
    assert "terminal sudo qualification passed" in noninteractive
    prompted = machine.succeed("su - operator -c '${ratoxTestHarness}/bin/iotox_terminal_posix_process_tests --sudo-shell-qualification ${ratoxTestHarness}/bin/iotox ${pkgs.bashInteractive}/bin/bash /run/wrappers/bin/sudo /run/current-system/sw/bin/id iotox-test-password'")
    assert "terminal sudo shell qualification passed" in prompted
  '';
}
