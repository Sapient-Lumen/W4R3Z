{ pkgs, ratoxTestHarness }:

pkgs.testers.runNixOSTest {
  name = "iotox-ratox-cgroup";

  nodes.machine = { ... }: {
    boot.kernelParams = [ "psi=1" ];
    boot.kernel.sysctl = {
      "kernel.unprivileged_userns_clone" = 1;
      "user.max_user_namespaces" = 63536;
    };
    environment.systemPackages = [ pkgs.coreutils pkgs.util-linux ];
  };

  testScript = ''
    start_all()
    machine.wait_for_unit("multi-user.target")
    machine.succeed("test $(stat -fc %T /sys/fs/cgroup) = cgroup2fs")
    machine.succeed("grep -qw cpu /sys/fs/cgroup/cgroup.controllers")
    machine.succeed("grep -qw memory /sys/fs/cgroup/cgroup.controllers")
    machine.succeed("grep -qw io /sys/fs/cgroup/cgroup.controllers")
    machine.succeed("test -r /proc/pressure/cpu && test -r /proc/pressure/memory && test -r /proc/pressure/io")

    lifecycle = machine.succeed("systemd-run --quiet --wait --pipe --collect --service-type=exec --unit=iotox-cgroup-lifecycle --property=Delegate=yes --setenv=PATH=/run/current-system/sw/bin ${ratoxTestHarness}/bin/iotox_terminal_cgroup_recovery_process_tests --lifecycle")
    assert "PASS boot-bound cgroup orphan recovery process oracle" in lifecycle
    memory = machine.succeed("systemd-run --quiet --wait --pipe --collect --service-type=exec --unit=iotox-cgroup-memory --property=Delegate=yes --setenv=PATH=/run/current-system/sw/bin ${ratoxTestHarness}/bin/iotox_terminal_cgroup_recovery_process_tests --memory-resource")
    assert "PASS memory/pids cgroup resource process oracle" in memory
    cpu = machine.succeed("systemd-run --quiet --wait --pipe --collect --service-type=exec --unit=iotox-cgroup-cpu --property=Delegate=yes --setenv=PATH=/run/current-system/sw/bin ${ratoxTestHarness}/bin/iotox_terminal_cgroup_recovery_process_tests --cpu-resource")
    assert "PASS CPU cgroup resource process oracle" in cpu
    io = machine.succeed("systemd-run --quiet --wait --pipe --collect --service-type=exec --unit=iotox-cgroup-io --property=Delegate=yes --setenv=PATH=/run/current-system/sw/bin ${ratoxTestHarness}/bin/iotox_terminal_cgroup_recovery_process_tests --io-resource")
    assert "PASS I/O cgroup resource process oracle" in io
    pressure = machine.succeed("systemd-run --quiet --wait --pipe --collect --service-type=exec --unit=iotox-cgroup-pressure --property=Delegate=yes --setenv=PATH=/run/current-system/sw/bin ${ratoxTestHarness}/bin/iotox_terminal_cgroup_recovery_process_tests --pressure-admission")
    assert "PASS cgroup PSI pressure-admission process oracle" in pressure
  '';
}
