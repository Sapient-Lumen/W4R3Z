from __future__ import annotations

from vhk.core.models import MacroPresetPrompt, PromptFormField
from vhk.project.preset_prompts import materialize_preset_prompt_form, prompt_preset_overlay


def test_materialize_preset_prompt_form_interpolates_defaults_and_choices() -> None:
    prompt = MacroPresetPrompt(
        title="Deploy ${env}",
        text="Ticket for ${service}",
        fields=[
            PromptFormField(name="version", label="Version", default="${default_version}"),
            PromptFormField(name="approve", label="Approve", kind="bool", default="${require_approval}"),
            PromptFormField(name="strategy", label="Strategy", kind="choice", choices_expr="strategies"),
        ],
    )

    materialized = materialize_preset_prompt_form(
        prompt,
        {
            "env": "prod",
            "service": "pegasus",
            "default_version": "1.2.3",
            "require_approval": True,
            "strategies": ["rolling", "blue-green"],
        },
    )

    assert materialized is not None
    assert materialized.title == "Deploy prod"
    assert materialized.text == "Ticket for pegasus"
    assert [(f.name, f.label, f.kind, f.default, f.choices) for f in materialized.fields] == [
        ("version", "Version", "text", "1.2.3", []),
        ("approve", "Approve", "bool", True, []),
        ("strategy", "Strategy", "choice", None, ["rolling", "blue-green"]),
    ]


def test_prompt_preset_overlay_dry_run_uses_defaults_and_first_choice() -> None:
    prompt = MacroPresetPrompt(
        fields=[
            PromptFormField(name="version", default="1.2.3"),
            PromptFormField(name="approve", kind="bool", default=True),
            PromptFormField(name="strategy", kind="choice", choices=["rolling", "blue-green"]),
        ]
    )

    values = prompt_preset_overlay(prompt, {}, dry_run=True)

    assert values == {"version": "1.2.3", "approve": True, "strategy": "rolling"}


def test_prompt_preset_overlay_can_load_and_save_named_profiles(tmp_path) -> None:
    from vhk.project.prompt_profiles import make_prompt_profile_store

    prompt = MacroPresetPrompt(
        fields=[
            PromptFormField(name="version", default="1.2.3"),
            PromptFormField(name="token", kind="password", default="secret"),
        ]
    )
    store = make_prompt_profile_store(tmp_path, ".vhk/prompt_profiles.json")
    store.save_profile("macro:deploy:preset:prod", "release", {"version": "9.9.9"})

    values = prompt_preset_overlay(
        prompt,
        {},
        dry_run=True,
        profile_store=store,
        profile_key="macro:deploy:preset:prod",
        prompt_profile="release",
    )

    assert values == {"version": "9.9.9", "token": "secret"}
