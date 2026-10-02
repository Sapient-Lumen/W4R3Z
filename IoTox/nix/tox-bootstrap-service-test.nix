{ pkgs, toxBootstrap }:

pkgs.testers.runNixOSTest {
  name = "iotox-tox-bootstrap-service";

  nodes.server = { ... }: {
    imports = [ ./iotox-tox-bootstrap-service.nix ];
    environment.systemPackages = [ pkgs.nftables ];

    services.iotox.toxBootstrap = {
      enable = true;
      package = toxBootstrap;
      addressFamily = "ipv4";
      openFirewall = true;
      memoryMax = "128M";
      cpuQuota = "25%";
      tasksMax = 32;
      restartSec = 2;
    };
  };

  testScript = ''
    start_all()
    server.wait_for_unit("iotox-tox-bootstrap.service")
    server.wait_for_open_port(33445)
    server.succeed("ss -H -lun | grep -Eq '(^|:)33445([[:space:]]|$)'")
    server.succeed("test $(stat -Lc %a /var/lib/iotox-tox-bootstrap) = 700")
    server.succeed("test $(stat -c %a /var/lib/iotox-tox-bootstrap/key) = 600")
    server.succeed("test $(stat -c %s /var/lib/iotox-tox-bootstrap/key) = 64")
    server.succeed("test $(stat -c %a /var/lib/iotox-tox-bootstrap/PUBLIC_ID.txt) = 600")
    server.succeed("grep -Eq '^[0-9A-F]{64}$' /var/lib/iotox-tox-bootstrap/PUBLIC_ID.txt")
    before = server.succeed("sha256sum /var/lib/iotox-tox-bootstrap/key /var/lib/iotox-tox-bootstrap/PUBLIC_ID.txt")
    server.succeed("systemctl restart iotox-tox-bootstrap.service")
    server.wait_for_unit("iotox-tox-bootstrap.service")
    server.wait_for_open_port(33445)
    server.fail("journalctl -u iotox-tox-bootstrap.service | grep -F 'Initialization: Invalid argument'")
    after = server.succeed("sha256sum /var/lib/iotox-tox-bootstrap/key /var/lib/iotox-tox-bootstrap/PUBLIC_ID.txt")
    assert before == after
    server.succeed("systemctl show iotox-tox-bootstrap.service -p DynamicUser --value | grep -Fx yes")
    server.succeed("systemctl show iotox-tox-bootstrap.service -p MemoryMax --value | grep -Fx 134217728")
    server.succeed("systemctl show iotox-tox-bootstrap.service -p TasksMax --value | grep -Fx 32")
    server.succeed("nft list ruleset | grep -q 33445")

    server.succeed("systemctl stop iotox-tox-bootstrap.service")
    server.succeed("chmod 0644 /var/lib/iotox-tox-bootstrap/key")
    server.fail("systemctl start iotox-tox-bootstrap.service")
    server.succeed("chmod 0600 /var/lib/iotox-tox-bootstrap/key")
    server.succeed("systemctl reset-failed iotox-tox-bootstrap.service")
    server.succeed("systemctl start iotox-tox-bootstrap.service")
    server.wait_for_unit("iotox-tox-bootstrap.service")
    server.wait_for_open_port(33445)
    final = server.succeed("sha256sum /var/lib/iotox-tox-bootstrap/key /var/lib/iotox-tox-bootstrap/PUBLIC_ID.txt")
    assert before == final
  '';
}
