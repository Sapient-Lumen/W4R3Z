from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from vhk.core.expr import eval_expr, interpolate
from vhk.core.models import Project, StepPromptForm
from vhk.project.preset_prompts import materialize_preset_prompt_form
from vhk.system.dialogs import FormField


@dataclass(frozen=True)
class PromptProfileDefinition:
    profile_key: str
    source: str
    macro: str
    preset: str | None
    title: str | None
    text: str | None
    fields: tuple[FormField, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_key": self.profile_key,
            "source": self.source,
            "macro": self.macro,
            "preset": self.preset,
            "title": self.title,
            "text": self.text,
            "fields": [
                {
                    "name": f.name,
                    "label": f.label,
                    "kind": f.kind,
                    "default": f.default,
                    "choices": list(f.choices),
                    "remember": bool(f.remember),
                }
                for f in self.fields
            ],
        }


def _render_value(v: Any, ctx: dict[str, Any]) -> Any:
    if isinstance(v, str):
        return interpolate(v, ctx)
    if isinstance(v, list):
        return [_render_value(x, ctx) for x in v]
    if isinstance(v, dict):
        return {k: _render_value(val, ctx) for k, val in v.items()}
    return v


def _eval_or_render(expr_or_value: Any, ctx: dict[str, Any]) -> Any:
    if isinstance(expr_or_value, str):
        rendered = interpolate(expr_or_value, ctx)
        try:
            return eval_expr(rendered, ctx)
        except Exception:
            return rendered
    return _render_value(expr_or_value, ctx)


def _iter_steps(steps) -> Iterable[Any]:
    for step in steps or []:
        yield step
        if hasattr(step, "then_steps"):
            yield from _iter_steps(getattr(step, "then_steps", []) or [])
        if hasattr(step, "else_steps"):
            yield from _iter_steps(getattr(step, "else_steps", []) or [])
        if hasattr(step, "steps") and not isinstance(step, StepPromptForm):
            yield from _iter_steps(getattr(step, "steps", []) or [])
        if hasattr(step, "catch_steps"):
            yield from _iter_steps(getattr(step, "catch_steps", []) or [])
        if hasattr(step, "finally_steps"):
            yield from _iter_steps(getattr(step, "finally_steps", []) or [])


def _profile_fields_from_prompt_step(step: StepPromptForm, ctx: dict[str, Any]) -> tuple[FormField, ...]:
    fields: list[FormField] = []
    for field in step.fields:
        default = _render_value(field.default, ctx)
        choices: list[str] = [str(x) for x in _render_value(field.choices, ctx)]
        if field.choices_expr is not None:
            resolved = _eval_or_render(field.choices_expr, ctx)
            if isinstance(resolved, (list, tuple)):
                choices = [str(x) for x in resolved]
            else:
                choices = []
        fields.append(
            FormField(
                name=field.name,
                label=interpolate(field.label, ctx) if field.label is not None else field.name,
                kind=field.kind,
                default=default,
                choices=choices,
                remember=bool(getattr(field, "remember", True)),
            )
        )
    return tuple(fields)


def build_prompt_profile_definitions(project: Project) -> dict[str, PromptProfileDefinition]:
    out: dict[str, PromptProfileDefinition] = {}

    for macro_name, macro in project.macros.items():
        macro_ctx = {"macro": {"name": macro_name}}
        for step in _iter_steps(getattr(macro, "steps", []) or []):
            if not isinstance(step, StepPromptForm):
                continue
            try:
                profile_key = interpolate(step.profile_key, macro_ctx) if step.profile_key is not None else None
            except Exception:
                profile_key = step.profile_key
            if not profile_key:
                profile_key = f"macro:{macro_name}:prompt:{step.out_var}"
            if profile_key not in out:
                try:
                    title = interpolate(step.title, macro_ctx) if step.title is not None else None
                except Exception:
                    title = step.title
                try:
                    text = interpolate(step.text, macro_ctx) if step.text is not None else None
                except Exception:
                    text = step.text
                out[str(profile_key)] = PromptProfileDefinition(
                    profile_key=str(profile_key),
                    source="prompt_form",
                    macro=macro_name,
                    preset=None,
                    title=title,
                    text=text,
                    fields=_profile_fields_from_prompt_step(step, macro_ctx),
                )

        for preset in getattr(macro, "presets", []) or []:
            preset_name = str(getattr(preset, "name", "") or "").strip()
            if not preset_name:
                continue
            prompt_form = getattr(preset, "prompt_form", None)
            if prompt_form is None:
                continue
            prompt_ctx = {"macro": {"name": macro_name}, "preset": {"name": preset_name}, **dict(getattr(preset, "vars", {}) or {})}
            try:
                materialized = materialize_preset_prompt_form(prompt_form, prompt_ctx, saved_values=None)
            except Exception:
                materialized = None
            if materialized is None or not materialized.profile_key:
                continue
            profile_key = str(materialized.profile_key)
            if profile_key not in out:
                out[profile_key] = PromptProfileDefinition(
                    profile_key=profile_key,
                    source="preset_prompt",
                    macro=macro_name,
                    preset=preset_name,
                    title=materialized.title,
                    text=materialized.text,
                    fields=tuple(materialized.fields),
                )

    return dict(sorted(out.items()))


def find_prompt_profile_definition(project: Project, profile_key: str) -> PromptProfileDefinition | None:
    return build_prompt_profile_definitions(project).get(str(profile_key))
