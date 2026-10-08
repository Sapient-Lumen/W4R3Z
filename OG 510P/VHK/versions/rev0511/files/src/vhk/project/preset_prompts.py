from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vhk.project.prompt_profiles import apply_saved_answers, sanitize_prompt_answers, PromptProfileStore

from vhk.core.expr import eval_expr, interpolate
from vhk.core.models import MacroPresetPrompt
from vhk.system import dialogs as dialogs_mod


@dataclass(frozen=True)
class MaterializedPromptForm:
    title: str | None
    text: str | None
    fields: list[dialogs_mod.FormField]
    profile_key: str | None = None

    @property
    def field_names(self) -> list[str]:
        return [f.name for f in self.fields]


def resolve_preset_profile_key(
    prompt_form: MacroPresetPrompt | None,
    ctx: dict[str, Any],
    *,
    macro_name: str,
    preset_name: str | None,
) -> str:
    raw = None
    if prompt_form is not None:
        raw = prompt_form.profile_key
    if raw is not None:
        try:
            resolved = interpolate(raw, ctx)
        except Exception:
            resolved = str(raw)
        if str(resolved).strip():
            return str(resolved).strip()
    return f"macro:{macro_name}:preset:{preset_name or 'default'}"


def _eval_or_render(expr_or_value: Any, ctx: dict[str, Any]) -> Any:
    if isinstance(expr_or_value, str):
        rendered = interpolate(expr_or_value, ctx)
        try:
            return eval_expr(rendered, ctx)
        except Exception:
            return rendered
    return expr_or_value


def materialize_preset_prompt_form(prompt_form: MacroPresetPrompt | None, ctx: dict[str, Any], *, saved_values: dict[str, Any] | None = None) -> MaterializedPromptForm | None:
    if prompt_form is None:
        return None
    title = interpolate(prompt_form.title, ctx) if prompt_form.title is not None else None
    text = interpolate(prompt_form.text, ctx) if prompt_form.text is not None else None
    fields: list[dialogs_mod.FormField] = []
    for field in prompt_form.fields:
        default = _eval_or_render(field.default, ctx)
        choices: list[str] = [str(x) for x in _eval_or_render(field.choices, ctx)]
        if field.choices_expr is not None:
            resolved = _eval_or_render(field.choices_expr, ctx)
            if not isinstance(resolved, (list, tuple)):
                raise ValueError(
                    f"Preset prompt field '{field.name}' choices_expr must resolve to a list/tuple, got {type(resolved).__name__}"
                )
            choices = [str(x) for x in resolved]
        fields.append(
            dialogs_mod.FormField(
                name=field.name,
                label=interpolate(field.label, ctx) if field.label is not None else field.name,
                kind=field.kind,
                default=default,
                choices=choices,
                remember=bool(getattr(field, 'remember', True)),
            )
        )
    fields = apply_saved_answers(fields, saved_values)
    profile_key = resolve_preset_profile_key(prompt_form, ctx, macro_name=str(ctx.get("macro", {}).get("name", "macro")), preset_name=str(ctx.get("preset", {}).get("name", "default")) if ctx.get("preset") else None)
    return MaterializedPromptForm(title=title, text=text, fields=fields, profile_key=profile_key)


def prompt_preset_overlay(
    prompt_form: MacroPresetPrompt | None,
    ctx: dict[str, Any],
    *,
    dry_run: bool = False,
    profile_store: PromptProfileStore | None = None,
    profile_key: str | None = None,
    prompt_profile: str | None = None,
    save_prompt_profile: str | None = None,
) -> dict[str, Any] | None:
    saved_values: dict[str, Any] = {}
    if profile_store is not None and profile_key:
        if prompt_profile:
            saved_values = profile_store.load_profile(profile_key, prompt_profile)
        else:
            saved_values = profile_store.load_last(profile_key)
    materialized = materialize_preset_prompt_form(prompt_form, ctx, saved_values=saved_values)
    if materialized is None:
        return {}
    if not materialized.fields:
        return {}
    if dry_run:
        values: dict[str, Any] = {}
        for field in materialized.fields:
            value = field.default
            if value is None and field.kind == "choice" and field.choices:
                value = field.choices[0]
            values[field.name] = value
        return values
    values = dialogs_mod.prompt_form(materialized.fields, title=materialized.title, text=materialized.text)
    if values is not None and profile_store is not None and profile_key:
        saved = sanitize_prompt_answers(materialized.fields, values)
        if saved:
            profile_store.save_last(profile_key, saved)
            if save_prompt_profile:
                profile_store.save_profile(profile_key, save_prompt_profile, saved)
    return values
