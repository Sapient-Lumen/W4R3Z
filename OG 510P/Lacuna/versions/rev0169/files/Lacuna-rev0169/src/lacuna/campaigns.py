from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

from . import __version__
from .errors import LacunaError
from .store import CUBE_CONFIG, Cube
from .util import atomic_write_json, new_id, require_id, require_string, utc_now

LIBRARY_CONFIG = "lacuna-library.json"
CAMPAIGN_CONFIG = "campaign.json"
CAMPAIGNS_DIRECTORY = "campaigns"
LIBRARY_SCHEMA = "lacuna.library.v1"
CAMPAIGN_SCHEMA = "lacuna.campaign.v1"
LIBRARY_FIELDS = {
    "schema",
    "project",
    "project_version",
    "library_id",
    "created_at",
    "selected_campaign_id",
}
CAMPAIGN_FIELDS = {
    "schema",
    "project",
    "project_version",
    "campaign_id",
    "slug",
    "title",
    "summary",
    "status",
    "owner_id",
    "player_id",
    "narrator_id",
    "created_at",
    "cube_directory",
}
CAMPAIGN_STATUSES = {"active", "archived"}
SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def _read_json(path: Path, *, code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LacunaError(code, f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LacunaError(code, f"{path} must contain a JSON object")
    return value


def require_slug(value: Any, field: str = "slug") -> str:
    if not isinstance(value, str) or not SLUG_RE.fullmatch(value):
        raise ValueError(
            f"{field} must be 1-63 lowercase ASCII letters, digits, or interior hyphens"
        )
    return value


def _validate_library_config(config: dict[str, Any]) -> dict[str, Any]:
    unexpected = sorted(set(config) - LIBRARY_FIELDS)
    if unexpected:
        raise LacunaError(
            "unexpected-library-field",
            "library config contains unrecognized fields",
            {"fields": unexpected},
        )
    if config.get("schema") != LIBRARY_SCHEMA or config.get("project") != "Lacuna":
        raise LacunaError("bad-library-config", "unsupported Lacuna library config")
    try:
        require_string(config.get("project_version"), "project_version", max_len=64)
        require_id(config.get("library_id"), "library_id")
        require_string(config.get("created_at"), "created_at", max_len=128)
        selected = config.get("selected_campaign_id")
        if selected is not None:
            require_id(selected, "selected_campaign_id")
    except ValueError as exc:
        raise LacunaError("bad-library-config", str(exc)) from exc
    return config


def _validate_campaign_config(config: dict[str, Any], *, path: Path) -> dict[str, Any]:
    unexpected = sorted(set(config) - CAMPAIGN_FIELDS)
    if unexpected:
        raise LacunaError(
            "unexpected-campaign-field",
            "campaign config contains unrecognized fields",
            {"path": str(path), "fields": unexpected},
        )
    if config.get("schema") != CAMPAIGN_SCHEMA or config.get("project") != "Lacuna":
        raise LacunaError("bad-campaign-config", f"unsupported campaign config at {path}")
    try:
        require_string(config.get("project_version"), "project_version", max_len=64)
        require_id(config.get("campaign_id"), "campaign_id")
        require_slug(config.get("slug"))
        require_string(config.get("title"), "title", max_len=512)
        require_string(config.get("summary"), "summary", allow_empty=True, max_len=4096)
        status = config.get("status")
        if status not in CAMPAIGN_STATUSES:
            raise ValueError(f"status must be one of {sorted(CAMPAIGN_STATUSES)}")
        require_id(config.get("owner_id"), "owner_id")
        require_id(config.get("player_id"), "player_id")
        require_id(config.get("narrator_id"), "narrator_id")
        require_string(config.get("created_at"), "created_at", max_len=128)
        if config.get("cube_directory") != ".":
            raise ValueError("cube_directory must be '.'")
    except ValueError as exc:
        raise LacunaError("bad-campaign-config", f"{path}: {exc}") from exc
    if path.parent.name != config["slug"]:
        raise LacunaError(
            "campaign-path-mismatch",
            "campaign slug does not match its directory name",
            {"path": str(path), "slug": config["slug"]},
        )
    return config


class CampaignLibrary:
    def __init__(self, root: Path, config: dict[str, Any]):
        self.root = root
        self.config = config

    @classmethod
    def init(cls, root: str | os.PathLike[str]) -> "CampaignLibrary":
        path = Path(root).expanduser().resolve()
        if path.exists() and any(path.iterdir() if path.is_dir() else [path]):
            raise LacunaError("library-exists", f"refusing to initialize nonempty path: {path}")
        path.mkdir(parents=True, exist_ok=True)
        (path / CAMPAIGNS_DIRECTORY).mkdir()
        config = {
            "schema": LIBRARY_SCHEMA,
            "project": "Lacuna",
            "project_version": __version__,
            "library_id": new_id("lib"),
            "created_at": utc_now(),
            "selected_campaign_id": None,
        }
        atomic_write_json(path / LIBRARY_CONFIG, config)
        return cls(path, config)

    @classmethod
    def open(cls, root: str | os.PathLike[str]) -> "CampaignLibrary":
        path = Path(root).expanduser().resolve()
        config_path = path / LIBRARY_CONFIG
        if not config_path.is_file():
            raise LacunaError("not-a-library", f"missing {LIBRARY_CONFIG} under {path}")
        config = _validate_library_config(_read_json(config_path, code="bad-library-config"))
        campaigns_path = path / CAMPAIGNS_DIRECTORY
        if not campaigns_path.is_dir():
            raise LacunaError("bad-library-layout", f"missing campaigns directory under {path}")
        return cls(path, config)

    @classmethod
    def ensure(cls, root: str | os.PathLike[str]) -> "CampaignLibrary":
        path = Path(root).expanduser().resolve()
        if (path / LIBRARY_CONFIG).is_file():
            return cls.open(path)
        if not path.exists() or (path.is_dir() and not any(path.iterdir())):
            return cls.init(path)
        raise LacunaError(
            "not-a-library",
            f"refusing to overlay a campaign library onto nonempty path: {path}",
        )

    @property
    def campaigns_root(self) -> Path:
        return self.root / CAMPAIGNS_DIRECTORY

    def _write_config(self) -> None:
        self.config["project_version"] = __version__
        atomic_write_json(self.root / LIBRARY_CONFIG, self.config)

    def campaigns(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        selected_id = self.config.get("selected_campaign_id")
        for directory in sorted(self.campaigns_root.iterdir(), key=lambda item: item.name):
            if not directory.is_dir() or directory.name.startswith("."):
                continue
            config_path = directory / CAMPAIGN_CONFIG
            if not config_path.is_file():
                raise LacunaError(
                    "orphan-campaign-directory",
                    f"campaign directory has no {CAMPAIGN_CONFIG}: {directory}",
                )
            item = _validate_campaign_config(
                _read_json(config_path, code="bad-campaign-config"),
                path=config_path,
            )
            if not (directory / CUBE_CONFIG).is_file():
                raise LacunaError(
                    "campaign-missing-cube",
                    f"campaign {item['slug']!r} has no cube",
                    {"path": str(directory)},
                )
            public = dict(item)
            public["selected"] = item["campaign_id"] == selected_id
            public["path"] = str(directory)
            result.append(public)
        return result

    def resolve(self, selector: str | None = None, *, require_active: bool = False) -> dict[str, Any]:
        campaigns = self.campaigns()
        if selector is None:
            selected_id = self.config.get("selected_campaign_id")
            if selected_id is None:
                raise LacunaError(
                    "no-campaign-selected",
                    "no campaign is selected; select one explicitly",
                )
            matches = [item for item in campaigns if item["campaign_id"] == selected_id]
        else:
            matches = [
                item
                for item in campaigns
                if item["campaign_id"] == selector or item["slug"] == selector
            ]
        if not matches:
            raise LacunaError(
                "unknown-campaign",
                f"no campaign matches {selector!r}" if selector is not None else "selected campaign is missing",
            )
        if len(matches) != 1:
            raise LacunaError("ambiguous-campaign", f"campaign selector {selector!r} is ambiguous")
        item = matches[0]
        if require_active and item["status"] != "active":
            raise LacunaError("campaign-inactive", f"campaign {item['slug']!r} is not active")
        return item

    def create_campaign(
        self,
        *,
        slug: str,
        title: str,
        summary: str = "",
        owner_id: str = "user",
        owner_label: str = "User",
        player_id: str = "player",
        player_label: str = "Player",
        narrator_id: str = "narrator",
        narrator_label: str = "Narrator",
    ) -> dict[str, Any]:
        try:
            slug = require_slug(slug)
            title = require_string(title, "title", max_len=512)
            summary = require_string(summary, "summary", allow_empty=True, max_len=4096)
            owner_id = require_id(owner_id, "owner_id")
            player_id = require_id(player_id, "player_id")
            narrator_id = require_id(narrator_id, "narrator_id")
            owner_label = require_string(owner_label, "owner_label", max_len=512)
            player_label = require_string(player_label, "player_label", max_len=512)
            narrator_label = require_string(narrator_label, "narrator_label", max_len=512)
        except ValueError as exc:
            raise LacunaError("bad-campaign-input", str(exc)) from exc
        if len({owner_id, player_id, narrator_id, "system"}) != 4:
            raise LacunaError(
                "campaign-agent-collision",
                "owner_id, player_id, narrator_id, and reserved 'system' must be distinct",
            )
        target = self.campaigns_root / slug
        if target.exists():
            raise LacunaError("campaign-exists", f"campaign slug {slug!r} already exists")
        existing = self.campaigns()
        campaign_id = new_id("cmp")
        created_at = utc_now()
        temporary = self.campaigns_root / f".creating-{campaign_id}"
        if temporary.exists():
            raise LacunaError("temporary-path-collision", f"temporary campaign path already exists: {temporary}")
        try:
            with Cube.init(temporary, owner_id=owner_id, owner_label=owner_label) as cube:
                cube.apply_operations(
                    actor_id=owner_id,
                    operations=[
                        {
                            "op": "register_agent",
                            "agent_id": player_id,
                            "kind": "human",
                            "label": player_label,
                            "metadata": {"campaign_role": "player"},
                        },
                        {
                            "op": "register_agent",
                            "agent_id": narrator_id,
                            "kind": "narrator",
                            "label": narrator_label,
                            "metadata": {"campaign_role": "narrator"},
                        },
                    ],
                    message="register default campaign participants",
                )
            manifest = {
                "schema": CAMPAIGN_SCHEMA,
                "project": "Lacuna",
                "project_version": __version__,
                "campaign_id": campaign_id,
                "slug": slug,
                "title": title,
                "summary": summary,
                "status": "active",
                "owner_id": owner_id,
                "player_id": player_id,
                "narrator_id": narrator_id,
                "created_at": created_at,
                "cube_directory": ".",
            }
            atomic_write_json(temporary / CAMPAIGN_CONFIG, manifest)
            os.replace(temporary, target)
        except Exception:
            if temporary.exists():
                shutil.rmtree(temporary, ignore_errors=True)
            raise
        if not existing:
            self.config["selected_campaign_id"] = campaign_id
            self._write_config()
        item = dict(manifest)
        item["selected"] = self.config.get("selected_campaign_id") == campaign_id
        item["path"] = str(target)
        return item

    def select(self, selector: str) -> dict[str, Any]:
        item = self.resolve(selector, require_active=True)
        self.config["selected_campaign_id"] = item["campaign_id"]
        self._write_config()
        item = dict(item)
        item["selected"] = True
        return {
            "event": "lacuna.campaign.selected",
            "schema": "lacuna.campaign-selection.v1",
            "library_id": self.config["library_id"],
            "campaign": item,
        }

    def summary(self) -> dict[str, Any]:
        campaigns = self.campaigns()
        return {
            "event": "lacuna.campaigns",
            "schema": "lacuna.campaign-list.v1",
            "library_id": self.config["library_id"],
            "library_path": str(self.root),
            "selected_campaign_id": self.config.get("selected_campaign_id"),
            "campaign_count": len(campaigns),
            "campaigns": campaigns,
        }


def resolve_cube_reference(reference: str | os.PathLike[str]) -> Path:
    """Resolve either a cube directory or a library's selected campaign."""
    path = Path(reference).expanduser().resolve()
    if (path / CUBE_CONFIG).is_file():
        return path
    if (path / LIBRARY_CONFIG).is_file():
        library = CampaignLibrary.open(path)
        return Path(library.resolve(require_active=True)["path"])
    return path
