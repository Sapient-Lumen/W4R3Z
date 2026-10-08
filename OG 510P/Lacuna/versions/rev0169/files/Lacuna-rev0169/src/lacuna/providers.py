from __future__ import annotations

from typing import Final

from .errors import LacunaError

PROVIDERS: Final[tuple[str, ...]] = (
    "portable",
    "codex",
    "claude-code",
    "gemini-cli",
    "chatgpt",
)

TURN_AGENT_ROLES: Final[tuple[str, ...]] = (
    "lacuna-planner",
    "lacuna-narrator",
    "lacuna-proposal-builder",
    "lacuna-verifier",
)

CHECKPOINT_AGENT_ROLES: Final[tuple[str, ...]] = (
    "lacuna-retcon-generator",
    "lacuna-retcon-judge",
    "lacuna-retcon-compressor",
    "lacuna-retcon-verifier",
)

CONTINUATION_AGENT_ROLES: Final[tuple[str, ...]] = (
    "lacuna-fresh-narrator",
)


def _aliases(
    *,
    portable: str,
    codex: str,
    claude: str,
    gemini: str,
    chatgpt: str,
) -> dict[str, str]:
    return {
        "portable": portable,
        "codex": codex,
        "claude-code": claude,
        "gemini-cli": gemini,
        "chatgpt": chatgpt,
    }


PROVIDER_AGENT_ALIASES: Final[dict[str, dict[str, str]]] = {
    "lacuna-planner": _aliases(
        portable="lacuna-planner",
        codex="lacuna_planner",
        claude="lacuna-planner",
        gemini="lacuna-planner",
        chatgpt="role-dedicated planner context",
    ),
    "lacuna-narrator": _aliases(
        portable="lacuna-narrator",
        codex="lacuna_narrator",
        claude="lacuna-narrator",
        gemini="lacuna-narrator",
        chatgpt="role-dedicated narrator context",
    ),
    "lacuna-fresh-narrator": _aliases(
        portable="lacuna-fresh-narrator",
        codex="lacuna_fresh_narrator",
        claude="lacuna-fresh-narrator",
        gemini="lacuna-fresh-narrator",
        chatgpt="fresh post-checkpoint narrator context",
    ),
    "lacuna-proposal-builder": _aliases(
        portable="lacuna-proposal-builder",
        codex="lacuna_proposal_builder",
        claude="lacuna-proposal-builder",
        gemini="lacuna-proposal-builder",
        chatgpt="role-dedicated proposal-builder context",
    ),
    "lacuna-verifier": _aliases(
        portable="lacuna-verifier",
        codex="lacuna_verifier",
        claude="lacuna-verifier",
        gemini="lacuna-verifier",
        chatgpt="independent role-dedicated verifier context",
    ),
    "lacuna-retcon-generator": _aliases(
        portable="lacuna-retcon-generator",
        codex="lacuna_retcon_generator",
        claude="lacuna-retcon-generator",
        gemini="lacuna-retcon-generator",
        chatgpt="role-dedicated retcon-generator context",
    ),
    "lacuna-retcon-judge": _aliases(
        portable="lacuna-retcon-judge",
        codex="lacuna_retcon_judge",
        claude="lacuna-retcon-judge",
        gemini="lacuna-retcon-judge",
        chatgpt="blind role-dedicated retcon-judge context",
    ),
    "lacuna-retcon-compressor": _aliases(
        portable="lacuna-retcon-compressor",
        codex="lacuna_retcon_compressor",
        claude="lacuna-retcon-compressor",
        gemini="lacuna-retcon-compressor",
        chatgpt="role-dedicated retcon-compressor context",
    ),
    "lacuna-retcon-verifier": _aliases(
        portable="lacuna-retcon-verifier",
        codex="lacuna_retcon_verifier",
        claude="lacuna-retcon-verifier",
        gemini="lacuna-retcon-verifier",
        chatgpt="independent role-dedicated retcon-verifier context",
    ),
}


def provider_aliases(role: str) -> dict[str, str]:
    try:
        return dict(PROVIDER_AGENT_ALIASES[role])
    except KeyError as exc:
        raise LacunaError(
            "unknown-provider-role",
            f"no provider aliases are registered for role {role!r}",
        ) from exc


def provider_alias(role: str, provider: str) -> str:
    if provider not in PROVIDERS:
        raise LacunaError(
            "unknown-provider",
            f"provider must be one of {list(PROVIDERS)}",
        )
    aliases = provider_aliases(role)
    return aliases[provider]
