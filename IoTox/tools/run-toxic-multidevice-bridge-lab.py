#!/usr/bin/env python3
"""Live Toxic <-> three-IoTox-device compatibility proof.

This is the stronger version of run-toxic-compat-bridge-lab.py. It proves a
single normal Toxic identity can interoperate with a three-device IoTox self
swarm:

  * Toxic friends every IoTox route.
  * The IoTox routes are a full Tox friendship mesh.
  * Toxic sends normal text to one bridge device.
  * That bridge device live-fans a signed bridge observation to the other
    self routes, skipping its own current route.
  * Every IoTox device commits the inbound bridge observation.
  * Every IoTox device can send a delegated normal-Tox bridge message to
    Toxic.
  * Each outbound bridge observation is fanned to the other self routes.
  * Final bridge stores on all three devices account for one inbound and three
    outbound observations.

The retained lab directory contains fresh private Tox savedata and should stay
owner-private.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import random
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Callable


DEFAULT_RECALL = "abacus abdomen abdominal abide abiding ability ablaze able\n"


def repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def load_single_device_lab_module():
    path = pathlib.Path(__file__).resolve().with_name("run-toxic-compat-bridge-lab.py")
    spec = importlib.util.spec_from_file_location("iotox_toxic_compat_lab", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


class LabError(RuntimeError):
    pass


def exact_hex(text: str, length: int) -> list[str]:
    return re.findall(
        rf"(?<![0-9A-Fa-f])([0-9A-Fa-f]{{{length}}})(?![0-9A-Fa-f])",
        text,
    )


def field(text: str, name: str) -> str | None:
    match = re.search(rf"^{re.escape(name)}=(.*)$", text, re.M)
    return match.group(1).strip() if match else None


def numeric_field(text: str, name: str) -> int:
    value = field(text, name)
    if value is None:
        raise LabError(f"missing numeric field {name}")
    try:
        return int(value)
    except ValueError as exc:
        raise LabError(f"field {name} is not numeric: {value}") from exc


def extra_outbound_retry_records(
    outbound_proofs: list[dict[str, object]], labels: list[str]
) -> dict[str, int]:
    extra: dict[str, int] = {label: 0 for label in labels}
    for proof in outbound_proofs:
        sender = str(proof.get("sender", ""))
        attempt = int(proof.get("attempt", 1) or 1)
        if sender in extra and attempt > 1:
            extra[sender] += attempt - 1
    return extra


def first_line(text: str) -> str:
    stripped = text.strip()
    return stripped.splitlines()[0] if stripped else "ok"


def command_succeeded_as_send(text: str) -> bool:
    lowered = text.lower()
    return not any(
        marker in lowered
        for marker in [
            "error",
            "not connected",
            "failed",
            "unavailable",
            "friend-not-found",
            "not-found",
            "offline",
        ]
    )


def parse_outbound_message_id(journal: str, body: str) -> str | None:
    for line in journal.splitlines():
        if "direction=outgoing" not in line or f"body={body}" not in line:
            continue
        match = re.search(r"message-id=([0-9]+)", line)
        if match:
            return match.group(1)
    return None


def has_receipt(journal: str, message_id: str) -> bool:
    needle = f"direction=receipt kind=normal message-id={message_id} "
    return needle in journal


def run_iotox_raw(
    binary: pathlib.Path,
    args: list[str],
    *,
    input_text: str | None = None,
    timeout: float = 20.0,
    check: bool = True,
) -> str:
    proc = subprocess.run(
        [str(binary)] + args,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    output = proc.stdout + proc.stderr
    if check and proc.returncode != 0:
        raise LabError(f"IoTox command failed rc={proc.returncode}: {args}\n{output}")
    return output


@dataclass
class ToxicPaths:
    root: pathlib.Path
    toxic_profile: pathlib.Path
    toxic_conf: pathlib.Path
    toxic_nodes: pathlib.Path
    toxic_logs: pathlib.Path
    toxic_raw: pathlib.Path
    toxic_screen: pathlib.Path


@dataclass
class Device:
    label: str
    binary: pathlib.Path
    lab: pathlib.Path
    runtime: pathlib.Path
    state: pathlib.Path
    identity: pathlib.Path
    ledger: pathlib.Path
    command_store: pathlib.Path
    log: pathlib.Path
    bridge_store: pathlib.Path
    delegation: pathlib.Path
    address: str = ""
    tox_key: str = ""
    principal: str = ""
    proc: subprocess.Popen[bytes] | None = None

    @classmethod
    def create(
        cls,
        label: str,
        binary: pathlib.Path,
        lab: pathlib.Path,
        runtime_base: pathlib.Path,
    ) -> "Device":
        root = lab / label
        root.mkdir(parents=True, exist_ok=False)
        return cls(
            label=label,
            binary=binary,
            lab=lab,
            runtime=runtime_base / label,
            state=root / "device.toxsave",
            identity=root / "device.identity",
            ledger=root / "authority.ledger",
            command_store=root / "commands.store",
            log=lab / f"{label}.log",
            bridge_store=root / "tox.bridge",
            delegation=lab / f"{label}.person.delegate",
        )

    def start(self, run_ms: int, native_tcp_only: bool) -> None:
        log = self.log.open("wb")
        self._log_handle = log
        command = [
            str(self.binary),
            "run",
            "--runtime",
            str(self.runtime),
            "--state",
            str(self.state),
            "--identity",
            str(self.identity),
            "--authority-ledger",
            str(self.ledger),
            "--command-store",
            str(self.command_store),
            "--run-ms",
            str(run_ms),
        ]
        if native_tcp_only:
            command.append("--native-tcp-only")
        self.proc = subprocess.Popen(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        print(f"[iotox-{self.label}] pid={self.proc.pid}", flush=True)

    def run(
        self,
        args: list[str],
        *,
        input_text: str | None = None,
        timeout: float = 20.0,
        check: bool = True,
    ) -> str:
        proc = subprocess.run(
            [
                str(self.binary),
                "--runtime",
                str(self.runtime),
                "--timeout-ms",
                "10000",
            ]
            + args,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        output = proc.stdout + proc.stderr
        if check and proc.returncode != 0:
            raise LabError(
                f"{self.label} command failed rc={proc.returncode}: {args}\n{output}"
            )
        return output

    def run_person(
        self,
        args: list[str],
        *,
        timeout: float = 20.0,
        check: bool = True,
    ) -> str:
        proc = subprocess.run(
            [
                str(self.binary),
                "--identity",
                str(self.identity),
                "--runtime",
                str(self.runtime),
                "--timeout-ms",
                "10000",
            ]
            + args,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        output = proc.stdout + proc.stderr
        if check and proc.returncode != 0:
            raise LabError(
                f"{self.label} person command failed rc={proc.returncode}: {args}\n{output}"
            )
        return output

    def peer_messages(self, peer_key: str) -> str:
        return self.run(["peer-messages", peer_key], check=False, timeout=10)

    def requests_text(self) -> str:
        return self.run(["requests"], check=False, timeout=10)

    def status_text(self) -> str:
        return self.run(["status"], check=False, timeout=10)

    def friend_events_text(self) -> str:
        return self.run(["friend-events"], check=False, timeout=10)

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            try:
                self.run(["stop"], timeout=5, check=False)
            except Exception:
                pass
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
        handle = getattr(self, "_log_handle", None)
        if handle is not None:
            handle.close()


class Lab:
    def __init__(self, args: argparse.Namespace):
        self.compat = load_single_device_lab_module()
        self.iotox = self.compat.resolve_iotox(args.iotox, not args.no_iotox_auto_build)
        self.toxic_binary = self.compat.resolve_toxic(args.toxic, args.toxic_nixpkgs)
        if args.lab:
            self.root = pathlib.Path(args.lab).resolve()
            if self.root.exists() and any(self.root.iterdir()):
                raise LabError(f"--lab path already exists and is not empty: {self.root}")
            self.root.mkdir(parents=True, exist_ok=True)
        else:
            self.root = pathlib.Path(tempfile.mkdtemp(prefix="iotox-toxic-multidev-lab-"))
        os.chmod(self.root, 0o700)
        self.nonce = "".join(random.choice("abcdef0123456789") for _ in range(10))
        self.args = args
        self.runtime_root = self.compat.short_runtime_dir("multidev", self.root)
        self.devices = [
            Device.create(label, self.iotox, self.root, self.runtime_root)
            for label in ["a", "b", "c"]
        ]
        for dirname in ["toxic-home", "toxic-xdg-config", "toxic-xdg-data", "toxic-logs"]:
            (self.root / dirname).mkdir(parents=True, exist_ok=True)
        self.toxic_paths = ToxicPaths(
            root=self.root,
            toxic_profile=self.root / "toxic-home" / "toxic_profile.tox",
            toxic_conf=self.root / "toxic.conf",
            toxic_nodes=self.root / "DHTnodes.json",
            toxic_logs=self.root / "toxic-logs",
            toxic_raw=self.root / "toxic.pty.raw",
            toxic_screen=self.root / "toxic.screen.txt",
        )
        self.compat.write_toxic_conf(self.toxic_paths)
        self.toxic = self.compat.ToxicPTY(
            self.toxic_binary, self.toxic_paths, args.toxic_force_tcp
        )
        self.toxic_address = ""
        self.toxic_key = ""
        self.roster = self.root / "self.roster"
        self.card = self.root / "person.card"
        self.summary_path = self.root / "proof-summary.json"

    def check_children(self, description: str) -> None:
        for device in self.devices:
            if device.proc and device.proc.poll() is not None:
                raise LabError(
                    f"{device.label} exited while waiting for {description}: "
                    f"rc={device.proc.returncode}\n"
                    + device.log.read_text(errors="replace")[-4000:]
                )

    def wait(
        self,
        description: str,
        predicate: Callable[[], object],
        *,
        timeout: float | None = None,
        step: float = 1.0,
    ) -> object:
        deadline = time.time() + (timeout if timeout is not None else self.args.wait_timeout)
        last_report = time.time()
        last_error: Exception | None = None
        while time.time() < deadline:
            try:
                result = predicate()
                if result:
                    return result
            except Exception as exc:
                last_error = exc
            self.check_children(description)
            if time.time() - last_report > 30:
                print(f"[wait] {description}...", flush=True)
                last_report = time.time()
            time.sleep(step)
        raise LabError(f"timeout waiting for {description}; last={last_error}")

    def toxic_log_text(self) -> str:
        return self.compat.read_logs(self.toxic_paths.toxic_logs)

    def wait_toxic_evidence(self, body: str, timeout: float | None = None) -> None:
        self.wait(
            f"Toxic log/display contains {body}",
            lambda: (self.toxic.read(0.5) or True)
            and (body in self.toxic_log_text() or body in self.toxic.screen()),
            timeout=timeout,
            step=0.5,
        )

    def wait_peer_message(
        self,
        receiver: Device,
        peer_key: str,
        needle: str,
        *,
        timeout: float | None = None,
    ) -> str:
        journal = ""

        def check() -> str | bool:
            nonlocal journal
            journal = receiver.peer_messages(peer_key)
            return journal if needle in journal else False

        self.wait(
            f"{receiver.label} peer message from {peer_key[:6]} contains {needle[:24]}",
            check,
            timeout=timeout,
            step=1.0,
        )
        return journal

    def toxic_tail(self, limit: int = 6000) -> str:
        try:
            self.toxic.read(0.5)
            return self.toxic.screen()[-limit:]
        except Exception as exc:
            return f"<unable to read Toxic PTY: {exc}>"

    def device_dossier(
        self,
        device: Device,
        *,
        latest_requests: str | None = None,
        include_toxic: bool = True,
    ) -> str:
        sections = [
            f"device={device.label}",
            f"tox-key={device.tox_key}",
            f"principal={device.principal}",
        ]
        requests = latest_requests if latest_requests is not None else device.requests_text()
        sections.append("requests-begin\n" + requests[-4000:] + "\nrequests-end")
        sections.append(
            "friend-events-begin\n"
            + device.friend_events_text()[-4000:]
            + "\nfriend-events-end"
        )
        sections.append(
            "status-begin\n" + device.status_text()[-4000:] + "\nstatus-end"
        )
        try:
            sections.append(
                "agent-log-tail-begin\n"
                + device.log.read_text(errors="replace")[-4000:]
                + "\nagent-log-tail-end"
            )
        except OSError as exc:
            sections.append(f"agent-log-tail=<unavailable: {exc}>")
        if include_toxic:
            sections.append(
                "toxic-screen-tail-begin\n"
                + self.toxic_tail()
                + "\ntoxic-screen-tail-end"
            )
            try:
                sections.append(
                    "toxic-autolog-tail-begin\n"
                    + self.toxic_log_text()[-4000:]
                    + "\ntoxic-autolog-tail-end"
                )
            except Exception as exc:
                sections.append(f"toxic-autolog-tail=<unavailable: {exc}>")
        return "\n".join(sections)

    def wait_device_request(
        self,
        receiver: Device,
        peer_key: str,
        description: str,
        *,
        timeout: float | None = None,
        include_toxic: bool = True,
        on_retry: Callable[[int], None] | None = None,
        retry_label: str = "friend request",
    ) -> None:
        latest_requests = ""
        retry_count = 0
        last_retry = time.time()
        latest_retry_error = ""

        def check() -> bool:
            nonlocal latest_requests, retry_count, last_retry, latest_retry_error
            if include_toxic:
                self.toxic.read(0.2)
            now = time.time()
            if on_retry is not None and now - last_retry >= self.args.request_retry_interval:
                retry_count += 1
                print(
                    f"[retry] resending {retry_label} attempt={retry_count + 1}",
                    flush=True,
                )
                try:
                    on_retry(retry_count + 1)
                    latest_retry_error = ""
                except Exception as exc:
                    latest_retry_error = str(exc)
                last_retry = now
            try:
                latest_requests = receiver.requests_text()
            except Exception as exc:
                latest_requests = f"<requests command failed: {exc}>"
                return False
            return peer_key.upper() in latest_requests.upper()

        try:
            self.wait(description, check, timeout=timeout, step=1.0)
        except LabError as exc:
            raise LabError(
                f"timeout waiting for {description}\n"
                + self.device_dossier(
                    receiver,
                    latest_requests=(
                        latest_requests
                        + (
                            "\nretry-error="
                            + latest_retry_error
                            if latest_retry_error
                            else ""
                        )
                    ),
                    include_toxic=include_toxic,
                )
            ) from exc

    def wait_toxic_receipt(self, sender: Device, message_id: str) -> None:
        self.wait(
            f"{sender.label} has Toxic read receipt {message_id}",
            lambda: has_receipt(sender.peer_messages(self.toxic_key), message_id),
            timeout=self.args.receipt_timeout,
            step=1.0,
        )

    def wait_normal_toxic_delivery(
        self, sender: Device, body: str, *, timeout: float | None = None
    ) -> str:
        message_id = ""

        def outbound_id() -> str | bool:
            nonlocal message_id
            journal = sender.peer_messages(self.toxic_key)
            found = parse_outbound_message_id(journal, body)
            if found:
                message_id = found
                return found
            return False

        self.wait(
            f"{sender.label} journal records outbound normal Toxic body {body}",
            outbound_id,
            timeout=timeout,
            step=0.5,
        )
        self.wait_toxic_receipt(sender, message_id)
        try:
            self.wait_toxic_evidence(body, timeout=self.args.toxic_ui_timeout)
        except LabError as exc:
            print(
                "[toxic] read receipt observed but UI/log evidence was not retained; "
                f"continuing with c-toxcore receipt evidence ({first_line(str(exc))})",
                flush=True,
            )
        return message_id

    def send_normal_to_toxic_with_delivery(
        self, sender: Device, body: str, *, timeout: float | None = None
    ) -> str:
        result = ""

        def attempt() -> bool:
            nonlocal result
            result = sender.run(
                ["message", f"key:{self.toxic_key}", body],
                check=False,
                timeout=10,
            )
            return command_succeeded_as_send(result)

        self.wait(
            f"{sender.label} normal send to Toxic accepted",
            attempt,
            timeout=timeout,
            step=2.0,
        )
        return self.wait_normal_toxic_delivery(sender, body, timeout=timeout)

    def start_devices(self) -> None:
        print(f"[lab] {self.root}", flush=True)
        print(f"[iotox] binary={self.iotox}", flush=True)
        print(f"[toxic] binary={self.toxic_binary}", flush=True)
        for device in self.devices:
            device.start(self.args.run_ms, self.args.toxic_force_tcp)
        for device in self.devices:
            self.wait(
                f"{device.label} ping",
                lambda device=device: "pong"
                in device.run(["ping"], check=False, timeout=5).lower(),
                timeout=self.args.start_timeout,
                step=0.5,
            )
            device.address = exact_hex(device.run(["address"]), 76)[0].upper()
            device.tox_key = device.address[:64]
            identity = device.run(["identity"])
            device.principal = field(identity, "device-public-key") or exact_hex(identity, 64)[0].upper()
            print(
                f"[iotox-{device.label}] tox_key={device.tox_key} "
                f"principal={device.principal}",
                flush=True,
            )
        if len({device.tox_key for device in self.devices}) != 3:
            raise LabError("IoTox devices did not have distinct Tox keys")
        if len({device.principal for device in self.devices}) != 3:
            raise LabError("IoTox devices did not have distinct stable principals")

    def start_toxic(self) -> None:
        self.toxic.start()
        self.toxic.read(2.0)
        if "encrypt" in self.toxic.screen().lower():
            print("[toxic] first-run encryption prompt -> n", flush=True)
            self.toxic.send("n\r")
        self.toxic.wait_for(lambda s: "Home" in s and "Contacts" in s, "initial screen", 30)
        self.toxic.send("/nick ToxicMulti\r")
        self.toxic.send("/status online\r")
        self.toxic.send("/myid\r")
        address = str(
            self.toxic.wait_for(
                lambda s: (exact_hex(s, 76) or [None])[-1],
                "Toxic /myid",
                30,
            )
        ).upper()
        self.toxic_address = address
        self.toxic_key = address[:64]
        print(f"[toxic] key={self.toxic_key}", flush=True)

    def friend_toxic_to_device(self, device: Device, *, bridge_inbound: bool) -> str | None:
        if self.args.toxic_force_tcp:
            def send_device_request(attempt: int) -> str:
                suffix = "" if attempt == 1 else f"-retry{attempt}"
                if attempt > 1:
                    device.run(
                        ["transport-peer-remove", f"key:{self.toxic_key}"],
                        check=False,
                    )
                return device.run(
                    [
                        "transport-peer-request",
                        self.toxic_address,
                        f"{device.label}-to-toxic-force-tcp-{self.nonce}{suffix}",
                    ]
                )

            send_device_request(1)
            try:
                req_id = self.compat.wait_for_toxic_friend_request(
                    self.toxic,
                    device.tox_key,
                    timeout=self.args.request_timeout,
                    on_retry=send_device_request,
                    retry_interval=self.args.request_retry_interval,
                    retry_label=f"{device.label}->Toxic force-TCP friend request",
                )
            except Exception as exc:
                raise LabError(
                    f"Toxic did not see {device.label} friend request: {exc}\n"
                    + self.device_dossier(device, include_toxic=True)
                ) from exc
            self.toxic.send(f"/accept {req_id}\r")
            self.toxic.wait_for(
                lambda s: "Friend request accepted." in s,
                f"Toxic accepts {device.label} request",
                30,
            )
            print(
                f"[friend] Toxic accepted {device.label} request id={req_id}",
                flush=True,
            )
        else:
            def send_toxic_request(attempt: int) -> None:
                suffix = "" if attempt == 1 else f"-retry{attempt}"
                self.toxic.send(
                    f"/add {device.address} toxic-to-{device.label}-{self.nonce}{suffix}\r"
                )

            send_toxic_request(1)
            self.wait_device_request(
                device,
                self.toxic_key,
                f"{device.label} sees Toxic request",
                timeout=self.args.request_timeout,
                include_toxic=True,
                on_retry=send_toxic_request,
                retry_label=f"Toxic->{device.label} /add",
            )
            device.run(["request-accept", self.toxic_key])
        probe = f"{device.label}-to-toxic-probe-{self.nonce}"
        self.send_normal_to_toxic_with_delivery(
            device, probe, timeout=self.args.connect_timeout
        )
        print(f"[friend] {device.label}<->Toxic ready", flush=True)

        if not bridge_inbound:
            return None
        inbound = f"toxic-to-{device.label}-inbound-{self.nonce}"
        attempts = [
            "\x0f\r" + inbound + "\r",
            "\x0f" + inbound + "\r",
            "\x10" + inbound + "\r",
            inbound + "\r",
            "\x0f\x0f" + inbound + "\r",
        ]
        for attempt, payload in enumerate(attempts, 1):
            self.toxic.send(payload)
            print(f"[toxic] inbound attempt to {device.label} #{attempt}", flush=True)
            try:
                self.wait_peer_message(
                    device,
                    self.toxic_key,
                    inbound,
                    timeout=self.args.inbound_attempt_timeout,
                )
                print(
                    f"[toxic] {device.label} recorded inbound Toxic text",
                    flush=True,
                )
                return inbound
            except LabError:
                continue
        raise LabError(f"Toxic did not send inbound text to {device.label}")

    def friend_self_mesh(self) -> None:
        pairs = [
            (self.devices[0], self.devices[1]),
            (self.devices[0], self.devices[2]),
            (self.devices[1], self.devices[2]),
        ]
        for left, right in pairs:
            def send_mesh_request(
                attempt: int,
                left: Device = left,
                right: Device = right,
            ) -> str:
                suffix = "" if attempt == 1 else f"-retry{attempt}"
                if attempt > 1:
                    left.run(
                        ["transport-peer-remove", f"key:{right.tox_key}"],
                        check=False,
                    )
                return left.run(
                    [
                        "transport-peer-request",
                        right.address,
                        f"self-mesh-{left.label}-{right.label}-{self.nonce}{suffix}",
                    ]
                )

            send_mesh_request(1)
            self.wait_device_request(
                right,
                left.tox_key,
                f"{right.label} sees {left.label} request",
                timeout=self.args.request_timeout,
                include_toxic=False,
                on_retry=send_mesh_request,
                retry_label=f"{left.label}->{right.label} self-mesh request",
            )
            right.run(["request-accept", left.tox_key])
            body = f"mesh-{left.label}-to-{right.label}-{self.nonce}"
            self.wait(
                f"{left.label} mesh send to {right.label}",
                lambda left=left, right=right, body=body: command_succeeded_as_send(
                    left.run(
                        ["message", f"key:{right.tox_key}", body],
                        check=False,
                        timeout=10,
                    )
                ),
                timeout=self.args.connect_timeout,
                step=2.0,
            )
            self.wait_peer_message(right, left.tox_key, body, timeout=self.args.visible_timeout)
            reverse = f"mesh-{right.label}-to-{left.label}-{self.nonce}"
            self.wait(
                f"{right.label} mesh send to {left.label}",
                lambda left=left, right=right, reverse=reverse: command_succeeded_as_send(
                    right.run(
                        ["message", f"key:{left.tox_key}", reverse],
                        check=False,
                        timeout=10,
                    )
                ),
                timeout=self.args.connect_timeout,
                step=2.0,
            )
            self.wait_peer_message(left, right.tox_key, reverse, timeout=self.args.visible_timeout)
            print(f"[mesh] {left.label}<->{right.label} ready", flush=True)

    def create_self_artifacts(self) -> None:
        run_iotox_raw(
            self.iotox,
            [
                "self-swarm",
                "create-recall-stdin",
                str(self.roster),
                self.devices[0].label,
                self.devices[0].principal,
                self.devices[0].tox_key,
                "operator",
                "interactive.terminal",
            ],
            input_text=self.args.recall_phrase,
        )
        for device in self.devices[1:]:
            run_iotox_raw(
                self.iotox,
                [
                    "self-swarm",
                    "join-recall-stdin",
                    str(self.roster),
                    device.label,
                    device.principal,
                    device.tox_key,
                    "operator",
                    "interactive.terminal",
                ],
                input_text=self.args.recall_phrase,
            )
        card = run_iotox_raw(
            self.iotox,
            ["person", "card-recall-stdin", str(self.roster), str(self.card)],
            input_text=self.args.recall_phrase,
        )
        print(
            f"[self] card {first_line(card)} routes={field(card, 'routes')}",
            flush=True,
        )
        for device in self.devices:
            delegation = run_iotox_raw(
                self.iotox,
                [
                    "person",
                    "delegate-recall-stdin",
                    str(self.roster),
                    device.label,
                    str(device.delegation),
                ],
                input_text=self.args.recall_phrase,
            )
            print(
                f"[self] delegation {device.label}: {first_line(delegation)}",
                flush=True,
            )

    def receive_bridge_on_all(self, payload_hex: str, delegation: pathlib.Path) -> None:
        for device in self.devices:
            receive = run_iotox_raw(
                self.iotox,
                [
                    "person",
                    "tox-bridge-receive",
                    payload_hex,
                    str(delegation),
                    str(device.bridge_store),
                ],
            )
            if "iotox-person-tox-bridge-receive-v1" not in receive:
                raise LabError(receive)

    def fanout_inbound(self, inbound_body: str) -> dict[str, object]:
        bridge = self.devices[0]
        output = bridge.run_person(
            [
                "person",
                "tox-bridge-fanout-in-delegated",
                "--bridge-store",
                str(bridge.bridge_store),
                str(self.card),
                str(bridge.delegation),
                self.toxic_key,
                "message",
                inbound_body,
            ],
            timeout=30,
        )
        print(f"[fanout-in] {first_line(output)}", flush=True)
        payload = field(output, "payload-hex")
        message_id = field(output, "message-id")
        if payload is None or message_id is None:
            raise LabError("inbound fanout did not expose payload/message id\n" + output)
        if "local-bridge=committed duplicate=0" not in output:
            raise LabError("inbound fanout did not commit sender bridge store\n" + output)
        if f"self-skip route={bridge.tox_key}" not in output:
            raise LabError("inbound fanout did not skip current route\n" + output)
        for device in self.devices[1:]:
            if f"self-sent route={device.tox_key}" not in output:
                raise LabError(f"inbound fanout did not send to {device.label}\n" + output)
            self.wait_peer_message(
                device,
                bridge.tox_key,
                message_id,
                timeout=self.args.visible_timeout,
            )
        self.receive_bridge_on_all(payload, bridge.delegation)
        print("[fanout-in] all devices committed inbound bridge observation", flush=True)
        return {"payload_hex": payload, "message_id": message_id}

    def bridge_send_from_device(self, sender: Device) -> dict[str, object]:
        failures: list[str] = []
        for attempt in range(1, self.args.bridge_send_attempts + 1):
            suffix = "" if attempt == 1 else f"-retry{attempt}"
            body = f"{sender.label}-bridge-to-toxic-{self.nonce}{suffix}"
            output = sender.run_person(
                [
                    "person",
                    "tox-bridge-send-out-delegated",
                    "--bridge-store",
                    str(sender.bridge_store),
                    str(self.card),
                    str(sender.delegation),
                    f"key:{self.toxic_key}",
                    "message",
                    body,
                ],
                timeout=30,
            )
            print(
                f"[send-out-{sender.label}] attempt={attempt} {first_line(output)}",
                flush=True,
            )
            payload = field(output, "payload-hex")
            bridge_message_id = field(output, "message-id")
            transport_match = re.search(
                r"^normal-tox-sent friend=[0-9]+ transport-message-id=([0-9]+)$",
                output,
                re.M,
            )
            normal_message_id = transport_match.group(1) if transport_match else None
            if payload is None or bridge_message_id is None or normal_message_id is None:
                raise LabError("bridge send output missing required fields\n" + output)
            if "local-bridge=committed duplicate=0" not in output:
                raise LabError(
                    f"{sender.label} bridge send did not commit sender bridge store\n"
                    + output
                )
            if f"self-skip route={sender.tox_key}" not in output:
                raise LabError(f"{sender.label} bridge send did not skip current route\n" + output)
            for other in self.devices:
                if other is sender:
                    continue
                if f"self-sent route={other.tox_key}" not in output:
                    raise LabError(
                        f"{sender.label} bridge send did not fan out to {other.label}\n"
                        + output
                    )
            try:
                self.wait_toxic_receipt(sender, normal_message_id)
                try:
                    self.wait_toxic_evidence(body, timeout=self.args.toxic_ui_timeout)
                except LabError as exc:
                    print(
                        f"[send-out-{sender.label}] Toxic read receipt observed but "
                        "UI/log evidence was not retained; continuing "
                        f"({first_line(str(exc))})",
                        flush=True,
                    )
                for other in self.devices:
                    if other is sender:
                        continue
                    self.wait_peer_message(
                        other,
                        sender.tox_key,
                        bridge_message_id,
                        timeout=self.args.visible_timeout,
                    )
                self.receive_bridge_on_all(payload, sender.delegation)
                print(
                    f"[send-out-{sender.label}] Toxic receipt and self-fanout observed",
                    flush=True,
                )
                return {
                    "sender": sender.label,
                    "body": body,
                    "payload_hex": payload,
                    "bridge_message_id": bridge_message_id,
                    "normal_message_id": normal_message_id,
                    "attempt": attempt,
                    "prior_failures": failures,
                }
            except LabError as exc:
                failures.append(str(exc))
                print(
                    f"[send-out-{sender.label}] attempt={attempt} lacked final Toxic evidence; retrying",
                    flush=True,
                )
        raise LabError(
            f"{sender.label} did not deliver a bridge message to Toxic after "
            f"{self.args.bridge_send_attempts} attempts\n" + "\n".join(failures)
        )

    def assert_final_status(
        self, outbound_proofs: list[dict[str, object]]
    ) -> dict[str, dict[str, int | str]]:
        extra_outbound_by_sender = extra_outbound_retry_records(
            outbound_proofs, [device.label for device in self.devices]
        )
        statuses: dict[str, dict[str, int | str]] = {}
        for device in self.devices:
            status = run_iotox_raw(
                self.iotox,
                ["person", "tox-bridge-status", str(device.bridge_store)],
            )
            entries = numeric_field(status, "entries")
            inbound = numeric_field(status, "inbound")
            outbound = numeric_field(status, "outbound")
            content_free = numeric_field(status, "content-free")
            expected_outbound = 3 + extra_outbound_by_sender.get(device.label, 0)
            expected_entries = 1 + expected_outbound
            if (
                entries != expected_entries
                or inbound != 1
                or outbound != expected_outbound
                or content_free != 1
            ):
                raise LabError(
                    f"unexpected bridge status for {device.label}; "
                    f"expected entries={expected_entries} inbound=1 "
                    f"outbound={expected_outbound} content-free=1\n"
                    + status
                )
            statuses[device.label] = {
                "entries": entries,
                "inbound": inbound,
                "outbound": outbound,
                "content_free": content_free,
                "extra_outbound_retry_records": extra_outbound_by_sender.get(
                    device.label, 0
                ),
                "raw": status,
            }
            print(
                f"[status-{device.label}] entries={entries} inbound=1 "
                f"outbound={outbound} extra-retry-records="
                f"{extra_outbound_by_sender.get(device.label, 0)}",
                flush=True,
            )
        return statuses

    def run(self) -> dict[str, object]:
        self.start_devices()
        self.start_toxic()
        inbound = self.friend_toxic_to_device(self.devices[0], bridge_inbound=True)
        if inbound is None:
            raise LabError("inbound bridge body was not produced")
        for device in self.devices[1:]:
            self.friend_toxic_to_device(device, bridge_inbound=False)
        self.friend_self_mesh()
        self.create_self_artifacts()
        inbound_proof = self.fanout_inbound(inbound)
        outbound_proofs = [self.bridge_send_from_device(device) for device in self.devices]
        final_status = self.assert_final_status(outbound_proofs)
        summary = {
            "schema": "iotox-toxic-multidevice-compat-live-proof-v1",
            "lab": str(self.root),
            "iotox_binary": str(self.iotox),
            "toxic_binary": str(self.toxic_binary),
            "toxic_force_tcp": self.args.toxic_force_tcp,
            "nonce": self.nonce,
            "toxic_key": self.toxic_key,
            "iotox_devices": {
                device.label: {
                    "tox_key": device.tox_key,
                    "principal": device.principal,
                }
                for device in self.devices
            },
            "proofs": {
                "toxic_friended_all_iotox_devices": True,
                "iotox_self_routes_full_mesh": True,
                "toxic_to_bridge_device_normal_text": inbound,
                "bridge_device_live_fanout_reached_other_self_devices": inbound_proof,
                "all_devices_committed_inbound_bridge_observation": True,
                "each_iotox_device_delivered_normal_tox_to_toxic": outbound_proofs,
                "live_bridge_commands_committed_sender_bridge_store": True,
                "outbound_observations_fanned_to_other_self_devices": True,
                "final_bridge_status_per_device": final_status,
            },
            "evidence_files": {
                "proof_summary": str(self.summary_path),
                "toxic_logs": str(self.toxic_paths.toxic_logs),
                "toxic_pty_raw": str(self.toxic_paths.toxic_raw),
                "toxic_screen": str(self.toxic_paths.toxic_screen),
                "runtime_root": str(self.runtime_root),
                "device_logs": {device.label: str(device.log) for device in self.devices},
                "bridge_stores": {
                    device.label: str(device.bridge_store) for device in self.devices
                },
            },
            "private_state_warning": (
                "lab contains fresh private Tox savedata and should stay owner-private"
            ),
        }
        self.summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2), flush=True)
        return summary

    def stop(self) -> None:
        try:
            self.toxic.dump_evidence()
            self.toxic.stop()
        finally:
            for device in self.devices:
                device.stop()


def parse_args(argv: list[str]) -> argparse.Namespace:
    compat = load_single_device_lab_module()
    parser = argparse.ArgumentParser(
        description="Run a live Toxic <-> three-IoTox-device bridge proof."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--iotox", help="IoTox binary to test")
    parser.add_argument(
        "--no-iotox-auto-build",
        action="store_true",
        help="do not auto-build source-linked IoTox when --iotox is omitted",
    )
    parser.add_argument("--toxic", help="Toxic binary to use")
    parser.add_argument(
        "--toxic-nixpkgs",
        default=compat.PINNED_TOXIC_NIXPKGS,
        help="Nixpkgs revision used to build Toxic when --toxic is omitted",
    )
    parser.add_argument("--lab", help="empty/private lab directory to use")
    parser.add_argument(
        "--toxic-force-tcp",
        action="store_true",
        help=(
            "launch Toxic with -t and all IoTox devices with --native-tcp-only; "
            "devices initiate friendship and Toxic accepts"
        ),
    )
    parser.add_argument("--run-ms", type=int, default=1_200_000)
    parser.add_argument("--start-timeout", type=float, default=60.0)
    parser.add_argument("--wait-timeout", type=float, default=300.0)
    parser.add_argument("--request-timeout", type=float, default=300.0)
    parser.add_argument("--request-retry-interval", type=float, default=45.0)
    parser.add_argument("--connect-timeout", type=float, default=300.0)
    parser.add_argument("--visible-timeout", type=float, default=180.0)
    parser.add_argument("--receipt-timeout", type=float, default=180.0)
    parser.add_argument(
        "--toxic-ui-timeout",
        type=float,
        default=15.0,
        help=(
            "optional wait for Toxic screen/autolog evidence after an authoritative "
            "read receipt has already arrived"
        ),
    )
    parser.add_argument("--inbound-attempt-timeout", type=float, default=45.0)
    parser.add_argument("--bridge-send-attempts", type=int, default=3)
    parser.add_argument("--recall-phrase", default=DEFAULT_RECALL)
    return parser.parse_args(argv)


def self_test() -> int:
    extra = extra_outbound_retry_records(
        [
            {"sender": "a", "attempt": 1},
            {"sender": "b", "attempt": 3},
            {"sender": "c", "attempt": 2},
        ],
        ["a", "b", "c"],
    )
    if extra != {"a": 0, "b": 2, "c": 1}:
        raise LabError(f"unexpected retry accounting: {extra}")
    status = (
        "iotox-person-tox-bridge-status-v1\n"
        "entries=6\n"
        "inbound=1\n"
        "outbound=5\n"
        "content-free=1\n"
    )
    if (
        numeric_field(status, "entries") != 6
        or numeric_field(status, "inbound") != 1
        or numeric_field(status, "outbound") != 5
        or numeric_field(status, "content-free") != 1
    ):
        raise LabError("bridge status numeric parser failed")
    print("iotox-toxic-multidevice-bridge-lab-self-test=pass")
    return 0


def main(argv: list[str]) -> int:
    lab: Lab | None = None
    try:
        args = parse_args(argv)
        if args.self_test:
            return self_test()
        lab = Lab(args)
        lab.run()
        return 0
    except (LabError, RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"[failed] {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        if lab is not None:
            lab.stop()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
