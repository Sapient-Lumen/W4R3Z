from __future__ import annotations

from pathlib import Path
from typing import Any

from .campaigns import LIBRARY_CONFIG, CampaignLibrary
from .entrance import MODEL_PROFILES, describe_model_reference
from .errors import LacunaError
from .store import CUBE_CONFIG, Cube
from .turnruns import begin_turn_run
from .util import pretty_json, require_id, require_string

PLAY_START_SCHEMA = "lacuna.play-start.v1"
PROFILE_MODES = {
    "chat": "solo",
    "workspace": "solo",
    "orchestrated": "auto",
}


def _resolve_play_reference(
    reference: str | Path,
    *,
    bootstrap: bool,
    campaign_slug: str,
    campaign_title: str,
    campaign_summary: str,
) -> tuple[dict[str, Any], list[str]]:
    """Resolve a cube/library, performing only explicit safe bootstrap actions."""
    path = Path(reference).expanduser().resolve()
    actions: list[str] = []

    if (path / CUBE_CONFIG).is_file():
        return describe_model_reference(path), actions

    if (path / LIBRARY_CONFIG).is_file():
        library = CampaignLibrary.open(path)
    elif not path.exists() or (path.is_dir() and not any(path.iterdir())):
        if not bootstrap:
            raise LacunaError(
                "play-bootstrap-required",
                "the play reference does not yet contain a cube or campaign library; pass --bootstrap",
                {"reference": str(path)},
            )
        library = CampaignLibrary.ensure(path)
        actions.append("initialized-campaign-library")
    else:
        raise LacunaError(
            "unsafe-play-bootstrap-path",
            "refusing to overlay Lacuna play state onto a foreign nonempty path",
            {"reference": str(path)},
        )

    campaigns = library.campaigns()
    selected_id = library.config.get("selected_campaign_id")
    if selected_id is None:
        active = [item for item in campaigns if item["status"] == "active"]
        if not active:
            if not bootstrap:
                raise LacunaError(
                    "play-bootstrap-required",
                    "the campaign library has no active campaign; pass --bootstrap to create one",
                    {"reference": str(path)},
                )
            created = library.create_campaign(
                slug=campaign_slug,
                title=campaign_title,
                summary=campaign_summary,
            )
            actions.append(f"created-campaign:{created['campaign_id']}")
        elif len(active) == 1:
            library.select(active[0]["campaign_id"])
            actions.append(f"selected-campaign:{active[0]['campaign_id']}")
        else:
            raise LacunaError(
                "ambiguous-play-campaign",
                "multiple active campaigns exist and none is selected; select one explicitly",
                {
                    "reference": str(path),
                    "campaigns": [
                        {"campaign_id": item["campaign_id"], "slug": item["slug"]}
                        for item in active
                    ],
                },
            )

    return describe_model_reference(path), actions


def start_play(
    reference: str | Path = ".lacuna-play",
    *,
    root: str | Path = ".lacuna-runs",
    player_input: str = "Will you DM?",
    profile: str = "orchestrated",
    bootstrap: bool = False,
    audience_id: str | None = None,
    actor_id: str | None = None,
    campaign_slug: str = "first-lacuna",
    campaign_title: str = "First Lacuna",
    campaign_summary: str = "A campaign bootstrapped from a direct request to play.",
) -> dict[str, Any]:
    """Turn one exact session-control sentence into a governed resumable run."""
    if profile not in MODEL_PROFILES:
        raise LacunaError("unknown-model-profile", f"profile must be one of {list(MODEL_PROFILES)}")
    try:
        player_input = require_string(player_input, "player_input", max_len=50000)
        if audience_id is not None:
            audience_id = require_id(audience_id, "audience_id")
        if actor_id is not None:
            actor_id = require_id(actor_id, "actor_id")
    except ValueError as exc:
        raise LacunaError("bad-play-start", str(exc)) from exc

    target, bootstrap_actions = _resolve_play_reference(
        reference,
        bootstrap=bootstrap,
        campaign_slug=campaign_slug,
        campaign_title=campaign_title,
        campaign_summary=campaign_summary,
    )
    campaign = target.get("campaign")
    if isinstance(campaign, dict):
        selected_audience_id = audience_id or str(campaign["player_id"])
        selected_actor_id = actor_id or str(campaign["narrator_id"])
    else:
        selected_audience_id = audience_id or "player"
        selected_actor_id = actor_id or "narrator"

    with Cube.open(target["resolved_cube_path"]) as cube:
        manifest = begin_turn_run(
            cube,
            reference=target["reference"],
            resolved_cube_path=target["resolved_cube_path"],
            root=root,
            player_input=player_input,
            input_kind="session-control",
            audience_id=selected_audience_id,
            actor_id=selected_actor_id,
            director=True,
            world_id=None,
            allow_anchor=False,
            mode=PROFILE_MODES[profile],
            include_planner_context_on_commit=False,
        )

    return {
        "event": "lacuna.play.started",
        "schema": PLAY_START_SCHEMA,
        "profile": profile,
        "input_kind": "session-control",
        "reference": target["reference"],
        "resolved_cube_path": target["resolved_cube_path"],
        "campaign": campaign,
        "bootstrap_actions": bootstrap_actions,
        "run": manifest,
        "next_action": manifest["next_action"],
        "nonclaims": [
            "Starting play opens a source-bound session-control request; it does not claim the sentence occurred inside the fiction.",
            "No model or subagent is invoked by this command.",
            "No narration has happened until the run reaches a passing commit receipt.",
        ],
    }


def play_start_markdown(start: dict[str, Any]) -> str:
    run = start["run"]
    lines = [
        "# Lacuna play start",
        "",
        f"- Profile: **{start['profile']}**",
        f"- Input kind: **{start['input_kind']}**",
        f"- Run: `{run['run_path']}`",
        f"- Status: **{run['status']}**",
        f"- Topology: **{run['selected_mode']}**",
        "",
        "The exact player sentence has been retained as session control, not fictionalized as an in-world deed.",
        "",
        "## Next action",
        "",
        run["next_action"]["action"],
    ]
    if run["next_action"]["input_path"] is not None:
        lines.extend(["", f"Complete input: `{run['next_action']['input_path']}`"])
    lines.extend(
        [
            "",
            "## Machine-readable start receipt",
            "",
            "```json",
            pretty_json(start),
            "```",
            "",
        ]
    )
    return "\n".join(lines)
