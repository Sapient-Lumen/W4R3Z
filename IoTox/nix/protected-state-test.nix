{ pkgs, iotoxSourceLinked }:

pkgs.testers.runNixOSTest {
  name = "iotox-protected-state-fscrypt-v2";
  globalTimeout = 15 * 60;

  nodes.machine = { ... }: {
    boot.supportedFilesystems = [ "ext4" ];
    environment.systemPackages = [
      pkgs.e2fsprogs
      pkgs.fscryptctl
      pkgs.gnugrep
      pkgs.util-linux
    ];
    virtualisation.emptyDiskImages = [ 512 ];
    virtualisation.memorySize = 2048;
  };

  testScript = ''
    start_all()
    machine.wait_for_unit("multi-user.target")
    machine.succeed("mkfs.ext4 -F -O encrypt /dev/vdb")
    machine.succeed("mkdir -p /state && mount /dev/vdb /state")
    machine.succeed("head -c 32 /dev/zero > /root/iotox-state.key && chmod 0600 /root/iotox-state.key")
    key_id = machine.succeed("fscryptctl add_key /state < /root/iotox-state.key").strip()
    assert len(key_id) == 32
    machine.succeed("mkdir /state/iotox && chmod 0700 /state/iotox")
    machine.succeed(f"fscryptctl set_policy {key_id} /state/iotox")
    machine.succeed("mkdir /state/iotox/core && chmod 0700 /state/iotox/core")
    machine.succeed("printf 'IOTOX-ENCRYPTED-CANARY-0303' > /state/iotox/canary && chmod 0600 /state/iotox/canary")

    options = f"--state /state/iotox/core/device.toxsave --runtime /run/iotox --no-default-bootstrap --no-default-relays --require-state-protection fscrypt-v2 --protected-state-root /state/iotox --protected-state-policy-id {key_id}"
    machine.succeed("test -z \"$(swapon --noheadings --show)\"")
    wrong_policy_id = ("0" if key_id[0] != "0" else "1") + key_id[1:]
    wrong_policy_options = f"--state /state/iotox/core/device.toxsave --runtime /run/iotox --no-default-bootstrap --no-default-relays --require-state-protection fscrypt-v2 --protected-state-root /state/iotox --protected-state-policy-id {wrong_policy_id}"
    machine.fail(f"${iotoxSourceLinked}/bin/iotox run-check {wrong_policy_options}")
    # Component-wise closure checks reject lexical-prefix, symlink, hard-link,
    # special-inode, and nested-mount escapes before any runtime surface.
    machine.succeed("mkdir /state/iotox-sibling && chmod 0700 /state/iotox-sibling")
    machine.fail(f"${iotoxSourceLinked}/bin/iotox run-check {options} --identity /state/iotox-sibling/device.identity")
    machine.succeed("ln -s core /state/iotox/escaped")
    machine.fail(f"${iotoxSourceLinked}/bin/iotox run-check {options} --identity /state/iotox/escaped/device.identity")
    machine.succeed("rm /state/iotox/escaped")
    machine.succeed("ln /state/iotox/canary /state/iotox/canary-hardlink")
    machine.fail(f"${iotoxSourceLinked}/bin/iotox run-check {options}")
    machine.succeed("rm /state/iotox/canary-hardlink")
    machine.succeed("mkfifo /state/iotox/special")
    machine.fail(f"${iotoxSourceLinked}/bin/iotox run-check {options}")
    machine.succeed("rm /state/iotox/special")
    machine.succeed("mkdir /outside /state/iotox/cross && chmod 0700 /outside && mount --bind /outside /state/iotox/cross")
    machine.fail(f"${iotoxSourceLinked}/bin/iotox run-check {options}")
    machine.succeed("umount /state/iotox/cross && rmdir /state/iotox/cross")
    report = machine.succeed(f"${iotoxSourceLinked}/bin/iotox run-check {options}")
    assert "decision=ready-for-start" in report
    assert f"protected-state=fscrypt-v2-policy={key_id}" in report
    assert "runtime=tmpfs" in report
    machine.succeed(f"${iotoxSourceLinked}/bin/iotox run {options} --run-ms 100")
    machine.succeed("test -s /state/iotox/core/device.toxsave")
    # RuntimeTree intentionally retains its private projections after an
    # orderly stop. Remove that known VM-only tree to prove the next refused
    # start creates nothing.
    machine.succeed("rm -rf -- /run/iotox")

    # A different live key does not satisfy the exact root policy. No runtime
    # surface may appear while the selected key is absent.
    machine.succeed(f"fscryptctl remove_key {key_id} /state")
    machine.succeed("printf 'different-iotox-fscrypt-key-000' | head -c 32 > /root/wrong.key")
    wrong_id = machine.succeed("fscryptctl add_key /state < /root/wrong.key").strip()
    assert wrong_id != key_id
    machine.fail(f"${iotoxSourceLinked}/bin/iotox run-check {options}")
    machine.succeed("test ! -e /run/iotox")
    machine.succeed(f"fscryptctl remove_key {wrong_id} /state")

    restored_id = machine.succeed("fscryptctl add_key /state < /root/iotox-state.key").strip()
    assert restored_id == key_id
    restored = machine.succeed(f"${iotoxSourceLinked}/bin/iotox run-check {options}")
    assert "decision=ready-for-start" in restored
    machine.succeed("sync && umount /state")
    machine.fail("grep -aFq 'IOTOX-ENCRYPTED-CANARY-0303' /dev/vdb")
  '';
}
