{ pkgs, ratoxTestHarness, iotoxRescueToolbox }:

pkgs.testers.runNixOSTest {
  name = "iotox-ratox-rescue-toolbox";

  nodes.machine = { ... }: {
    users.groups.operator.gid = 1000;
    users.users.operator = {
      isNormalUser = true;
      uid = 1000;
      group = "operator";
      home = "/home/operator";
    };
  };

  testScript = ''
    start_all()
    machine.wait_for_unit("multi-user.target")
    discover = machine.succeed("su - operator -c '${ratoxTestHarness}/bin/iotox --shell ${iotoxRescueToolbox}/bin/oksh --toolbox-dir ${iotoxRescueToolbox}/bin terminal-shell-discover'")
    assert "user=operator uid=1000 gid=1000" in discover
    assert "source=explicit" in discover
    assert "toolbox-dir=${iotoxRescueToolbox}/bin" in discover
    machine.succeed("su - operator -c '${ratoxTestHarness}/bin/iotox --shell ${iotoxRescueToolbox}/bin/oksh --toolbox-dir ${iotoxRescueToolbox}/bin terminal-profile-toolbox-template rescue' > /tmp/rescue.profile")
    machine.succeed("grep -F 'identity=account:1000:1000' /tmp/rescue.profile")
    machine.succeed("grep -F 'confinement=baseline' /tmp/rescue.profile")
    machine.succeed("grep -F 'allow-privilege-escalation=0' /tmp/rescue.profile")
    machine.succeed("grep -Eq '^executable-sha256=[0-9a-f]{64}$' /tmp/rescue.profile")
    machine.succeed("grep -Eq '^toolbox-sha256=[0-9a-f]{64}$' /tmp/rescue.profile")
    output = machine.succeed("su - operator -c '${ratoxTestHarness}/bin/iotox_terminal_posix_process_tests --rescue-toolbox-qualification ${ratoxTestHarness}/bin/iotox ${iotoxRescueToolbox}/bin/oksh ${iotoxRescueToolbox}/bin'")
    assert "terminal rescue toolbox qualification passed" in output
  '';
}
