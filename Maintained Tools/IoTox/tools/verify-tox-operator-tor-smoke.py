#!/usr/bin/env python3
"""Independently verify a canonical IoTox operator-Tor qualification receipt."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import ipaddress
import json
import re
import tempfile
from pathlib import Path


HEX_64 = re.compile(r"^[0-9a-f]{64}$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_NONCLAIMS = {
    "anonymity-proof",
    "censorship-resistance-proof",
    "multi-exit-or-multi-network-reliability",
    "public-relay-sla",
    "representative-deployment-qualification",
    "automatic-route-or-terminal-recovery-policy",
}
ROUTE_HEALTH_SEMANTICS = (
    "auxiliary-only-no-carrier-or-session-epoch-mutation"
)
ROUTE_TARGET_SEMANTICS = (
    "auxiliary-only-explicit-numeric-relay-no-carrier-or-session-epoch-mutation"
)
APPLICATION_CIRCUIT_PURPOSES = {"GENERAL", "CONFLUX_LINKED"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            result.update(chunk)
    return result.hexdigest()


def exact_keys(value: dict[str, object], expected: set[str], label: str) -> None:
    missing = expected - set(value)
    extra = set(value) - expected
    require(not missing and not extra,
            f"{label} schema drift: missing={sorted(missing)} extra={sorted(extra)}")


def verify_node(node: object) -> str:
    require(isinstance(node, dict), "node record is not an object")
    exact_keys(node, {"address", "port", "public_key"}, "node record")
    address = ipaddress.ip_address(str(node["address"]))
    require(address.is_global, "node address is not globally routable")
    require(isinstance(node["port"], int) and 1 <= node["port"] <= 65535,
            "node port is invalid")
    require(isinstance(node["public_key"], str)
            and re.fullmatch(r"[0-9A-F]{64}", node["public_key"]) is not None,
            "node public key is not canonical uppercase hex")
    host = f"[{address.compressed}]" if address.version == 6 else address.compressed
    return f"{host}:{node['port']}"


def verify_socket_observation(
    observation: object, expected_proxy: str, expected_phase: str, require_live: bool
) -> None:
    require(isinstance(observation, dict), "agent socket observation is not an object")
    exact_keys(
        observation,
        {"phase", "tcp_remote_endpoints", "udp_socket_count"},
        "agent socket observation",
    )
    require(observation["phase"] == expected_phase, "agent socket phase ordering drifted")
    remotes = observation["tcp_remote_endpoints"]
    require(isinstance(remotes, list) and all(isinstance(item, str) for item in remotes),
            "agent TCP remote set is malformed")
    require(set(remotes) <= {expected_proxy}, "agent socket evidence contains a non-proxy route")
    if require_live:
        require(remotes == [expected_proxy], "live agent socket evidence omits the exact proxy")
    require(observation["udp_socket_count"] == 0, "agent socket evidence contains native UDP")


def verify_circuit(observation: object, phase: str, targets: set[str]) -> None:
    require(isinstance(observation, dict), "Tor circuit observation is not an object")
    exact_keys(
        observation,
        {
            "bootstrap_progress", "circuit_hop_count", "circuit_path_sha256",
            "circuit_purpose", "phase",
            "public_tcp_remote_count", "public_tcp_remote_set_sha256", "stream_target",
        },
        "Tor circuit observation",
    )
    require(observation["phase"] == phase, "Tor circuit phase ordering drifted")
    require(observation["bootstrap_progress"] == 100, "Tor bootstrap was incomplete")
    require(isinstance(observation["circuit_hop_count"], int)
            and observation["circuit_hop_count"] >= 3,
            "Tor application circuit contains fewer than three hops")
    require(isinstance(observation["circuit_path_sha256"], str)
            and HEX_64.fullmatch(observation["circuit_path_sha256"]) is not None,
            "Tor circuit path digest is malformed")
    require(observation["circuit_purpose"] in APPLICATION_CIRCUIT_PURPOSES,
            "Tor circuit purpose is not a public application purpose")
    require(observation["stream_target"] in targets,
            "Tor stream target is outside the explicit public relay set")
    require(isinstance(observation["public_tcp_remote_count"], int)
            and observation["public_tcp_remote_count"] > 0,
            "Tor process has no public TCP socket evidence")
    require(isinstance(observation["public_tcp_remote_set_sha256"], str)
            and HEX_64.fullmatch(observation["public_tcp_remote_set_sha256"]) is not None,
            "Tor public socket-set digest is malformed")


def verify_route_health(
    observation: object, phase: str, carrier: str, boundary: str, upstream: str,
) -> None:
    require(isinstance(observation, dict), "route-health observation is not an object")
    exact_keys(
        observation,
        {
            "application", "application_error", "application_rtt_us",
            "carrier_connection", "local_boundary", "local_boundary_rtt_us",
            "phase", "semantics", "upstream",
        },
        "route-health observation",
    )
    require(observation["phase"] == phase, "route-health phase ordering drifted")
    require(observation["carrier_connection"] == carrier,
            "route-health carrier truth drifted")
    require(observation["local_boundary"] == boundary,
            "route-health local-boundary truth drifted")
    require(observation["upstream"] == upstream,
            "route-health upstream classification drifted")
    require(isinstance(observation["local_boundary_rtt_us"], int)
            and 0 <= observation["local_boundary_rtt_us"] <= 500000,
            "route-health local observation exceeded its bounded representation")
    require(observation["application"] == "not-sampled"
            and observation["application_rtt_us"] is None
            and observation["application_error"] == "none",
            "route-health carrier sample contains application evidence")
    require(observation["semantics"] == ROUTE_HEALTH_SEMANTICS,
            "route-health mutation disclaimer drifted")


def verify_route_target_health(
    observation: object,
    phase: str,
    carrier: str,
    stage: str,
    health: set[str],
    reply: int | None,
) -> None:
    require(isinstance(observation, dict), "route-target observation is not an object")
    exact_keys(
        observation,
        {
            "carrier_connection", "network", "phase", "probe_stage", "semantics",
            "socks_reply_code", "target_health", "target_rtt_us", "target_source",
        },
        "route-target observation",
    )
    require(observation["phase"] == phase, "route-target phase ordering drifted")
    require(observation["carrier_connection"] == carrier,
            "route-target carrier truth drifted")
    require(observation["network"] == "Tox/Tor", "route-target network drifted")
    require(observation["probe_stage"] == stage, "route-target stage drifted")
    require(observation["target_health"] in health, "route-target health drifted")
    require(observation["socks_reply_code"] == reply, "route-target reply drifted")
    require(isinstance(observation["target_rtt_us"], int)
            and 0 <= observation["target_rtt_us"] <= 5_000_000,
            "route-target duration exceeded its bound")
    require(observation["target_source"] == "configured-tcp-relay-0",
            "route-target source drifted")
    require(observation["semantics"] == ROUTE_TARGET_SEMANTICS,
            "route-target mutation disclaimer drifted")


def verify_route_target_circuit(
    observation: object, phase: str, target: str,
) -> None:
    require(isinstance(observation, dict), "route-target circuit is not an object")
    exact_keys(
        observation,
        {
            "circuit_hop_count", "circuit_path_sha256", "circuit_purpose",
            "control_authenticated",
            "phase", "source_port_was_new", "stream_id_sha256", "stream_target",
            "target_source",
        },
        "route-target circuit",
    )
    require(observation["phase"] == phase, "route-target circuit phase drifted")
    require(observation["control_authenticated"] is True,
            "route-target circuit was not control-authenticated")
    require(observation["source_port_was_new"] is True,
            "route-target stream reused a preexisting Agent SOCKS source")
    require(observation["stream_target"] == target,
            "route-target circuit names a different target")
    require(observation["target_source"] == "configured-tcp-relay-0",
            "route-target circuit source drifted")
    require(isinstance(observation["circuit_hop_count"], int)
            and observation["circuit_hop_count"] >= 3,
            "route-target circuit has fewer than three hops")
    require(observation["circuit_purpose"] in APPLICATION_CIRCUIT_PURPOSES,
            "route-target circuit purpose is not a public application purpose")
    for key in ("circuit_path_sha256", "stream_id_sha256"):
        require(isinstance(observation[key], str)
                and HEX_64.fullmatch(observation[key]) is not None,
                f"route-target circuit {key} is malformed")


def verify_receipt(path: Path, runner: Path | None = None) -> dict[str, object]:
    raw = path.read_bytes()
    receipt = json.loads(raw)
    require(isinstance(receipt, dict), "receipt root is not an object")
    require(raw == canonical(receipt), "receipt is not canonical one-line JSON")
    exact_keys(
        receipt,
        {
            "agent_socket_observations", "carrier", "circuit_observations",
            "direct_relay_socket_observed", "dns_policy", "fixture", "initial_online_ms",
            "iotox_sha256", "iotox_version", "native_udp_socket_observed", "network",
            "node_records", "nonclaims", "operator_tor_smoke_sha256",
            "outage_agent_socket_sample_count", "outage_agent_socket_samples_sha256",
            "outage_hold_ms", "proxy_loss_to_offline_ms", "proxy_restart_count",
            "proxy_loss_to_local_boundary_ms",
            "proxy_restart_to_online_ms", "recovery_observed", "scope", "socks_endpoint",
            "route_health_observations",
            "route_target_circuit_observations", "route_target_observations",
            "source_commit", "source_tree_clean", "tor_binary_path", "tor_configuration",
            "tor_configuration_sha256", "tor_invocation", "tor_sha256", "tor_version",
            "total_gate_ms", "utc_completed",
        },
        "operator Tor receipt",
    )
    require(receipt["carrier"] == "tcp" and receipt["network"] == "Tox/Tor",
            "receipt carrier/network is not strict Tox/Tor TCP")
    require(receipt["fixture"] == "operator-owned-tor-public-numeric-relay",
            "receipt fixture identity drifted")
    require(receipt["scope"]
            == "operator-tor-public-relay-single-host-single-sample-not-anonymity-proof",
            "receipt scope overclaims its evidence")
    require(receipt["direct_relay_socket_observed"] is False
            and receipt["native_udp_socket_observed"] is False,
            "receipt admits a native route leak")
    require(receipt["recovery_observed"] is True and receipt["proxy_restart_count"] == 1,
            "receipt does not bind one Tor restart and recovery")
    require(receipt["source_tree_clean"] is True
            and isinstance(receipt["source_commit"], str)
            and SHA1.fullmatch(receipt["source_commit"]) is not None,
            "receipt source identity is malformed")
    for key in ("iotox_sha256", "operator_tor_smoke_sha256", "tor_sha256"):
        require(isinstance(receipt[key], str) and HEX_64.fullmatch(receipt[key]) is not None,
                f"receipt {key} is malformed")
    require(isinstance(receipt["iotox_version"], str) and receipt["iotox_version"],
            "IoTox version is empty")
    require(isinstance(receipt["tor_version"], str) and "Tor version" in receipt["tor_version"],
            "Tor version is empty or unrecognized")
    require(isinstance(receipt["tor_binary_path"], str)
            and Path(receipt["tor_binary_path"]).is_absolute(),
            "Tor binary path is not absolute")
    require(receipt["dns_policy"]
            == "iotox-native-dns-disabled;numeric-relays-only;tor-directory-network-owned-by-tor",
            "DNS ownership policy drifted")
    require(set(receipt["nonclaims"]) == EXPECTED_NONCLAIMS,
            "operator Tor nonclaims are incomplete")

    nodes = receipt["node_records"]
    require(isinstance(nodes, list) and nodes, "receipt has no public relay records")
    ordered_targets = [verify_node(node) for node in nodes]
    targets = set(ordered_targets)
    require(len(targets) == len(nodes), "receipt contains duplicate public relay endpoints")

    proxy = receipt["socks_endpoint"]
    require(isinstance(proxy, str) and re.fullmatch(r"127\.0\.0\.1:[1-9][0-9]{0,4}", proxy),
            "SOCKS endpoint is not canonical IPv4 loopback")
    proxy_port = int(proxy.rsplit(":", 1)[1])
    require(proxy_port <= 65535, "SOCKS endpoint port exceeds 65535")
    sockets = receipt["agent_socket_observations"]
    require(isinstance(sockets, list) and len(sockets) == 3,
            "receipt must contain initial, outage-final, and recovered agent sockets")
    verify_socket_observation(sockets[0], proxy, "initial", True)
    verify_socket_observation(sockets[1], proxy, "outage-final", False)
    verify_socket_observation(sockets[2], proxy, "recovered", True)

    circuits = receipt["circuit_observations"]
    require(isinstance(circuits, list) and len(circuits) == 2,
            "receipt must contain initial and recovered Tor circuits")
    verify_circuit(circuits[0], "initial", targets)
    verify_circuit(circuits[1], "recovered", targets)

    route_health = receipt["route_health_observations"]
    require(isinstance(route_health, list) and len(route_health) == 4,
            "receipt must contain four ordered route-health observations")
    verify_route_health(
        route_health[0], "initial", "tcp", "reachable",
        "carrier-reported-online",
    )
    verify_route_health(
        route_health[1], "post-tor-exit", "tcp", "refused",
        "carrier-reported-online",
    )
    verify_route_health(
        route_health[2], "authoritative-offline", "offline", "refused",
        "blocked-by-local-boundary",
    )
    verify_route_health(
        route_health[3], "recovered", "tcp", "reachable",
        "carrier-reported-online",
    )

    route_targets = receipt["route_target_observations"]
    require(isinstance(route_targets, list) and len(route_targets) == 3,
            "receipt must contain three ordered route-target observations")
    verify_route_target_health(
        route_targets[0], "initial", "tcp", "complete", {"reachable"}, 0,
    )
    verify_route_target_health(
        route_targets[1], "post-tor-exit", "tcp", "proxy-connect",
        {"refused", "unreachable", "failed"}, None,
    )
    verify_route_target_health(
        route_targets[2], "recovered", "tcp", "complete", {"reachable"}, 0,
    )
    target_circuits = receipt["route_target_circuit_observations"]
    require(isinstance(target_circuits, list) and len(target_circuits) == 2,
            "receipt must contain initial/recovered route-target circuits")
    verify_route_target_circuit(target_circuits[0], "initial", ordered_targets[0])
    verify_route_target_circuit(target_circuits[1], "recovered", ordered_targets[0])

    for key in (
        "initial_online_ms", "proxy_loss_to_offline_ms", "proxy_restart_to_online_ms",
        "total_gate_ms",
    ):
        require(isinstance(receipt[key], int) and receipt[key] > 0,
                f"receipt {key} is not a positive duration")
    require(isinstance(receipt["outage_hold_ms"], int) and receipt["outage_hold_ms"] >= 10000,
            "Tor outage was not held for the qualification minimum")
    require(isinstance(receipt["proxy_loss_to_local_boundary_ms"], int)
            and 0 < receipt["proxy_loss_to_local_boundary_ms"] <= 5000,
            "local route-loss observation exceeded five seconds")
    require(receipt["proxy_loss_to_local_boundary_ms"]
            < receipt["proxy_loss_to_offline_ms"],
            "auxiliary local loss did not precede authoritative carrier loss")
    require(isinstance(receipt["outage_agent_socket_sample_count"], int)
            and receipt["outage_agent_socket_sample_count"] >= 10,
            "Tor outage has fewer than ten route-leak samples")
    require(isinstance(receipt["outage_agent_socket_samples_sha256"], str)
            and HEX_64.fullmatch(receipt["outage_agent_socket_samples_sha256"]) is not None,
            "Tor outage socket sample digest is malformed")

    configuration = receipt["tor_configuration"]
    require(isinstance(configuration, list)
            and len(configuration) == 11
            and all(isinstance(line, str) for line in configuration),
            "normalized Tor configuration is malformed")
    expected_configuration = [
        "AvoidDiskWrites 1",
        "ClientOnly 1",
        "ClientUseIPv6 0",
        "CookieAuthentication 1",
        "CookieAuthFile <RUN_ROOT>/control.authcookie",
        "ControlSocket <RUN_ROOT>/control.sock",
        "DataDirectory <RUN_ROOT>/tor-data",
        "SafeSocks 0",
        "SocksPolicy accept 127.0.0.1",
        "SocksPolicy reject *",
        f"SocksPort {proxy}",
    ]
    require(configuration == expected_configuration,
            "normalized Tor configuration differs from the qualified policy")
    require(receipt["tor_configuration_sha256"] == canonical_digest(configuration),
            "normalized Tor configuration digest mismatch")
    require(receipt["tor_invocation"]
            == ["--defaults-torrc", "/dev/null", "-f", "<RUN_ROOT>/torrc"],
            "Tor invocation drifted")
    try:
        completed = datetime.datetime.fromisoformat(str(receipt["utc_completed"]))
    except ValueError as error:
        raise RuntimeError("receipt completion time is not ISO 8601") from error
    require(completed.tzinfo is not None and completed.utcoffset() == datetime.timedelta(0),
            "receipt completion time is not UTC")
    if runner is not None:
        require(receipt["operator_tor_smoke_sha256"] == digest(runner),
                "operator Tor runner digest mismatch")
    return receipt


def self_test() -> int:
    proxy = "127.0.0.1:39060"
    configuration = [
        "AvoidDiskWrites 1", "ClientOnly 1", "ClientUseIPv6 0", "CookieAuthentication 1",
        "CookieAuthFile <RUN_ROOT>/control.authcookie", "ControlSocket <RUN_ROOT>/control.sock",
        "DataDirectory <RUN_ROOT>/tor-data", "SafeSocks 0", "SocksPolicy accept 127.0.0.1",
        "SocksPolicy reject *", "SocksPort 127.0.0.1:39060",
    ]
    socket_live = {"phase": "initial", "tcp_remote_endpoints": [proxy], "udp_socket_count": 0}
    socket_out = {"phase": "outage-final", "tcp_remote_endpoints": [], "udp_socket_count": 0}
    socket_recovered = dict(socket_live, phase="recovered")
    circuit = {
        "bootstrap_progress": 100, "circuit_hop_count": 3,
        "circuit_path_sha256": "1" * 64, "circuit_purpose": "GENERAL",
        "phase": "initial",
        "public_tcp_remote_count": 2, "public_tcp_remote_set_sha256": "2" * 64,
        "stream_target": "8.8.8.8:443",
    }
    route_health = {
        "application": "not-sampled", "application_error": "none",
        "application_rtt_us": None, "carrier_connection": "tcp",
        "local_boundary": "reachable", "local_boundary_rtt_us": 123,
        "phase": "initial", "semantics": ROUTE_HEALTH_SEMANTICS,
        "upstream": "carrier-reported-online",
    }
    route_target = {
        "carrier_connection": "tcp", "network": "Tox/Tor", "phase": "initial",
        "probe_stage": "complete", "semantics": ROUTE_TARGET_SEMANTICS,
        "socks_reply_code": 0, "target_health": "reachable",
        "target_rtt_us": 456, "target_source": "configured-tcp-relay-0",
    }
    target_circuit = {
        "circuit_hop_count": 3, "circuit_path_sha256": "8" * 64,
        "circuit_purpose": "CONFLUX_LINKED", "control_authenticated": True,
        "phase": "initial",
        "source_port_was_new": True, "stream_id_sha256": "9" * 64,
        "stream_target": "8.8.8.8:443",
        "target_source": "configured-tcp-relay-0",
    }
    receipt: dict[str, object] = {
        "agent_socket_observations": [socket_live, socket_out, socket_recovered],
        "carrier": "tcp", "circuit_observations": [circuit, dict(circuit, phase="recovered")],
        "direct_relay_socket_observed": False,
        "dns_policy": "iotox-native-dns-disabled;numeric-relays-only;tor-directory-network-owned-by-tor",
        "fixture": "operator-owned-tor-public-numeric-relay", "initial_online_ms": 1000,
        "iotox_sha256": "3" * 64, "iotox_version": "IoTox 0.45.0 rev0045",
        "native_udp_socket_observed": False, "network": "Tox/Tor",
        "node_records": [{"address": "8.8.8.8", "port": 443, "public_key": "A" * 64}],
        "nonclaims": sorted(EXPECTED_NONCLAIMS), "operator_tor_smoke_sha256": "4" * 64,
        "outage_agent_socket_sample_count": 10, "outage_agent_socket_samples_sha256": "5" * 64,
        "outage_hold_ms": 10000, "proxy_loss_to_offline_ms": 30000,
        "proxy_loss_to_local_boundary_ms": 100,
        "proxy_restart_count": 1, "proxy_restart_to_online_ms": 5000,
        "recovery_observed": True,
        "route_health_observations": [
            route_health,
            dict(route_health, phase="post-tor-exit", local_boundary="refused"),
            dict(
                route_health, phase="authoritative-offline",
                carrier_connection="offline", local_boundary="refused",
                upstream="blocked-by-local-boundary",
            ),
            dict(route_health, phase="recovered"),
        ],
        "route_target_circuit_observations": [
            target_circuit, dict(target_circuit, phase="recovered"),
        ],
        "route_target_observations": [
            route_target,
            dict(
                route_target, phase="post-tor-exit", probe_stage="proxy-connect",
                socks_reply_code=None, target_health="refused",
            ),
            dict(route_target, phase="recovered"),
        ],
        "scope": "operator-tor-public-relay-single-host-single-sample-not-anonymity-proof",
        "socks_endpoint": proxy, "source_commit": "6" * 40, "source_tree_clean": True,
        "tor_binary_path": "/nix/store/example/bin/tor", "tor_configuration": configuration,
        "tor_configuration_sha256": canonical_digest(configuration),
        "tor_invocation": ["--defaults-torrc", "/dev/null", "-f", "<RUN_ROOT>/torrc"],
        "tor_sha256": "7" * 64, "tor_version": "Tor version 0.4.8.11.",
        "total_gate_ms": 60000, "utc_completed": "2026-08-27T12:00:00+00:00",
    }
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "receipt.json"
        path.write_bytes(canonical(receipt))
        verify_receipt(path)
        receipt["native_udp_socket_observed"] = True
        path.write_bytes(canonical(receipt))
        try:
            verify_receipt(path)
        except RuntimeError:
            pass
        else:
            raise RuntimeError("verifier accepted a native UDP leak")
    print("iotox operator Tor receipt verifier self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", nargs="?", type=Path)
    parser.add_argument("--runner", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        return self_test()
    require(arguments.receipt is not None, "receipt path is required")
    verify_receipt(arguments.receipt, arguments.runner)
    print(f"operator-tor-receipt=verified:{arguments.receipt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
