#!/usr/bin/env python3
"""Live IoTox <-> Toxic normal-Tox compatibility and bridge proof.

This harness intentionally uses stock Toxic as an external Tox client instead
of another IoTox process. It proves, from fresh isolated state, that:

  * Toxic can send a normal friend request to IoTox in the default route lab.
  * In the forced-TCP lab, IoTox can send a normal friend request to Toxic
    and Toxic can accept it with its stock `/accept` command.
  * IoTox can accept that request.
  * IoTox normal text reaches Toxic.
  * Toxic normal text reaches IoTox's peer message journal.
  * The observed Toxic message can be wrapped as a signed delegated
    normal-Tox compatibility bridge envelope, committed idempotently, and
    planned for outbound normal-Tox delivery.

The lab directory is mode 0700 and is kept by default because it contains the
evidence. It also contains fresh private Tox savedata; delete it deliberately
when no longer needed.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import pty
import random
import re
import select
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Callable


PINNED_TOXIC_NIXPKGS = "50ab793786d9de88ee30ec4e4c24fb4236fc2674"
DEFAULT_RECALL = "abacus abdomen abdominal abide abiding ability ablaze able\n"


ANSI_RE = re.compile(
    r"(?:\x1b\][^\x1b]*(?:\x1b\\|\x07))"
    r"|(?:\x1b\[[0-?]*[ -/]*[@-~])"
    r"|(?:\x1b[()][A-Za-z0-9])"
)


class LabError(RuntimeError):
    pass


@dataclass
class LabPaths:
    root: pathlib.Path
    runtime: pathlib.Path
    state: pathlib.Path
    identity: pathlib.Path
    ledger: pathlib.Path
    command_store: pathlib.Path
    iotox_log: pathlib.Path
    toxic_profile: pathlib.Path
    toxic_conf: pathlib.Path
    toxic_nodes: pathlib.Path
    toxic_logs: pathlib.Path
    toxic_raw: pathlib.Path
    toxic_screen: pathlib.Path
    roster: pathlib.Path
    person_card: pathlib.Path
    delegation: pathlib.Path
    bridge_store: pathlib.Path
    summary: pathlib.Path


def repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def shell_run(cmd: list[str], *, timeout: float = 120.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def executable(path: pathlib.Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def short_runtime_dir(label: str, retained_root: pathlib.Path) -> pathlib.Path:
    """Return a repo-local short runtime path for Unix-domain control sockets.

    Retained proof roots can be deeply nested under .sandwurm/massive-soak.
    IoTox's local-control socket is a Unix-domain pathname, so the runtime
    directory itself must stay short even when the evidence directory is long.
    The runtime is lab-private operational state; proof summaries and durable
    savedata stay in the caller's retained lab root.
    """

    base = repo_root() / ".sandwurm" / "tr"
    base.mkdir(parents=True, exist_ok=True)
    os.chmod(base, 0o700)
    safe_label = (re.sub(r"[^A-Za-z0-9_.-]+", "-", label).strip("-") or "lab")[:8]
    suffix = "".join(random.choice("abcdef0123456789") for _ in range(8))
    path = base / f"{safe_label}.{suffix}"
    path.mkdir(mode=0o700)
    (path / "retained-root.txt").write_text(str(retained_root.resolve()) + "\n", encoding="utf-8")
    return path


def build_source_linked_iotox() -> pathlib.Path:
    if shutil.which("nix") is None or shutil.which("git") is None or shutil.which("tar") is None:
        raise LabError("nix/git/tar are required to auto-build source-linked IoTox")
    # Build from a clean git archive. This avoids local flake evaluation
    # failures caused by runtime FIFOs or other non-regular generated files,
    # and it gives the compatibility lab the same source-linked binary used by
    # the Sandwurm route/storage qualification gates.
    root = repo_root()
    with tempfile.TemporaryDirectory(prefix="iotox-source-linked-flake-") as tmp:
        archive = subprocess.run(
            ["git", "-C", str(root), "archive", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
        )
        if archive.returncode != 0:
            raise LabError(
                "git archive HEAD failed while preparing source-linked build\n"
                + archive.stderr.decode("utf-8", errors="replace")
            )
        extract = subprocess.run(
            ["tar", "-x", "-C", tmp],
            input=archive.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
        )
        if extract.returncode != 0:
            raise LabError(
                "tar failed while preparing source-linked build\n"
                + extract.stderr.decode("utf-8", errors="replace")
            )
        result = shell_run(
            ["nix", "build", f"{tmp}#iotoxSourceLinked", "--no-link", "--print-out-paths"],
            timeout=1800,
        )
    if result.returncode != 0:
        raise LabError(
            "nix could not build source-linked IoTox\nSTDOUT:\n"
            + result.stdout
            + "\nSTDERR:\n"
            + result.stderr
        )
    out = pathlib.Path(result.stdout.strip().splitlines()[-1]) / "bin" / "iotox"
    if not executable(out):
        raise LabError(f"source-linked IoTox build did not produce an executable at {out}")
    return out.resolve()


def resolve_iotox(value: str | None, auto_build: bool) -> pathlib.Path:
    candidates: list[pathlib.Path] = []
    for raw in [value, os.environ.get("IOTOX_BINARY"), os.environ.get("IOTOX_BIN")]:
        if raw:
            candidates.append(pathlib.Path(raw))
    for candidate in candidates:
        if executable(candidate):
            return candidate.resolve()
    if auto_build:
        return build_source_linked_iotox()
    root = repo_root()
    for candidate in [
        root / "build" / "iotox-nix-debug" / "iotox",
        root / "build" / "gcc-debug" / "iotox",
        root / "build" / "debug" / "iotox",
    ]:
        if executable(candidate):
            return candidate.resolve()
    found = shutil.which("iotox")
    if found:
        return pathlib.Path(found).resolve()
    raise LabError(
        "could not find an IoTox binary; pass --iotox PATH or build "
        "the source-linked package first"
    )


def build_pinned_toxic(nixpkgs_rev: str) -> pathlib.Path:
    if shutil.which("nix") is None:
        raise LabError("could not find Toxic and nix is unavailable; pass --toxic PATH")
    result = shell_run(
        [
            "nix",
            "build",
            f"github:NixOS/nixpkgs/{nixpkgs_rev}#toxic",
            "--no-link",
            "--print-out-paths",
        ],
        timeout=600,
    )
    if result.returncode != 0:
        raise LabError(
            "nix could not build pinned Toxic\nSTDOUT:\n"
            + result.stdout
            + "\nSTDERR:\n"
            + result.stderr
        )
    store_path = pathlib.Path(result.stdout.strip().splitlines()[-1])
    toxic = store_path / "bin" / "toxic"
    if not executable(toxic):
        raise LabError(f"pinned Toxic build did not produce an executable at {toxic}")
    return toxic


def resolve_toxic(value: str | None, nixpkgs_rev: str) -> pathlib.Path:
    candidates: list[pathlib.Path] = []
    for raw in [value, os.environ.get("TOXIC_BINARY"), os.environ.get("TOXIC_BIN")]:
        if raw:
            candidates.append(pathlib.Path(raw))
    found = shutil.which("toxic")
    if found:
        candidates.append(pathlib.Path(found))
    for candidate in candidates:
        if executable(candidate):
            return candidate.resolve()
    return build_pinned_toxic(nixpkgs_rev).resolve()


def clean_terminal(text: str) -> str:
    text = ANSI_RE.sub("", text)
    return "".join(
        ch if ch in "\n\r\t" or 32 <= ord(ch) < 127 else " " for ch in text
    )


def find_exact_hex(text: str, length: int) -> list[str]:
    return re.findall(
        rf"(?<![0-9A-Fa-f])([0-9A-Fa-f]{{{length}}})(?![0-9A-Fa-f])",
        text,
    )


def make_lab_paths(root_arg: str | None) -> LabPaths:
    if root_arg:
        root = pathlib.Path(root_arg).resolve()
        if root.exists() and any(root.iterdir()):
            raise LabError(f"--lab path already exists and is not empty: {root}")
        root.mkdir(parents=True, exist_ok=True)
    else:
        root = pathlib.Path(tempfile.mkdtemp(prefix="iotox-toxic-live-lab-"))
    os.chmod(root, 0o700)
    for dirname in ["iotox", "toxic-home", "toxic-xdg-config", "toxic-xdg-data", "toxic-logs"]:
        (root / dirname).mkdir(parents=True, exist_ok=True)
    return LabPaths(
        root=root,
        runtime=short_runtime_dir("single", root) / "iotox",
        state=root / "iotox" / "device.toxsave",
        identity=root / "iotox" / "device.identity",
        ledger=root / "iotox" / "authority.ledger",
        command_store=root / "iotox" / "commands.store",
        iotox_log=root / "iotox.log",
        toxic_profile=root / "toxic-home" / "toxic_profile.tox",
        toxic_conf=root / "toxic.conf",
        toxic_nodes=root / "DHTnodes.json",
        toxic_logs=root / "toxic-logs",
        toxic_raw=root / "toxic.pty.raw",
        toxic_screen=root / "toxic.screen.txt",
        roster=root / "self.roster",
        person_card=root / "person.card",
        delegation=root / "desktop.person.delegate",
        bridge_store=root / "tox.bridge",
        summary=root / "proof-summary.json",
    )


def write_toxic_conf(paths: LabPaths) -> None:
    # Toxic uses libconfig syntax; keep this minimal and deterministic.
    paths.toxic_conf.write_text(
        f"""ui = {{
  timestamps=false;
  alerts=false;
  show_notification_content=false;
  bell_on_message=false;
  bell_on_filetrans=false;
  bell_on_filetrans_accept=false;
  bell_on_invite=false;
  autolog=true;
  show_welcome_msg=false;
  show_connection_msg=true;
  nodeslist_update_freq=0;
  autosave_freq=1;
}};
tox = {{
  chatlogs_path="{paths.toxic_logs}/";
}};
""",
        encoding="utf-8",
    )
    # Pinned from the official nodes.tox.chat JSON on 2026-09-30.  Keep this
    # list numeric-only so the lab does not add DNS as a hidden dependency, and
    # prefer nodes that currently advertise TCP support because the forced-TCP
    # Toxic compatibility soak is the fragile route.
    scan_time = 1790740800
    node_rows = [
        ("144.217.167.73", 33445, [33445, 3389], "7E5668E0EE09E19F320AD47902419331FFEE147BB3606769CFBE921A2A2FD34C", "velusip", "CA", True),
        ("172.105.109.31", 33445, [33445], "D46E97CF995DC1820B92B7D899E152A217D36ABE22730FEA4B6BF1BFC06C617C", "amr", "CA", True),
        ("144.172.88.203", 33445, [443, 33445], "2016A0F2797EE3A8B004BA623F11AAFC8146F1B8F45107232A1A1AECCE856674", "Rajesh", "AE", True),
        ("172.104.215.182", 33445, [443, 3389, 33445], "DA2BD927E01CD05EBCC2574EBE5BEBB10FF59AE0B2105A7D1E2B40E49BB20239", "zero-one", "US", True),
        ("188.214.122.30", 33445, [33445, 3389], "2A9F7A620581D5D1B09B004624559211C5ED3D1D712E8066ACDB0896A7335705", "turambar", "EG", True),
        ("95.181.230.108", 33445, [33445, 3389], "B5FFECB4E4C26409EBB88DB35793E7B39BFA3BA12AC04C096950CB842E3E130A", "wdwp", "RU", True),
        ("188.245.84.166", 33445, [3389, 443, 33445], "96B66D300BA2B59B98FC42DB1325E7092388F0379593E680ABDBEA03B9C9CE03", "Careplus", "DE", True),
        ("86.107.187.54", 33445, [33445, 3389], "2C0F90965134C7BEFAFE72B077A19221628D7045BB51C1165A2C75CDB2B32634", "Boca", "NL", True),
        ("119.59.101.63", 33445, [33445], "197F746696062FA3BD07BB3BC0656ABD6692B4DAA27DACF0F474754F2B09B060", "Felix", "TH", True),
        ("167.17.40.142", 33445, [33445, 3389], "E84453123B44A47120FFB469CBCDEEF078D3785D7AD7F6C5B2351CB5DDE2C54C", "refan", "FI", True),
        ("172.86.77.39", 33445, [443, 33445], "AFFD3FAD3460E62A894E439534B27E5A5DCFE379C1C0FB78DEF1B150A87E900F", "Rajesh", "AE", True),
        ("145.239.1.105", 33445, [33445], "1658A9A64046C20F48FB2A47E56045233AB0AC0706974FC5904F9E74F452D908", "Peace186", "DE", True),
        ("5.19.249.240", 38296, [38296, 3389], "DA98A4C0CD7473A133E115FEA2EBDAEEA2EF4F79FD69325FC070DA4DE4BA3238", "Toxdaemon", "RU", False),
    ]
    nodes = {
        "last_scan": scan_time,
        "last_refresh": scan_time,
        "nodes": [
            {
                "ipv4": ipv4,
                "ipv6": "-",
                "port": port,
                "tcp_ports": tcp_ports,
                "public_key": public_key,
                "maintainer": maintainer,
                "location": location,
                "status_udp": status_udp,
                "status_tcp": True,
                "last_ping": scan_time,
            }
            for ipv4, port, tcp_ports, public_key, maintainer, location, status_udp
            in node_rows
        ],
    }
    # Toxic 0.15.x's nodes parser reads one line and searches for exact
    # no-whitespace tokens such as `"ipv4":"`.  Pretty-printed JSON is valid
    # JSON but not valid Toxic input for this parser.
    paths.toxic_nodes.write_text(
        json.dumps(nodes, separators=(",", ":")) + "\n", encoding="utf-8"
    )


class IoToxControl:
    def __init__(self, binary: pathlib.Path, paths: LabPaths):
        self.binary = binary
        self.paths = paths

    def run(
        self,
        args: list[str],
        *,
        input_text: str | None = None,
        timeout: float = 20.0,
        check: bool = True,
        runtime: bool = True,
        identity: pathlib.Path | None = None,
    ) -> str:
        cmd = [str(self.binary)]
        if identity is not None:
            cmd += ["--identity", str(identity)]
        if runtime:
            cmd += ["--runtime", str(self.paths.runtime), "--timeout-ms", "10000"]
        cmd += args
        proc = subprocess.run(
            cmd,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        text = proc.stdout + proc.stderr
        if check and proc.returncode != 0:
            raise LabError(
                f"IoTox command failed rc={proc.returncode}: {cmd}\n{text}"
            )
        return text


class ToxicPTY:
    def __init__(self, binary: pathlib.Path, paths: LabPaths, force_tcp: bool):
        self.binary = binary
        self.paths = paths
        self.force_tcp = force_tcp
        self.master: int | None = None
        self.proc: subprocess.Popen[bytes] | None = None
        self.raw = bytearray()

    def start(self) -> None:
        master, slave = pty.openpty()
        env = os.environ.copy()
        env.update(
            {
                "HOME": str(self.paths.root / "toxic-home"),
                "XDG_CONFIG_HOME": str(self.paths.root / "toxic-xdg-config"),
                "XDG_DATA_HOME": str(self.paths.root / "toxic-xdg-data"),
                "TERM": "xterm-256color",
                "TOXIC_NO_SOUND": "1",
                "NO_AT_BRIDGE": "1",
            }
        )
        cmd = [
            str(self.binary),
            "-4",
            "-f",
            str(self.paths.toxic_profile),
            "-c",
            str(self.paths.toxic_conf),
            "-n",
            str(self.paths.toxic_nodes),
        ]
        if self.force_tcp:
            cmd.insert(1, "-t")
        self.proc = subprocess.Popen(
            cmd,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            env=env,
            close_fds=True,
        )
        os.close(slave)
        os.set_blocking(master, False)
        self.master = master

    def read(self, wait: float = 0.1) -> None:
        if self.master is None:
            return
        end = time.time() + wait
        while True:
            ready, _, _ = select.select([self.master], [], [], max(0.0, end - time.time()))
            if not ready:
                break
            try:
                chunk = os.read(self.master, 8192)
            except (BlockingIOError, OSError):
                break
            if not chunk:
                break
            self.raw.extend(chunk)
            if time.time() >= end:
                break

    def raw_text(self) -> str:
        return self.raw.decode("utf-8", errors="replace")

    def screen(self) -> str:
        return clean_terminal(self.raw_text())

    def dump_evidence(self) -> None:
        """Persist the PTY transcript/screen for post-run audit.

        Toxic's curses display and autologging are useful diagnostics, but
        autolog files are not consistently produced in the non-interactive PTY
        labs.  The c-toxcore read receipt remains the authoritative delivery
        proof; these files preserve the human-visible terminal state when it
        exists.
        """

        self.read(0.1)
        try:
            self.paths.toxic_raw.write_bytes(bytes(self.raw))
        except OSError:
            pass
        try:
            self.paths.toxic_screen.write_text(self.screen(), encoding="utf-8")
        except OSError:
            pass

    def send(self, text: str) -> None:
        if self.master is None:
            raise LabError("Toxic PTY was not started")
        os.write(self.master, text.encode("utf-8"))
        time.sleep(0.15)
        self.read(0.2)

    def wait_for(
        self,
        predicate: Callable[[str], str | bool | None],
        label: str,
        timeout: float,
    ) -> str | bool:
        end = time.time() + timeout
        last_report = time.time()
        while time.time() < end:
            self.read(0.25)
            if self.proc and self.proc.poll() is not None:
                raise LabError(
                    f"Toxic exited while waiting for {label}, rc={self.proc.returncode}\n"
                    + self.screen()[-5000:]
                )
            result = predicate(self.screen())
            if result:
                return result
            if time.time() - last_report > 30:
                print(f"[toxic] still waiting for {label}...", flush=True)
                last_report = time.time()
        raise LabError(f"timeout waiting for {label}\n" + self.screen()[-6000:])

    def stop(self) -> None:
        if self.master is not None:
            try:
                os.write(self.master, b"/quit\r")
            except OSError:
                pass
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.proc.kill()


def first_line(text: str) -> str:
    stripped = text.strip()
    return stripped.splitlines()[0] if stripped else "ok"


def read_logs(directory: pathlib.Path) -> str:
    content = []
    try:
        paths = sorted(directory.iterdir())
    except OSError:
        return ""
    for path in paths:
        if path.is_file():
            try:
                content.append(path.read_text(errors="replace"))
            except OSError:
                pass
    return "\n".join(content)


def toxic_request_id(screen: str, peer_key: str) -> str | None:
    # Toxic's curses screen is driven through a PTY in the live labs.  Under
    # load it can echo a command and the refreshed request row without a clean
    # newline between them, for example:
    #
    #   /requests0 : ABCD...
    #
    # The request is real and visible to a human, but the old clean-line-only
    # parser missed it.  Keep the strict key binding, while accepting the
    # command-echo-adjacent shape Toxic actually emits.
    key = re.escape(peer_key.upper())
    normalized = clean_terminal(screen).replace("\r", "\n")
    patterns = [
        rf"(?im)^\s*([0-9]+)\s*:\s*{key}\s*(?:$|\n)",
        rf"(?i)/requests\s*([0-9]+)\s*:\s*{key}(?=\s|$)",
        rf"(?im)(?:^|\n)[^\n]*?\b([0-9]+)\s*:\s*{key}(?=\s|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            return match.group(1)
    return None


def wait_for_toxic_friend_request(
    toxic: ToxicPTY,
    peer_key: str,
    *,
    timeout: float,
    on_retry: Callable[[int], None] | None = None,
    retry_interval: float = 45.0,
    retry_label: str = "IoTox friend request",
) -> str:
    deadline = time.time() + timeout
    last_request_command = 0.0
    last_retry = time.time()
    retry_count = 0
    retry_errors: list[str] = []
    last_report = time.time()
    while time.time() < deadline:
        now = time.time()
        if now - last_request_command >= 2.0:
            toxic.send("/requests\r")
            last_request_command = now
        if on_retry is not None and now - last_retry >= retry_interval:
            retry_count += 1
            print(
                f"[retry] resending {retry_label} attempt={retry_count + 1}",
                flush=True,
            )
            try:
                on_retry(retry_count + 1)
            except Exception as exc:
                retry_errors.append(f"attempt={retry_count + 1}: {exc}")
            last_retry = now
        toxic.read(0.25)
        req_id = toxic_request_id(toxic.screen(), peer_key)
        if req_id is not None:
            return req_id
        if toxic.proc and toxic.proc.poll() is not None:
            raise LabError(
                "Toxic exited while waiting for IoTox friend request, "
                f"rc={toxic.proc.returncode}\n"
                + toxic.screen()[-5000:]
            )
        if time.time() - last_report > 30:
            print("[toxic] still waiting for IoTox friend request...", flush=True)
            last_report = time.time()
        time.sleep(0.5)
    raise LabError(
        "Toxic did not list IoTox friend request\nTOXIC:\n"
        + toxic.screen()[-6000:]
        + (
            "\nRETRY-ERRORS:\n" + "\n".join(retry_errors[-10:])
            if retry_errors
            else ""
        )
    )


def wait_for_iotox_ping(iotox: IoToxControl, proc: subprocess.Popen[bytes], timeout: float) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            raise LabError(
                f"IoTox exited early rc={proc.returncode}\n"
                + iotox.paths.iotox_log.read_text(errors="replace")[-4000:]
            )
        try:
            pong = iotox.run(["ping"], timeout=5)
            if pong.strip():
                print(f"[iotox] ping ok: {first_line(pong)}", flush=True)
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise LabError(
        "IoTox ping timeout\n" + iotox.paths.iotox_log.read_text(errors="replace")[-4000:]
    )


def parse_iotox_address(text: str) -> str:
    matches = find_exact_hex(text, 76)
    if matches:
        return matches[0].upper()
    raise LabError("could not parse IoTox Tox address from:\n" + text)


def parse_iotox_principal(text: str) -> str:
    match = re.search(r"public-key=([0-9A-Fa-f]{64})", text)
    if match:
        return match.group(1).upper()
    matches = find_exact_hex(text, 64)
    if matches:
        return matches[0].upper()
    raise LabError("could not parse IoTox device principal from:\n" + text)


def run_lab(args: argparse.Namespace) -> dict[str, object]:
    iotox_bin = resolve_iotox(args.iotox, not args.no_iotox_auto_build)
    toxic_bin = resolve_toxic(args.toxic, args.toxic_nixpkgs)
    paths = make_lab_paths(args.lab)
    write_toxic_conf(paths)

    nonce = "".join(random.choice("abcdef0123456789") for _ in range(10))
    print(f"[lab] {paths.root}", flush=True)
    print(f"[iotox] binary={iotox_bin}", flush=True)
    print(f"[toxic] binary={toxic_bin}", flush=True)

    iotox = IoToxControl(iotox_bin, paths)
    toxic = ToxicPTY(toxic_bin, paths, args.toxic_force_tcp)
    iotox_run_args = [
        str(iotox_bin),
        "run",
        "--runtime",
        str(paths.runtime),
        "--state",
        str(paths.state),
        "--identity",
        str(paths.identity),
        "--authority-ledger",
        str(paths.ledger),
        "--command-store",
        str(paths.command_store),
        "--run-ms",
        str(args.run_ms),
    ]
    if args.toxic_force_tcp:
        iotox_run_args.append("--native-tcp-only")
    with paths.iotox_log.open("wb") as log:
        daemon = subprocess.Popen(
            iotox_run_args,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    print(f"[iotox] pid={daemon.pid}", flush=True)

    try:
        wait_for_iotox_ping(iotox, daemon, args.start_timeout)
        iotox_address = parse_iotox_address(iotox.run(["address"]))
        iotox_tox_key = iotox_address[:64]
        iotox_principal = parse_iotox_principal(iotox.run(["identity"]))
        print(f"[iotox] address={iotox_address}", flush=True)
        print(f"[iotox] tox_key={iotox_tox_key}", flush=True)
        print(f"[iotox] principal={iotox_principal}", flush=True)

        toxic.start()
        toxic.read(2.0)
        if "encrypt" in toxic.screen().lower():
            print("[toxic] first-run encryption prompt -> n", flush=True)
            toxic.send("n\r")
        toxic.wait_for(lambda s: "Home" in s and "Contacts" in s, "initial screen", 30)
        toxic.send("/nick ToxicLab\r")
        toxic.send("/status online\r")
        toxic.send("/myid\r")
        toxic_address = str(
            toxic.wait_for(
                lambda s: (find_exact_hex(s, 76) or [None])[-1],
                "Toxic /myid",
                30,
            )
        ).upper()
        toxic_key = toxic_address[:64]
        print(f"[toxic] address={toxic_address}", flush=True)
        print(f"[toxic] tox_key={toxic_key}", flush=True)

        friendship_setup = "toxic-request-iotox-accept"
        if args.toxic_force_tcp:
            def send_iotox_request(attempt: int) -> str:
                suffix = "" if attempt == 1 else f"-retry{attempt}"
                if attempt > 1:
                    iotox.run(
                        ["transport-peer-remove", f"key:{toxic_key}"],
                        check=False,
                    )
                return iotox.run(
                    [
                        "transport-peer-request",
                        toxic_address,
                        f"iotox-toxic-force-tcp-lab-{nonce}{suffix}",
                    ]
                )

            request = send_iotox_request(1)
            print(f"[iotox] sent friend request to Toxic: {first_line(request)}", flush=True)
            req_id = wait_for_toxic_friend_request(
                toxic,
                iotox_tox_key,
                timeout=args.request_timeout,
                on_retry=send_iotox_request,
                retry_interval=args.request_retry_interval,
                retry_label="IoTox->Toxic force-TCP friend request",
            )
            toxic.send(f"/accept {req_id}\r")
            toxic.wait_for(
                lambda s: "Friend request accepted." in s,
                "Toxic friend request acceptance",
                30,
            )
            print(f"[toxic] accepted IoTox friend request id={req_id}", flush=True)
            friendship_setup = "iotox-request-toxic-accept"
        else:
            def send_toxic_request(attempt: int) -> None:
                suffix = "" if attempt == 1 else f"-retry{attempt}"
                toxic.send(f"/add {iotox_address} toxic-compat-lab-{nonce}{suffix}\r")

            send_toxic_request(1)
            print("[toxic] sent /add to IoTox", flush=True)
            deadline = time.time() + args.request_timeout
            last_retry = time.time()
            retry_count = 0
            last_report = time.time()
            requests = ""
            while time.time() < deadline:
                toxic.read(0.2)
                requests = iotox.run(["requests"], timeout=10, check=False)
                if toxic_key in requests.upper():
                    print("[iotox] saw Toxic friend request", flush=True)
                    break
                if daemon.poll() is not None:
                    raise LabError(
                        f"IoTox exited while waiting for friend request rc={daemon.returncode}\n"
                        + paths.iotox_log.read_text(errors="replace")[-4000:]
                    )
                if time.time() - last_report > 30:
                    print("[iotox] still waiting for friend request...", flush=True)
                    last_report = time.time()
                now = time.time()
                if now - last_retry >= args.request_retry_interval:
                    retry_count += 1
                    print(
                        f"[retry] resending Toxic->IoTox /add attempt={retry_count + 1}",
                        flush=True,
                    )
                    send_toxic_request(retry_count + 1)
                    last_retry = now
                time.sleep(1.0)
            else:
                raise LabError(
                    "IoTox did not see Toxic friend request\nREQUESTS:\n"
                    + requests
                    + "\nTOXIC:\n"
                    + toxic.screen()[-5000:]
                    + "\nIOTOX LOG:\n"
                    + paths.iotox_log.read_text(errors="replace")[-5000:]
                )
            accept = iotox.run(["request-accept", toxic_key])
            print(f"[iotox] accepted Toxic request: {first_line(accept)}", flush=True)

        out_msg = f"iotox-to-toxic-{nonce}"
        send_result = ""
        deadline = time.time() + args.connect_timeout
        last_report = time.time()
        while time.time() < deadline:
            toxic.read(0.25)
            send_result = iotox.run(
                ["message", f"key:{toxic_key}", out_msg],
                timeout=10,
                check=False,
            )
            lowered = send_result.lower()
            if not any(
                marker in lowered
                for marker in [
                    "error",
                    "not connected",
                    "failed",
                    "unavailable",
                    "friend-not-found",
                    "not-found",
                ]
            ):
                print("[iotox] normal outbound send accepted", flush=True)
                break
            if time.time() - last_report > 30:
                print(
                    "[iotox] waiting for friend connection before normal send...",
                    flush=True,
                )
                last_report = time.time()
            time.sleep(2.0)
        else:
            raise LabError(
                "IoTox could not send normal message to Toxic before deadline\n"
                + send_result
                + "\nPEERS:\n"
                + iotox.run(["peers"], check=False)
                + "\nTOXIC:\n"
                + toxic.screen()[-6000:]
            )

        deadline = time.time() + args.visible_timeout
        while time.time() < deadline:
            toxic.read(0.5)
            if out_msg in read_logs(paths.toxic_logs) or out_msg in toxic.screen():
                print("[toxic] received IoTox normal text", flush=True)
                break
            time.sleep(0.5)
        else:
            raise LabError(
                "Toxic did not visibly/log receive outbound text\nLOGS="
                + str(list(paths.toxic_logs.glob("*")))
                + "\nTOXIC:\n"
                + toxic.screen()[-6000:]
            )

        in_msg = f"toxic-to-iotox-{nonce}"
        attempts = [
            "\x0f\r" + in_msg + "\r",
            "\x0f" + in_msg + "\r",
            "\x10" + in_msg + "\r",
            in_msg + "\r",
            "\x0f\x0f" + in_msg + "\r",
            "\x10\x10" + in_msg + "\r",
        ]
        peer_messages = ""
        for attempt_number, payload in enumerate(attempts, 1):
            toxic.send(payload)
            print(f"[toxic] attempted normal chat send #{attempt_number}", flush=True)
            deadline = time.time() + args.inbound_attempt_timeout
            while time.time() < deadline:
                toxic.read(0.25)
                peer_messages = iotox.run(
                    ["peer-messages", toxic_key],
                    timeout=10,
                    check=False,
                )
                if in_msg in peer_messages:
                    print("[iotox] recorded Toxic normal inbound text", flush=True)
                    break
                time.sleep(0.5)
            else:
                continue
            break
        else:
            raise LabError(
                "IoTox did not record Toxic inbound text\nPEER MESSAGES:\n"
                + peer_messages
                + "\nTOXIC:\n"
                + toxic.screen()[-8000:]
            )

        create = iotox.run(
            [
                "self-swarm",
                "create-recall-stdin",
                str(paths.roster),
                "desktop",
                iotox_principal,
                iotox_tox_key,
                "operator",
                "interactive.terminal",
            ],
            input_text=args.recall_phrase,
            runtime=False,
        )
        card = iotox.run(
            ["person", "card-recall-stdin", str(paths.roster), str(paths.person_card)],
            input_text=args.recall_phrase,
            runtime=False,
        )
        delegation = iotox.run(
            [
                "person",
                "delegate-recall-stdin",
                str(paths.roster),
                "desktop",
                str(paths.delegation),
            ],
            input_text=args.recall_phrase,
            runtime=False,
        )
        if not paths.roster.exists() or not paths.person_card.exists() or not paths.delegation.exists():
            raise LabError("self/person setup did not create expected artifacts")
        print("[bridge] self roster/card/delegation created", flush=True)

        bridge_plan = iotox.run(
            [
                "person",
                "tox-bridge-plan-in-delegated",
                "--bridge-store",
                str(paths.bridge_store),
                str(paths.person_card),
                str(paths.delegation),
                toxic_key,
                "message",
                in_msg,
            ],
            runtime=False,
            identity=paths.identity,
        )
        payload_match = re.search(r"^payload-hex=([0-9A-Fa-f]+)$", bridge_plan, re.M)
        if not payload_match:
            raise LabError("bridge inbound plan did not print payload-hex\n" + bridge_plan)
        payload_hex = payload_match.group(1)
        if "local-bridge-store=" + str(paths.bridge_store) not in bridge_plan:
            raise LabError("bridge inbound plan did not bind local bridge store\n" + bridge_plan)
        if "local-bridge-commit-command=iotox person tox-bridge-receive" not in bridge_plan:
            raise LabError("bridge inbound plan did not print local commit command\n" + bridge_plan)
        receive = iotox.run(
            [
                "person",
                "tox-bridge-receive",
                payload_hex,
                str(paths.delegation),
                str(paths.bridge_store),
            ],
            runtime=False,
        )
        duplicate = iotox.run(
            [
                "person",
                "tox-bridge-receive",
                payload_hex,
                str(paths.delegation),
                str(paths.bridge_store),
            ],
            runtime=False,
        )
        bridge_status = iotox.run(
            ["person", "tox-bridge-status", str(paths.bridge_store)],
            runtime=False,
        )
        if "bridge=committed duplicate=0" not in receive:
            raise LabError("bridge first receive did not commit\n" + receive)
        if "duplicate=1" not in duplicate or "mutated=0" not in duplicate:
            raise LabError("bridge duplicate receive was not idempotent\n" + duplicate)
        if "entries=1" not in bridge_status or "inbound=1" not in bridge_status:
            raise LabError("bridge status did not account for inbound commit\n" + bridge_status)

        bridge_out_msg = f"iotox-bridge-out-{nonce}"
        bridge_out_plan = iotox.run(
            [
                "person",
                "tox-bridge-plan-out-delegated",
                "--bridge-store",
                str(paths.bridge_store),
                str(paths.person_card),
                str(paths.delegation),
                toxic_key,
                "message",
                bridge_out_msg,
            ],
            runtime=False,
            identity=paths.identity,
        )
        expected_command = f"normal-tox-send-command=iotox message-hex key:{toxic_key}"
        if expected_command not in bridge_out_plan:
            raise LabError(
                "bridge outbound plan did not target the actual Toxic key\n"
                + bridge_out_plan
            )
        if "local-bridge-commit-command=iotox person tox-bridge-receive" not in bridge_out_plan:
            raise LabError(
                "bridge outbound plan did not print local commit command\n"
                + bridge_out_plan
            )
        print(
            "[bridge] signed inbound observation committed idempotently; "
            "outbound plan targets Toxic key",
            flush=True,
        )

        summary = {
            "schema": "iotox-toxic-compat-live-proof-v1",
            "lab": str(paths.root),
            "iotox_binary": str(iotox_bin),
            "toxic_binary": str(toxic_bin),
            "toxic_force_tcp": args.toxic_force_tcp,
            "iotox_tox_key": iotox_tox_key,
            "toxic_tox_key": toxic_key,
            "nonce": nonce,
            "proofs": {
                "friendship_setup": friendship_setup,
                "toxic_friend_request_seen_by_iotox": not args.toxic_force_tcp,
                "iotox_friend_request_seen_by_toxic": args.toxic_force_tcp,
                "iotox_accepted_toxic_request": not args.toxic_force_tcp,
                "toxic_accepted_iotox_request": args.toxic_force_tcp,
                "iotox_to_toxic_normal_text": out_msg,
                "toxic_to_iotox_normal_text": in_msg,
                "tox_bridge_plan_prints_local_commit_command": True,
                "tox_bridge_inbound_status": [
                    line
                    for line in bridge_status.splitlines()
                    if line.startswith(
                        ("entries=", "inbound=", "outbound=", "content-free=")
                    )
                ],
                "tox_bridge_duplicate_idempotent": True,
                "tox_bridge_outbound_plan_targets_toxic": True,
            },
            "evidence_files": {
                "proof_summary": str(paths.summary),
                "iotox_log": str(paths.iotox_log),
                "toxic_logs": str(paths.toxic_logs),
                "toxic_pty_raw": str(paths.toxic_raw),
                "toxic_screen": str(paths.toxic_screen),
                "iotox_peer_messages": str(paths.runtime / "peer-messages"),
                "bridge_store": str(paths.bridge_store),
            },
            "private_state_warning": (
                "lab contains fresh private Tox savedata and should stay owner-private"
            ),
            "schemas": {
                "self_swarm": first_line(create),
                "person_card": first_line(card),
                "delegation": first_line(delegation),
                "bridge_plan": first_line(bridge_plan),
                "bridge_receive": first_line(receive),
                "bridge_status": first_line(bridge_status),
            },
        }
        paths.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2), flush=True)
        return summary
    finally:
        toxic.dump_evidence()
        toxic.stop()
        if daemon.poll() is None:
            try:
                iotox.run(["stop"], timeout=5, check=False)
            except Exception:
                pass
            try:
                daemon.wait(timeout=10)
            except subprocess.TimeoutExpired:
                daemon.terminate()
                try:
                    daemon.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    daemon.kill()


def self_test() -> int:
    key = "A" * 64
    cases = {
        "clean": f"0 : {key}\nrequest body\n",
        "carriage-return": f"/requests\r0 : {key}\rrequest body\r",
        "pty-adjacent-echo": f"/requests0 : {key}\nrequest body\n",
        "prompt-adjacent-echo": f"$ /requests0 : {key}\nrequest body\n",
        "dirty-line": f"Home /requests0 : {key}\nrequest body\n",
    }
    for name, text in cases.items():
        if toxic_request_id(text, key) != "0":
            raise LabError(f"Toxic request parser missed {name}")
    if toxic_request_id(f"/requests0 : {'B' * 64}\n", key) is not None:
        raise LabError("Toxic request parser matched the wrong key")
    print("iotox-toxic-compat-bridge-lab-self-test=pass")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a live IoTox <-> Toxic compatibility bridge lab."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--iotox", help="IoTox binary to test")
    parser.add_argument(
        "--no-iotox-auto-build",
        action="store_true",
        help="do not auto-build the source-linked IoTox package when --iotox is omitted",
    )
    parser.add_argument("--toxic", help="Toxic binary to use as the external Tox client")
    parser.add_argument(
        "--toxic-nixpkgs",
        default=PINNED_TOXIC_NIXPKGS,
        help="Nixpkgs revision used to build Toxic when --toxic is omitted",
    )
    parser.add_argument("--lab", help="empty/private lab directory to use")
    parser.add_argument(
        "--toxic-force-tcp",
        action="store_true",
        help=(
            "launch Toxic with -t and IoTox with --native-tcp-only; "
            "friendship is initiated from IoTox and accepted in Toxic"
        ),
    )
    parser.add_argument(
        "--run-ms",
        type=int,
        default=900_000,
        help="IoTox daemon fixture lifetime in milliseconds",
    )
    parser.add_argument("--start-timeout", type=float, default=45.0)
    parser.add_argument("--request-timeout", type=float, default=300.0)
    parser.add_argument("--request-retry-interval", type=float, default=45.0)
    parser.add_argument("--connect-timeout", type=float, default=300.0)
    parser.add_argument("--visible-timeout", type=float, default=60.0)
    parser.add_argument("--inbound-attempt-timeout", type=float, default=35.0)
    parser.add_argument(
        "--recall-phrase",
        default=DEFAULT_RECALL,
        help="test RecallRoot phrase used only inside the temporary self/person artifacts",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        if args.self_test:
            return self_test()
        run_lab(args)
        return 0
    except (LabError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"[failed] {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
