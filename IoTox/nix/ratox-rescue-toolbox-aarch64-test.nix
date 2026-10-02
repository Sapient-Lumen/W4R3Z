{ pkgs, ratoxTestHarness, iotoxRescueToolboxAarch64 }:

pkgs.testers.runNixOSTest {
  name = "iotox-ratox-rescue-toolbox-aarch64-binfmt-boundary";

  nodes.machine = { ... }: {
    boot.binfmt.emulatedSystems = [ "aarch64-linux" ];
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
    machine.succeed("test -r /proc/sys/fs/binfmt_misc/aarch64-linux")
    machine.succeed("grep -Fq 'interpreter /run/binfmt/aarch64-linux' /proc/sys/fs/binfmt_misc/aarch64-linux")
    machine.succeed("su - operator -c \"${iotoxRescueToolboxAarch64}/bin/oksh -c 'echo direct-aarch64'\" | grep -Fxq direct-aarch64")
    discover = machine.succeed("su - operator -c '${ratoxTestHarness}/bin/iotox --shell ${iotoxRescueToolboxAarch64}/bin/oksh --toolbox-dir ${iotoxRescueToolboxAarch64}/bin terminal-shell-discover'")
    assert "user=operator uid=1000 gid=1000" in discover
    assert "source=explicit" in discover
    assert "toolbox-dir=${iotoxRescueToolboxAarch64}/bin" in discover
    output = machine.succeed("su - operator -c '${ratoxTestHarness}/bin/iotox_terminal_posix_process_tests --rescue-toolbox-qualification ${ratoxTestHarness}/bin/iotox ${iotoxRescueToolboxAarch64}/bin/oksh ${iotoxRescueToolboxAarch64}/bin' 2>&1 || true")
    assert "PTY child setup failed at final fexecve: No such file or directory" in output
    assert "terminal rescue toolbox qualification passed" not in output
  '';
}
