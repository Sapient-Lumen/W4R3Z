from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

import yaml

from vhk.core.models import Project
from vhk.project.strategy import _mpris_service_analysis


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text).strip()).strip("-").lower()
    return slug or "project"


def default_playerctl_dir(project: Project) -> Path:
    return Path(project.root_dir) / "integrations" / "playerctl"


def default_playerctl_base_name(project: Project) -> str:
    return f"vhk-{_slugify(project.name)}-playerctl"


@dataclass(frozen=True)
class PlayerctlRoute:
    route_id: str
    macro: str
    description: str
    bus: str
    sender: str | None
    path: str | None
    interface: str | None
    member: str | None
    player: str | None
    player_selector: str
    run_argv: tuple[str, ...]
    helper_path: Path

    def to_dict(self) -> dict[str, object]:
        return {
            "route_id": self.route_id,
            "macro": self.macro,
            "description": self.description,
            "bus": self.bus,
            "sender": self.sender,
            "path": self.path,
            "interface": self.interface,
            "member": self.member,
            "player": self.player,
            "player_selector": self.player_selector,
            "run_argv": list(self.run_argv),
            "helper_path": str(self.helper_path),
        }


@dataclass(frozen=True)
class PlayerctlPackManifest:
    project: str
    out_dir: Path
    base_name: str
    routes: tuple[PlayerctlRoute, ...]
    commands_path: Path
    routes_path: Path
    readme_path: Path
    helper_paths: tuple[Path, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "project": self.project,
            "out_dir": str(self.out_dir),
            "base_name": self.base_name,
            "route_count": len(self.routes),
            "routes": [item.to_dict() for item in self.routes],
            "commands_path": str(self.commands_path),
            "routes_path": str(self.routes_path),
            "readme_path": str(self.readme_path),
            "helper_paths": [str(path) for path in self.helper_paths],
        }


def build_playerctl_routes(
    project: Project,
    *,
    out_dir: Path,
    command: str = "vhk",
) -> list[PlayerctlRoute]:
    analysis = _mpris_service_analysis(project=project)
    root = Path(project.root_dir)
    argv_base = tuple(shlex.split(command or "vhk")) or ("vhk",)
    helper_dir = out_dir / "bin"
    routes: list[PlayerctlRoute] = []
    for idx, row in enumerate(list(analysis.get("rows") or []), start=1):
        macro = str(row.get("macro") or "macro")
        player = str(row.get("player") or "").strip() or None
        member = str(row.get("member") or "").strip() or "signal"
        route_id = _slugify(f"{macro}-{player or 'any'}-{member}-{idx}")
        helper_path = helper_dir / f"{route_id}.sh"
        macro_obj = getattr(project, "macros", {}).get(macro)
        description = str(getattr(macro_obj, "description", None) or getattr(macro_obj, "name", None) or macro)
        run_argv = (*argv_base, "run", str(root), macro, "--quiet")
        routes.append(
            PlayerctlRoute(
                route_id=route_id,
                macro=macro,
                description=description,
                bus=str(row.get("bus") or "session"),
                sender=str(row.get("sender") or "").strip() or None,
                path=str(row.get("path_name") or "").strip() or None,
                interface=str(row.get("interface") or "").strip() or None,
                member=member,
                player=player,
                player_selector=player or "%any",
                run_argv=run_argv,
                helper_path=helper_path,
            )
        )
    return routes


def render_playerctl_routes_yaml(project: Project, *, routes: list[PlayerctlRoute]) -> str:
    payload = {
        "project": project.name,
        "generated_by": "vhk gen-playerctl-pack",
        "notes": [
            "This pack is a thin playerctl/MPRIS adapter handoff. It does not replace VHK macro semantics.",
            "Review each player selector and fallback path before relying on automatic latest-player behavior.",
        ],
        "routes": [
            {
                "id": item.route_id,
                "macro": item.macro,
                "description": item.description,
                "mpris": {
                    "bus": item.bus,
                    "sender": item.sender,
                    "path": item.path,
                    "interface": item.interface,
                    "member": item.member,
                    "player": item.player,
                },
                "playerctl": {
                    "player_selector": item.player_selector,
                    "status_example": f"playerctl --player {shlex.quote(item.player_selector)} status",
                    "metadata_follow_example": (
                        "playerctl --follow --player "
                        f"{shlex.quote(item.player_selector)} metadata --format "
                        "'{{playerName}}\\t{{status}}\\t{{default(artist,\"\")}}\\t{{default(title,\"\")}}'"
                    ),
                },
                "vhk": {
                    "run_command": shlex.join(item.run_argv),
                    "helper_script": str(item.helper_path),
                },
            }
            for item in routes
        ],
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def render_playerctl_commands_json(project: Project, *, routes: list[PlayerctlRoute]) -> str:
    payload = {
        "project": project.name,
        "route_count": len(routes),
        "routes": [
            {
                **item.to_dict(),
                "status_command": f"playerctl --player {shlex.quote(item.player_selector)} status",
                "metadata_follow_command": (
                    "playerctl --follow --player "
                    f"{shlex.quote(item.player_selector)} metadata --format "
                    "'{{playerName}}\\t{{status}}\\t{{default(artist,\"\")}}\\t{{default(title,\"\")}}'"
                ),
                "run_command": shlex.join(item.run_argv),
            }
            for item in routes
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_playerctl_helper_script(project: Project, *, route: PlayerctlRoute) -> str:
    run_command = shlex.join(route.run_argv)
    player_hint = route.player_selector
    return dedent(
        f'''\
        #!/usr/bin/env bash
        set -euo pipefail

        # Generated by `vhk gen-playerctl-pack` for project: {project.name}
        # Route id: {route.route_id}
        # This stays intentionally thin: playerctl owns target-player selection and
        # follow semantics, while VHK still owns the macro graph.

        PLAYERCTL=${{PLAYERCTL:-playerctl}}
        VHK_RUN_MODE=${{VHK_RUN_MODE:-print}}
        PLAYER=${{PLAYER:-{player_hint}}}
        QUERY=${{PLAYERCTL_QUERY:-metadata}}
        STATUS_FORMAT=${{PLAYERCTL_STATUS_FORMAT:-{{{{playerName}}}}\t{{{{status}}}}}}
        METADATA_FORMAT=${{PLAYERCTL_FORMAT:-{{{{playerName}}}}\t{{{{status}}}}\t{{{{default(artist,"")}}}}\t{{{{default(title,"")}}}}}}
        RUN_COMMAND={run_command!r}

        player_args=()
        if [[ -n "$PLAYER" && "$PLAYER" != "%any" ]]; then
          player_args+=(--player "$PLAYER")
        fi

        if [[ "$QUERY" == "status" ]]; then
          cmd=("$PLAYERCTL" --follow "${{player_args[@]}}" status --format "$STATUS_FORMAT")
        else
          cmd=("$PLAYERCTL" --follow "${{player_args[@]}}" metadata --format "$METADATA_FORMAT")
        fi

        if [[ "$VHK_RUN_MODE" == "run" ]]; then
          "${{cmd[@]}}" | while IFS= read -r _line; do
            sh -lc "$RUN_COMMAND"
          done
        else
          exec "${{cmd[@]}}"
        fi
        '''
    )


def render_playerctl_readme(project: Project, *, manifest: PlayerctlPackManifest) -> str:
    lines = [
        f"# {project.name} playerctl / MPRIS pack",
        "",
        "Generated by `vhk gen-playerctl-pack`.",
        "",
        "This pack makes the MPRIS lane concrete without turning VHK into a media-control daemon.",
        "The generated files keep one reviewable route catalog:",
        "",
        "- `vhk.playerctl.routes.yml` — route-by-route mapping from observed MPRIS waits to playerctl selectors and VHK macro ids",
        "- `vhk.playerctl.commands.json` — machine-readable command examples and helper paths",
        "- `bin/*.sh` — thin helper wrappers that either print `playerctl --follow` output or, when `VHK_RUN_MODE=run`, invoke the matching `vhk run ...` command on each update",
        "",
        "## Why this exists",
        "",
        "Linux media apps already share the MPRIS D-Bus contract, and playerctl sits on top of that contract instead of faking media automation through focus-sensitive key replay. This pack keeps that seam reviewable.",
        "",
        "## Routes",
        "",
    ]
    if not manifest.routes:
        lines.extend([
            "No MPRIS-shaped `WaitForDbusSignal` steps were found in this project.",
            "",
            "Create one or more waits against `org.mpris.MediaPlayer2*` and regenerate the pack.",
        ])
        return "\n".join(lines) + "\n"

    for item in manifest.routes:
        lines.extend([
            f"### `{item.route_id}`",
            "",
            f"- macro: `{item.macro}`",
            f"- player selector: `{item.player_selector}`",
            f"- bus/interface/member: `{item.bus}` / `{item.interface or 'unknown'}` / `{item.member or 'unknown'}`",
            f"- helper: `{item.helper_path.name}`",
            f"- run command: `{shlex.join(item.run_argv)}`",
            "",
        ])
    lines.extend([
        "## Notes",
        "",
        "- `playerctld` is often the right companion when you want commands to follow the most recently active player rather than pinning a single player name.",
        "- Keep app-specific IPC adapters (for example mpv JSON IPC) separate from this pack; MPRIS/playerctl is the shared media lane, not a universal app-control backend.",
    ])
    return "\n".join(lines) + "\n"


def write_playerctl_pack(
    project: Project,
    *,
    out_dir: Path,
    command: str = "vhk",
    base_name: str | None = None,
) -> PlayerctlPackManifest:
    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    helper_dir = target_dir / "bin"
    helper_dir.mkdir(parents=True, exist_ok=True)

    routes = build_playerctl_routes(project, out_dir=target_dir, command=command)
    resolved_base_name = str(base_name or default_playerctl_base_name(project)).strip() or default_playerctl_base_name(project)
    routes_path = target_dir / "vhk.playerctl.routes.yml"
    commands_path = target_dir / "vhk.playerctl.commands.json"
    readme_path = target_dir / "README.md"

    for route in routes:
        route.helper_path.write_text(render_playerctl_helper_script(project, route=route), encoding="utf-8")
        route.helper_path.chmod(route.helper_path.stat().st_mode | 0o111)

    manifest = PlayerctlPackManifest(
        project=project.name,
        out_dir=target_dir,
        base_name=resolved_base_name,
        routes=tuple(routes),
        commands_path=commands_path,
        routes_path=routes_path,
        readme_path=readme_path,
        helper_paths=tuple(route.helper_path for route in routes),
    )

    routes_path.write_text(render_playerctl_routes_yaml(project, routes=routes), encoding="utf-8")
    commands_path.write_text(render_playerctl_commands_json(project, routes=routes), encoding="utf-8")
    readme_path.write_text(render_playerctl_readme(project, manifest=manifest), encoding="utf-8")
    return manifest
