from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from vhk.core.models import Macro, MacroPreset, MacroPresetPrompt, Project


@dataclass(frozen=True)
class ResolvedPreset:
    macro_name: str
    macro: Macro
    preset_name: str | None = None
    preset: MacroPreset | None = None
    vars: dict[str, Any] = field(default_factory=dict)
    prompt_form: MacroPresetPrompt | None = None

    @property
    def entry_id(self) -> str:
        if self.preset_name:
            return f"{self.macro_name}@{self.preset_name}"
        return self.macro_name


def resolve_macro_preset(project: Project, macro_name: str, *, preset_name: str | None = None) -> ResolvedPreset:
    if macro_name not in project.macros:
        raise KeyError(macro_name)

    macro = project.macros[macro_name]
    if not preset_name:
        return ResolvedPreset(macro_name=macro_name, macro=macro, preset_name=None, preset=None, vars={}, prompt_form=None)

    wanted = str(preset_name).strip()
    for preset in macro.presets:
        if str(preset.name).strip() == wanted:
            return ResolvedPreset(
                macro_name=macro_name,
                macro=macro,
                preset_name=wanted,
                preset=preset,
                vars=dict(preset.vars or {}),
                prompt_form=preset.prompt_form,
            )
    raise KeyError(f"{macro_name}@{wanted}")
